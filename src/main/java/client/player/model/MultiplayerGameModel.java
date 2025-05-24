package client.player.model;

import GameModule.GameService;
import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;
import java.util.*;

public class MultiplayerGameModel {
    public interface LobbyStateListener {
        void onLobbyUpdate(LobbyState state);
    }

    public static class LobbyState {
        private String state;
        private List<String> players;
        private int maxPlayers;
        private long creationTime;
        private int queueTimeSeconds;
        private Map<String, Object> gameState;

        public String getState() { return state; }
        public List<String> getPlayers() { return players; }
        public int getMaxPlayers() { return maxPlayers; }
        public long getCreationTime() { return creationTime; }
        public int getQueueTimeSeconds() { return queueTimeSeconds; }
        public Map<String, Object> getGameState() { return gameState; }

        public int getIntFromGameState(String key, int defaultValue) {
            if (gameState == null || !gameState.containsKey(key)) return defaultValue;
            Object value = gameState.get(key);
            if (value instanceof Number) {
                return ((Number) value).intValue();
            }
            return defaultValue;
        }

        public String getStringFromGameState(String key, String defaultValue) {
            if (gameState == null || !gameState.containsKey(key)) return defaultValue;
            Object value = gameState.get(key);
            return value != null ? value.toString() : defaultValue;
        }

        @SuppressWarnings("unchecked")
        public Map<String, Integer> getScoresFromGameState() {
            if (gameState == null || !gameState.containsKey("scores")) return new HashMap<>();
            Object scoresObj = gameState.get("scores");
            if (scoresObj instanceof Map) {
                Map<String, Object> scores = (Map<String, Object>) scoresObj;
                Map<String, Integer> result = new HashMap<>();
                for (Map.Entry<String, Object> entry : scores.entrySet()) {
                    if (entry.getValue() instanceof Number) {
                        result.put(entry.getKey(), ((Number) entry.getValue()).intValue());
                    }
                }
                return result;
            }
            return new HashMap<>();
        }
    }

    private final GameService gameService;
    private final String username;
    private String lobbyId;
    private LobbyStateListener lobbyStateListener;
    private final Gson gson = new Gson();

    public MultiplayerGameModel(GameService gameService, String username) {
        this.gameService = gameService;
        this.username = username;
    }

    public void startGame() {
        try {
            lobbyId = gameService.startMultiplayerGame(username);
        } catch (Exception e) {
            System.err.println("Error starting multiplayer game: " + e.getMessage());
        }
    }

    public void updateLobbyState() {
        try {
            String stateJson = gameService.getMultiplayerLobbyState(username);
            LobbyState state = gson.fromJson(stateJson, LobbyState.class);
            if (lobbyStateListener != null) {
                lobbyStateListener.onLobbyUpdate(state);
            }
        } catch (Exception e) {
            System.err.println("Error updating lobby state: " + e.getMessage());
        }
    }

    public boolean makeGuess(char letter) {
        try {
            return gameService.sendMultiplayerGuess(username, letter);
        } catch (Exception e) {
            System.err.println("Error making guess: " + e.getMessage());
            return false;
        }
    }

    public void setLobbyStateListener(LobbyStateListener listener) {
        this.lobbyStateListener = listener;
    }

    public GameService getGameService() {
        return gameService;
    }

    public String getUsername() {
        return username;
    }

    public String getLobbyId() {
        return lobbyId;
    }

    public boolean startNextRound() {
        try {
            return gameService.startMultiplayerNextRound(username);
        } catch (Exception e) {
            System.err.println("Error starting next multiplayer round: " + e.getMessage());
            return false;
        }
    }
} 