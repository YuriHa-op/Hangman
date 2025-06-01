package client.player.helper;

import javafx.animation.KeyFrame;
import javafx.animation.Timeline;
import javafx.application.Platform;
import javafx.scene.control.Label;
import javafx.util.Duration;
import animatefx.animation.Shake;
import javafx.animation.PauseTransition;

public class GameTimerHelper {
    private Timeline timerTimeline;
    private int remainingTime;
    private Runnable onTimeUp;
    private Label timerLabel;
    private String defaultTimerColorStyle = ""; // Or your default style like "-fx-text-fill: white;"

    public GameTimerHelper(Label timerLabel, Runnable onTimeUp) {
        this.timerLabel = timerLabel;
        this.onTimeUp = onTimeUp;
        if (timerLabel != null) {
            // Assuming the default style is the initial one or you can set it here.
            // For simplicity, we capture any inline style if set, or use empty for CSS default.
            this.defaultTimerColorStyle = timerLabel.getStyle(); 
        }
    }

    private void playShakeAndProceed(Runnable onProceed) {
        if (timerLabel != null) {
            new Shake(timerLabel).play();
            PauseTransition pause = new PauseTransition(Duration.millis(300)); 
            pause.setOnFinished(event -> {
                if (onProceed != null) {
                    onProceed.run();
                }
            });
            pause.play();
        } else {
            if (onProceed != null) {
                onProceed.run();
            }
        }
    }

    public void startRoundTimer(int roundTime, int initialRemainingTime) {
        stopRoundTimer();
        this.remainingTime = initialRemainingTime;

        if (this.remainingTime <= 0) {
            this.remainingTime = 0;
            
            // This will queue label text/color update on the FX thread
            updateLabelAndColor(); 

            // This will queue another task on the FX thread to play shake then call onTimeUp
            Platform.runLater(() -> playShakeAndProceed(onTimeUp));
            return; 
        }

        // Initial set of time and color for timers starting > 0
        updateLabelAndColor(); 

        timerTimeline = new Timeline();
        timerTimeline.setCycleCount(this.remainingTime); 
        timerTimeline.getKeyFrames().add(
                new KeyFrame(Duration.seconds(1), event -> {
                    this.remainingTime--;
                    updateLabelAndColor(); // Update text and color every second
                    if (this.remainingTime <= 0) {
                        stopRoundTimer();
                        // When timeline reaches zero, also play shake then call onTimeUp
                        Platform.runLater(() -> playShakeAndProceed(onTimeUp));
                    }
                })
        );
        timerTimeline.play();
    }

    public void stopRoundTimer() {
        if (timerTimeline != null) timerTimeline.stop();
    }

    private void updateLabelAndColor() {
        if (timerLabel == null) return;

        Platform.runLater(() -> {
            timerLabel.setText(String.valueOf(remainingTime));
            if (remainingTime <= 0) {
                timerLabel.setStyle("-fx-text-fill: red;");
                // Consider adding Shake here if timer directly goes to 0 and stops
                // However, startRoundTimer already handles immediate onTimeUp for initial <= 0
            } else if (remainingTime <= 5) { 
                timerLabel.setStyle("-fx-text-fill: red;");
            } else if (remainingTime <= 15) {
                timerLabel.setStyle("-fx-text-fill: yellow;");
            } else {
                timerLabel.setStyle(defaultTimerColorStyle); // Reset to default
            }
        });
    }

    public int getRemainingTime() {
        return remainingTime;
    }

    // Call this to reset timer label to default appearance when timer is not active
    public void resetTimerLabelAppearance() {
        if (timerLabel != null) {
            Platform.runLater(() -> {
                timerLabel.setText(""); // Clear text
                timerLabel.setStyle(defaultTimerColorStyle); // Reset color
            });
        }
    }

    public void setTime(int seconds) {
        stopRoundTimer();
        this.remainingTime = seconds;
        updateLabelAndColor();
    }
} 