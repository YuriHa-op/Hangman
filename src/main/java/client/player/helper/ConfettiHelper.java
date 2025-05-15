package client.player.helper;

import javafx.animation.*;
import javafx.scene.layout.Pane;
import javafx.scene.paint.Color;
import javafx.scene.shape.Rectangle;
import javafx.util.Duration;
import java.util.Random;

public class ConfettiHelper {
    public static void showConfetti(Pane parent) {
        if (parent == null || parent.getWidth() <= 0 || parent.getHeight() <= 0) return;
        Pane confettiPane = new Pane();
        confettiPane.setPickOnBounds(false);
        parent.getChildren().add(confettiPane);
        confettiPane.toFront();
        int confettiCount = 100;
        Random random = new Random();
        double centerX = parent.getWidth() / 2.0;
        double centerY = parent.getHeight() / 2.0;
        for (int i = 0; i < confettiCount; i++) {
            Rectangle confetti = new Rectangle(8, 18);
            confetti.setArcWidth(8);
            confetti.setArcHeight(8);
            confetti.setFill(Color.color(random.nextDouble(), random.nextDouble(), random.nextDouble()));
            confetti.setTranslateX(centerX);
            confetti.setTranslateY(centerY);
            confettiPane.getChildren().add(confetti);
            double angle = random.nextDouble() * 2 * Math.PI;
            double speed = 200 + random.nextDouble() * 350;
            double dx = Math.cos(angle) * speed;
            double dy = Math.sin(angle) * speed;
            double duration = 1.5 + random.nextDouble() * 1.2;
            RotateTransition rotate = new RotateTransition(Duration.seconds(duration), confetti);
            rotate.setByAngle(360 + random.nextInt(360));
            TranslateTransition explode = new TranslateTransition(Duration.seconds(duration), confetti);
            explode.setByX(dx);
            explode.setByY(dy);
            FadeTransition fade = new FadeTransition(Duration.seconds(duration), confetti);
            fade.setFromValue(1.0);
            fade.setToValue(0.0);
            ParallelTransition pt = new ParallelTransition(confetti, explode, rotate, fade);
            pt.setOnFinished(e -> confettiPane.getChildren().remove(confetti));
            pt.play();
        }
        Timeline removePane = new Timeline(new KeyFrame(Duration.seconds(2.7), e -> parent.getChildren().remove(confettiPane)));
        removePane.play();
    }
} 