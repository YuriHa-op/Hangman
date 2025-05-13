package client.player.helper;

import javafx.animation.*;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.layout.*;
import javafx.scene.paint.Color;
import javafx.scene.shape.Rectangle;
import javafx.stage.Modality;
import javafx.stage.Stage;
import javafx.util.Duration;

import java.util.Random;//victory animation
import animatefx.animation.Tada;
import animatefx.animation.FadeInDown;

public class GameViewHelper {

    public static void showWinCelebration(Stage owner, String word, String message, Runnable onContinue) {
        Stage celebrationStage = new Stage();
        celebrationStage.initModality(Modality.APPLICATION_MODAL);
        celebrationStage.initOwner(owner);
        celebrationStage.setTitle("VICTORY!");

        StackPane root = new StackPane();
        root.setStyle("-fx-background-color: rgba(0, 0, 0, 0.8); -fx-background-radius: 10;");

        VBox content = new VBox(20);
        content.setAlignment(Pos.CENTER);
        content.setPadding(new Insets(30));
        content.setMaxWidth(400);
        content.setMaxHeight(400);

        Label victoryLabel = new Label("VICTORY!");
        victoryLabel.setStyle("-fx-font-family: 'Minecraft'; -fx-font-size: 48px; -fx-text-fill: gold; -fx-font-weight: bold;");

        Label wordLabel = new Label("The word was: " + word);
        wordLabel.setStyle("-fx-font-family: 'Minecraft'; -fx-font-size: 24px; -fx-text-fill: #55FF55;");

        Label messageLabel = new Label(message);
        messageLabel.setStyle("-fx-font-family: 'Minecraft'; -fx-font-size: 18px; -fx-text-fill: white;");
        messageLabel.setWrapText(true);

        Button continueButton = new Button("Continue");
        continueButton.setStyle("-fx-font-family: 'Minecraft'; -fx-font-size: 20px; -fx-background-color: #55AA55; " +
                "-fx-text-fill: white; -fx-padding: 10 20; -fx-background-radius: 5;");
        continueButton.setOnAction(e -> {
            celebrationStage.close();
            if (onContinue != null) onContinue.run();
        });

        content.getChildren().addAll(victoryLabel, wordLabel, messageLabel, continueButton);
        root.getChildren().add(content);

        // Particle effect
        Pane particlePane = new Pane();
        root.getChildren().add(0, particlePane);

        Scene scene = new Scene(root, 500, 400);
        scene.setFill(Color.TRANSPARENT);
        celebrationStage.setScene(scene);

        // Animations
        ScaleTransition bounce = new ScaleTransition(Duration.millis(500), victoryLabel);
        bounce.setFromX(0.5);
        bounce.setFromY(0.5);
        bounce.setToX(1.2);
        bounce.setToY(1.2);
        bounce.setCycleCount(2);
        bounce.setAutoReverse(true);

        Random random = new Random();
        Timeline particleTimeline = new Timeline(
                new KeyFrame(Duration.millis(100), e -> {
                    for (int i = 0; i < 5; i++) {
                        Rectangle particle = new Rectangle(5, 5);
                        particle.setFill(Color.color(
                                random.nextDouble(), random.nextDouble(), random.nextDouble()));

                        double startX = random.nextDouble() * 500;
                        particle.setTranslateX(startX);
                        particle.setTranslateY(400);

                        particlePane.getChildren().add(particle);

                        TranslateTransition move = new TranslateTransition(
                                Duration.seconds(1 + random.nextDouble() * 2), particle);
                        move.setToY(-random.nextDouble() * 400);
                        move.setToX(startX + (random.nextDouble() * 100 - 50));

                        FadeTransition fade = new FadeTransition(Duration.seconds(2), particle);
                        fade.setFromValue(1.0);
                        fade.setToValue(0.0);

                        ParallelTransition pt = new ParallelTransition(particle, move, fade);
                        pt.setOnFinished(ev -> particlePane.getChildren().remove(particle));
                        pt.play();
                    }
                })
        );
        particleTimeline.setCycleCount(30);

        celebrationStage.setOnShown(e -> {
            // AnimateFX: Tada for label, FadeInDown for root
            new Tada(victoryLabel).play();
            new FadeInDown(root).play();
            bounce.play();
            particleTimeline.play();
        });

        celebrationStage.showAndWait();
    }

    public static void showGameOverDialog(Stage owner, String message, boolean isWin, Runnable onClose) {
        Dialog<ButtonType> dialog = new Dialog<>();
        dialog.setTitle("Game Over");
        dialog.initOwner(owner);
        dialog.initModality(Modality.APPLICATION_MODAL);

        DialogPane dialogPane = dialog.getDialogPane();
        dialogPane.getStylesheets().add(GameViewHelper.class.getResource("/client/player/view/GameView.css").toExternalForm());
        dialogPane.getStyleClass().add("minecraft-dialog");

        VBox content = new VBox(10);
        content.setAlignment(Pos.CENTER);
        content.getStyleClass().add("gameover-background");

        Label resultLabel = new Label(isWin ? "You Win!" : "Game Over");
        resultLabel.getStyleClass().add("gameover-title");
        resultLabel.setStyle("-fx-text-fill: " + (isWin ? "#55FF55" : "#FF5555") + ";");

        ScaleTransition st = new ScaleTransition(Duration.millis(300), resultLabel);
        st.setFromX(0.8);
        st.setFromY(0.8);
        st.setToX(1.0);
        st.setToY(1.0);
        st.setInterpolator(Interpolator.EASE_OUT);
        st.play();

        Label messageLabel = new Label(message);
        messageLabel.setWrapText(true);
        messageLabel.getStyleClass().add("gameover-message");

        content.getChildren().addAll(resultLabel, messageLabel);
        dialogPane.setContent(content);
        dialogPane.getButtonTypes().add(ButtonType.OK);

        Button okButton = (Button) dialogPane.lookupButton(ButtonType.OK);
        okButton.getStyleClass().add("gameover-button");

        okButton.setOnAction(e -> {
            dialog.close();
            if (onClose != null) onClose.run();
        });

        dialog.setOnShown(e -> {
            // AnimateFX: Tada for resultLabel, FadeInDown for dialogPane
            new Tada(resultLabel).play();
            new FadeInDown(dialogPane).play();
        });

        dialog.showAndWait();
    }
}