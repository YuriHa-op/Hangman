public static class LobbyState {
    private String state;
    private List<String> players;
    private int maxPlayers;
    private long creationTime;
    private int queueTimeSeconds;
    private Map<String, Object> gameState;
    private Map<String, Integer> playerWinStreaks;
    private List<String> events;

    public String getState() { return state; }
    public List<String> getPlayers() { return players; }
    public int getMaxPlayers() { return maxPlayers; }
    public long getCreationTime() { return creationTime; }
    public int getQueueTimeSeconds() { return queueTimeSeconds; }
    public Map<String, Object> getGameState() { return gameState; }
    public List<String> getEvents() { return events != null ? events : Collections.emptyList(); }

    public int getIntFromGameState(String key, int defaultValue) {
        if (gameState == null || !gameState.containsKey(key)) return defaultValue;
        Object value = gameState.get(key);
        if (value instanceof Integer) {
            return (Integer) value;
        } else if (value instanceof Number) {
            return ((Number) value).intValue();
        } else {
            throw new IllegalArgumentException("Invalid type for key: " + key);
        }
    }
} 