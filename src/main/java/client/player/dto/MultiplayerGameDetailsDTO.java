package client.player.dto;

import java.util.List;

public class MultiplayerGameDetailsDTO {
    private String gameId;
    private int totalRounds;
    private String overallWinner;
    private List<String> players;
    private List<MultiplayerRoundInfoDTO> rounds;
    private long gameEndTime;

    // Getters
    public String getGameId() {
        return gameId;
    }

    public int getTotalRounds() {
        return totalRounds;
    }

    public String getOverallWinner() {
        return overallWinner;
    }

    public List<String> getPlayers() {
        return players;
    }

    public List<MultiplayerRoundInfoDTO> getRounds() {
        return rounds;
    }

    public long getGameEndTime() {
        return gameEndTime;
    }
} 