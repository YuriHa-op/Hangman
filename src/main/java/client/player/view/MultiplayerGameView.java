package client.player.view;

import GameModule.GameService;
import client.player.controller.MultiplayerGameViewController;
import client.player.model.MultiplayerGameModel;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;
import javafx.stage.StageStyle;

public class MultiplayerGameView {
    private Stage stage;
    private MultiplayerGameViewController controller;
    private Parent root;

    public void start(Stage stage, GameService gameService, String username, Runnable onBackToMenu) {
        this.stage = stage;
        try {
            stage.initStyle(StageStyle.UNDECORATED);
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/client/player/view/MultiplayerGameView.fxml"));
            root = loader.load();
            controller = loader.getController();
            MultiplayerGameModel model = new MultiplayerGameModel(gameService, username);
            controller.setStage(stage);
            controller.setModel(model);
            controller.setOnBackToMenu(() -> {
                this.close();
                if (onBackToMenu != null) {
                    onBackToMenu.run();
                }
            });
            controller.startNewGame();

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

            Scene scene = new Scene(root);
            stage.setScene(scene);
            stage.setTitle("What's The Word - Multiplayer Game");
            stage.setResizable(false);
            stage.setMinWidth(900);
            stage.setMinHeight(950);
            stage.setWidth(950);
            stage.setHeight(1000);
            stage.setOnCloseRequest(event -> {
                controller.handleBackToMenu();
                controller.handleBackToMenu();
                if (gameService != null && username != null) {
                    gameService.endGameSession(username);
                }
            });
        } catch (Exception e) {
            System.err.println("Error loading MultiplayerGameView: " + e.getMessage());
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
