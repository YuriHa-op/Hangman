package client.admin.view;

import GameModule.GameService;
import client.admin.controller.AdminMatchHistoryController;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Modality;
import javafx.stage.Stage;
import javafx.stage.StageStyle;
import java.util.function.Consumer;

public class AdminMatchHistoryView {
    private Stage stage;
    private AdminMatchHistoryController controller;
    private Parent root;

    public void showPlayerHistory(GameService gameService, String username, Consumer<String> outputCallback, Stage ownerStage) {
        try {
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/client/admin/view/AdminMatchHistoryView.fxml"));
            root = loader.load();
            controller = loader.getController();

            stage = new Stage();
            stage.initStyle(StageStyle.DECORATED); // Or UNDECORATED if you want to keep the player's style
            stage.initOwner(ownerStage); // Set owner to the leaderboard stage
            stage.initModality(Modality.WINDOW_MODAL); // Block interaction with owner while this is open

            controller.setStage(stage);
            controller.setGameService(gameService);
            controller.setTargetUsername(username);
            controller.setOutputCallback(outputCallback);
            controller.loadSelectedHistory();

            // Optional: Make window draggable if UNDECORATED
            // If DECORATED, the OS handles this.
            // final double[] xOffset = {0};
            // final double[] yOffset = {0};
            // root.setOnMousePressed(event -> {
            //     xOffset[0] = event.getSceneX();
            //     yOffset[0] = event.getSceneY();
            // });
            // root.setOnMouseDragged(event -> {
            //     stage.setX(event.getScreenX() - xOffset[0]);
            //     stage.setY(event.getScreenY() - yOffset[0]);
            // });

            Scene scene = new Scene(root);
            // Reference the new AdminMatchHistory.css file
            scene.getStylesheets().add(getClass().getResource("AdminMatchHistory.css").toExternalForm());
            
            stage.setScene(scene);
            stage.setTitle("Match History for " + username);
            stage.setResizable(true);
            stage.setMinWidth(800);
            stage.setMinHeight(600);
            stage.setWidth(900);
            stage.setHeight(650);
            
            // stage.setOnCloseRequest(event -> controller.handleClose()); // Already handled by button
            
            stage.showAndWait(); // Use showAndWait to block owner until this is closed

        } catch (Exception e) {
            if (outputCallback != null) {
                outputCallback.accept("Error loading Admin Match History View: " + e.getMessage());
            }
            e.printStackTrace();
        }
    }
} 