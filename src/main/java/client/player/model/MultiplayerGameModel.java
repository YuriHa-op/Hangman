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
        private Map<String, Integer> playerWinStreaks;

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

        @SuppressWarnings("unchecked")
        public String getPlayerMaskedWord(String player) {
            if (gameState == null || !gameState.containsKey("maskedWords")) return "";
            Object mapObj = gameState.get("maskedWords");
            if (mapObj instanceof Map) {
                Map<String, String> map = (Map<String, String>) mapObj;
                return map.getOrDefault(player, "");
            }
            return "";
        }

        @SuppressWarnings("unchecked")
        public int getPlayerIncorrectGuesses(String player) {
            if (gameState == null || !gameState.containsKey("incorrectGuessesMap")) return 0;
            Object mapObj = gameState.get("incorrectGuessesMap");
            if (mapObj instanceof Map) {
                Map<String, Number> map = (Map<String, Number>) mapObj;
                Number n = map.get(player);
                return n != null ? n.intValue() : 0;
            }
            return 0;
        }

        @SuppressWarnings("unchecked")
        public Set<Character> getPlayerGuesses(String player) {
            if (gameState == null || !gameState.containsKey("playerGuessesMap")) return new HashSet<>();
            Object mapObj = gameState.get("playerGuessesMap");
            if (mapObj instanceof Map) {
                Map<String, Object> map = (Map<String, Object>) mapObj;
                Object guessesObj = map.get(player);
                if (guessesObj instanceof List) {
                    List<Object> list = (List<Object>) guessesObj;
                    Set<Character> result = new HashSet<>();
                    for (Object o : list) {
                        if (o instanceof String && ((String) o).length() == 1) {
                            result.add(((String) o).charAt(0));
                        }
                    }
                    return result;
                }
            }
            return new HashSet<>();
        }

        @SuppressWarnings("unchecked")
        public String getPlayerActualWord(String player) {
            if (gameState == null || !gameState.containsKey("allCurrentWords")) return "";
            Object mapObj = gameState.get("allCurrentWords");
            if (mapObj instanceof Map) {
                Map<String, Object> map = (Map<String, Object>) mapObj;
                Object wordObj = map.get(player);
                if (wordObj instanceof String) {
                    return (String) wordObj;
                }
            }
            return "";
        }

        @SuppressWarnings("unchecked")
        public int getPlayerWinStreak(String player) {
            if (gameState == null || !gameState.containsKey("playerWinStreaks")) return 0;
            Object mapObj = gameState.get("playerWinStreaks");
            if (mapObj instanceof Map) {
                Map<String, Number> map = (Map<String, Number>) mapObj;
                Number n = map.get(player);
                return n != null ? n.intValue() : 0;
            }
            return 0;
        }

        public String getGameId() {
            return getStringFromGameState("gameId", null);
        }

        @SuppressWarnings("unchecked")
        public List<String> getAllPlayersEver() {
            if (gameState == null || !gameState.containsKey("allPlayersEver")) return new ArrayList<>(getPlayers());
            Object playersObj = gameState.get("allPlayersEver");
            if (playersObj instanceof List) {
                return (List<String>) playersObj;
            }
            return new ArrayList<>(getPlayers());
        }

        @SuppressWarnings("unchecked")
        public List<String> getGameEvents() {
            if (gameState == null || !gameState.containsKey("gameEvents")) return new ArrayList<>();
            Object eventsObj = gameState.get("gameEvents");
            if (eventsObj instanceof List) {
                return (List<String>) eventsObj;
            }
            return new ArrayList<>();
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
            GameModule.Bool result = gameService.sendMultiplayerGuess(username, letter);
            return result.value() == GameModule.Bool.BOOL_TRUE.value();
        } catch (Exception e) {
            System.err.println("Error making guess: " + e.getMessage());
            return false;
        }
    }

    public void setLobbyStateListener(LobbyStateListener listener) {
        this.lobbyStateListener = listener;
    }

    public void leaveGame() {
        if (username != null && !username.isEmpty()) {
            try {
                gameService.leaveMultiplayerGame(username);
            } catch (Exception e) {
                System.err.println("Error leaving multiplayer game: " + e.getMessage());
            }
        }
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
            GameModule.Bool result = gameService.startMultiplayerNextRound(username);
            return result.value() == GameModule.Bool.BOOL_TRUE.value();
        } catch (Exception e) {
            System.err.println("Error starting next multiplayer round: " + e.getMessage());
            return false;
        }
    }

    public void playerReadyForFirstRound() {
        if (username != null && !username.isEmpty()) {
            try {
                gameService.playerReadyForFirstRound(username);
            } catch (Exception e) {
                System.err.println("Error signaling player ready for first round: " + e.getMessage());
            }
        }
    }

    public String getMatchDetails(String gameId) {
        try {
            return gameService.getMatchDetails(gameId);
        } catch (Exception e) {
            System.err.println("Error getting match details: " + e.getMessage());
            return null;
        }
    }
} 