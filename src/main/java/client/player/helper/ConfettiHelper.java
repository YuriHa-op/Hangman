package client.player.helper;

import javafx.animation.*;
import javafx.application.Platform;
import javafx.scene.layout.Pane;
import javafx.scene.paint.Color;
import javafx.scene.shape.Rectangle;
import javafx.util.Duration;
import java.util.Random;

public class ConfettiHelper {

    public static void showConfetti(Pane parent) {
        if (parent == null) {
            return;
        }

        if (parent.getWidth() <= 0 || parent.getHeight() <= 0) {
            Platform.runLater(() -> {
                if (parent.getWidth() <= 0 || parent.getHeight() <= 0) {
                    System.err.println("ConfettiHelper: Parent dimensions still invalid after deferral. Width: " + parent.getWidth() + ", Height: " + parent.getHeight());
                    return;
                }
                createAndAnimateConfetti(parent);
            });
        } else {
            createAndAnimateConfetti(parent);
        }
    }

    private static void createAndAnimateConfetti(Pane parent) {
        Pane confettiPane = new Pane();
        confettiPane.setPickOnBounds(false);
        parent.getChildren().add(confettiPane);
        confettiPane.toFront();

        int confettiCount = 200;
        Random random = new Random();

        double centerX = parent.getWidth() / 2.0;
        double centerY = parent.getHeight() / 2.0;

        double maxDurationSeconds = 0;

        for (int i = 0; i < confettiCount; i++) {
            Rectangle confetti = new Rectangle(random.nextInt(5) + 5, random.nextInt(10) + 10);
            confetti.setArcWidth(8);
            confetti.setArcHeight(8);
            confetti.setFill(Color.color(random.nextDouble(), random.nextDouble(), random.nextDouble()));

            confetti.setTranslateX(centerX);
            confetti.setTranslateY(centerY);

            confettiPane.getChildren().add(confetti);

            double angle = random.nextDouble() * 2 * Math.PI;
            double travelDistance = Math.min(parent.getWidth(), parent.getHeight()) * (0.4 + random.nextDouble() * 0.3);

            double dx = Math.cos(angle) * travelDistance;
            double dy = Math.sin(angle) * travelDistance;

            double currentDurationSeconds = 1.8 + random.nextDouble() * 1.5;
            if (currentDurationSeconds > maxDurationSeconds) {
                maxDurationSeconds = currentDurationSeconds;
            }

            RotateTransition rotate = new RotateTransition(Duration.seconds(currentDurationSeconds), confetti);
            rotate.setByAngle(360 * (random.nextInt(2) + 1));

            TranslateTransition explode = new TranslateTransition(Duration.seconds(currentDurationSeconds), confetti);
            explode.setToX(centerX + dx);
            explode.setToY(centerY + dy);
            explode.setInterpolator(Interpolator.EASE_OUT);

            FadeTransition fade = new FadeTransition(Duration.seconds(currentDurationSeconds), confetti);
            fade.setFromValue(0.9);
            fade.setToValue(0.0);
            fade.setInterpolator(Interpolator.EASE_IN);

            PauseTransition pause = new PauseTransition(Duration.millis(random.nextInt(300)));

            SequentialTransition st = new SequentialTransition(pause, new ParallelTransition(confetti, explode, rotate, fade));
            st.setOnFinished(e -> confettiPane.getChildren().remove(confetti));
            st.play();
        }

        if (maxDurationSeconds > 0) {
            final double finalMaxDuration = maxDurationSeconds;
            Timeline removePaneTimeline = new Timeline(
                new KeyFrame(Duration.seconds(finalMaxDuration + 0.5),
                e -> {
                    if (parent.getChildren().contains(confettiPane)) {
                        parent.getChildren().remove(confettiPane);
                    }
            }));
            removePaneTimeline.play();
        } else if (confettiCount == 0) {
             if (parent.getChildren().contains(confettiPane)) {
                parent.getChildren().remove(confettiPane);
            }
        }
    }
} 