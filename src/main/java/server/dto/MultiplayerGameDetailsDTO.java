package server.dto;

import java.util.List;

public class MultiplayerGameDetailsDTO {
    public String gameId;
    public int totalRounds;
    public String overallWinner;
    public List<String> players;
    public List<MultiplayerRoundInfoDTO> rounds;
    public long gameEndTime;

    // Default constructor for GSON
    public MultiplayerGameDetailsDTO() {}

    public MultiplayerGameDetailsDTO(String gameId, int totalRounds, String overallWinner, List<String> players, List<MultiplayerRoundInfoDTO> rounds, long gameEndTime) {
        this.gameId = gameId;
        this.totalRounds = totalRounds;
        this.overallWinner = overallWinner;
        this.players = players;
        this.rounds = rounds;
        this.gameEndTime = gameEndTime;
    }
} 