package client.player.controller.results;

import client.player.model.PlayerScoreEntry;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.fxml.FXML;
import javafx.scene.control.Button;
import javafx.scene.control.TableColumn;
import javafx.scene.control.TableView;
import javafx.scene.control.cell.PropertyValueFactory;
import javafx.stage.Stage;

import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public class GameResultsViewController {

    @FXML
    private TableView<PlayerScoreEntry> resultsTable;
    @FXML
    private TableColumn<PlayerScoreEntry, Integer> rankColumn;
    @FXML
    private TableColumn<PlayerScoreEntry, String> playerColumn;
    @FXML
    private TableColumn<PlayerScoreEntry, Integer> scoreColumn;
    @FXML
    private Button okButton;

    private Stage stage;
    private Runnable onOkAction;

    @FXML
    public void initialize() {
        rankColumn.setCellValueFactory(new PropertyValueFactory<>("rank"));
        playerColumn.setCellValueFactory(new PropertyValueFactory<>("playerName"));
        scoreColumn.setCellValueFactory(new PropertyValueFactory<>("score"));
    }

    public void setStage(Stage stage) {
        this.stage = stage;
    }

    public void setOnOkAction(Runnable onOkAction) {
        this.onOkAction = onOkAction;
    }

    public void populateResults(List<String> playerNames, Map<String, Integer> scores) {
        List<PlayerScoreEntry> entries = playerNames.stream()
                .map(name -> new PlayerScoreEntry(0, name, scores.getOrDefault(name, 0)))
                .sorted(Comparator.comparingInt(PlayerScoreEntry::getScore).reversed())
                .collect(Collectors.toList());

        ObservableList<PlayerScoreEntry> observableEntries = FXCollections.observableArrayList();
        for (int i = 0; i < entries.size(); i++) {
            PlayerScoreEntry originalEntry = entries.get(i);
            // Create new entry with rank
            observableEntries.add(new PlayerScoreEntry(i + 1, originalEntry.getPlayerName(), originalEntry.getScore()));
        }

        resultsTable.setItems(observableEntries);
    }

    @FXML
    private void handleOkButton() {
        if (stage != null) {
            stage.close();
        }
        if (onOkAction != null) {
            onOkAction.run();
        }
    }
} 