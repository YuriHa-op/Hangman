package client.admin.model;

public class SystemSettings {
    private int waitingTimeSeconds;
    private int roundTimeSeconds;

    public SystemSettings(int waitingTimeSeconds, int roundTimeSeconds) {
        this.waitingTimeSeconds = waitingTimeSeconds;
        this.roundTimeSeconds = roundTimeSeconds;
    }

    // Getters and setters
    public int getWaitingTimeSeconds() {
        return waitingTimeSeconds;
    }

    public void setWaitingTimeSeconds(int waitingTimeSeconds) {
        this.waitingTimeSeconds = waitingTimeSeconds;
    }

    public int getRoundTimeSeconds() {
        return roundTimeSeconds;
    }

    public void setRoundTimeSeconds(int roundTimeSeconds) {
        this.roundTimeSeconds = roundTimeSeconds;
    }
}