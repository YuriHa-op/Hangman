package client.player.controller;

import javafx.animation.KeyFrame;
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
import animatefx.animation.FadeInDown;
import animatefx.animation.Tada;
import animatefx.animation.Pulse;
import javafx.animation.FadeTransition;

public class MatchFoundDialogController {
    @FXML private Label player1Name;
    @FXML private Label player2Name;
    @FXML private ImageView player1Pfp;
    @FXML private ImageView player2Pfp;
    @FXML private Label countdownLabel;
    @FXML private VBox root;
    @FXML private Label matchTitle;
    @FXML private ImageView backgroundImage;
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
                backgroundImage.setFitWidth(500);
                backgroundImage.setFitHeight(350);
                backgroundImage.setOpacity(0.3);
                // Fade-in animation for background
                FadeTransition fade = new FadeTransition(Duration.seconds(1.2), backgroundImage);
                fade.setFromValue(0.0);
                fade.setToValue(0.3);
                fade.play();
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
            // Set static images (replace with your own images if desired)
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
            // Animate root and title (use root from loader and matchTitle from controller)
            if (root != null) new FadeInDown(root).play();
            if (controller.matchTitle != null) new Tada(controller.matchTitle).play();
            controller.startCountdown();
            dialog.show();
        } catch (Exception e) {
            e.printStackTrace();
            if (onCountdownFinished != null) onCountdownFinished.run();
        }
    }

    private void startCountdown() {
        countdownLabel.setText(String.valueOf(countdown));
        countdownTimeline = new Timeline(new KeyFrame(Duration.seconds(1), e -> {
            countdown--;
            if (countdown > 0) {
                countdownLabel.setText(String.valueOf(countdown));
                new Pulse(countdownLabel).play();
            } else {
                countdownLabel.setText("Go!");
                new Pulse(countdownLabel).play();
                countdownTimeline.stop();
                if (dialogStage != null) dialogStage.close();
                if (onCountdownFinished != null) onCountdownFinished.run();
            }
        }));
        countdownTimeline.setCycleCount(5);
        countdownTimeline.play();
    }
} 