package server.dto;

public class SPSinglePlayerRoundInfoDTO {
    public int roundNumber;
    public String word;
    public String winner;

    // Default constructor for GSON
    public SPSinglePlayerRoundInfoDTO() {}

    public SPSinglePlayerRoundInfoDTO(int roundNumber, String word, String winner) {
        this.roundNumber = roundNumber;
        this.word = word;
        this.winner = winner;
    }
} 