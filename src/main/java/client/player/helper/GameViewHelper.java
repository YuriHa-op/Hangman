package client.player.helper;

import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.layout.*;
import javafx.scene.paint.Color;
import javafx.stage.Modality;
import javafx.stage.Stage;
import javafx.stage.StageStyle;

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

        Scene scene = new Scene(root, 500, 400);
        scene.setFill(Color.TRANSPARENT);
        celebrationStage.setScene(scene);

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

        dialog.showAndWait();
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

        dialog.setResultConverter(dialogButton -> {
            if (dialogButton == leaveButton) {
                if (onExit != null) onExit.run();
            }
            return null;
        });

        dialog.showAndWait();
    }

    public static void showRoundWinner(TextArea gameOutput, int roundNum, String winner, boolean playerWon) {
        String msg = "\n§l§a[Round " + (roundNum + 1) + "] Winner: " + winner + (playerWon ? " (You!)" : "") + "\n";
        gameOutput.appendText(msg);
    }

    public static void showNoRoundWinner(TextArea gameOutput) {
        String msg = "\n§l§e[Round] No winner this round.\n";
        gameOutput.appendText(msg);
    }
}
