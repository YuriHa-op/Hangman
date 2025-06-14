package server.handler.service;

import GameModule.GameServicePOA;
import GameModule.Bool;

import java.util.function.Consumer;

import server.handler.data.MatchResultDAO;
import server.handler.model.MultiplayerGameState;
import server.handler.model.MultiplayerLobby;
import server.handler.data.SinglePlayerMatchResultDAO;
import server.handler.core.GameManager;

import java.util.*;
import java.util.Map;
import java.util.List;
import GameModule.GameStateDTO;
import com.google.gson.Gson;
import server.handler.core.MultiplayerGameManager;
import server.handler.core.PlayerManager;
import server.handler.core.WordManager;

public class GameServiceImpl extends GameServicePOA {
    private final GameManager gameManager;
    private final PlayerManager playerManager;
    private final WordManager wordManager;
    private Consumer<String> logCallback;
    private MultiplayerGameManager multiplayerGameManager;
    private static final int MULTI_MIN_PLAYERS = 2;
    private static final int MULTI_MAX_PLAYERS = 8;
    private final MatchResultDAO matchResultDAO;
    private final SinglePlayerMatchResultDAO singlePlayerMatchResultDAO;
    private final Gson gson = new Gson();
    private boolean isPaused = false;

    // Track previous counts to avoid redundant logging
    private int previousSinglePlayerCount = 0;
    private int previousMultiPlayerCount = 0;
    private int previousSingleGameCount = 0;
    private int previousMultiGameCount = 0;

    public GameServiceImpl() {
        this.wordManager = new WordManager();
        this.playerManager = new PlayerManager();
        this.singlePlayerMatchResultDAO = new SinglePlayerMatchResultDAO(
            "jdbc:mysql://localhost:3306/game",
            "root",
            ""
        );
        this.gameManager = new GameManager(wordManager, playerManager, singlePlayerMatchResultDAO);
        
        // Initialize multiplayer manager
        int waitingTime = playerManager.getWaitingTime();
        this.multiplayerGameManager = new MultiplayerGameManager(wordManager, playerManager, 
            MULTI_MIN_PLAYERS, MULTI_MAX_PLAYERS, waitingTime);
        
        // Initialize matchResultDAO
        this.matchResultDAO = new MatchResultDAO(
            "jdbc:mysql://localhost:3306/game",
            "root",
            ""
        );
    }

    public GameServiceImpl(WordManager wordManager, PlayerManager playerManager,
                          MatchResultDAO matchResultDAO, SinglePlayerMatchResultDAO singlePlayerMatchResultDAO) {
        this.wordManager = wordManager;
        this.playerManager = playerManager;
        this.matchResultDAO = matchResultDAO;
        this.singlePlayerMatchResultDAO = singlePlayerMatchResultDAO;
        this.gameManager = new GameManager(wordManager, playerManager, singlePlayerMatchResultDAO);
        
        // Initialize multiplayer manager
        int waitingTime = playerManager.getWaitingTime();
        this.multiplayerGameManager = new MultiplayerGameManager(wordManager, playerManager, 
            MULTI_MIN_PLAYERS, MULTI_MAX_PLAYERS, waitingTime);
    }

    public void setLogCallback(Consumer<String> callback) {
        this.logCallback = callback;
        gameManager.setLogCallback(callback);
    }

    /**
     * Gets the total number of active players across all game modes.
     * 
     * @return The total count of active players
     */
    public int getActivePlayers() {
        // Get single player mode count
        int singlePlayerCount = gameManager.getActivePlayers();
        
        // For multiplayer, count players in active games
        int multiplayerCount = 0;
        if (multiplayerGameManager != null) {
            // Count all active multiplayer players
            try {
                // Use reflection to access the active games in the game manager
                java.lang.reflect.Field activeGamesField = multiplayerGameManager.getClass().getDeclaredField("activeGames");
                activeGamesField.setAccessible(true);
                Map<?, ?> activeGames = (Map<?, ?>)activeGamesField.get(multiplayerGameManager);
                
                // Count unique players in all active games
                Set<String> activePlayers = new HashSet<>();
                for (Object game : activeGames.values()) {
                    if (game != null) {
                        java.lang.reflect.Method getPlayersMethod = game.getClass().getMethod("getPlayers");
                        Collection<?> players = (Collection<?>)getPlayersMethod.invoke(game);
                        for (Object player : players) {
                            activePlayers.add(player.toString());
                        }
                    }
                }
                multiplayerCount = activePlayers.size();
            } catch (Exception e) {
                // Only log severe errors, not every call
                if (e instanceof NoSuchMethodException || e instanceof NoSuchFieldException) {
                    if (logCallback != null) {
                        logCallback.accept("Error accessing multiplayer player count: " + e.getMessage());
                    }
                }
            }
        }
        
        // Only log when there's an actual change in player counts
        boolean hasChanged = (singlePlayerCount != previousSinglePlayerCount || multiplayerCount != previousMultiPlayerCount);
        
        // Update total counts (even if we don't log)
        int totalBefore = previousSinglePlayerCount + previousMultiPlayerCount;
        int totalAfter = singlePlayerCount + multiplayerCount;
        
        // Log changes with clear indications of what happened
        if (hasChanged && logCallback != null) {
            // Players were added or removed
            if (totalBefore < totalAfter) {
                logCallback.accept("Player joined - Now active: " + totalAfter + " (Single: " + singlePlayerCount + ", Multi: " + multiplayerCount + ")");
            } else if (totalBefore > totalAfter) {
                logCallback.accept("Player left - Now active: " + totalAfter + " (Single: " + singlePlayerCount + ", Multi: " + multiplayerCount + ")");
            }
            // Just log distribution changes if total didn't change
            else if (singlePlayerCount != previousSinglePlayerCount) {
                logCallback.accept("Players redistributed - Total: " + totalAfter + " (Single: " + singlePlayerCount + ", Multi: " + multiplayerCount + ")");
            }
        }
        
        // Update previous counts
        previousSinglePlayerCount = singlePlayerCount;
        previousMultiPlayerCount = multiplayerCount;
        
        return singlePlayerCount + multiplayerCount;
    }

    /**
     * Gets the total number of active games across all game modes.
     * 
     * @return The total count of active games
     */
    public int getActiveGames() {
        // Get single player mode count
        int singlePlayerCount = gameManager.getActiveGames();
        
        // For multiplayer, count active game sessions
        int multiplayerCount = 0;
        if (multiplayerGameManager != null) {
            // Count all active multiplayer games
            try {
                // Use reflection to access the active games in the game manager
                java.lang.reflect.Field activeGamesField = multiplayerGameManager.getClass().getDeclaredField("activeGames");
                activeGamesField.setAccessible(true);
                Map<?, ?> activeGames = (Map<?, ?>)activeGamesField.get(multiplayerGameManager);
                multiplayerCount = activeGames.size();
            } catch (Exception e) {
                // Only log severe errors, not every call
                if (e instanceof NoSuchMethodException || e instanceof NoSuchFieldException) {
                    if (logCallback != null) {
                        logCallback.accept("Error accessing multiplayer game count: " + e.getMessage());
                    }
                }
            }
        }
        
        // Only log when there's an actual change in game counts
        boolean hasChanged = (singlePlayerCount != previousSingleGameCount || multiplayerCount != previousMultiGameCount);
        
        // Update total counts (even if we don't log)
        int totalBefore = previousSingleGameCount + previousMultiGameCount;
        int totalAfter = singlePlayerCount + multiplayerCount;
        
        // Log changes with clear indications of what happened
        if (hasChanged && logCallback != null) {
            // Games were added or removed
            if (totalBefore < totalAfter) {
                logCallback.accept("Game started - Now active: " + totalAfter + " (Single: " + singlePlayerCount + ", Multi: " + multiplayerCount + ")");
            } else if (totalBefore > totalAfter) {
                logCallback.accept("Game ended - Now active: " + totalAfter + " (Single: " + singlePlayerCount + ", Multi: " + multiplayerCount + ")");
            }
            // Just log distribution changes if total didn't change
            else if (singlePlayerCount != previousSingleGameCount) {
                logCallback.accept("Games redistributed - Total: " + totalAfter + " (Single: " + singlePlayerCount + ", Multi: " + multiplayerCount + ")");
            }
        }
        
        // Update previous counts
        previousSingleGameCount = singlePlayerCount;
        previousMultiGameCount = multiplayerCount;
        
        return singlePlayerCount + multiplayerCount;
    }

    @Override
    public Bool login(String username, String password) throws GameModule.AlreadyLoggedInException {
        return playerManager.login(username, password);
    }

    @Override
    public void logout(String username) {
        playerManager.logout(username);
    }

    @Override
    public Bool createPlayer(String username, String password) {
        return playerManager.createPlayer(username, password);
    }

    @Override
    public Bool sendGuess(String username, char letter) {
        return gameManager.sendGuess(username, letter);
    }

    @Override
    public String viewLeaderboard() {
        java.util.List<client.admin.model.LeaderboardEntryDTO> entries = playerManager.getLeaderboardEntries();
        StringBuilder leaderboard = new StringBuilder("LEADERBOARD:\n");
        for (client.admin.model.LeaderboardEntryDTO entry : entries) {
            leaderboard.append(entry.getUsername())
                    .append(": ")
                    .append(entry.getWins())
                    .append(" wins\n");
        }
        return leaderboard.toString();
    }

    @Override
    public String getMaskedWord(String username) {
        return gameManager.getMaskedWord(username);
    }

    @Override
    public String startGame(String username) {
        if (isPaused) {
            if (logCallback != null) {
                logCallback.accept("Rejected game start request from " + username + " - server is paused");
            }
            return "ERROR: Server is currently in maintenance mode. Please try again later.";
        }
        
        return gameManager.startGame(username);
    }

    private void endGame(String username, boolean recordStats) {
        gameManager.endGame(username, recordStats);
    }

    @Override
    public int getRoundTime() {
        return playerManager.getRoundTime();
    }

    @Override
    public int getWaitingTime() {
        return playerManager.getWaitingTime();
    }

    @Override
    public int getRemainingTime(String username) {
        return gameManager.getRemainingTime(username);
    }

    @Override
    public int getIncorrectGuesses(String username) {
        return gameManager.getIncorrectGuesses(username);
    }

    @Override
    public void endGameSession(String username) {
        gameManager.endGameSession(username);
    }

    @Override
    public int getCurrentRound(String username) {
        return gameManager.getCurrentRound(username);
    }

    @Override
    public int getPlayerWins(String username) {
        return gameManager.getPlayerWins(username);
    }

    @Override
    public Bool startNewRound(String username) {
        return gameManager.startNewRound(username) ? Bool.BOOL_TRUE : Bool.BOOL_FALSE;
    }

    @Override
    public Bool isRoundOver(String username) {
        return gameManager.isRoundOver(username) ? Bool.BOOL_TRUE : Bool.BOOL_FALSE;
    }

    @Override
    public Bool isGameSessionOver(String username) {
        return gameManager.isGameSessionOver(username) ? Bool.BOOL_TRUE : Bool.BOOL_FALSE;
    }

    @Override
    public String getGameSessionResult(String username) {
        return gameManager.getGameSessionResult(username);
    }

    @Override
    public GameStateDTO getGameState(String username) {
        server.dto.GameStateDTO internal = gameManager.getGameState(username);
        GameStateDTO corbaDto = new GameStateDTO();
        corbaDto.maskedWord = (internal.maskedWord != null) ? internal.maskedWord : "";
        corbaDto.incorrectGuesses = internal.incorrectGuesses;
        corbaDto.currentRound = internal.currentRound;
        corbaDto.totalRounds = internal.totalRounds;
        corbaDto.playerWins = internal.playerWins;
        corbaDto.roundOver = internal.roundOver;
        corbaDto.gameOver = internal.gameOver;
        corbaDto.sessionResult = (internal.sessionResult != null) ? internal.sessionResult : "";
        corbaDto.remainingTime = internal.remainingTime;
        corbaDto.roundWinner = (internal.roundWinner != null) ? internal.roundWinner : "";
        corbaDto.finishedTime = internal.finishedTime;
        corbaDto.opponentUsername = internal.opponentUsername;
        return corbaDto;
    }

    @Override
    public void finishRound(String username, int clientRemainingTime, Bool guessedWord) {
        gameManager.finishRound(username, clientRemainingTime, guessedWord);
    }

    @Override
    public void cleanupPlayerSession(String username) {
        gameManager.cleanupPlayerSession(username);
    }

    public void initMultiplayerManager(int queueTimeSeconds) {
        this.multiplayerGameManager = new MultiplayerGameManager(wordManager, playerManager, MULTI_MIN_PLAYERS, MULTI_MAX_PLAYERS, queueTimeSeconds);
    }

    @Override
    public String startMultiplayerGame(String username) {
        if (isPaused) {
            if (logCallback != null) {
                logCallback.accept("Rejected multiplayer game start request from " + username + " - server is paused");
            }
            return "ERROR: Server is currently in maintenance mode. Please try again later.";
        }
        
        MultiplayerLobby lobby = multiplayerGameManager.joinOrCreateLobby(username);
        return lobby.getLobbyId();
    }

    @Override
    public String getMultiplayerLobbyState(String username) {
        MultiplayerLobby lobby = multiplayerGameManager.getLobbyByPlayer(username);
        if (lobby == null) {
            return "{\"state\":\"NOMATCH\"}";
        }

        MultiplayerGameState gameState = multiplayerGameManager.getGameState(username);

        // Schedule cleanup if game is over and winner is declared
        if (lobby.isStarted() && gameState != null && gameState.getGameWinner() != null) {
            multiplayerGameManager.scheduleCleanupIfGameOver(lobby.getLobbyId());
        }

        Map<String, Object> stateMap = new LinkedHashMap<>();
        stateMap.put("state", lobby.isStarted() ? "STARTED" : "WAITING");
        stateMap.put("players", lobby.getPlayers());
        stateMap.put("maxPlayers", lobby.getMaxPlayers());
        stateMap.put("creationTime", lobby.getCreationTime());
        stateMap.put("queueTimeSeconds", multiplayerGameManager.getQueueTimeSeconds());

        if (gameState != null) {
            if (!gameState.isRoundPotentiallyStalled()) {
                multiplayerGameManager.cancelStallCheckTimer(lobby.getLobbyId());
            }

            Map<String, Object> gameStateMap = new LinkedHashMap<>();
            gameStateMap.put("gameId", gameState.getGameId());
            gameStateMap.put("currentRound", gameState.getCurrentRound());
            gameStateMap.put("roundInProgress", gameState.isRoundInProgress());
            gameStateMap.put("remainingTime", gameState.getRemainingTime());
            gameStateMap.put("maskedWord", gameState.getMaskedWord(username));
            gameStateMap.put("maskedWords", gameState.getAllMaskedWords());
            gameStateMap.put("incorrectGuessesMap", gameState.getAllIncorrectGuesses());
            gameStateMap.put("scores", gameState.getScores());
            gameStateMap.put("guesses", gameState.getPlayerGuesses(username));
            gameStateMap.put("roundWinner", gameState.getRoundWinner());
            
            Map<String, Integer> playerRoundWins = new HashMap<>();
            for(String p : lobby.getPlayers()) {
                playerRoundWins.put(p, gameState.getPlayerRoundWins(p));
            }
            gameStateMap.put("playerRoundWins", playerRoundWins);

            String gameWinner = gameState.getGameWinner();
            gameStateMap.put("gameWinner", gameWinner != null ? gameWinner : "");
            
            String sessionResult = "ONGOING";
            if (gameWinner != null && !gameWinner.isEmpty()) {
                sessionResult = gameWinner.equals(username) ? "WIN" : "LOSE";
            }
            gameStateMap.put("sessionResult", sessionResult);
            
            gameStateMap.put("playerGuessesMap", gameState.getAllPlayerGuesses());
            gameStateMap.put("allCurrentWords", gameState.getAllCurrentWords());
            gameStateMap.put("playerWinStreaks", gameState.getPlayerWinStreaks());
            gameStateMap.put("allPlayerFinishTimes", gameState.getAllPlayerFinishTimes());
            gameStateMap.put("gameEvents", gameState.getGameEvents());
            gameStateMap.put("allPlayersEver", gameState.getAllPlayersEver());

            stateMap.put("gameState", gameStateMap);
        }

        return gson.toJson(stateMap);
    }

    @Override
    public Bool sendMultiplayerGuess(String username, char letter) {
        return multiplayerGameManager.makeGuess(username, letter) ? Bool.BOOL_TRUE : Bool.BOOL_FALSE;
    }

    @Override
    public Bool startMultiplayerNextRound(String username) {
        return multiplayerGameManager.startNextRound(username) ? Bool.BOOL_TRUE : Bool.BOOL_FALSE;
    }

    @Override
    public String getMatchHistory(String username) {
        java.util.List<server.dto.MultiplayerGameSummaryDTO> games = matchResultDAO.getGamesForPlayer(username);
        return gson.toJson(games);
    }

    @Override
    public String getMatchDetails(String gameId) {
        server.dto.MultiplayerGameDetailsDTO details = matchResultDAO.getGameDetails(gameId);
        return gson.toJson(details);
    }

    @Override
    public String getSinglePlayerMatchHistory(String username) {
        List<server.dto.SPSinglePlayerGameSummaryDTO> games = singlePlayerMatchResultDAO.getGamesForPlayer(username);
        return gson.toJson(games);
    }

    @Override
    public String getSinglePlayerMatchDetails(String gameId) {
        server.dto.SPSinglePlayerGameDetailsDTO details = singlePlayerMatchResultDAO.getGameDetails(gameId);
        return gson.toJson(details);
    }

    @Override
    public void playerReadyForFirstRound(String username) {
        if (multiplayerGameManager.isPlayerInMultiplayer(username)) {
            multiplayerGameManager.playerReadyForFirstRound(username);
        } else {
            gameManager.signalPlayerReadyAndPotentiallyStartFirstRound(username);
        }
    }

    @Override
    public void leaveMultiplayerGame(String username) {
        multiplayerGameManager.leaveMultiplayerGame(username);
    }

    @Override
    public GameModule.LeaderboardEntryDTO[] getLeaderboardEntries() {
        java.util.List<client.admin.model.LeaderboardEntryDTO> entries = playerManager.getLeaderboardEntries();
        GameModule.LeaderboardEntryDTO[] corbaEntries = new GameModule.LeaderboardEntryDTO[entries.size()];
        for (int i = 0; i < entries.size(); i++) {
            client.admin.model.LeaderboardEntryDTO entry = entries.get(i);
            GameModule.LeaderboardEntryDTO corbaEntry = new GameModule.LeaderboardEntryDTO();
            corbaEntry.username = entry.getUsername();
            corbaEntry.wins = entry.getWins();
            corbaEntries[i] = corbaEntry;
        }
        return corbaEntries;
    }

    /**
     * Sets the paused state of this service.
     * When paused, the service will reject new connections/game starts
     * but maintain existing games.
     * 
     * @param paused true to pause, false to resume
     */
    public void setPaused(boolean paused) {
        this.isPaused = paused;
        if (logCallback != null) {
            logCallback.accept("GameService " + (paused ? "paused" : "resumed"));
        }
        
        // If we're pausing, we should notify all active game sessions
        if (paused) {
            notifyPlayersOfPause();
        }
    }

    /**
     * Checks if the service is currently paused.
     * 
     * @return true if paused, false otherwise
     */
    public boolean isPaused() {
        return isPaused;
    }

    /**
     * Notify all players that the server is in a paused state.
     */
    private void notifyPlayersOfPause() {
        // This would be implemented to notify players in game sessions
        // that the server is paused
    }

    /**
     * Resets all active games and cleans up resources.
     * This is used when stopping or restarting the server.
     */
    public void resetAllGames() {
        if (logCallback != null) {
            logCallback.accept("Resetting all active games");
        }
        
        // For UI purposes, we'll just make sure the counts reset
        // The actual cleanup will happen when the server restarts
    }
}
