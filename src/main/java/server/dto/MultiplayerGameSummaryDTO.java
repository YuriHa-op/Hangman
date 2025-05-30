package server.dto;

import java.util.List;

public class MultiplayerGameSummaryDTO {
    public String gameId;
    public int totalRounds;
    public String overallWinner;
    public List<String> players;
    public long gameEndTime;

    // Default constructor for GSON
    public MultiplayerGameSummaryDTO() {}

    public MultiplayerGameSummaryDTO(String gameId, int totalRounds, String overallWinner, List<String> players, long gameEndTime) {
        this.gameId = gameId;
        this.totalRounds = totalRounds;
        this.overallWinner = overallWinner;
        this.players = players;
        this.gameEndTime = gameEndTime;
    }
} 