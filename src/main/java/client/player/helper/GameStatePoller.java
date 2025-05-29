package client.player.helper;

import javafx.animation.KeyFrame;
import javafx.animation.Timeline;
import javafx.util.Duration;

public class GameStatePoller {
    private Timeline pollTimer;
    private Runnable pollAction;
    private int intervalMillis;

    public GameStatePoller(Runnable pollAction, int intervalMillis) {
        this.pollAction = pollAction;
        this.intervalMillis = intervalMillis;
    }

    public void start() {
        stop();
        pollTimer = new Timeline(new KeyFrame(Duration.millis(intervalMillis), e -> pollAction.run()));
        pollTimer.setCycleCount(Timeline.INDEFINITE);
        pollTimer.play();
    }

    public void stop() {
        if (pollTimer != null) pollTimer.stop();
    }
} 