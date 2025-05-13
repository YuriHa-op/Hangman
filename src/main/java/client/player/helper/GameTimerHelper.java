package client.player.helper;

import javafx.animation.KeyFrame;
import javafx.animation.Timeline;
import javafx.application.Platform;
import javafx.scene.control.Label;
import javafx.util.Duration;

public class GameTimerHelper {
    private Timeline timerTimeline;
    private int remainingTime;
    private Runnable onTimeUp;
    private Label timerLabel;

    public GameTimerHelper(Label timerLabel, Runnable onTimeUp) {
        this.timerLabel = timerLabel;
        this.onTimeUp = onTimeUp;
    }

    public void startRoundTimer(int roundTime, int initialRemaining) {
        stopRoundTimer();
        this.remainingTime = (initialRemaining > 0 && initialRemaining <= roundTime) ? initialRemaining : roundTime;
        updateLabel();
        timerTimeline = new Timeline();
        timerTimeline.setCycleCount(remainingTime);
        timerTimeline.getKeyFrames().add(
                new KeyFrame(Duration.seconds(1), event -> {
                    remainingTime--;
                    updateLabel();
                    if (remainingTime <= 10) timerLabel.setStyle("-fx-text-fill: red;");
                    if (remainingTime <= 0) {
                        stopRoundTimer();
                        if (onTimeUp != null) Platform.runLater(onTimeUp);
                    }
                })
        );
        timerTimeline.play();
    }

    public void stopRoundTimer() {
        if (timerTimeline != null) timerTimeline.stop();
    }

    private void updateLabel() {
        Platform.runLater(() -> timerLabel.setText(String.valueOf(remainingTime)));
    }

    public int getRemainingTime() {
        return remainingTime;
    }
} 