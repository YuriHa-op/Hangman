package client.player.view.results;

import client.player.controller.results.GameResultsViewController;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Modality;
import javafx.stage.Stage;
import javafx.stage.StageStyle;

import java.util.List;
import java.util.Map;

public class GameResultsView {
    private Stage stage;
    private GameResultsViewController controller;

    public void showResults(Stage owner, List<String> playerNames, Map<String, Integer> scores, Runnable onOkAction) {
        try {
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/client/player/view/results/GameResultsView.fxml"));
            Parent root = loader.load();

            controller = loader.getController();

            stage = new Stage();
            stage.initOwner(owner);
            stage.initModality(Modality.APPLICATION_MODAL);
            stage.initStyle(StageStyle.UNDECORATED);
            stage.setTitle("Game Results");

            controller.setStage(stage);
            controller.populateResults(playerNames, scores);
            controller.setOnOkAction(() -> {
                stage.close();
                if (onOkAction != null) {
                    onOkAction.run();
                }
            });

            Scene scene = new Scene(root);

            stage.setScene(scene);
            stage.showAndWait();

        } catch (Exception e) {
            System.err.println("Error loading GameResultsView: " + e.getMessage());
            e.printStackTrace();
            // Fallback if results view fails
            if (onOkAction != null) {
                onOkAction.run();
            }
        }
    }
} 