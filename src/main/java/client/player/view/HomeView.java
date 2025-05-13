package client.player.view;

import GameModule.GameService;
import client.player.controller.HomeViewController;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;

public class HomeView {
    private Stage stage;
    private HomeViewController controller;

    public void start(Stage primaryStage, GameService gameService, String username, Runnable onLogout) {
        this.stage = primaryStage;
        try {
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/client/player/view/HomeView.fxml"));
            Parent root = loader.load();
            controller = loader.getController();
            controller.setStage(stage);
            controller.setGameService(gameService);
            controller.setUsername(username);
            controller.setOnLogout(onLogout);

            Scene scene = new Scene(root);
            stage.setScene(scene);
            stage.setTitle("Home - What's The Word");
            stage.setResizable(false);
            stage.setWidth(650);
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