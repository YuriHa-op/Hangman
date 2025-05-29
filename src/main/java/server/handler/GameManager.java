package server.handler;

import java.util.*;
import java.util.function.Consumer;
import java.sql.*;
import server.dto.GameStateDTO;
import server.dto.SPSinglePlayerRoundInfoDTO;
import java.util.UUID;
import GameModule.Bool;

public class GameManager {
    private final WordManager wordManager;
    private final PlayerManager playerManager;
    private Consumer<String> logCallback;
    private final SinglePlayerMatchResultDAO singlePlayerMatchResultDAO;

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

    // For 1v1 Match History
    private Map<String, String> playerGameSessionIds = new HashMap<>();
    private Map<String, List<SPSinglePlayerRoundInfoDTO>> gameSessionRounds = new HashMap<>();
    private Map<String, Boolean> gameSessionHistorySaved = new HashMap<>();

    public GameManager(WordManager wordManager, PlayerManager playerManager, SinglePlayerMatchResultDAO singlePlayerMatchResultDAO) {
        this.wordManager = wordManager;
        this.playerManager = playerManager;
        this.singlePlayerMatchResultDAO = singlePlayerMatchResultDAO;
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

    public Bool sendGuess(String username, char letter) {
        if (roundFinished.getOrDefault(username, Collections.emptyMap()).getOrDefault(playerRounds.getOrDefault(username, 0), false)) {
            return Bool.BOOL_FALSE; // Round already marked as finished for this player
        }
        if (!activeGames.containsKey(username)) {
            return Bool.BOOL_FALSE; // Player not in an active game
        }

        String targetWord = activeGames.get(username);
        StringBuilder progress = playerProgress.get(username);
        long startTime = roundStartTime.getOrDefault(username, 0L);
        int serverRoundTimeSetting = playerManager.getRoundTime(); // Server's configured round time in seconds

        // Check for round timeout
        if (System.currentTimeMillis() - startTime > serverRoundTimeSetting * 1000L) {
            finishRound(username, 0, Bool.BOOL_FALSE); // Timeout: 0 time left, did not guess
            return Bool.BOOL_FALSE; // Guess does not count as correct due to timeout
        }

        boolean correctGuessForThisLetter = false;
        for (int i = 0; i < targetWord.length(); i++) {
            if (targetWord.charAt(i) == letter) {
                progress.setCharAt(i * 2, letter);
                correctGuessForThisLetter = true;
            }
        }

        // Calculate current remaining time for potential finishRound call
        long currentRemainingTimeSeconds = 0;
        if(roundStartTime.containsKey(username)){
            long elapsedSeconds = (System.currentTimeMillis() - roundStartTime.get(username)) / 1000;
            currentRemainingTimeSeconds = Math.max(0, serverRoundTimeSetting - elapsedSeconds);
        }

        if (!correctGuessForThisLetter) {
            int misses = missedGuesses.getOrDefault(username, 0) + 1;
            missedGuesses.put(username, misses);
            if (misses >= MAX_MISSES) {
                finishRound(username, currentRemainingTimeSeconds, Bool.BOOL_FALSE); // Max misses, word not guessed
                return Bool.BOOL_FALSE; // Current guess was incorrect and led to max misses
            }
        }

        // Check if word is fully guessed (this check should come after processing the current letter's effect)
        if (!progress.toString().contains("_")) { // Word fully guessed
            finishRound(username, currentRemainingTimeSeconds, Bool.BOOL_TRUE); // Word guessed
            // If word is complete, this guess (if correct) or a previous one led to completion.
            // The primary return should reflect if THIS letter was part of the word.
            // However, standard Hangman might just consider the game won at this point.
            // Let's return TRUE if the word is complete, as the state is now 'won round'.
            return Bool.BOOL_TRUE;
        }

        // If game continues, return if this specific guess for *this letter* was correct or not
        return correctGuessForThisLetter ? Bool.BOOL_TRUE : Bool.BOOL_FALSE;
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
            // Generate a unique game ID for this 1v1 match session
            String gameSessionId = UUID.randomUUID().toString();
            playerGameSessionIds.put(username, gameSessionId);
            playerGameSessionIds.put(matchedPlayer, gameSessionId);
            gameSessionRounds.put(gameSessionId, new ArrayList<>());

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

    public void finishRound(String username, long clientRemainingTime, Bool guessedWordBool) {
        boolean guessedWord = guessedWordBool == Bool.BOOL_TRUE;
        int currentRound = playerRounds.getOrDefault(username, 0);
        roundFinished.computeIfAbsent(username, k -> new HashMap<>()).put(currentRound, true);
        roundGuessedWord.computeIfAbsent(username, k -> new HashMap<>()).put(currentRound, guessedWord);
        roundFinishTime.computeIfAbsent(username, k -> new HashMap<>()).put(currentRound, clientRemainingTime);
        String opponent = matchedPlayers.get(username);
        if (opponent != null && roundFinished.containsKey(opponent) && roundFinished.get(opponent).getOrDefault(currentRound, false)) {
            determineRoundWinner(username, currentRound);
        }
    }

    private void determineRoundWinner(String username, int round) {
        String opponent = matchedPlayers.get(username);

        if (opponent == null) return; // Should not happen in a matched game

        // Ensure both players have marked this round as finished on the server.
        boolean playerMarkedFinished = roundFinished.getOrDefault(username, Collections.emptyMap()).getOrDefault(round, false);
        boolean opponentMarkedFinished = roundFinished.getOrDefault(opponent, Collections.emptyMap()).getOrDefault(round, false);

        if (!(playerMarkedFinished && opponentMarkedFinished)) {
            // If not both players have officially finished the round (according to server state),
            // it's too early to determine a winner.
            return;
        }

        // CRITICAL CHECK: Has the winner for this round (for this pair) already been determined and recorded?
        // We check against 'username's map. If it's there, it means the logic below has run.
        // Since lastRoundWinner is updated for both players simultaneously, checking one is enough.
        if (lastRoundWinner.containsKey(username) && lastRoundWinner.get(username).containsKey(round)) {
            // This round's winner determination has already been processed. Do nothing further to prevent duplicates.
            return;
        }
        // As a safeguard, one might also check the opponent; however, if the map is updated for both players
        // when a winner is first determined, checking one player (e.g., the one triggering this call) is sufficient.
        // if (lastRoundWinner.containsKey(opponent) && lastRoundWinner.get(opponent).containsKey(round)) {
        //     return;
        // }

        // Proceed with determining the winner logic as it hasn't been done yet for this round.
        boolean playerGuessed = roundGuessedWord.getOrDefault(username, Collections.emptyMap()).getOrDefault(round, false);
        boolean opponentGuessed = roundGuessedWord.getOrDefault(opponent, Collections.emptyMap()).getOrDefault(round, false);

        if (!(roundFinished.getOrDefault(username, Collections.emptyMap()).getOrDefault(round, false) &&
              roundFinished.getOrDefault(opponent, Collections.emptyMap()).getOrDefault(round, false))) {
            return; // Wait until both are finished
        }

        String roundWinner = null;
        if (playerGuessed && opponentGuessed) {
            long playerTime = roundFinishTime.getOrDefault(username, Collections.emptyMap()).getOrDefault(round, Long.MIN_VALUE);
            long opponentTime = roundFinishTime.getOrDefault(opponent, Collections.emptyMap()).getOrDefault(round, Long.MIN_VALUE);
            if (playerTime > opponentTime) {
                roundWinner = username;
            } else if (opponentTime > playerTime) {
                roundWinner = opponent;
            }
        } else if (playerGuessed) {
            roundWinner = username;
        } else if (opponentGuessed) {
            roundWinner = opponent;
        }

        String gameSessionId = playerGameSessionIds.get(username);
        if (gameSessionId != null && gameSessionRounds.containsKey(gameSessionId)) {
            String wordForRound = activeGames.getOrDefault(username, "");
            if (playerWords.containsKey(username) && playerWords.get(username).size() > round) {
                 wordForRound = playerWords.get(username).get(round);
            }

            gameSessionRounds.get(gameSessionId).add(
                new SPSinglePlayerRoundInfoDTO(round + 1, wordForRound, roundWinner)
            );
        }

        // Record the determined winner (or null if no one won) for both players.
        // This is the state that the guard check above relies on.
        lastRoundWinner.computeIfAbsent(username, k -> new HashMap<>()).put(round, roundWinner);
        lastRoundWinner.computeIfAbsent(opponent, k -> new HashMap<>()).put(round, roundWinner);

        if (roundWinner != null) {
            incrementRoundWin(roundWinner);
        }
    }

    private void incrementRoundWin(String username) {
        int wins = playerWins.getOrDefault(username, 0) + 1;
        playerWins.put(username, wins);

        String opponent = matchedPlayers.get(username);
        int opponentWins = opponent != null ? playerWins.getOrDefault(opponent, 0) : 0;

        boolean gameJustEnded = false;
        String gameSessionId = playerGameSessionIds.get(username);
        String gameWinner = null;

        if (wins >= 3) {
            setGameSessionResult(username, "WIN");
            if (opponent != null) {
                setGameSessionResult(opponent, "LOSE");
            } else {
                setGameSessionResult(username, "WIN (no opponent)");
            }
            gameWinner = username;
            playerManager.updatePlayerWins(username, playerManager.getTotalWins(username) + 1);
            gameJustEnded = true;
        } else if (opponent != null && opponentWins >= 3) {
            setGameSessionResult(opponent, "WIN");
            setGameSessionResult(username, "LOSE");
            gameWinner = opponent;
            playerManager.updatePlayerWins(opponent, playerManager.getTotalWins(opponent) + 1);
            gameJustEnded = true;
        }

        if (gameJustEnded && gameSessionId != null) {
            List<String> playersInGame = new ArrayList<>();
            playersInGame.add(username);
            if (opponent != null) {
                playersInGame.add(opponent);
            }
            List<SPSinglePlayerRoundInfoDTO> rounds = gameSessionRounds.getOrDefault(gameSessionId, new ArrayList<>());
            saveGameSessionHistory(gameSessionId, playersInGame, rounds, gameWinner);
        }
    }

    private void saveGameSessionHistory(String gameSessionId, List<String> players, List<SPSinglePlayerRoundInfoDTO> rounds, String overallWinner) {
        if (gameSessionId != null && singlePlayerMatchResultDAO != null && !gameSessionHistorySaved.getOrDefault(gameSessionId, false)) {
            int totalRoundsPlayed = rounds.size();
            if (players.isEmpty() && !rounds.isEmpty()) {
                System.err.println("[HISTORY SAVE ERROR] Players list is empty for gameSessionId: " + gameSessionId + " but rounds exist. Aborting save.");
                return; 
            }

            SinglePlayerMatchResultDAO.SinglePlayerMatchResult matchResult = new SinglePlayerMatchResultDAO.SinglePlayerMatchResult(
                    gameSessionId,
                    totalRoundsPlayed,
                    overallWinner, 
                    players,
                    rounds,
                    System.currentTimeMillis()
            );
            singlePlayerMatchResultDAO.saveMatchResult(matchResult);
            gameSessionHistorySaved.put(gameSessionId, true); 
        } else if (gameSessionId != null && gameSessionHistorySaved.getOrDefault(gameSessionId, false)) {
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

        String gameSessionId = playerGameSessionIds.remove(username);
        if (gameSessionId != null && !playerGameSessionIds.containsValue(gameSessionId)) {
            gameSessionRounds.remove(gameSessionId);
            gameSessionHistorySaved.remove(gameSessionId); 
        }
    }

    public int getRemainingTime(String username) {
        long currentTime = System.currentTimeMillis();

        if (!roundStartTime.containsKey(username)) {
            return 0;
        }
        if (!playerRounds.containsKey(username)) { 
            return 0;
        }

        int currentRoundForPlayer = playerRounds.get(username);

        if (roundFinished.getOrDefault(username, Collections.emptyMap()).getOrDefault(currentRoundForPlayer, false)) {
            return 0;
        }

        long startTime = roundStartTime.get(username);
        long elapsedMillis = currentTime - startTime;

        int serverRoundTimeSeconds = playerManager.getRoundTime();
        long remainingMillis = (serverRoundTimeSeconds * 1000L) - elapsedMillis;

        int finalRemainingSeconds = (int) Math.max(0, remainingMillis / 1000);
        return finalRemainingSeconds;
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
            
            String nextWord = null;
            if (wordList != null && newRound < wordList.size()) { 
                nextWord = wordList.get(newRound);
            } else { 
                if (wordList == null) {
                    wordList = new ArrayList<>();
                    playerWords.put(username, wordList); 
                }
 
                Set<String> usedWords = new HashSet<>(wordList); 
                List<String> allWordsFromManager = new ArrayList<>(wordManager.getWords());
                Collections.shuffle(allWordsFromManager);
 
                for (String w : allWordsFromManager) {
                    if (!usedWords.contains(w)) {
                        nextWord = w;
                        break; 
                    }
                }
 
                if (nextWord == null) { 
                    if (!allWordsFromManager.isEmpty()) {
                        nextWord = allWordsFromManager.get(0); 
                    } else { 
                        System.err.println("[ERROR] WordManager is empty. Cannot find a word for new round for user " + username);
                        if (!wordList.isEmpty()) {
                            nextWord = wordList.get(new java.util.Random().nextInt(wordList.size()));
                        } else {
                            return false; 
                        }
                    }
                }
                wordList.add(nextWord); 
            }
 
            if (nextWord == null) {
                System.err.println("[CRITICAL] Failed to determine nextWord for " + username + " in startNewRound.");
                return false;
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
            roundFinishTime.computeIfAbsent(username, k -> new HashMap<>()).remove(newRound);
            roundGuessedWord.computeIfAbsent(username, k -> new HashMap<>()).remove(newRound);
            lastRoundWinner.computeIfAbsent(username, k -> new HashMap<>()).remove(newRound);

            return true;
        }
        return false;
    }

    public boolean isRoundOver(String username) {
        if (!activeGames.containsKey(username)) {
            return true;
        }
        String maskedWord = getMaskedWord(username);
        boolean wordGuessed = (maskedWord != null && !maskedWord.isEmpty() && !maskedWord.contains("_"));
        int incorrect = getIncorrectGuesses(username);
        boolean maxMisses = incorrect >= MAX_MISSES;
        
        int remTime = getRemainingTime(username); 
        boolean timeUp = remTime <= 0;

        return wordGuessed || maxMisses || timeUp;
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
            dto.roundOver = Bool.BOOL_FALSE;
            dto.gameOver = Bool.BOOL_FALSE;
            dto.sessionResult = "";
            dto.remainingTime = 0;
            dto.roundWinner = null;
            dto.finishedTime = 0;
            return dto;
        }

        int currentRoundForPlayer = playerRounds.getOrDefault(username, 0); 
        boolean isAlreadyMarkedFinished = roundFinished.getOrDefault(username, Collections.emptyMap())
                                            .getOrDefault(currentRoundForPlayer, false);

        if (!isAlreadyMarkedFinished) {
            int remainingTimeForTimeoutCheck = getRemainingTime(username); 
            String currentMaskedWordForTimeoutCheck = getMaskedWord(username);
            int currentIncorrectGuessesForTimeoutCheck = getIncorrectGuesses(username);

            boolean wordGuessedTimeoutCheck = (currentMaskedWordForTimeoutCheck != null && !currentMaskedWordForTimeoutCheck.isEmpty() && !currentMaskedWordForTimeoutCheck.contains("_"));
            boolean maxMissesReachedTimeoutCheck = currentIncorrectGuessesForTimeoutCheck >= MAX_MISSES;

            if (!wordGuessedTimeoutCheck && !maxMissesReachedTimeoutCheck && remainingTimeForTimeoutCheck <= 0) {
                finishRound(username, 0, Bool.BOOL_FALSE);
            }
        }

        String maskedWord = getMaskedWord(username);
        dto.maskedWord = (maskedWord != null) ? maskedWord : "";
        dto.incorrectGuesses = getIncorrectGuesses(username);
        dto.currentRound = currentRoundForPlayer; 
        dto.totalRounds = 0; 
        dto.playerWins = getPlayerWins(username);
        
        boolean roundOverBoolean = isRoundOver(username);
        dto.roundOver = roundOverBoolean ? Bool.BOOL_TRUE : Bool.BOOL_FALSE;
        
        boolean gameOverBoolean = isGameSessionOver(username);
        dto.gameOver = gameOverBoolean ? Bool.BOOL_TRUE : Bool.BOOL_FALSE;
        
        String sessionResult = gameSessionResult.get(username);
        dto.sessionResult = (sessionResult != null) ? sessionResult : "ONGOING";
        dto.remainingTime = getRemainingTime(username); 
        dto.finishedTime = roundFinishTime.getOrDefault(username, Collections.emptyMap()).getOrDefault(currentRoundForPlayer, 0L).intValue();
        
        String opponent = matchedPlayers.get(username);
        if (roundOverBoolean && opponent != null &&
            roundFinished.getOrDefault(username, Collections.emptyMap()).getOrDefault(currentRoundForPlayer, false) &&
            roundFinished.getOrDefault(opponent, Collections.emptyMap()).getOrDefault(currentRoundForPlayer, false)) {
            String winner = lastRoundWinner.getOrDefault(username, Collections.emptyMap()).getOrDefault(currentRoundForPlayer, null);
            dto.roundWinner = (winner != null) ? winner : ""; 
        } else {
            dto.roundWinner = ""; 
        }
        return dto;
    }

    public void endGameSession(String username) {
        String opponent = matchedPlayers.get(username);
        String gameSessionId = playerGameSessionIds.get(username);

        if (gameSessionId == null || gameSessionHistorySaved.getOrDefault(gameSessionId, false)) {
             if (opponent != null && !isGameSessionOver(username) && !isGameSessionOver(opponent)) {
                setGameSessionResult(opponent, "WIN");
                setGameSessionResult(username, "LOSE");
             }
            return; 
        }

        String overallWinnerForSave = null;
        if (opponent != null && !isGameSessionOver(username) && !isGameSessionOver(opponent)) {
            setGameSessionResult(opponent, "WIN");
            setGameSessionResult(username, "LOSE");
            overallWinnerForSave = opponent; 
            int totalOpponentWins = playerManager.getTotalWins(opponent);
            playerManager.updatePlayerWins(opponent, totalOpponentWins + 1);
        } else { 
            if (getGameSessionResult(username).equals("WIN")) {
                overallWinnerForSave = username;
            } else if (opponent != null && getGameSessionResult(opponent).equals("WIN")) {
                overallWinnerForSave = opponent;
            } else if (opponent == null && "WIN".equals(gameSessionResult.get(username))) {
                overallWinnerForSave = username; 
            }
        }

        List<String> playersInGame = new ArrayList<>();
        playersInGame.add(username);
        if (opponent != null) {
            playersInGame.add(opponent);
        }
        List<SPSinglePlayerRoundInfoDTO> rounds = gameSessionRounds.getOrDefault(gameSessionId, new ArrayList<>());
        saveGameSessionHistory(gameSessionId, playersInGame, rounds, overallWinnerForSave);
    }

    public void cleanupPlayerSession(String username) {
        String opponent = matchedPlayers.get(username);
        cleanupPlayerState(username);
        gameSessionResult.remove(username);

        if (opponent != null) {
            matchedPlayers.remove(opponent); 
        }
        matchedPlayers.remove(username); 
    }
}
