package client.player.helper;

import javafx.animation.KeyFrame;
import javafx.animation.Timeline;
import javafx.util.Duration;

public class GameStatePoller {
    private Timeline pollTimer;
    private Runnable pollAction;
    private int intervalSeconds;

    public GameStatePoller(Runnable pollAction, int intervalSeconds) {
        this.pollAction = pollAction;
        this.intervalSeconds = intervalSeconds;
    }

    public void start() {
        stop();
        pollTimer = new Timeline(new KeyFrame(Duration.seconds(intervalSeconds), e -> pollAction.run()));
        pollTimer.setCycleCount(Timeline.INDEFINITE);
        pollTimer.play();
    }

    public void stop() {
        if (pollTimer != null) pollTimer.stop();
    }
} 