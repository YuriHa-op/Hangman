package client.player.model;

import javafx.beans.property.SimpleIntegerProperty;
import javafx.beans.property.SimpleStringProperty;

public class PlayerScoreEntry {
    private final SimpleIntegerProperty rank;
    private final SimpleStringProperty playerName;
    private final SimpleIntegerProperty score;

    public PlayerScoreEntry(int rank, String playerName, int score) {
        this.rank = new SimpleIntegerProperty(rank);
        this.playerName = new SimpleStringProperty(playerName);
        this.score = new SimpleIntegerProperty(score);
    }

    public int getRank() {
        return rank.get();
    }

    public SimpleIntegerProperty rankProperty() {
        return rank;
    }

    public String getPlayerName() {
        return playerName.get();
    }

    public SimpleStringProperty playerNameProperty() {
        return playerName;
    }

    public int getScore() {
        return score.get();
    }

    public SimpleIntegerProperty scoreProperty() {
        return score;
    }
} 