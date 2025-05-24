package server.handler;

import java.util.ArrayList;
import java.util.List;

public class MultiplayerLobby {
    private final String lobbyId;
    private final List<String> players;
    private final long creationTime;
    private boolean started;
    private final int minPlayers;
    private final int maxPlayers;

    public MultiplayerLobby(String lobbyId, int minPlayers, int maxPlayers) {
        this.lobbyId = lobbyId;
        this.players = new ArrayList<>();
        this.creationTime = System.currentTimeMillis();
        this.started = false;
        this.minPlayers = minPlayers;
        this.maxPlayers = maxPlayers;
    }

    public String getLobbyId() {
        return lobbyId;
    }

    public List<String> getPlayers() {
        return players;
    }

    public long getCreationTime() {
        return creationTime;
    }

    public boolean isStarted() {
        return started;
    }

    public void setStarted(boolean started) {
        this.started = started;
    }

    public boolean addPlayer(String username) {
        if (players.size() < maxPlayers && !players.contains(username)) {
            players.add(username);
            return true;
        }
        return false;
    }

    public void removePlayer(String username) {
        players.remove(username);
    }

    public boolean isFull() {
        return players.size() >= maxPlayers;
    }

    public boolean isReady() {
        return players.size() >= minPlayers;
    }

    public boolean isExpired(int queueTimeSeconds) {
        return (System.currentTimeMillis() - creationTime) > queueTimeSeconds * 1000L;
    }

    public int getMaxPlayers() {
        return maxPlayers;
    }
} 