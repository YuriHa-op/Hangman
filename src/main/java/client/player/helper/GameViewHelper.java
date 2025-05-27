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
import javafx.stage.StageStyle;
import javafx.util.Duration;

import java.util.Random;//victory animation
import animatefx.animation.Tada;
import animatefx.animation.FadeInDown;
import animatefx.animation.Bounce;

public class GameViewHelper {

    public static void showWinCelebration(Stage owner, String word, String message, Runnable onContinue) {
        Stage celebrationStage = new Stage();
        celebrationStage.initModality(Modality.APPLICATION_MODAL);
        celebrationStage.initOwner(owner);
        celebrationStage.initStyle(StageStyle.TRANSPARENT);
        celebrationStage.setTitle("VICTORY!");

        StackPane root = new StackPane();
        root.setStyle("-fx-background-color: rgba(0, 0, 0, 0.85); -fx-border-color: gold; -fx-border-width: 2px; -fx-background-radius: 15px; -fx-border-radius: 15px;");

        VBox content = new VBox(20);
        content.setAlignment(Pos.CENTER);
        content.setPadding(new Insets(30));
        content.setMaxWidth(400);
        content.setMaxHeight(400);
        content.setStyle("-fx-background-color: transparent;");

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

        content.getChildren().addAll(victoryLabel, wordLabel, messageLabel, continueButton);
        root.getChildren().add(content);

        // Make window draggable
        final double[] xOffset = {0};
        final double[] yOffset = {0};

        root.setOnMousePressed(event -> {
            xOffset[0] = event.getSceneX();
            yOffset[0] = event.getSceneY();
        });

        root.setOnMouseDragged(event -> {
            celebrationStage.setX(event.getScreenX() - xOffset[0]);
            celebrationStage.setY(event.getScreenY() - yOffset[0]);
        });

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
        // Original logic: onContinue runs when the button is clicked and stage is closed.
        continueButton.setOnAction(e -> {
            celebrationStage.close();
            if (onContinue != null) onContinue.run();
        });

        celebrationStage.showAndWait();
    }

    public static void showGameOverDialog(Stage owner, String message, boolean isWin, Runnable onClose) {
        Stage dialog = new Stage();
        dialog.initOwner(owner);
        dialog.initModality(Modality.APPLICATION_MODAL);
        dialog.initStyle(StageStyle.UNDECORATED); // Removes window buttons

        VBox content = new VBox(10);
        content.setAlignment(Pos.CENTER);
        content.getStyleClass().add("gameover-background");
        content.getStylesheets().add(GameViewHelper.class.getResource("/client/player/view/GameView.css").toExternalForm());

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

        Button okButton = new Button("OK");
        okButton.getStyleClass().add("gameover-button");
        okButton.setOnAction(e -> {
            dialog.close();
            if (onClose != null) onClose.run();
        });

        content.getChildren().addAll(resultLabel, messageLabel, okButton);

        Scene scene = new Scene(content);
        dialog.setScene(scene);

        // Make it draggable
        final Delta dragDelta = new Delta();
        content.setOnMousePressed(event -> {
            dragDelta.x = dialog.getX() - event.getScreenX();
            dragDelta.y = dialog.getY() - event.getScreenY();
        });
        content.setOnMouseDragged(event -> {
            dialog.setX(event.getScreenX() + dragDelta.x);
            dialog.setY(event.getScreenY() + dragDelta.y);
        });

        // AnimateFX: Optional
        dialog.setOnShown(e -> {
            new Tada(resultLabel).play();
            new FadeInDown(content).play();
        });

        dialog.showAndWait();
    }

    // Helper class for dragging
    private static class Delta {
        double x, y;
    }


    public static void showExitGameDialog(Stage owner, Runnable onExit) {
        Dialog<ButtonType> dialog = new Dialog<>();
        dialog.setTitle("Exit Game");
        dialog.initOwner(owner);
        dialog.initModality(Modality.APPLICATION_MODAL);

        DialogPane dialogPane = dialog.getDialogPane();
        dialogPane.getStylesheets().add(GameViewHelper.class.getResource("/client/player/view/GameView.css").toExternalForm());
        dialogPane.getStyleClass().add("minecraft-dialog");

        VBox content = new VBox(15);
        content.setAlignment(Pos.CENTER);
        content.getStyleClass().add("gameover-background");

        Label titleLabel = new Label("Are you sure you want to leave the game?");
        titleLabel.setStyle("-fx-font-family: 'Minecraftia', 'Arial Black', sans-serif; -fx-font-size: 22px; -fx-text-fill: #FF5555; -fx-font-weight: bold;");
        Label messageLabel = new Label("Leaving will forfeit the game and return you to the home menu.");
        messageLabel.setWrapText(true);
        messageLabel.setStyle("-fx-font-family: 'Minecraftia', 'Arial Black', sans-serif; -fx-font-size: 16px; -fx-text-fill: #FFFFFF;");

        content.getChildren().addAll(titleLabel, messageLabel);
        dialogPane.setContent(content);
        ButtonType leaveButton = new ButtonType("Leave", ButtonBar.ButtonData.OK_DONE);
        ButtonType cancelButton = new ButtonType("Cancel", ButtonBar.ButtonData.CANCEL_CLOSE);
        dialogPane.getButtonTypes().setAll(leaveButton, cancelButton);

        Button leaveBtn = (Button) dialogPane.lookupButton(leaveButton);
        leaveBtn.setStyle("-fx-background-color: #FF5555; -fx-text-fill: white; -fx-font-family: 'Minecraftia', 'Arial Black', sans-serif; -fx-font-size: 16px; -fx-background-radius: 5;");
        Button cancelBtn = (Button) dialogPane.lookupButton(cancelButton);
        cancelBtn.setStyle("-fx-background-color: #555555; -fx-text-fill: white; -fx-font-family: 'Minecraftia', 'Arial Black', sans-serif; -fx-font-size: 16px; -fx-background-radius: 5;");

        dialog.setOnShown(e -> {
            new Tada(titleLabel).play();
            new FadeInDown(dialogPane).play();
        });

        dialog.setResultConverter(dialogButton -> {
            if (dialogButton == leaveButton) {
                if (onExit != null) onExit.run();
            }
            return null;
        });

        dialog.showAndWait();
    }

    public static void animateWordDisplay(Label label) {
        // Minecraft-style bounce and color effect
        ScaleTransition scale = new ScaleTransition(Duration.millis(250), label);
        scale.setFromX(1.0);
        scale.setFromY(1.0);
        scale.setToX(1.2);
        scale.setToY(1.2);
        scale.setAutoReverse(true);
        scale.setCycleCount(2);

        // For Label, setStyle to change text fill color as FillTransition is for Shapes
        String originalStyle = label.getStyle();
        // Append new style, assuming originalStyle might not end with a semicolon
        String newStyle = originalStyle + (originalStyle.trim().endsWith(";") ? "" : ";") + " -fx-text-fill: #55FF55;";
        label.setStyle(newStyle);
        scale.setOnFinished(e -> label.setStyle(originalStyle)); // Revert to original style

        scale.play();
    }

    public static void showRoundWinner(TextArea gameOutput, int roundNum, String winner, boolean playerWon) {
        String msg = "\n§l§a[Round " + (roundNum + 1) + "] Winner: " + winner + (playerWon ? " (You!)" : "") + "\n";
        gameOutput.appendText(msg);
    }

    public static void showNoRoundWinner(TextArea gameOutput) {
        String msg = "\n§l§e[Round] No winner this round.\n";
        gameOutput.appendText(msg);
    }

    // Explosion animation for round transition
    public static void explodeNode(javafx.scene.Node node, Runnable onFinished) {
        if (node == null) {
            if (onFinished != null) onFinished.run();
            return;
        }
        javafx.animation.ScaleTransition scale = new javafx.animation.ScaleTransition(javafx.util.Duration.millis(400), node);
        scale.setFromX(1.0);
        scale.setFromY(1.0);
        scale.setToX(2.5);
        scale.setToY(2.5);
        scale.setInterpolator(javafx.animation.Interpolator.EASE_IN);

        javafx.animation.FadeTransition fade = new javafx.animation.FadeTransition(javafx.util.Duration.millis(350), node);
        fade.setFromValue(1.0);
        fade.setToValue(0.0);

        javafx.animation.ParallelTransition pt = new javafx.animation.ParallelTransition(node, scale, fade);
        pt.setOnFinished(e -> {
            node.setVisible(false);
            // Reset properties for potential reuse
            node.setScaleX(1.0);
            node.setScaleY(1.0);
            node.setOpacity(1.0);
            if (onFinished != null) onFinished.run();
        });
        pt.play();
    }
}
