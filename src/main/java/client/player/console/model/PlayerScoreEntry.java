package client.player.console.model;

public class PlayerScoreEntry {
    private int rank;
    private String playerName;
    private int score;

    public PlayerScoreEntry(int rank, String playerName, int score) {
        this.rank = rank;
        this.playerName = playerName;
        this.score = score;
    }

    public int getRank() {
        return rank;
    }

    public void setRank(int rank) {
        this.rank = rank;
    }

    public String getPlayerName() {
        return playerName;
    }

    public void setPlayerName(String playerName) {
        this.playerName = playerName;
    }

    public int getScore() {
        return score;
    }

    public void setScore(int score) {
        this.score = score;
    }
} 