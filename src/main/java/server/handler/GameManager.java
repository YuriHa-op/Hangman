package server.handler;

import java.util.*;
import java.util.function.Consumer;
import java.sql.*;
import server.dto.GameStateDTO;

public class GameManager {
    private final WordManager wordManager;
    private final PlayerManager playerManager;
    private Consumer<String> logCallback;

    // Game state fields
    private Map<String, String> activeGames = new HashMap<>();
    private Map<String, StringBuilder> playerProgress = new HashMap<>();
    private Map<String, Map<Integer, Boolean>> roundFinished = new HashMap<>();
    private Map<String, List<String>> playerWords = new HashMap<>();
    private Map<String, Integer> missedGuesses = new HashMap<>();
    private Map<String, Long> roundStartTime = new HashMap<>();
    private static final int MAX_MISSES = 5;
    private Map<String, Integer> playerRounds = new HashMap<>();
    private Map<String, Integer> playerWins = new HashMap<>();
    private Map<String, Long> waitingPlayers = new HashMap<>();
    private Map<String, String> matchedPlayers = new HashMap<>();
    private Map<String, String> gameSessionResult = new HashMap<>();
    private Map<String, Map<Integer, Long>> roundFinishTime = new HashMap<>();
    private Map<String, Map<Integer, Boolean>> roundGuessedWord = new HashMap<>();
    private Map<String, Map<Integer, String>> lastRoundWinner = new HashMap<>();

    public GameManager(WordManager wordManager, PlayerManager playerManager) {
        this.wordManager = wordManager;
        this.playerManager = playerManager;
    }

    public void setLogCallback(Consumer<String> callback) {
        this.logCallback = callback;
    }


    private void setGameSessionResult(String username, String result) {
        if (username != null) {
            gameSessionResult.put(username, result);
        }
    }

    public int getActivePlayers() {
        // Players in a game or waiting for a match
        Set<String> players = new HashSet<>();
        players.addAll(activeGames.keySet());
        players.addAll(waitingPlayers.keySet());
        return players.size();
    }

    public int getActiveGames() {
        // Each game is a unique pair of matched players
        return matchedPlayers.size() / 2;
    }

    public boolean sendGuess(String username, char letter) {
        if (roundFinished.getOrDefault(username, Collections.emptyMap()).getOrDefault(playerRounds.getOrDefault(username, 0), false)) {
            return false;
        }
        if (!activeGames.containsKey(username)) {
            return false;
        }
        String targetWord = activeGames.get(username);
        StringBuilder progress = playerProgress.get(username);
        long startTime = roundStartTime.getOrDefault(username, 0L);
        int roundTime = playerManager.getRoundTime();
        if (System.currentTimeMillis() - startTime > roundTime * 1000) {
            endGame(username, false);
            return false;
        }
        boolean correctGuess = false;
        for (int i = 0; i < targetWord.length(); i++) {
            if (targetWord.charAt(i) == letter) {
                progress.setCharAt(i * 2, letter);
                correctGuess = true;
            }
        }
        if (!correctGuess) {
            int misses = missedGuesses.getOrDefault(username, 0) + 1;
            missedGuesses.put(username, misses);
            if (misses >= MAX_MISSES) {
                endGame(username, false);
                return false;
            }
        }
        if (!progress.toString().contains("_")) {
            endGame(username, true);
            return correctGuess;
        }
        return correctGuess;
    }

    public String getMaskedWord(String username) {
        StringBuilder progress = playerProgress.get(username);
        return (progress != null) ? progress.toString() : "";
    }

    public String startGame(String username) {
        endGameSession(username); // Always clean up any old state first
        if (activeGames.containsKey(username)) {
            return "You are already in a game.";
        }

        waitingPlayers.remove(username);
        String matchedPlayer = findWaitingPlayer();
        if (matchedPlayer != null && !matchedPlayer.equals(username)) {
            // Generate a large shuffled list of unique words for this match
            List<String> allWords = new ArrayList<>(wordManager.getWords());
            Collections.shuffle(allWords);
            int wordCount = Math.min(20, allWords.size());
            List<String> matchWords = new ArrayList<>(allWords.subList(0, wordCount));
            String word = matchWords.get(0);
            setupMatchedPlayers(username, matchedPlayer, matchWords, word);
            StringBuilder maskedWord = new StringBuilder();
            for (int i = 0; i < word.length(); i++) {
                maskedWord.append("_ ");
            }
            return maskedWord.toString();
        } else {
            waitingPlayers.put(username, System.currentTimeMillis());
            cleanupPlayerState(username);
            return "WAITING_FOR_MATCH";
        }

    }

    private void setupMatchedPlayers(String player1, String player2, List<String> wordList, String firstWord) {
        playerWords.put(player1, new ArrayList<>(wordList));
        playerWords.put(player2, new ArrayList<>(wordList));
        playerRounds.put(player1, 0);
        playerRounds.put(player2, 0);
        activeGames.put(player1, firstWord);
        activeGames.put(player2, firstWord);
        StringBuilder maskedWord = new StringBuilder();
        for (int i = 0; i < firstWord.length(); i++) {
            maskedWord.append("_ ");
        }
        playerProgress.put(player1, new StringBuilder(maskedWord));
        playerProgress.put(player2, new StringBuilder(maskedWord));
        matchedPlayers.put(player1, player2);
        matchedPlayers.put(player2, player1);
        waitingPlayers.remove(player2);
        missedGuesses.put(player1, 0);
        missedGuesses.put(player2, 0);
        roundStartTime.put(player1, System.currentTimeMillis());
        roundStartTime.put(player2, System.currentTimeMillis());
        playerWins.put(player1, 0);
        playerWins.put(player2, 0);
        roundFinished.computeIfAbsent(player1, k -> new HashMap<>()).put(0, false);
        roundFinished.computeIfAbsent(player2, k -> new HashMap<>()).put(0, false);
    }

    private String findWaitingPlayer() {
        long currentTime = System.currentTimeMillis();
        List<String> playersToRemove = new ArrayList<>();
        String matchedPlayer = null;
        for (Map.Entry<String, Long> entry : waitingPlayers.entrySet()) {
            String waitingUsername = entry.getKey();
            long waitingStartTime = entry.getValue();
            if (currentTime - waitingStartTime <= playerManager.getWaitingTime() * 1000) {
                if (matchedPlayer == null) {
                    matchedPlayer = waitingUsername;
                }
            } else {
                playersToRemove.add(waitingUsername);
            }
        }
        for (String username : playersToRemove) {
            waitingPlayers.remove(username);
        }
        return matchedPlayer;
    }

   public void endGame(String username, boolean recordStats) {
       if (roundFinished.getOrDefault(username, Collections.emptyMap()).getOrDefault(playerRounds.getOrDefault(username, 0), false)) {
           return;
       }
       if (username == null) {
           return;
       }
       if (!activeGames.containsKey(username)) {
           return;
       }
   }

    public void finishRound(String username, long clientRemainingTime, boolean guessedWord) {
        int currentRound = playerRounds.getOrDefault(username, 0);
        System.out.println("[DEBUG] finishRound called for " + username + ", guessedWord=" + guessedWord + ", clientRemainingTime=" + clientRemainingTime + ", round=" + currentRound);
        roundFinished.computeIfAbsent(username, k -> new HashMap<>()).put(currentRound, true);
        roundGuessedWord.computeIfAbsent(username, k -> new HashMap<>()).put(currentRound, guessedWord);
        // Store the finish time as the remaining time reported by the client
        roundFinishTime.computeIfAbsent(username, k -> new HashMap<>()).put(currentRound, clientRemainingTime);
        String opponent = matchedPlayers.get(username);
        int opponentRound = playerRounds.getOrDefault(opponent, 0);
        System.out.println("[DEBUG] finishRound: opponent=" + opponent + ", opponent finished=" + (opponent != null && roundFinished.containsKey(opponent) && roundFinished.get(opponent).getOrDefault(currentRound, false)));
        if (opponent != null && roundFinished.containsKey(opponent) && roundFinished.get(opponent).getOrDefault(currentRound, false)) {
            determineRoundWinner(username, currentRound);
        }
    }

    private void determineRoundWinner(String username, int round) {
        String opponent = matchedPlayers.get(username);
        // Prevent double counting
        if (lastRoundWinner.getOrDefault(username, Collections.emptyMap()).containsKey(round)) {
            System.out.println("[DEBUG] determineRoundWinner: winner already set for round " + round);
            return;
        }
        System.out.println("[DEBUG] determineRoundWinner called for " + username + " vs " + opponent + " round=" + round);
        if (opponent == null) return;
        boolean playerGuessed = roundGuessedWord.getOrDefault(username, Collections.emptyMap()).getOrDefault(round, false);
        boolean opponentGuessed = roundGuessedWord.getOrDefault(opponent, Collections.emptyMap()).getOrDefault(round, false);
        System.out.println("[DEBUG] playerGuessed=" + playerGuessed + ", opponentGuessed=" + opponentGuessed);
        if (!(roundFinished.getOrDefault(username, Collections.emptyMap()).getOrDefault(round, false) && roundFinished.getOrDefault(opponent, Collections.emptyMap()).getOrDefault(round, false))) {
            System.out.println("[DEBUG] determineRoundWinner: not both finished");
            return; // Wait until both are finished
        }
        String winner = null;
        if (playerGuessed && opponentGuessed) {
            long playerTime = roundFinishTime.getOrDefault(username, Collections.emptyMap()).getOrDefault(round, Long.MIN_VALUE);
            long opponentTime = roundFinishTime.getOrDefault(opponent, Collections.emptyMap()).getOrDefault(round, Long.MIN_VALUE);
            System.out.println("[DEBUG] Both guessed: " + username + " time=" + playerTime + ", " + opponent + " time=" + opponentTime);
            if (playerTime > opponentTime) {
                incrementRoundWin(username);
                winner = username;
            } else if (opponentTime > playerTime) {
                incrementRoundWin(opponent);
                winner = opponent;
            }
            // If equal, no one wins (tie)
        } else if (playerGuessed) {
            incrementRoundWin(username);
            winner = username;
        } else if (opponentGuessed) {
            incrementRoundWin(opponent);
            winner = opponent;
        }
        // else: no one wins
        System.out.println("[DEBUG] Winner for this round: " + winner);
        lastRoundWinner.computeIfAbsent(username, k -> new HashMap<>()).put(round, winner);
        lastRoundWinner.computeIfAbsent(opponent, k -> new HashMap<>()).put(round, winner);
    }

    private void incrementRoundWin(String username) {
        int wins = playerWins.getOrDefault(username, 0) + 1;
        playerWins.put(username, wins);
        System.out.println("[DEBUG] incrementRoundWin: " + username + " now has " + wins + " wins");
        // Check for game session win
        String opponent = matchedPlayers.get(username);
        int opponentWins = opponent != null ? playerWins.getOrDefault(opponent, 0) : 0;
        if (wins >= 3) {
            setGameSessionResult(username, "WIN");
            if (opponent != null) {
                setGameSessionResult(opponent, "LOSE");
            }
            // Persist win count in the database
            playerManager.updatePlayerWins(username, wins);
        } else if (opponent != null && opponentWins >= 3) {
            setGameSessionResult(opponent, "WIN");
            setGameSessionResult(username, "LOSE");
            // Persist win count for opponent
            playerManager.updatePlayerWins(opponent, opponentWins);
        }
    }

    private void cleanupPlayerState(String username) {
        activeGames.remove(username);
        playerProgress.remove(username);
        missedGuesses.remove(username);
        roundStartTime.remove(username);
        playerRounds.remove(username);
        playerWins.remove(username);
        playerWords.remove(username);
        matchedPlayers.remove(username);
        roundFinished.remove(username);
        roundFinishTime.remove(username);
        roundGuessedWord.remove(username);
        lastRoundWinner.remove(username);
    }

    public int getRemainingTime(String username) {
        if (!roundStartTime.containsKey(username)) return 0;
        long elapsed = (System.currentTimeMillis() - roundStartTime.get(username)) / 1000;
        int roundTime = playerManager.getRoundTime();
        int remaining = roundTime - (int) elapsed;
        if (remaining <= 0) {
            roundFinished.computeIfAbsent(username, k -> new HashMap<>()).put(playerRounds.getOrDefault(username, 0), true);
            endGame(username, false);
            // After ending the game for this player, check if opponent is also finished and determine winner
            String opponent = matchedPlayers.get(username);
            if (opponent != null && roundFinished.containsKey(opponent) && roundFinished.get(opponent).getOrDefault(playerRounds.getOrDefault(username, 0), false)) {
                determineRoundWinner(username, playerRounds.getOrDefault(username, 0));
            }
            return 0;
        }
        return remaining;
    }

    public int getIncorrectGuesses(String username) {
        return missedGuesses.getOrDefault(username, 0);
    }

    public int getCurrentRound(String username) {
        return playerRounds.getOrDefault(username, 0);
    }

    public int getPlayerWins(String username) {
        return playerWins.getOrDefault(username, 0);
    }

    public boolean startNewRound(String username) {
        boolean isFinished = roundFinished.getOrDefault(username, Collections.emptyMap()).getOrDefault(playerRounds.getOrDefault(username, 0), false);
        int currentRound = playerRounds.getOrDefault(username, 0);
        String opponent = matchedPlayers.get(username);
        int playerWinsCount = getPlayerWins(username);
        int opponentWinsCount = opponent != null ? getPlayerWins(opponent) : 0;
        if (isFinished && playerWinsCount < 3 && opponentWinsCount < 3) {
            int newRound = currentRound + 1;
            playerRounds.put(username, newRound);
            List<String> wordList = playerWords.get(username);
            List<String> opponentWordList = opponent != null ? playerWords.get(opponent) : null;
            // If wordList is exhausted, pick a new word from the global pool that hasn't been used in this match
            String nextWord = null;
            if (wordList != null && wordList.size() > newRound) {
                nextWord = wordList.get(newRound);
            } else {
                Set<String> usedWords = new HashSet<>(wordList != null ? wordList : Collections.emptyList());
                List<String> allWords = new ArrayList<>(wordManager.getWords());
                Collections.shuffle(allWords);
                for (String w : allWords) {
                    if (!usedWords.contains(w)) {
                        nextWord = w;
                        wordList.add(w);
                        if (opponentWordList != null && opponentWordList.size() == wordList.size() - 1) {
                            opponentWordList.add(w);
                        }
                        break;
                    }
                }
                if (nextWord == null) {
                    // fallback: just reuse a random word
                    nextWord = allWords.get(0);
                    wordList.add(nextWord);
                    if (opponentWordList != null && opponentWordList.size() == wordList.size() - 1) {
                        opponentWordList.add(nextWord);
                    }
                }
            }
            activeGames.put(username, nextWord);
            StringBuilder maskedWord = new StringBuilder();
            for (int i = 0; i < nextWord.length(); i++) {
                maskedWord.append("_ ");
            }
            playerProgress.put(username, new StringBuilder(maskedWord));
            missedGuesses.put(username, 0);
            roundStartTime.put(username, System.currentTimeMillis());
            roundFinished.computeIfAbsent(username, k -> new HashMap<>()).put(newRound, false);
            // Reset round finish time and guessed status
            roundFinishTime.computeIfAbsent(username, k -> new HashMap<>()).remove(newRound);
            roundGuessedWord.computeIfAbsent(username, k -> new HashMap<>()).remove(newRound);
            // Clear last round winner for new round
            lastRoundWinner.computeIfAbsent(username, k -> new HashMap<>()).remove(newRound);
            return true;
        }
        return false;
    }

    public boolean isRoundOver(String username) {
        if (!activeGames.containsKey(username)) return true;
        String maskedWord = getMaskedWord(username);
        boolean timeUp = getRemainingTime(username) <= 0;
        return !maskedWord.contains("_") || getIncorrectGuesses(username) >= 5 || timeUp;
    }

    public boolean isGameSessionOver(String username) {
        String opponent = matchedPlayers.getOrDefault(username, null);
        int playerWins = getPlayerWins(username);
        int opponentWins = opponent != null ? getPlayerWins(opponent) : 0;
        return playerWins >= 3 || opponentWins >= 3;
    }

    public boolean isGameSessionWinner(String username) {
        return getPlayerWins(username) >= 3;
    }

    public String getGameSessionResult(String username) {
        String opponent = matchedPlayers.getOrDefault(username, null);
        int playerWins = getPlayerWins(username);
        int opponentWins = opponent != null ? getPlayerWins(opponent) : 0;
        if (playerWins >= 3) {
            return "WIN";
        } else if (opponentWins >= 3) {
            return "LOSE";
        }
        return "ONGOING";
    }

    public GameStateDTO getGameState(String username) {
        GameStateDTO dto = new GameStateDTO();
        if (waitingPlayers.containsKey(username)) {
            dto.maskedWord = "WAITING_FOR_MATCH";
            dto.incorrectGuesses = 0;
            dto.currentRound = 0;
            dto.totalRounds = 0;
            dto.playerWins = 0;
            dto.roundOver = false;
            dto.gameOver = false;
            dto.sessionResult = "";
            dto.remainingTime = 0;
            dto.roundWinner = null;
            return dto;
        }
        String maskedWord = getMaskedWord(username);
        dto.maskedWord = (maskedWord != null) ? maskedWord : "";
        dto.incorrectGuesses = getIncorrectGuesses(username);
        int currentRound = getCurrentRound(username);
        dto.currentRound = currentRound;
        dto.totalRounds = 0; // Not used anymore
        dto.playerWins = getPlayerWins(username);
        dto.roundOver = isRoundOver(username);
        dto.gameOver = isGameSessionOver(username);
        String sessionResult = getGameSessionResult(username);
        dto.sessionResult = (sessionResult != null) ? sessionResult : "";
        dto.remainingTime = getRemainingTime(username);
        // Set finishedTime for this player (0 if not finished)
        dto.finishedTime = roundFinishTime.getOrDefault(username, Collections.emptyMap()).getOrDefault(currentRound, 0L).intValue();
        // Only set roundWinner if both players finished the round
        String opponent = matchedPlayers.get(username);
        if (dto.roundOver && opponent != null &&
            roundFinished.getOrDefault(username, Collections.emptyMap()).getOrDefault(currentRound, false) &&
            roundFinished.getOrDefault(opponent, Collections.emptyMap()).getOrDefault(currentRound, false)) {
            String winner = lastRoundWinner.getOrDefault(username, Collections.emptyMap()).getOrDefault(currentRound, null);
            dto.roundWinner = (winner != null) ? winner : "";
        } else {
            dto.roundWinner = "";
        }
        return dto;
    }

    // Add a public method to fully reset a player's session and their match
    public void endGameSession(String username) {
        String opponent = matchedPlayers.get(username);
        cleanupPlayerState(username);
        if (opponent != null) {
            cleanupPlayerState(opponent);
            gameSessionResult.remove(opponent);
        }
        gameSessionResult.remove(username);
    }
} 