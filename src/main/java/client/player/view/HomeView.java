package client.player.view;

import GameModule.GameService;
import client.player.controller.HomeViewController;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;
import javafx.stage.StageStyle;

public class HomeView {
    private Stage stage;
    private HomeViewController controller;

    public void start(Stage primaryStage, GameService gameService, String username, Runnable onLogout) {
        this.stage = primaryStage;
        try {
            // Remove default window decorations (no title bar/buttons)
            stage.initStyle(StageStyle.UNDECORATED);

            // Load FXML
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/client/player/view/HomeView.fxml"));
            Parent root = loader.load();

            // Get and configure controller
            controller = loader.getController();
            controller.setStage(stage);
            controller.setGameService(gameService);
            controller.setUsername(username);
            controller.setOnLogout(onLogout);

            // Make window draggable
            final double[] xOffset = {0};
            final double[] yOffset = {0};

            root.setOnMousePressed(event -> {
                xOffset[0] = event.getSceneX();
                yOffset[0] = event.getSceneY();
            });

            root.setOnMouseDragged(event -> {
                stage.setX(event.getScreenX() - xOffset[0]);
                stage.setY(event.getScreenY() - yOffset[0]);
            });

            // Set up scene
            Scene scene = new Scene(root);
            stage.setScene(scene);
            stage.setTitle("Home - What's The Word");
            stage.setResizable(false);
            stage.setWidth(750);
            stage.setHeight(650);
        } catch (Exception e) {
            System.err.println("Error loading HomeView: " + e.getMessage());
            e.printStackTrace();
        }
    }

    public void show() {
        stage.show();
    }

    public void close() {
        stage.close();
    }
}
