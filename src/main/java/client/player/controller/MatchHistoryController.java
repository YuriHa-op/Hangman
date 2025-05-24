package client.player.controller;

import GameModule.GameService;
import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;
import javafx.application.Platform;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.fxml.FXML;
import javafx.scene.control.*;
import javafx.stage.Stage;
import javafx.util.Callback;
import java.lang.reflect.Type;
import java.util.List;
import java.util.stream.Collectors;

public class MatchHistoryController {
    @FXML private TableView<MatchSummary> historyTable;
    @FXML private TableColumn<MatchSummary, String> colGameId;
    @FXML private TableColumn<MatchSummary, String> colPlayers;
    @FXML private TableColumn<MatchSummary, String> colWinner;
    @FXML private TableColumn<MatchSummary, String> colRounds;
    @FXML private TableColumn<MatchSummary, Void> colDetails;
    @FXML private Button closeButton;

    private Stage stage;
    private GameService gameService;
    private String username;
    private Runnable onBackToMenu;
    private final Gson gson = new Gson();
    private ObservableList<MatchSummary> matchData = FXCollections.observableArrayList();

    public void setStage(Stage stage) { this.stage = stage; }
    public void setGameService(GameService gameService) { this.gameService = gameService; }
    public void setUsername(String username) { this.username = username; }
    public void setOnBackToMenu(Runnable onBackToMenu) { this.onBackToMenu = onBackToMenu; }

    @FXML
    public void initialize() {
        colGameId.setCellValueFactory(cellData -> cellData.getValue().gameIdProperty());
        colPlayers.setCellValueFactory(cellData -> cellData.getValue().playersProperty());
        colWinner.setCellValueFactory(cellData -> cellData.getValue().winnerProperty());
        colRounds.setCellValueFactory(cellData -> cellData.getValue().roundsProperty());
        addDetailsButtonToTable();
        historyTable.setItems(matchData);
        if (closeButton != null) {
            closeButton.setOnAction(e -> handleBackToMenu());
        }
    }

    public void loadHistory() {
        new Thread(() -> {
            try {
                String json = gameService.getMatchHistory(username);
                Type listType = new TypeToken<List<GameSummary>>(){}.getType();
                List<GameSummary> summaries = gson.fromJson(json, listType);
                List<MatchSummary> rows = summaries.stream().map(MatchSummary::fromGameSummary).collect(Collectors.toList());
                Platform.runLater(() -> {
                    matchData.setAll(rows);
                });
            } catch (Exception e) {
                Platform.runLater(() -> {
                    matchData.clear();
                });
            }
        }).start();
    }

    private void addDetailsButtonToTable() {
        colDetails.setCellFactory(new Callback<TableColumn<MatchSummary, Void>, TableCell<MatchSummary, Void>>() {
            @Override
            public TableCell<MatchSummary, Void> call(final TableColumn<MatchSummary, Void> param) {
                return new TableCell<MatchSummary, Void>() {
                    private final Button btn = new Button("Details");
                    {
                        btn.getStyleClass().add("details-button");
                        btn.setOnAction((event) -> {
                            MatchSummary data = getTableView().getItems().get(getIndex());
                            showMatchDetailsDialog(data.getGameId());
                        });
                    }
                    @Override
                    public void updateItem(Void item, boolean empty) {
                        super.updateItem(item, empty);
                        if (empty) {
                            setGraphic(null);
                        } else {
                            setGraphic(btn);
                        }
                    }
                };
            }
        });
    }

    private void showMatchDetailsDialog(String gameId) {
        new Thread(() -> {
            try {
                String json = gameService.getMatchDetails(gameId);
                Platform.runLater(() -> {
                    MatchDetailsDialogController.showDialog(stage, json);
                });
            } catch (Exception e) {
                Platform.runLater(() -> {
                    Alert alert = new Alert(Alert.AlertType.ERROR, "Failed to load match details.");
                    alert.initOwner(stage);
                    alert.showAndWait();
                });
            }
        }).start();
    }

    public void handleBackToMenu() {
        if (stage != null) stage.close();
        if (onBackToMenu != null) onBackToMenu.run();
    }

    // --- Data classes for TableView ---
    public static class MatchSummary {
        private final javafx.beans.property.SimpleStringProperty gameId;
        private final javafx.beans.property.SimpleStringProperty players;
        private final javafx.beans.property.SimpleStringProperty winner;
        private final javafx.beans.property.SimpleStringProperty rounds;
        public MatchSummary(String gameId, String players, String winner, String rounds) {
            this.gameId = new javafx.beans.property.SimpleStringProperty(gameId);
            this.players = new javafx.beans.property.SimpleStringProperty(players);
            this.winner = new javafx.beans.property.SimpleStringProperty(winner);
            this.rounds = new javafx.beans.property.SimpleStringProperty(rounds);
        }
        public String getGameId() { return gameId.get(); }
        public javafx.beans.property.SimpleStringProperty gameIdProperty() { return gameId; }
        public String getPlayers() { return players.get(); }
        public javafx.beans.property.SimpleStringProperty playersProperty() { return players; }
        public String getWinner() { return winner.get(); }
        public javafx.beans.property.SimpleStringProperty winnerProperty() { return winner; }
        public String getRounds() { return rounds.get(); }
        public javafx.beans.property.SimpleStringProperty roundsProperty() { return rounds; }
        public static MatchSummary fromGameSummary(GameSummary g) {
            String players = String.join(", ", g.players);
            String winner = g.overallWinner != null ? g.overallWinner : "";
            String rounds = String.valueOf(g.totalRounds);
            return new MatchSummary(g.gameId, players, winner, rounds);
        }
    }
    // --- Data class for JSON parsing ---
    public static class GameSummary {
        public String gameId;
        public int totalRounds;
        public String overallWinner;
        public List<String> players;
    }
} 