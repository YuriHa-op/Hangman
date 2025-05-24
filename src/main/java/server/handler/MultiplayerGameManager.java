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
        scheduler.schedule(() -> startLobbyIfReady(lobbyId), queueTimeSeconds, TimeUnit.SECONDS);
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
        return game.makeGuess(username, letter);
    }

    public boolean startNewRound(String lobbyId) {
        MultiplayerGameState game = activeGames.get(lobbyId);
        if (game == null) return false;
        return game.startNewRound();
    }

    public void cleanupGame(String lobbyId) {
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
            // Increment winner's win count in the database (if not already done)
            String winner = game.getGameWinner();
            if (winner != null && !winner.isEmpty()) {
                int totalWins = playerManager.getTotalWins(winner);
                playerManager.updatePlayerWins(winner, totalWins + 1);
            }
            saveMatchResultToDatabase(game.getMatchResult());
            // Delay cleanup so clients can receive final state
            scheduler.schedule(() -> cleanupGame(lobby.getLobbyId()), 5, java.util.concurrent.TimeUnit.SECONDS);
            return false;
        }
        return game.startNewRound();
    }

    // Save match result to DB (stub for now)
    private void saveMatchResultToDatabase(MultiplayerGameState.MatchResult result) {
        matchResultDAO.saveMatchResult(result);
    }

    public void scheduleCleanupIfGameOver(String lobbyId) {
        MultiplayerGameState game = activeGames.get(lobbyId);
        if (game != null && game.getGameWinner() != null && !cleanupScheduled.contains(lobbyId)) {
            cleanupScheduled.add(lobbyId);
            // Save result, update DB, etc. if needed
            saveMatchResultToDatabase(game.getMatchResult());
            scheduler.schedule(() -> {
                cleanupGame(lobbyId);
                cleanupScheduled.remove(lobbyId);
            }, 7, TimeUnit.SECONDS); // 7 seconds for clients to poll result
        }
    }

    // Additional methods for game state, guesses, win condition, etc. will be added as needed.
} 