package client.admin.model;

public class SystemStatisticsDTO {
    private int totalGames;
    private int wins;
    private int losses;
    private double winRate;
    private int waitingTime;
    private int roundTime;

    public SystemStatisticsDTO(int totalGames, int wins, int losses, double winRate, int waitingTime, int roundTime) {
        this.totalGames = totalGames;
        this.wins = wins;
        this.losses = losses;
        this.winRate = winRate;
        this.waitingTime = waitingTime;
        this.roundTime = roundTime;
    }

    public int getTotalGames() { return totalGames; }
    public void setTotalGames(int totalGames) { this.totalGames = totalGames; }
    public int getWins() { return wins; }
    public void setWins(int wins) { this.wins = wins; }
    public int getLosses() { return losses; }
    public void setLosses(int losses) { this.losses = losses; }
    public double getWinRate() { return winRate; }
    public void setWinRate(double winRate) { this.winRate = winRate; }
    public int getWaitingTime() { return waitingTime; }
    public void setWaitingTime(int waitingTime) { this.waitingTime = waitingTime; }
    public int getRoundTime() { return roundTime; }
    public void setRoundTime(int roundTime) { this.roundTime = roundTime; }
} 