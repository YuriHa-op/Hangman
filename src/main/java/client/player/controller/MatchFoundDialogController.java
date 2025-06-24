package client.player.controller;

import javafx.animation.*;
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
import javafx.stage.StageStyle;
import javafx.util.Duration;
import javafx.scene.layout.HBox;
import javafx.scene.Node;
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
            } catch (Exception e) {
                System.err.println("Could not load background image for MatchFoundDialog: " + e.getMessage());
            }
        }
    }

    public static void showDialog(Stage owner, String player1, String player2, boolean isPlayer1, String player1Pfp, String player2Pfp, Runnable onCountdownFinished) {
        try {
            FXMLLoader loader = new FXMLLoader(MatchFoundDialogController.class.getResource("/client/player/view/MatchFoundDialog.fxml"));
            StackPane root = loader.load();
            MatchFoundDialogController controller = loader.getController();
            controller.onCountdownFinished = onCountdownFinished;
            controller.player1Name.setText(player1);
            controller.player2Name.setText(player2);
            controller.player1Pfp.setImage(new Image(MatchFoundDialogController.class.getResourceAsStream(player1Pfp)));
            controller.player2Pfp.setImage(new Image(MatchFoundDialogController.class.getResourceAsStream(player2Pfp)));

            Stage dialog = new Stage();
            controller.dialogStage = dialog;
            dialog.initOwner(owner);
            dialog.initModality(Modality.APPLICATION_MODAL);
            dialog.initStyle(StageStyle.UNDECORATED);
            dialog.setTitle("Match Found");

            Scene scene = new Scene(root);
            scene.setFill(javafx.scene.paint.Color.TRANSPARENT);
            dialog.setScene(scene);
            String cssPath = "/client/player/view/MatchFoundDialog.css";
            String css = MatchFoundDialogController.class.getResource(cssPath).toExternalForm();
            if (css != null) {
                dialog.getScene().getStylesheets().add(css);
            } else {
                System.err.println("Could not load CSS for MatchFoundDialog: " + cssPath);
            }

            dialog.setOnCloseRequest(event -> event.consume());

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
        countdownTimeline = new Timeline(new KeyFrame(Duration.seconds(1), e -> {
            countdown--;
            if (countdown > 0) {
                countdownLabel.setText(String.valueOf(countdown));
            } else {
                countdownLabel.setText("Go!");
                countdownTimeline.stop();
                if (dialogStage != null) dialogStage.close();
                if (onCountdownFinished != null) onCountdownFinished.run();
            }
        }));
        countdownTimeline.setCycleCount(5);
        countdownTimeline.play();
    }
}

