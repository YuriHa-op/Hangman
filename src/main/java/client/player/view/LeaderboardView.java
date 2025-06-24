package client.player.view;

import GameModule.GameService;
import client.player.controller.LeaderboardController;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;

public class LeaderboardView {
    private Stage stage;
    private LeaderboardController controller;

    public void start(Stage stage, GameService gameService, Runnable onBackToMenu) {
        this.stage = stage;
        try {
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/client/player/view/LeaderboardsView.fxml"));
            Parent root = loader.load();
            controller = loader.getController();

            controller.setStage(stage);
            controller.setOnBackToMenu(onBackToMenu);
            controller.setGameService(gameService);

            Scene scene = new Scene(root);
            stage.setScene(scene);
            stage.setTitle("Leaderboard - What's The Word");
            stage.setResizable(false);
            stage.setWidth(650);
            stage.setHeight(550);
        } catch (Exception e) {
            System.err.println("Error loading LeaderboardView: " + e.getMessage());
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