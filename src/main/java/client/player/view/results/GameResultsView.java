package client.player.view.results;

import client.player.dto.MultiplayerGameDetailsDTO;
import client.player.model.MultiplayerGameModel;
import client.player.model.PlayerScoreEntry;
import com.google.gson.Gson;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.TableColumn;
import javafx.scene.control.TableView;
import javafx.scene.control.cell.PropertyValueFactory;
import javafx.stage.Modality;
import javafx.stage.Stage;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public class GameResultsView {

    @FXML private TableView<PlayerScoreEntry> scoresTable;
    @FXML private TableColumn<PlayerScoreEntry, Integer> rankColumn;
    @FXML private TableColumn<PlayerScoreEntry, String> playerColumn;
    @FXML private TableColumn<PlayerScoreEntry, Integer> scoreColumn;
    @FXML private Button detailsButton;
    @FXML private Button okButton;

    private Stage stage;
    private Runnable onOkAction;
    private MultiplayerGameModel model;
    private String gameId;

    public void showResults(Stage owner, List<String> playerNames, Map<String, Integer> finalScores, MultiplayerGameModel model, String gameId, Runnable onOkAction) {
        this.onOkAction = onOkAction;
        this.model = model;
        this.gameId = gameId;

        try {
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/client/player/view/results/GameResultsView.fxml"));
            loader.setController(this);
            Parent root = loader.load();

            stage = new Stage();
            stage.initModality(Modality.WINDOW_MODAL);
            stage.initOwner(owner);
            stage.setTitle("Game Results");
            stage.setScene(new Scene(root));
            
            populateScores(playerNames, finalScores);

            stage.showAndWait();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void populateScores(List<String> allPlayers, Map<String, Integer> finalScores) {
        rankColumn.setCellValueFactory(new PropertyValueFactory<>("rank"));
        playerColumn.setCellValueFactory(new PropertyValueFactory<>("playerName"));
        scoreColumn.setCellValueFactory(new PropertyValueFactory<>("score"));

        List<PlayerScoreEntry> scoreEntries = allPlayers.stream()
            .map(playerName -> new PlayerScoreEntry(0, playerName, finalScores.getOrDefault(playerName, 0)))
            .sorted(Comparator.comparingInt(PlayerScoreEntry::getScore).reversed())
            .collect(Collectors.toList());

        ObservableList<PlayerScoreEntry> finalEntries = FXCollections.observableArrayList();
        for (int i = 0; i < scoreEntries.size(); i++) {
            PlayerScoreEntry current = scoreEntries.get(i);
            finalEntries.add(new PlayerScoreEntry(i + 1, current.getPlayerName(), current.getScore()));
        }

        scoresTable.setItems(finalEntries);
    }

    @FXML
    private void handleDetailsButton() {
        if (model != null && gameId != null) {
            String detailsJson = model.getMatchDetails(gameId);
            if (detailsJson != null) {
                Gson gson = new Gson();
                MultiplayerGameDetailsDTO details = gson.fromJson(detailsJson, MultiplayerGameDetailsDTO.class);
                showDetailsDialog(details);
            } else {
                // Handle error - maybe show an alert
                System.err.println("Could not retrieve match details for gameId: " + gameId);
            }
        }
    }

    private void showDetailsDialog(MultiplayerGameDetailsDTO details) {
        try {
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/client/player/view/results/GameDetailsView.fxml"));
            Parent root = loader.load();

            GameDetailsViewController controller = loader.getController();
            controller.setDetails(details);

            Stage detailsStage = new Stage();
            detailsStage.initModality(Modality.WINDOW_MODAL);
            detailsStage.initOwner(this.stage);
            detailsStage.setTitle("Match Details");
            detailsStage.setScene(new Scene(root));
            detailsStage.showAndWait();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    @FXML
    private void handleOkButton() {
        stage.close();
        if (onOkAction != null) {
            onOkAction.run();
        }
    }
} 