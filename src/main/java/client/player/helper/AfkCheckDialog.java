package client.player.helper;

import javafx.animation.KeyFrame;
import javafx.animation.Timeline;
import javafx.application.Platform;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.layout.VBox;
import javafx.stage.Modality;
import javafx.stage.Stage;
import javafx.stage.StageStyle;
import javafx.util.Duration;

import java.util.concurrent.atomic.AtomicInteger;

public class AfkCheckDialog {

    private static Stage dialogStage;
    private static Timeline countdownTimeline;

    public static void show(Stage ownerStage, Runnable onYesClicked, Runnable onTimedOut) {
        if (dialogStage != null && dialogStage.isShowing()) {
            Platform.runLater(() -> {
                if (dialogStage != null && dialogStage.isShowing()) {
                    dialogStage.toFront();
                }
            });
            return;
        }

        Platform.runLater(() -> {
            dialogStage = new Stage();
            dialogStage.initOwner(ownerStage);
            dialogStage.initModality(Modality.APPLICATION_MODAL);
            dialogStage.initStyle(StageStyle.UNDECORATED);
            dialogStage.setResizable(false);

            VBox dialogVBox = new VBox(20);
            dialogVBox.setAlignment(Pos.CENTER);
            dialogVBox.setStyle("-fx-padding: 30; -fx-background-color: #2c3e50; -fx-border-color: #f1c40f; -fx-border-width: 3; -fx-background-radius: 10; -fx-border-radius: 10;");

            Scene dialogScene = new Scene(dialogVBox);
            dialogStage.setScene(dialogScene);
            dialogStage.setAlwaysOnTop(true);

            Label titleLabel = new Label("Are you still in the game?");
            titleLabel.setStyle("-fx-font-family: 'Minecraftia'; -fx-font-size: 24px; -fx-text-fill: #f1c40f;");

            AtomicInteger countdownSeconds = new AtomicInteger(10);
            Label countdownLabel = new Label("Closing in: " + countdownSeconds.get() + "s");
            countdownLabel.setStyle("-fx-font-family: 'Minecraftia'; -fx-font-size: 18px; -fx-text-fill: white;");

            Button yesButton = new Button("Yes, I'm here!");
            String baseStyle = "-fx-font-family: 'Minecraftia'; -fx-font-size: 18px; -fx-background-color: #27ae60; -fx-text-fill: white; -fx-padding: 10 20; -fx-background-radius: 5; -fx-cursor: hand;";
            String hoverStyle = "-fx-font-family: 'Minecraftia'; -fx-font-size: 18px; -fx-background-color: #2ecc71; -fx-text-fill: white; -fx-padding: 10 20; -fx-background-radius: 5; -fx-cursor: hand;";
            yesButton.setStyle(baseStyle);
            yesButton.setOnMouseEntered(e -> yesButton.setStyle(hoverStyle));
            yesButton.setOnMouseExited(e -> yesButton.setStyle(baseStyle));
            
            yesButton.setOnAction(event -> {
                if (countdownTimeline != null) {
                    countdownTimeline.stop();
                }
                if (onYesClicked != null) {
                    onYesClicked.run();
                }
                closeDialogInternal();
            });

            dialogVBox.getChildren().addAll(titleLabel, countdownLabel, yesButton);

            countdownTimeline = new Timeline(new KeyFrame(Duration.seconds(1), e -> {
                int remaining = countdownSeconds.decrementAndGet();
                countdownLabel.setText("Closing in: " + remaining + "s");
                if (remaining <= 0) {
                    countdownTimeline.stop();
                    if (onTimedOut != null) {
                        onTimedOut.run();
                    }
                    closeDialogInternal();
                }
            }));
            countdownTimeline.setCycleCount(countdownSeconds.get());
            countdownTimeline.play();

            dialogStage.setOnHidden(eventHidden -> {
                if (countdownTimeline != null) {
                    countdownTimeline.stop();
                }
                AfkCheckDialog.dialogStage = null;
                AfkCheckDialog.countdownTimeline = null;
            });
            
            dialogStage.showAndWait();
        });
    }

    private static void closeDialogInternal() {
        if (dialogStage != null) {
            Stage currentStage = dialogStage;
            Platform.runLater(() -> {
                if (currentStage != null && currentStage.isShowing()) {
                     currentStage.close();
                }
            });
        }
    }
    
    public static void closeDialog() {
        closeDialogInternal();
    }

    public static boolean isShowing() {
        return dialogStage != null && dialogStage.isShowing();
    }

    // New method for the "Last Chance" dialog
    private static Stage lastChanceDialogStage; // Separate stage for the new dialog

    public static void showLastChanceDialog(Stage ownerStage, Runnable onLastChanceClicked) {
        if (lastChanceDialogStage != null && lastChanceDialogStage.isShowing()) {
            Platform.runLater(() -> {
                if (lastChanceDialogStage != null && lastChanceDialogStage.isShowing()) {
                    lastChanceDialogStage.toFront();
                }
            });
            return; // Already showing
        }

        Platform.runLater(() -> {
            lastChanceDialogStage = new Stage();
            lastChanceDialogStage.initOwner(ownerStage);
            lastChanceDialogStage.initModality(Modality.APPLICATION_MODAL);
            lastChanceDialogStage.initStyle(StageStyle.UNDECORATED);
            lastChanceDialogStage.setResizable(false);

            VBox dialogVBox = new VBox(15); // A bit less spacing
            dialogVBox.setAlignment(Pos.CENTER);
            // Simplified style, can be adjusted
            dialogVBox.setStyle("-fx-padding: 25; -fx-background-color: #34495e; -fx-border-color: #7f8c8d; -fx-border-width: 2; -fx-background-radius: 8; -fx-border-radius: 8;");

            Label messageLabel = new Label("Server may be cleaning up the game due to inactivity.");
            messageLabel.setStyle("-fx-font-family: 'Minecraftia'; -fx-font-size: 16px; -fx-text-fill: white; -fx-text-alignment: center; -fx-wrap-text: true;");

            Button lastChanceButton = new Button("Try Next Round (Last Chance)");
            String baseStyle = "-fx-font-family: 'Minecraftia'; -fx-font-size: 14px; -fx-background-color: #e67e22; -fx-text-fill: white; -fx-padding: 8 15; -fx-background-radius: 5; -fx-cursor: hand;";
            String hoverStyle = "-fx-font-family: 'Minecraftia'; -fx-font-size: 14px; -fx-background-color: #d35400; -fx-text-fill: white; -fx-padding: 8 15; -fx-background-radius: 5; -fx-cursor: hand;";
            lastChanceButton.setStyle(baseStyle);
            lastChanceButton.setOnMouseEntered(e -> lastChanceButton.setStyle(hoverStyle));
            lastChanceButton.setOnMouseExited(e -> lastChanceButton.setStyle(baseStyle));

            lastChanceButton.setOnAction(event -> {
                // Close this specific dialog *first*
                if (lastChanceDialogStage != null && lastChanceDialogStage.isShowing()) {
                    lastChanceDialogStage.close();
                }
                // Then run the callback
                if (onLastChanceClicked != null) {
                    onLastChanceClicked.run();
                }
            });

            dialogVBox.getChildren().addAll(messageLabel, lastChanceButton);

            Scene dialogScene = new Scene(dialogVBox);
            lastChanceDialogStage.setScene(dialogScene);
            lastChanceDialogStage.setAlwaysOnTop(true);

            lastChanceDialogStage.setOnHidden(eventHidden -> {
                lastChanceDialogStage = null; // Allow garbage collection
            });

            lastChanceDialogStage.show(); // Not showAndWait, to allow other UI updates if necessary
        });
    }

    // Method to allow external closing of the last chance dialog
    public static void closeLastChanceDialog() {
        Platform.runLater(() -> {
            if (lastChanceDialogStage != null && lastChanceDialogStage.isShowing()) {
                lastChanceDialogStage.close();
            }
        });
    }
} 