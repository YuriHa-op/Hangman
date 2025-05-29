package client.player.controller;

import GameModule.GameService;
import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;
import javafx.application.Platform;
import javafx.beans.property.SimpleLongProperty;
import javafx.beans.property.SimpleStringProperty;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.fxml.FXML;
import javafx.scene.control.*;
import javafx.stage.Stage;
import javafx.util.Callback;
import server.dto.MultiplayerGameSummaryDTO;
import server.dto.SPSinglePlayerGameSummaryDTO;

import java.lang.reflect.Type;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.stream.Collectors;

public class MatchHistoryController {
    @FXML private TableView<MatchSummary> historyTable;
    // @FXML private TableColumn<MatchSummary, String> colGameId; // Removed for player view
    @FXML private TableColumn<MatchSummary, String> colDateTime;
    @FXML private TableColumn<MatchSummary, String> colPlayers;
    @FXML private TableColumn<MatchSummary, String> colWinner;
    @FXML private TableColumn<MatchSummary, String> colRounds;
    @FXML private TableColumn<MatchSummary, Void> colDetails;
    @FXML private Button closeButton;
    @FXML private ComboBox<String> historyTypeComboBox;

    private Stage stage;
    private GameService gameService;
    private String username;
    private Runnable onBackToMenu;
    private final Gson gson = new Gson();
    private ObservableList<MatchSummary> matchData = FXCollections.observableArrayList();
    private static final SimpleDateFormat DATE_FORMAT = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");

    public void setStage(Stage stage) { this.stage = stage; }
    public void setGameService(GameService gameService) { this.gameService = gameService; }
    public void setUsername(String username) { this.username = username; }
    public void setOnBackToMenu(Runnable onBackToMenu) { this.onBackToMenu = onBackToMenu; }

    @FXML
    public void initialize() {
        // colGameId.setCellValueFactory(cellData -> cellData.getValue().gameIdProperty()); // Removed for player view
        colDateTime.setCellValueFactory(cellData -> cellData.getValue().dateTimeProperty());
        colPlayers.setCellValueFactory(cellData -> cellData.getValue().playersProperty());
        colWinner.setCellValueFactory(cellData -> cellData.getValue().winnerProperty());
        colRounds.setCellValueFactory(cellData -> cellData.getValue().roundsProperty());
        addDetailsButtonToTable();
        historyTable.setItems(matchData);

        historyTypeComboBox.setItems(FXCollections.observableArrayList("Multiplayer Matches", "1v1 Matches"));
        historyTypeComboBox.setValue("Multiplayer Matches"); // Default selection
        historyTypeComboBox.setOnAction(event -> loadSelectedHistory());

        if (closeButton != null) {
            closeButton.setOnAction(e -> handleBackToMenu());
        }
        // Load initial history (defaulting to Multiplayer)
        loadSelectedHistory();
    }

    private void loadSelectedHistory() {
        String selectedType = historyTypeComboBox.getValue();
        if ("1v1 Matches".equals(selectedType)) {
            loadHistory("singleplayer");
        } else {
            loadHistory("multiplayer");
        }
    }

    public void loadHistory(String mode) {
        new Thread(() -> {
            try {
                String json;
                Type listType;
                if ("singleplayer".equals(mode)) {
                    json = gameService.getSinglePlayerMatchHistory(username);
                    listType = new TypeToken<List<SPSinglePlayerGameSummaryDTO>>(){}.getType();
                    List<SPSinglePlayerGameSummaryDTO> spSummaries = gson.fromJson(json, listType);
                    List<MatchSummary> rows = spSummaries.stream().map(MatchSummary::fromSPSinglePlayerGameSummary).collect(Collectors.toList());
                    Platform.runLater(() -> matchData.setAll(rows));
                } else { // multiplayer
                    json = gameService.getMatchHistory(username);
                    listType = new TypeToken<List<MultiplayerGameSummaryDTO>>(){}.getType();
                    List<MultiplayerGameSummaryDTO> summaries = gson.fromJson(json, listType);
                    List<MatchSummary> rows = summaries.stream().map(MatchSummary::fromMultiplayerGameSummary).collect(Collectors.toList());
                    Platform.runLater(() -> matchData.setAll(rows));
                }
            } catch (Exception e) {
                Platform.runLater(() -> {
                    matchData.clear();
                    // Consider showing an error alert
                    Alert alert = new Alert(Alert.AlertType.ERROR, "Failed to load " + mode + " match history: " + e.getMessage());
                    alert.initOwner(stage);
                    alert.showAndWait();
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
        String selectedType = historyTypeComboBox.getValue();
        String mode = "1v1 Matches".equals(selectedType) ? "singleplayer" : "multiplayer";

        new Thread(() -> {
            try {
                String json;
                if ("singleplayer".equals(mode)) {
                    json = gameService.getSinglePlayerMatchDetails(gameId);
                } else { // multiplayer
                    json = gameService.getMatchDetails(gameId);
                }
                Platform.runLater(() -> {
                    // Assuming MatchDetailsDialogController can handle both types or we adapt it
                    MatchDetailsDialogController.showDialog(stage, json, mode); // Pass mode to dialog
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
        private final SimpleStringProperty gameId;
        private final SimpleStringProperty players;
        private final SimpleStringProperty winner;
        private final SimpleStringProperty rounds;
        private final SimpleLongProperty gameEndTimeEpoch;
        private final SimpleStringProperty dateTime;

        public MatchSummary(String gameId, String players, String winner, String rounds, long gameEndTimeEpoch) {
            this.gameId = new SimpleStringProperty(gameId);
            this.players = new SimpleStringProperty(players);
            this.winner = new SimpleStringProperty(winner);
            this.rounds = new SimpleStringProperty(rounds);
            this.gameEndTimeEpoch = new SimpleLongProperty(gameEndTimeEpoch);
            this.dateTime = new SimpleStringProperty(gameEndTimeEpoch > 0 ? DATE_FORMAT.format(new Date(gameEndTimeEpoch)) : "N/A");
        }
        public String getGameId() { return gameId.get(); }
        public SimpleStringProperty gameIdProperty() { return gameId; }
        public String getPlayers() { return players.get(); }
        public SimpleStringProperty playersProperty() { return players; }
        public String getWinner() { return winner.get(); }
        public SimpleStringProperty winnerProperty() { return winner; }
        public String getRounds() { return rounds.get(); }
        public SimpleStringProperty roundsProperty() { return rounds; }
        public long getGameEndTimeEpoch() { return gameEndTimeEpoch.get(); }
        public SimpleLongProperty gameEndTimeEpochProperty() { return gameEndTimeEpoch; }
        public String getDateTime() { return dateTime.get(); }
        public SimpleStringProperty dateTimeProperty() { return dateTime; }

        public static MatchSummary fromMultiplayerGameSummary(MultiplayerGameSummaryDTO g) {
            String players = String.join(", ", g.players);
            String winner = g.overallWinner != null ? g.overallWinner : "";
            String rounds = String.valueOf(g.totalRounds);
            return new MatchSummary(g.gameId, players, winner, rounds, g.gameEndTime);
        }

        public static MatchSummary fromSPSinglePlayerGameSummary(SPSinglePlayerGameSummaryDTO g) {
            String players = String.join(", ", g.players);
            String winner = g.overallWinner != null ? g.overallWinner : "";
            String rounds = String.valueOf(g.totalRounds);
            // Ensure gameId is non-null, default to empty string if necessary
            return new MatchSummary(g.gameId != null ? g.gameId : "", players, winner, rounds, g.gameEndTime);
        }
    }
} 