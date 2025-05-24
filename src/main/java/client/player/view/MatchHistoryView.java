package client.player.view;

import GameModule.GameService;
import client.player.controller.MatchHistoryController;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;

public class MatchHistoryView {
    private Stage stage;
    private MatchHistoryController controller;
    private Parent root;

    public void start(Stage stage, GameService gameService, String username, Runnable onBackToMenu) {
        this.stage = stage;
        try {
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/client/player/view/MatchHistoryView.fxml"));
            root = loader.load();
            controller = loader.getController();
            controller.setStage(stage);
            controller.setGameService(gameService);
            controller.setUsername(username);
            controller.setOnBackToMenu(onBackToMenu);
            controller.loadHistory();
            Scene scene = new Scene(root);
            stage.setScene(scene);
            stage.setTitle("Match History");
            stage.setResizable(true);
            stage.setMinWidth(800);
            stage.setMinHeight(600);
            stage.setWidth(900);
            stage.setHeight(650);
            stage.setOnCloseRequest(event -> {
                controller.handleBackToMenu();
            });
        } catch (Exception e) {
            System.err.println("Error loading MatchHistoryView: " + e.getMessage());
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