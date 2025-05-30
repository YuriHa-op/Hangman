package server.dto;

public class MultiplayerRoundInfoDTO {
    public int roundNumber;
    public String word;
    public String winner;

    // Default constructor for GSON
    public MultiplayerRoundInfoDTO() {}

    public MultiplayerRoundInfoDTO(int roundNumber, String word, String winner) {
        this.roundNumber = roundNumber;
        this.word = word;
        this.winner = winner;
    }
} 