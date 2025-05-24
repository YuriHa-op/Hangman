package client.player.controller;

import animatefx.animation.*;
import javafx.animation.*;
import javafx.animation.Timeline;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.scene.Scene;
import javafx.scene.control.Label;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.layout.VBox;
import javafx.scene.layout.StackPane;
import javafx.stage.Modality;
import javafx.stage.Stage;
import javafx.util.Duration;
import javafx.scene.layout.HBox;
import javafx.scene.Node;
import client.player.helper.ConfettiHelper;
import javafx.scene.layout.Pane;
import javafx.application.Platform;

public class MatchFoundDialogController {
    @FXML private Label player1Name;
    @FXML private Label player2Name;
    @FXML private ImageView player1Pfp;
    @FXML private ImageView player2Pfp;
    @FXML private Label countdownLabel;
    @FXML private Label matchTitle;
    @FXML private ImageView backgroundImage;
    @FXML private HBox playerRow; // Add fx:id="playerRow" to the HBox in FXML
    @FXML private Label matchVs;   // Add fx:id="matchVs" to the "vs" label in FXML
    @FXML private StackPane root;

    private Timeline countdownTimeline;
    private int countdown = 5;
    private Runnable onCountdownFinished;
    private Stage dialogStage;

    @FXML
    public void initialize() {
        if (backgroundImage != null) {
            try {
                Image bgImg = new Image(getClass().getResourceAsStream("/client/player/view/pasobeso.png"));
                backgroundImage.setImage(bgImg);
                backgroundImage.setPreserveRatio(false);
                animateBackground();
            } catch (Exception e) {
                System.err.println("Could not load background image for MatchFoundDialog: " + e.getMessage());
            }
        }
    }

    public static void showDialog(Stage owner, String player1, String player2, Runnable onCountdownFinished) {
        try {
            FXMLLoader loader = new FXMLLoader(MatchFoundDialogController.class.getResource("/client/player/view/MatchFoundDialog.fxml"));
            StackPane root = loader.load();
            MatchFoundDialogController controller = loader.getController();
            controller.onCountdownFinished = onCountdownFinished;
            controller.player1Name.setText(player1);
            controller.player2Name.setText(player2);
            controller.player1Pfp.setImage(new Image(MatchFoundDialogController.class.getResourceAsStream("/client/player/view/player1.png")));
            controller.player2Pfp.setImage(new Image(MatchFoundDialogController.class.getResourceAsStream("/client/player/view/player2.png")));
            Stage dialog = new Stage();
            controller.dialogStage = dialog;
            dialog.initOwner(owner);
            dialog.initModality(Modality.APPLICATION_MODAL);
            dialog.setScene(new Scene(root));
            dialog.setTitle("Match Found");
            dialog.setResizable(false);
            dialog.getScene().getStylesheets().add(MatchFoundDialogController.class.getResource("/client/player/view/MatchFoundDialog.css").toExternalForm());

            // Disable the close (X) button
            dialog.setOnCloseRequest(event -> event.consume());

            // Fade in the dialog
            if (root != null) controller.fadeInNode(root);

            // Slide in player panels and bounce avatars
            controller.slideAndBouncePlayers();

            // Bounce "vs" label and rotate
            controller.bounceAndRotateVs();

            // Slightly rotate avatars
            controller.rotateAvatars();

            // Show confetti burst on open, but only after layout
            Platform.runLater(() -> {
                if (controller.root != null && controller.root.getWidth() > 0 && controller.root.getHeight() > 0) {
                    ConfettiHelper.showConfetti(controller.root);
                }
            });

            controller.startCountdown();
            dialog.show();
        } catch (Exception e) {
            e.printStackTrace();
            if (onCountdownFinished != null) onCountdownFinished.run();
        }
    }

    private void startCountdown() {
        countdown = 5;
        countdownLabel.setText(String.valueOf(countdown));
        playCountdownAnimation();
        countdownTimeline = new Timeline(new KeyFrame(Duration.seconds(1), e -> {
            countdown--;
            if (countdown > 0) {
                countdownLabel.setText(String.valueOf(countdown));
                playCountdownAnimation();
            } else {
                countdownLabel.setText("Go!");
                playGoPulse();
                // Show confetti only if root is valid
                if (root != null && root.getWidth() > 0 && root.getHeight() > 0) {
                    ConfettiHelper.showConfetti(root);
                }
                countdownTimeline.stop();
                if (dialogStage != null) dialogStage.close();
                if (onCountdownFinished != null) onCountdownFinished.run();
            }
        }));
        countdownTimeline.setCycleCount(5);
        countdownTimeline.play();
    }

    private void playCountdownAnimation() {
        if (countdownLabel != null) {
            try {
                new ZoomIn(countdownLabel).play();
            } catch (Exception e) {
                // fallback: no animation
            }
        }
    }

    private void playGoPulse() {
        if (countdownLabel != null) {
            try {
                new Pulse(countdownLabel).play();
            } catch (Exception e) {
                // fallback: no animation
            }
        }
    }

    private void fadeInNode(Node node) {
        if (node == null) return;
        FadeTransition ft = new FadeTransition(Duration.millis(700), node);
        ft.setFromValue(0);
        ft.setToValue(1);
        ft.play();
    }

    private void slideAndBouncePlayers() {
        if (playerRow != null && playerRow.getChildren().size() >= 3) {
            VBox leftPanel = (VBox) playerRow.getChildren().get(0);
            VBox rightPanel = (VBox) playerRow.getChildren().get(2);
            try {
                new SlideInLeft(leftPanel).play();
                new SlideInRight(rightPanel).play();
                ImageView leftAvatar = (ImageView) leftPanel.getChildren().get(0);
                ImageView rightAvatar = (ImageView) rightPanel.getChildren().get(0);
                new BounceIn(leftAvatar).play();
                new BounceIn(rightAvatar).play();
            } catch (Exception e) {
                // fallback: no animation
            }
        }
    }

    private void bounceAndRotateVs() {
        if (matchVs != null) {
            try {
                new BounceIn(matchVs).play();
                RotateTransition rotate = new RotateTransition(Duration.seconds(1.2), matchVs);
                rotate.setByAngle(20);
                rotate.setAutoReverse(true);
                rotate.setCycleCount(2);
                rotate.play();
            } catch (Exception e) {
                // fallback: no animation
            }
        }
    }

    private void rotateAvatars() {
        if (playerRow != null && playerRow.getChildren().size() >= 3) {
            VBox leftPanel = (VBox) playerRow.getChildren().get(0);
            VBox rightPanel = (VBox) playerRow.getChildren().get(2);
            try {
                ImageView leftAvatar = (ImageView) leftPanel.getChildren().get(0);
                ImageView rightAvatar = (ImageView) rightPanel.getChildren().get(0);
                RotateTransition rotateLeft = new RotateTransition(Duration.seconds(1.2), leftAvatar);
                rotateLeft.setByAngle(-15);
                rotateLeft.setAutoReverse(true);
                rotateLeft.setCycleCount(2);
                rotateLeft.play();
                RotateTransition rotateRight = new RotateTransition(Duration.seconds(1.2), rightAvatar);
                rotateRight.setByAngle(15);
                rotateRight.setAutoReverse(true);
                rotateRight.setCycleCount(2);
                rotateRight.play();
            } catch (Exception e) {
                // fallback: no animation
            }
        }
    }

    private void animateBackground() {
        if (backgroundImage != null) {
            try {
                ScaleTransition scale = new ScaleTransition(Duration.seconds(4), backgroundImage);
                scale.setFromX(1.0);
                scale.setFromY(1.0);
                scale.setToX(1.05);
                scale.setToY(1.05);
                scale.setAutoReverse(true);
                scale.setCycleCount(Animation.INDEFINITE);
                scale.play();

                FadeTransition fade = new FadeTransition(Duration.seconds(4), backgroundImage);
                fade.setFromValue(0.85);
                fade.setToValue(1.0);
                fade.setAutoReverse(true);
                fade.setCycleCount(Animation.INDEFINITE);
                fade.play();
            } catch (Exception e) {
                // fallback: no animation
            }
        }
    }
}

