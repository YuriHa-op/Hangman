package client.player.helper;

import javafx.animation.KeyFrame;
import javafx.animation.Timeline;
import javafx.application.Platform;
import javafx.scene.control.Label;
import javafx.util.Duration;
import animatefx.animation.Shake;

public class GameTimerHelper {
    private Timeline roundTimeline;
    private int remainingSeconds;
    private Label timerLabel;
    private Runnable onTimeUp;
    private boolean internalHasTimedUp = false; // Flag to track if timer completed

    public GameTimerHelper(Label timerLabel, Runnable onTimeUp) {
        this.timerLabel = timerLabel;
        this.onTimeUp = onTimeUp;
        this.internalHasTimedUp = false; // Initialize
    }

    public void startRoundTimer(int totalSeconds, int currentRemainingSeconds) {
        stopRoundTimerActual(); // Stop any existing timeline to prevent multiple timers
        this.internalHasTimedUp = false; // Reset flag for this new timing session
        this.remainingSeconds = currentRemainingSeconds > 0 ? currentRemainingSeconds : totalSeconds;

        if (this.remainingSeconds <= 0) { // If starting with no time, it's immediately timed up
            this.internalHasTimedUp = true;
            timerLabel.setText("0");
            if (onTimeUp != null) {
                Platform.runLater(onTimeUp); // Ensure UI updates on JavaFX thread
            }
            return; // No need to start a timeline
        }

        timerLabel.setText(String.valueOf(this.remainingSeconds));
        roundTimeline = new Timeline(new KeyFrame(Duration.seconds(1), event -> {
            remainingSeconds--;
            if (remainingSeconds <= 0) {
                timerLabel.setText("0");
                stopRoundTimerActual(); // Stop the timeline
                this.internalHasTimedUp = true; // Set flag: timer has completed
                if (onTimeUp != null) {
                    onTimeUp.run();
                }
            } else {
                timerLabel.setText(String.valueOf(remainingSeconds));
            }
        }));
        roundTimeline.setCycleCount(this.remainingSeconds > 0 ? this.remainingSeconds : Timeline.INDEFINITE); // Ensure cycle count is positive or indefinite
        if (this.remainingSeconds > 0) {
            roundTimeline.play();
        }
    }

    public void stopRoundTimer() {
        // This method is called to stop the visual timer,
        // but should not reset internalHasTimedUp, as that flag indicates
        // whether this timer instance *did* complete.
        stopRoundTimerActual();
    }

    private void stopRoundTimerActual() {
        if (roundTimeline != null) {
            roundTimeline.stop();
            roundTimeline = null;
        }
    }

    public boolean hasTimedUp() {
        return internalHasTimedUp;
    }
}