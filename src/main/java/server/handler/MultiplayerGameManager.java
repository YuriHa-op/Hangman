package server.handler;

import java.util.*;
import java.util.concurrent.*;

public class MultiplayerGameManager {
    private final Map<String, MultiplayerLobby> activeLobbies = new ConcurrentHashMap<>();
    private final Map<String, MultiplayerGameState> activeGames = new ConcurrentHashMap<>();
    private final int minPlayers;
    private final int maxPlayers;
    private final int queueTimeSeconds;
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);
    private final WordManager wordManager;
    private final PlayerManager playerManager;
    private final MatchResultDAO matchResultDAO = new MatchResultDAO(
        "jdbc:mysql://localhost:3306/game", // DB URL
        "root", // DB user (change as needed)
        ""      // DB password (change as needed)
    );
    private final Set<String> cleanupScheduled = ConcurrentHashMap.newKeySet();
    // Track round timers for each lobby
    private final Map<String, ScheduledFuture<?>> roundTimers = new ConcurrentHashMap<>();
    private final Map<String, ScheduledFuture<?>> stallCheckTimers = new ConcurrentHashMap<>();
    private static final int STALL_CHECK_TIMEOUT_SECONDS = 30;

    public MultiplayerGameManager(WordManager wordManager, PlayerManager playerManager, int minPlayers, int maxPlayers, int queueTimeSeconds) {
        this.wordManager = wordManager;
        this.playerManager = playerManager;
        this.minPlayers = minPlayers;
        this.maxPlayers = maxPlayers;
        this.queueTimeSeconds = queueTimeSeconds;
    }

    public synchronized MultiplayerLobby joinOrCreateLobby(String username) {
        // Try to find an open lobby
        for (MultiplayerLobby lobby : activeLobbies.values()) {
            if (!lobby.isStarted() && !lobby.isFull()) {
                if (lobby.addPlayer(username)) {
                    return lobby;
                }
            }
        }
        // No open lobby, create a new one
        String lobbyId = UUID.randomUUID().toString();
        MultiplayerLobby newLobby = new MultiplayerLobby(lobbyId, minPlayers, maxPlayers);
        newLobby.addPlayer(username);
        activeLobbies.put(lobbyId, newLobby);
        // Schedule lobby start after queue time
        scheduler.schedule(() -> {
            try {
                startLobbyIfReady(lobbyId);
            } catch (Throwable t) {
                logMessage("ERROR in scheduled startLobbyIfReady for lobby " + lobbyId + ": " + t.getMessage());
                // Consider further error handling, e.g., cleaning up the lobby
            }
        }, queueTimeSeconds, TimeUnit.SECONDS);
        return newLobby;
    }

    private void startLobbyIfReady(String lobbyId) {
        MultiplayerLobby lobby = activeLobbies.get(lobbyId);
        if (lobby == null || lobby.isStarted()) return;
        
        if (lobby.isReady()) {
            lobby.setStarted(true);
            // Create new game state for this lobby
            MultiplayerGameState gameState = new MultiplayerGameState(
                lobbyId,
                lobby.getPlayers(),
                wordManager,
                playerManager.getRoundTime()
            );
            activeGames.put(lobbyId, gameState);
            gameState.startNewRound();
            scheduleRoundTimer(lobbyId);
        } else {
            // Not enough players, notify and remove lobby
            for (String player : lobby.getPlayers()) {
                // State will be handled by client polling
                removePlayerFromLobby(player);
            }
            activeLobbies.remove(lobbyId);
        }
    }

    public MultiplayerLobby getLobbyByPlayer(String username) {
        for (MultiplayerLobby lobby : activeLobbies.values()) {
            if (lobby.getPlayers().contains(username)) {
                return lobby;
            }
        }
        return null;
    }

    public void removePlayerFromLobby(String username) {
        MultiplayerLobby lobby = getLobbyByPlayer(username);
        if (lobby != null) {
            lobby.removePlayer(username);
            if (lobby.getPlayers().isEmpty()) {
                activeLobbies.remove(lobby.getLobbyId());
                activeGames.remove(lobby.getLobbyId());
            }
        }
    }

    public int getQueueTimeSeconds() {
        return queueTimeSeconds;
    }

    public MultiplayerGameState getGameState(String username) {
        for (MultiplayerGameState game : activeGames.values()) {
            if (game.getPlayers().contains(username)) {
                return game;
            }
        }
        return null;
    }

    public boolean makeGuess(String username, char letter) {
        MultiplayerGameState game = getGameState(username);
        if (game == null) return false;
        cancelStallCheckTimer(game.getLobbyId());
        return game.makeGuess(username, letter);
    }

    public boolean startNewRound(String lobbyId) {
        MultiplayerGameState game = activeGames.get(lobbyId);
        if (game == null) return false;
        boolean started = game.startNewRound();
        if (started) {
            cancelStallCheckTimer(lobbyId);
            scheduleRoundTimer(lobbyId);
        } else {
            if (game.isRoundPotentiallyStalled()) {
                scheduleStallCheckTimer(lobbyId);
            }
        }
        return started;
    }

    public void cleanupGame(String lobbyId) {
        cancelRoundTimer(lobbyId);
        activeLobbies.remove(lobbyId);
        activeGames.remove(lobbyId);
    }

    // Add a public method to start the next round for a lobby
    public boolean startNextRound(String username) {
        MultiplayerLobby lobby = getLobbyByPlayer(username);
        if (lobby == null) return false;
        MultiplayerGameState game = activeGames.get(lobby.getLobbyId());
        if (game == null) return false;

        // If game is finished, save result and schedule cleanup
        if (game.getGameWinner() != null) {
            // Check if the game win has already been processed
            if (!game.isGameWinProcessed()) {
                String winner = game.getGameWinner();
                if (winner != null && !winner.isEmpty()) {
                    int totalWins = playerManager.getTotalWins(winner);
                    playerManager.updatePlayerWins(winner, totalWins + 1);
                    game.setGameWinProcessed(true); // Mark as processed
                    logMessage("Game win processed for " + winner + " in lobby " + lobby.getLobbyId());
                }
                saveMatchResultToDatabase(game.getMatchResult()); // Save match result regardless of win processing for stats
            }
            
            // Delay cleanup so clients can receive final state
            // Schedule cleanup only once using the cleanupScheduled set
            if (!cleanupScheduled.contains(lobby.getLobbyId())) {
                cleanupScheduled.add(lobby.getLobbyId());
                scheduler.schedule(() -> {
                    try {
                        cleanupGame(lobby.getLobbyId());
                        cleanupScheduled.remove(lobby.getLobbyId());
                        logMessage("Game cleaned up for lobby " + lobby.getLobbyId());
                    } catch (Throwable t) {
                        logMessage("ERROR in scheduled cleanupGame (game over path) for lobby " + lobby.getLobbyId() + ": " + t.getMessage());
                    }
                }, 7, java.util.concurrent.TimeUnit.SECONDS); // Increased from 5 to 7 for more buffer
            }
            return false; // Game is over, no next round to start
        }

        boolean started = game.startNewRound();
        if (started) {
            cancelStallCheckTimer(lobby.getLobbyId());
            scheduleRoundTimer(lobby.getLobbyId());
        } else {
            if (game.isRoundPotentiallyStalled()) {
                scheduleStallCheckTimer(lobby.getLobbyId());
            }
        }
        return started;
    }

    // Save match result to DB (stub for now)
    private void saveMatchResultToDatabase(MultiplayerGameState.MatchResult result) {
        matchResultDAO.saveMatchResult(result);
        logMessage("Match result saved for game ID: " + result.gameId);
    }

    // Add a simple logging method to help track processing
    private void logMessage(String message) {
        System.out.println("[MultiplayerGameManager] " + message);
    }

    public void scheduleCleanupIfGameOver(String lobbyId) {
        MultiplayerGameState game = activeGames.get(lobbyId);
        if (game != null && game.getGameWinner() != null && !cleanupScheduled.contains(lobbyId)) {
            cleanupScheduled.add(lobbyId);
            // Save result, update DB, etc. if needed
            saveMatchResultToDatabase(game.getMatchResult());
            scheduler.schedule(() -> {
                try {
                    cleanupGame(lobbyId);
                    cleanupScheduled.remove(lobbyId);
                } catch (Throwable t) {
                    logMessage("ERROR in scheduled cleanupGame (scheduleCleanupIfGameOver) for lobby " + lobbyId + ": " + t.getMessage());
                }
            }, 7, TimeUnit.SECONDS); // 7 seconds for clients to poll result
        }
    }

    private void scheduleRoundTimer(String lobbyId) {
        // Cancel any existing timer for this lobby
        ScheduledFuture<?> prev = roundTimers.remove(lobbyId);
        if (prev != null) prev.cancel(false);
        ScheduledFuture<?> future = scheduler.schedule(() -> {
            try {
                MultiplayerGameState state = activeGames.get(lobbyId);
                if (state != null) {
                    state.forceEndRound();
                    if (state.isRoundPotentiallyStalled()) {
                        scheduleStallCheckTimer(lobbyId);
                    }
                }
            } catch (Throwable t) {
                logMessage("ERROR in scheduleRoundTimer task for lobby " + lobbyId + ": " + t.getMessage());
            }
        }, playerManager.getRoundTime(), TimeUnit.SECONDS);
        roundTimers.put(lobbyId, future);
    }

    private void cancelRoundTimer(String lobbyId) {
        ScheduledFuture<?> future = roundTimers.remove(lobbyId);
        if (future != null) future.cancel(false);
    }

    private void scheduleStallCheckTimer(String lobbyId) {
        logMessage("Scheduling stall check for lobby: " + lobbyId);
        cancelStallCheckTimer(lobbyId);
        ScheduledFuture<?> future = scheduler.schedule(() -> {
            try {
                logMessage("Stall check triggered for lobby: " + lobbyId + ". Cleaning up game.");
                cleanupGame(lobbyId);
            } catch (Throwable t) {
                logMessage("ERROR in stall check timer task for lobby " + lobbyId + ": " + t.getMessage());
            }
        }, STALL_CHECK_TIMEOUT_SECONDS, TimeUnit.SECONDS);
        stallCheckTimers.put(lobbyId, future);
    }

    public void cancelStallCheckTimer(String lobbyId) {
        ScheduledFuture<?> future = stallCheckTimers.remove(lobbyId);
        if (future != null) {
            future.cancel(false);
            logMessage("Cancelled stall check timer for lobby: " + lobbyId);
        }
    }

    // Additional methods for game state, guesses, win condition, etc. will be added as needed.
} 