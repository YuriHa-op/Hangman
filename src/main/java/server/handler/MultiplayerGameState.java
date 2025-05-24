package server.handler;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

public class MultiplayerGameState {
    private final String lobbyId;
    private final List<String> players;
    private final Map<String, Integer> playerScores;
    private final Map<String, StringBuilder> playerProgress;
    private final Map<String, Set<Character>> playerGuesses;
    private final Map<String, Long> playerFinishTimes;
    private final Map<String, Integer> playerMisses;
    private String currentWord;
    private int currentRound;
    private boolean roundInProgress;
    private long roundStartTime;
    private final int roundTimeSeconds;
    private final WordManager wordManager;
    private final Map<Integer, String> roundWinners = new HashMap<>(); // round -> winner username
    private final Map<String, Integer> playerRoundWins = new HashMap<>(); // player -> rounds won
    private String gameWinner = null;
    private final List<RoundResult> roundResults = new ArrayList<>();
    private final String gameId = UUID.randomUUID().toString();
    private final List<String> matchWords = new ArrayList<>(); // Shuffled list of words for this match

    public MultiplayerGameState(String lobbyId, List<String> players, WordManager wordManager, int roundTimeSeconds) {
        this.lobbyId = lobbyId;
        this.players = new ArrayList<>(players);
        this.wordManager = wordManager;
        this.roundTimeSeconds = roundTimeSeconds;
        this.playerScores = new ConcurrentHashMap<>();
        this.playerProgress = new ConcurrentHashMap<>();
        this.playerGuesses = new ConcurrentHashMap<>();
        this.playerFinishTimes = new ConcurrentHashMap<>();
        this.playerMisses = new ConcurrentHashMap<>();
        this.currentRound = 0;
        this.roundInProgress = false;
        
        // Initialize player scores, guesses, and misses
        for (String player : players) {
            playerScores.put(player, 0);
            playerGuesses.put(player, new HashSet<>());
            playerMisses.put(player, 0);
        }
        // Initialize shuffled word list for this match
        List<String> allWords = new ArrayList<>(wordManager.getWords());
        Collections.shuffle(allWords);
        matchWords.addAll(allWords);
    }

    public synchronized boolean startNewRound() {
        if (roundInProgress) return false;
        
        currentWord = selectNewWord();
        if (currentWord == null) return false;

        roundInProgress = true;
        roundStartTime = System.currentTimeMillis();
        
        // Reset player progress, guesses, and misses for new round
        for (String player : players) {
            StringBuilder maskedWord = new StringBuilder();
            for (int i = 0; i < currentWord.length(); i++) {
                maskedWord.append("_ ");
            }
            playerProgress.put(player, new StringBuilder(maskedWord));
            playerGuesses.get(player).clear();
            playerFinishTimes.remove(player);
            playerMisses.put(player, 0);
        }
        
        currentRound++;
        return true;
    }

    private String selectNewWord() {
        if (matchWords.isEmpty()) return null;
        int idx = currentRound % matchWords.size();
        return matchWords.get(idx);
    }

    public synchronized boolean makeGuess(String username, char letter) {
        if (!roundInProgress || !players.contains(username)) return false;
        // Prevent further guesses if player is finished (guessed word or 5 misses)
        if (isPlayerFinished(username)) return false;
        
        Set<Character> guesses = playerGuesses.get(username);
        if (guesses.contains(letter)) return false;
        
        guesses.add(letter);
        StringBuilder progress = playerProgress.get(username);
        boolean correct = false;
        
        for (int i = 0; i < currentWord.length(); i++) {
            if (currentWord.charAt(i) == letter) {
                progress.setCharAt(i * 2, letter);
                correct = true;
            }
        }

        if (!correct) {
            int misses = playerMisses.getOrDefault(username, 0) + 1;
            playerMisses.put(username, misses);
            // If player reaches 5 misses, mark as finished
            if (misses >= 5) {
                playerFinishTimes.putIfAbsent(username, System.currentTimeMillis());
            }
        }

        // Check if player has completed the word
        if (!progress.toString().contains("_")) {
            playerFinishTimes.putIfAbsent(username, System.currentTimeMillis());
        }

        // Always check round completion after a guess
        checkRoundCompletion();
        return correct;
    }

    private void checkRoundCompletion() {
        // Check if all players have finished (guessed word or 5 misses) or time is up
        boolean allFinished = players.stream().allMatch(p -> 
            playerFinishTimes.containsKey(p) || 
            playerMisses.getOrDefault(p, 0) >= 5 || 
            System.currentTimeMillis() - roundStartTime >= roundTimeSeconds * 1000);
        
        if (allFinished) {
            endRound();
        }
    }

    private void endRound() {
        if (!roundInProgress) return;
        roundInProgress = false;

        // Find players who completed the word (guessed all letters)
        List<Map.Entry<String, Long>> finishers = new ArrayList<>();
        for (String player : players) {
            StringBuilder progress = playerProgress.get(player);
            if (progress != null && !progress.toString().contains("_")) {
                Long finishTime = playerFinishTimes.get(player);
                if (finishTime != null) {
                    finishers.add(new AbstractMap.SimpleEntry<>(player, finishTime));
                }
            }
        }

        // Sort by finish time
        finishers.sort(Map.Entry.comparingByValue());

        String roundWinner = "";
        if (!finishers.isEmpty()) {
            String winner = finishers.get(0).getKey();
            roundWinners.put(currentRound, winner);
            // Increment round wins
            int wins = playerRoundWins.getOrDefault(winner, 0) + 1;
            playerRoundWins.put(winner, wins);
            // Increment score (for UI)
            playerScores.put(winner, wins); // Keep scores in sync with round wins
            // Check for game winner (first to 3 round wins)
            if (wins >= 3 && gameWinner == null) {
                gameWinner = winner;
            }
            roundWinner = winner;
        } else {
            // No winner for this round
            roundWinners.put(currentRound, "");
        }
        // Track round result for DB
        roundResults.add(new RoundResult(currentRound, currentWord, roundWinner));
    }

    public String getMaskedWord(String username) {
        return playerProgress.getOrDefault(username, new StringBuilder()).toString();
    }

    public int getScore(String username) {
        return playerScores.getOrDefault(username, 0);
    }

    public Map<String, Integer> getScores() {
        return new HashMap<>(playerScores);
    }

    public int getCurrentRound() {
        return currentRound;
    }

    public boolean isRoundInProgress() {
        return roundInProgress;
    }

    public int getRemainingTime() {
        if (!roundInProgress) return 0;
        long elapsed = (System.currentTimeMillis() - roundStartTime) / 1000;
        return Math.max(0, roundTimeSeconds - (int)elapsed);
    }

    public String getLobbyId() {
        return lobbyId;
    }

    public List<String> getPlayers() {
        return new ArrayList<>(players);
    }

    public String getCurrentWord() {
        return currentWord;
    }

    public Long getPlayerFinishTime(String username) {
        return playerFinishTimes.get(username);
    }

    public Set<Character> getPlayerGuesses(String username) {
        return new HashSet<>(playerGuesses.getOrDefault(username, new HashSet<>()));
    }

    public int getIncorrectGuesses(String username) {
        return playerMisses.getOrDefault(username, 0);
    }

    // Add a method to check if a player is finished (guessed word or 5 misses)
    public boolean isPlayerFinished(String username) {
        return playerFinishTimes.containsKey(username) ||
               playerMisses.getOrDefault(username, 0) >= 5 ||
               (playerProgress.containsKey(username) && !playerProgress.get(username).toString().contains("_"));
    }

    public String getRoundWinner() {
        return roundWinners.getOrDefault(currentRound, "");
    }

    public String getGameWinner() {
        return gameWinner;
    }

    public int getPlayerRoundWins(String username) {
        return playerRoundWins.getOrDefault(username, 0);
    }

    // --- Add for match result tracking ---
    public static class RoundResult {
        public final int roundNumber;
        public final String word;
        public final String winner;
        public RoundResult(int roundNumber, String word, String winner) {
            this.roundNumber = roundNumber;
            this.word = word;
            this.winner = winner;
        }
    }
    public static class MatchResult {
        public final String gameId;
        public final int totalRounds;
        public final String overallWinner;
        public final List<String> players;
        public final List<RoundResult> rounds;
        public MatchResult(String gameId, int totalRounds, String overallWinner, List<String> players, List<RoundResult> rounds) {
            this.gameId = gameId;
            this.totalRounds = totalRounds;
            this.overallWinner = overallWinner;
            this.players = players;
            this.rounds = rounds;
        }
    }

    // --- Add method to get match result for DB ---
    public MatchResult getMatchResult() {
        return new MatchResult(
            gameId,
            currentRound,
            gameWinner,
            new ArrayList<>(players),
            new ArrayList<>(roundResults)
        );
    }
} 