import javafx.animation.KeyFrame;
import javafx.animation.Timeline;
import javafx.application.Platform;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.layout.StackPane;
import javafx.stage.Stage;
import javafx.util.Duration;

import java.util.concurrent.atomic.AtomicInteger;

public class AfkCheckDialog {

    private static Stage dialogStage;
    private static Timeline countdownTimeline;

    public static void show(Runnable onTimedOut) {
        if (dialogStage != null) {
            return; // Already showing
        }

        dialogStage = new Stage();
        dialogStage.setTitle("AFK Check");
        dialogStage.setResizable(false);

        StackPane root = new StackPane();
        dialogStage.setScene(new javafx.scene.Scene(root, 300, 150));

        Label titleLabel = new Label("Are you still in the game?");
        titleLabel.setStyle("-fx-font-family: 'Minecraftia'; -fx-font-size: 24px; -fx-text-fill: #f1c40f;");

        AtomicInteger countdownSeconds = new AtomicInteger(10);
        Label countdownLabel = new Label("Closing in: " + countdownSeconds.get() + "s");
        countdownLabel.setStyle("-fx-font-family: 'Minecraftia'; -fx-font-size: 18px; -fx-text-fill: white;");

        Button yesButton = new Button("Yes, I'm here!");

        root.getChildren().addAll(titleLabel, countdownLabel, yesButton);

        countdownTimeline = new Timeline(new KeyFrame(Duration.seconds(1), event -> {
            int remaining = countdownSeconds.decrementAndGet();
            countdownLabel.setText("Closing in: " + remaining + "s");
            if (remaining <= 0) {
                countdownTimeline.stop();
                titleLabel.setText("AFK Timeout");
                countdownLabel.setText("Waiting for server/other players...");
                yesButton.setDisable(true);
                yesButton.setText("Timed Out");
                if (onTimedOut != null) {
                    onTimedOut.run();
                }
            }
        }));
        countdownTimeline.setCycleCount(Timeline.INDEFINITE);

        yesButton.setOnAction(event -> {
            if (countdownTimeline != null) {
                countdownTimeline.stop();
            }
            dialogStage = null;
            countdownTimeline = null;
        });

        dialogStage.setOnHidden(event -> {
            if (countdownTimeline != null) {
                countdownTimeline.stop();
            }
            dialogStage = null;
            countdownTimeline = null;
        });

        dialogStage.showAndWait();
    }

    public static boolean isShowing() {
        return dialogStage != null;
    }
} 