package client.player.console.dto;

import client.player.dto.MultiplayerRoundInfoDTO;

import java.util.List;

public class MultiplayerGameDetailsDTO {
    private String gameId;
    private int totalRounds;
    private String overallWinner;
    private List<String> players;
    private List<client.player.dto.MultiplayerRoundInfoDTO> rounds;
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