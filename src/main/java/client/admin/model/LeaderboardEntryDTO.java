package client.admin.model;

public class LeaderboardEntryDTO {
    private String username;
    private int wins;

    public LeaderboardEntryDTO(String username, int wins) {
        this.username = username;
        this.wins = wins;
    }

    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }
    public int getWins() { return wins; }
    public void setWins(int wins) { this.wins = wins; }
} 