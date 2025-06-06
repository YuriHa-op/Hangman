package server.handler;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

public class MultiplayerGameState {
    private final String lobbyId;
    private final List<String> players;
    private final Set<String> allPlayersEver;
    private final Map<String, Integer> playerScores;
    private final Map<String, StringBuilder> playerProgress;
    private final Map<String, Set<Character>> playerGuesses;
    private final Map<String, Integer> playerIncorrectGuesses;
    private final Map<String, Long> playerFinishTimes;
    private final Map<String, Integer> playerMisses;
    private final Map<String, Integer> playerWinStreaks;
    private final Map<String, String> playerCurrentWords;
    private String currentWord;
    private int currentRound;
    private boolean roundInProgress;
    private volatile long roundStartTime;
    private final int roundTimeSeconds;
    private final WordManager wordManager;
    private final Map<Integer, String> roundWinners = new HashMap<>();
    private final Map<String, Integer> playerRoundWins;
    private String gameWinner = null;
    private final List<RoundResult> roundResults = new ArrayList<>();
    private final String gameId = UUID.randomUUID().toString();
    private final List<String> matchWords = new ArrayList<>();
    private boolean gameWinProcessed = false;
    private boolean roundPotentiallyStalled = false;
    private final Map<String, Boolean> playerReady = new ConcurrentHashMap<>();

    public MultiplayerGameState(String lobbyId, List<String> players, WordManager wordManager, int roundTimeSeconds) {
        this.lobbyId = lobbyId;
        this.players = new ArrayList<>(players);
        this.allPlayersEver = new HashSet<>(players);
        this.wordManager = wordManager;
        this.roundTimeSeconds = roundTimeSeconds;
        this.playerScores = new ConcurrentHashMap<>();
        this.playerProgress = new ConcurrentHashMap<>();
        this.playerGuesses = new ConcurrentHashMap<>();
        this.playerIncorrectGuesses = new ConcurrentHashMap<>();
        this.playerFinishTimes = new ConcurrentHashMap<>();
        this.playerMisses = new ConcurrentHashMap<>();
        this.currentRound = -1;
        this.roundInProgress = false;
        this.playerWinStreaks = new ConcurrentHashMap<>();
        this.playerRoundWins = new ConcurrentHashMap<>();
        this.playerCurrentWords = new ConcurrentHashMap<>();
        
        for (String player : players) {
            playerScores.put(player, 0);
            playerGuesses.put(player, new HashSet<>());
            playerMisses.put(player, 0);
            playerWinStreaks.put(player, 0);
        }
        List<String> allWords = new ArrayList<>(wordManager.getWords());
        Collections.shuffle(allWords);
        matchWords.addAll(allWords);
        resetPlayerReady();
    }

    public synchronized boolean startNewRound() {
        if (roundInProgress) return false;
        
        currentRound++;
        roundPotentiallyStalled = false;
        
        currentWord = selectNewWord();
        
        if (currentWord == null) {
            currentRound--;
            return false;
        }

        roundInProgress = true;
        roundStartTime = System.currentTimeMillis();
        
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
        
        return true;
    }

    private String selectNewWord() {
        if (matchWords.isEmpty()) return null;
        if (currentRound < 0) return null;

        int idx = currentRound % matchWords.size();
        return matchWords.get(idx);
    }

    public synchronized boolean makeGuess(String username, char letter) {
        if (!roundInProgress || !players.contains(username)) return false;
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
            if (misses >= 5) {
                playerFinishTimes.putIfAbsent(username, System.currentTimeMillis());
            }
        }

        if (!progress.toString().contains("_")) {
            playerFinishTimes.putIfAbsent(username, System.currentTimeMillis());
        }

        checkRoundCompletion();
        return correct;
    }

    private void checkRoundCompletion() {
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

        finishers.sort(Map.Entry.comparingByValue());

        String actualRoundWinner = "";
        if (!finishers.isEmpty()) {
            String winner = finishers.get(0).getKey();
            roundWinners.put(currentRound, winner);
            int wins = playerRoundWins.getOrDefault(winner, 0) + 1;
            playerRoundWins.put(winner, wins);
            playerScores.put(winner, wins);
            if (wins >= 3 && gameWinner == null) {
                gameWinner = winner;
            }
            actualRoundWinner = winner;
        } else {
            roundWinners.put(currentRound, "");
        }

        if (!actualRoundWinner.isEmpty()) {
            for (String player : players) {
                if (player.equals(actualRoundWinner)) {
                    playerWinStreaks.put(player, playerWinStreaks.getOrDefault(player, 0) + 1);
                } else {
                    playerWinStreaks.put(player, 0);
                }
            }
        } else {
            for (String player : players) {
                playerWinStreaks.put(player, 0);
            }
            roundPotentiallyStalled = true;
        }

        roundResults.add(new RoundResult(currentRound + 1, currentWord, actualRoundWinner));
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

    public boolean isPlayerFinished(String username) {
        return playerFinishTimes.containsKey(username) ||
               playerMisses.getOrDefault(username, 0) >= 6 ||
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
        public final long gameEndTime;

        public MatchResult(String gameId, int totalRounds, String overallWinner, List<String> players, List<RoundResult> rounds, long gameEndTime) {
            this.gameId = gameId;
            this.totalRounds = totalRounds;
            this.overallWinner = overallWinner;
            this.players = players;
            this.rounds = rounds;
            this.gameEndTime = gameEndTime;
        }
    }

    public MatchResult getMatchResult() {
        return new MatchResult(
            gameId,
            currentRound + 1,
            gameWinner,
            new ArrayList<>(allPlayersEver),
            new ArrayList<>(roundResults),
            System.currentTimeMillis()
        );
    }

    public synchronized void forceEndRound() {
        if (roundInProgress) {
            endRound();
        }
    }

    public synchronized boolean isGameWinProcessed() {
        return gameWinProcessed;
    }

    public synchronized void setGameWinProcessed(boolean gameWinProcessed) {
        this.gameWinProcessed = gameWinProcessed;
    }

    public Map<String, String> getAllMaskedWords() {
        Map<String, String> map = new HashMap<>();
        for (String player : players) {
            map.put(player, getMaskedWord(player));
        }
        return map;
    }

    public Map<String, Integer> getAllIncorrectGuesses() {
        Map<String, Integer> map = new HashMap<>();
        for (String player : players) {
            map.put(player, getIncorrectGuesses(player));
        }
        return map;
    }

    public Map<String, Set<Character>> getAllPlayerGuesses() {
        Map<String, Set<Character>> map = new HashMap<>();
        for (String player : players) {
            map.put(player, getPlayerGuesses(player));
        }
        return map;
    }

    public Map<String, String> getAllCurrentWords() {
        Map<String, String> map = new HashMap<>();
        for (String player : players) {
            map.put(player, currentWord != null ? currentWord : "");
        }
        return map;
    }

    public Map<String, Integer> getPlayerWinStreaks() {
        return new HashMap<>(playerWinStreaks);
    }

    public boolean isRoundPotentiallyStalled() {
        return roundPotentiallyStalled;
    }

    public Map<String, Long> getAllPlayerFinishTimes() {
        return new ConcurrentHashMap<>(playerFinishTimes);
    }

    public synchronized void recordPlayerJoined(String username) {
        allPlayersEver.add(username);
    }

    public String getGameId() {
        return this.gameId;
    }

    public synchronized void removePlayer(String username) {
        players.remove(username);
        playerScores.remove(username);
        playerProgress.remove(username);
        playerGuesses.remove(username);
        playerIncorrectGuesses.remove(username);
        playerFinishTimes.remove(username);
        playerMisses.remove(username);
        playerWinStreaks.remove(username);
        playerRoundWins.remove(username);
        playerCurrentWords.remove(username);
        playerReady.remove(username);
    }

    public void setPlayerReady(String username) {
        playerReady.put(username, true);
    }

    public boolean areAllPlayersReady() {
        for (String player : players) {
            if (!Boolean.TRUE.equals(playerReady.get(player))) {
                return false;
            }
        }
        return true;
    }

    public void resetPlayerReady() {
        for (String player : players) {
            playerReady.put(player, false);
        }
    }
} 