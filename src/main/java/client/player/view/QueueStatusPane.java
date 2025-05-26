package client.player.view;

import javafx.geometry.Pos;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.layout.HBox;
import javafx.scene.layout.VBox;
import javafx.scene.text.Font;

public class QueueStatusPane extends VBox {
    private final Label queueLabel;
    private final Label timerLabel;
    private final Label playerCountLabel;
    private final Button cancelButton;

    public QueueStatusPane() {
        setAlignment(Pos.CENTER);
        setSpacing(8);
        setStyle("-fx-background-color: rgba(0,0,0,0.7); -fx-padding: 16; -fx-background-radius: 10; -fx-border-radius: 10; -fx-border-color: #ffdd00; -fx-border-width: 2px;");

        queueLabel = new Label("Queueing for Match...");
        queueLabel.setFont(Font.font("Minecraftia", 20));
        queueLabel.setStyle("-fx-text-fill: #ffdd00;");

        timerLabel = new Label("30");
        timerLabel.setFont(Font.font("Minecraftia", 18));
        timerLabel.setStyle("-fx-text-fill: #ffffff;");

        playerCountLabel = new Label("0/8 players");
        playerCountLabel.setFont(Font.font("Minecraftia", 16));
        playerCountLabel.setStyle("-fx-text-fill: #ffffff;");

        cancelButton = new Button("Cancel");
        cancelButton.setFont(Font.font("Minecraftia", 14));
        cancelButton.setStyle("-fx-background-color: #d32f2f; -fx-text-fill: #fff; -fx-background-radius: 8; -fx-cursor: hand;");

        HBox infoBox = new HBox(20, timerLabel, playerCountLabel);
        infoBox.setAlignment(Pos.CENTER);

        getChildren().addAll(queueLabel, infoBox, cancelButton);
    }

    public void setTimer(int seconds) {
        timerLabel.setText(String.valueOf(seconds));
    }

    public void setPlayerCount(int current, int max) {
        playerCountLabel.setText(current + "/" + max + " players");
    }

    public Button getCancelButton() {
        return cancelButton;
    }
} 