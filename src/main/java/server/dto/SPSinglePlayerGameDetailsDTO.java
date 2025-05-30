package server.dto;

import java.util.List;

public class SPSinglePlayerGameDetailsDTO {
    public String gameId;
    public int totalRounds;
    public String overallWinner;
    public List<String> players;
    public List<SPSinglePlayerRoundInfoDTO> rounds;
    public long gameEndTime;

    // Default constructor for GSON
    public SPSinglePlayerGameDetailsDTO() {}

    public SPSinglePlayerGameDetailsDTO(String gameId, int totalRounds, String overallWinner, List<String> players, List<SPSinglePlayerRoundInfoDTO> rounds, long gameEndTime) {
        this.gameId = gameId;
        this.totalRounds = totalRounds;
        this.overallWinner = overallWinner;
        this.players = players;
        this.rounds = rounds;
        this.gameEndTime = gameEndTime;
    }
} 