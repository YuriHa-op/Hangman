package client.player.view;

import GameModule.GameService;
import client.player.controller.GameViewController;
import client.player.model.GameModel;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;

public class GameView {
    private Stage stage;
    private GameViewController controller;
    private Parent root;

    public void start(Stage stage, GameService gameService, String username, Runnable onBackToMenu) {
        this.stage = stage;
        try {
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/client/player/view/GameView.fxml"));
            root = loader.load();

            // Get controller from FXML
            controller = loader.getController();

            // Create model
            GameModel model = new GameModel(gameService, username);

            // Setup UI component controller with dependencies
            controller.setStage(stage);
            controller.setModel(model);

            // Properly handle returning to menu
            controller.setOnBackToMenu(() -> {
                this.close(); // Close the game view window
                if (onBackToMenu != null) {
                    onBackToMenu.run(); // Show the menu
                }
            });

            // Start new game or resume existing one
            String maskedWord = gameService.getMaskedWord(username);
            if (maskedWord != null && !maskedWord.isEmpty() && !maskedWord.equals("WAITING_FOR_MATCH")) {
                controller.resumeGame();
            } else {
                controller.startNewGame();
            }

            Scene scene = new Scene(root);
            stage.setScene(scene);
            stage.setTitle("What's The Word - Game");
<<<<<<< HEAD
            stage.setResizable(false);
=======
            stage.setResizable(true);
            stage.setMinWidth(850);
            stage.setMinHeight(900);
>>>>>>> main
            stage.setWidth(900);
            stage.setHeight(950);
        } catch (Exception e) {
            System.err.println("Error loading GameView: " + e.getMessage());
            e.printStackTrace();
        }
    }

    public void show() {
        stage.show();
        if (controller != null) {
            controller.onReturned();
        }
    }

    public void close() {
        stage.close();
    }
}
