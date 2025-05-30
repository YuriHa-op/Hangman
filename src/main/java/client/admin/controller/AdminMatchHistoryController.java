package client.admin.controller;

import GameModule.GameService;
// Removed direct import of GameSummary and MatchSummary from player controller, as they are defined below if different
// or assumed to be compatible if Admin uses the same DAO's GameSummary
import client.player.controller.MatchDetailsDialogController; 
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
import java.lang.reflect.Type;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.function.Consumer; 
import java.util.stream.Collectors;
// Import DTOs used by both history types if they are not already available through other means
import server.dto.MultiplayerGameSummaryDTO;
import server.dto.SPSinglePlayerGameSummaryDTO;

public class AdminMatchHistoryController {
    @FXML private TableView<MatchSummary> historyTable;
    @FXML private TableColumn<MatchSummary, String> colGameId;
    @FXML private TableColumn<MatchSummary, String> colDateTime; // New Column
    @FXML private TableColumn<MatchSummary, String> colPlayers;
    @FXML private TableColumn<MatchSummary, String> colWinner;
    @FXML private TableColumn<MatchSummary, String> colRounds;
    @FXML private TableColumn<MatchSummary, Void> colDetails;
    @FXML private Button closeButton;
    @FXML private ComboBox<String> historyTypeComboBox; // Added ComboBox

    private Stage stage;
    private GameService gameService;
    private String targetUsername; 
    private Consumer<String> outputCallback; 
    private final Gson gson = new Gson();
    private ObservableList<MatchSummary> matchData = FXCollections.observableArrayList();
    private static final SimpleDateFormat DATE_FORMAT = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");

    public void setStage(Stage stage) { this.stage = stage; }
    public void setGameService(GameService gameService) { this.gameService = gameService; }
    public void setTargetUsername(String username) { this.targetUsername = username; }
    public void setOutputCallback(Consumer<String> outputCallback) { this.outputCallback = outputCallback; }

    @FXML
    public void initialize() {
        colGameId.setCellValueFactory(cellData -> cellData.getValue().gameIdProperty());
        colDateTime.setCellValueFactory(cellData -> cellData.getValue().dateTimeProperty()); // New Column Value Factory
        colPlayers.setCellValueFactory(cellData -> cellData.getValue().playersProperty());
        colWinner.setCellValueFactory(cellData -> cellData.getValue().winnerProperty());
        colRounds.setCellValueFactory(cellData -> cellData.getValue().roundsProperty());
        addDetailsButtonToTable();
        historyTable.setItems(matchData);

        historyTypeComboBox.setItems(FXCollections.observableArrayList("Multiplayer Matches", "1v1 Matches"));
        historyTypeComboBox.setValue("Multiplayer Matches"); // Default selection
        historyTypeComboBox.setOnAction(event -> loadSelectedHistory());

        if (closeButton != null) {
            closeButton.setOnAction(e -> handleClose());
        }
        // Load initial history (defaulting to Multiplayer)
        loadSelectedHistory(); // Changed from loadHistory() to loadSelectedHistory()
    }

    public void loadSelectedHistory() {
        String selectedType = historyTypeComboBox.getValue();
        if ("1v1 Matches".equals(selectedType)) {
            loadHistory("singleplayer");
        } else {
            loadHistory("multiplayer");
        }
    }

    // Modified loadHistory to accept a mode parameter
    public void loadHistory(String mode) { 
        if (gameService == null || targetUsername == null) {
            logError("GameService or Username not set. Cannot load history.");
            return;
        }
        new Thread(() -> {
            try {
                String json;
                List<MatchSummary> rows;
                if ("singleplayer".equals(mode)) {
                    json = gameService.getSinglePlayerMatchHistory(targetUsername);
                    Type listType = new TypeToken<List<SPSinglePlayerGameSummaryDTO>>(){}.getType();
                    List<SPSinglePlayerGameSummaryDTO> spSummaries = gson.fromJson(json, listType);
                    if (spSummaries == null) {
                        Platform.runLater(() -> {
                            logMessage("No 1v1 match history found for " + targetUsername + " or error in data.");
                            matchData.clear();
                        });
                        return;
                    }
                    rows = spSummaries.stream()
                                     .map(MatchSummary::fromSPSinglePlayerGameSummary)
                                     .collect(Collectors.toList());
                } else { // multiplayer
                    json = gameService.getMatchHistory(targetUsername); 
                    Type listType = new TypeToken<List<MultiplayerGameSummaryDTO>>(){}.getType(); 
                    List<MultiplayerGameSummaryDTO> summaries = gson.fromJson(json, listType);
                    if (summaries == null) {
                         Platform.runLater(() -> {
                            logMessage("No multiplayer match history found for " + targetUsername + " or error in data.");
                            matchData.clear();
                        });
                        return;
                    }
                    rows = summaries.stream()
                                     .map(MatchSummary::fromMultiplayerGameSummary) // Changed from fromGameSummary
                                     .collect(Collectors.toList());
                }

                Platform.runLater(() -> {
                    matchData.setAll(rows);
                    logMessage(mode + " match history loaded for " + targetUsername);
                });
            } catch (Exception e) {
                Platform.runLater(() -> {
                    logError("Failed to load " + mode + " match history for " + targetUsername + ": " + e.getMessage());
                    matchData.clear(); 
                });
                e.printStackTrace();
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
                            String gameId = data.getGameId();
                            String selectedType = historyTypeComboBox.getValue();
                            String mode = "1v1 Matches".equals(selectedType) ? "singleplayer" : "multiplayer";
                            String jsonDetails;
                            if ("singleplayer".equals(mode)) {
                                jsonDetails = gameService.getSinglePlayerMatchDetails(gameId);
                            } else {
                                jsonDetails = gameService.getMatchDetails(gameId);
                            }
                            MatchDetailsDialogController.showDialog(stage, jsonDetails, mode); 
                        });
                    }
                    @Override
                    public void updateItem(Void item, boolean empty) {
                        super.updateItem(item, empty);
                        setGraphic(empty ? null : btn);
                    }
                };
            }
        });
    }

    @FXML
    private void handleClose() {
        if (stage != null) {
            stage.close();
        }
    }

    private void logMessage(String message) {
        if (outputCallback != null) {
            outputCallback.accept("AdminMH: " + message);
        } else {
            System.out.println("AdminMH: " + message);
        }
    }

    private void logError(String error) {
        if (outputCallback != null) {
            outputCallback.accept("AdminMH ERROR: " + error);
        } else {
            System.err.println("AdminMH ERROR: " + error);
        }
    }

    // --- Data classes for TableView (can be shared if identical to player's or defined here) ---
    // Assuming GameSummary comes from the DAO and is compatible
    // If MatchSummary is identical to Player's, it can be imported. Otherwise, defined here.
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

        // Renamed fromGameSummary to fromMultiplayerGameSummary for clarity
        public static MatchSummary fromMultiplayerGameSummary(MultiplayerGameSummaryDTO g) {
            String players = String.join(", ", g.players);
            String winner = g.overallWinner != null ? g.overallWinner : "";
            String rounds = String.valueOf(g.totalRounds);
            return new MatchSummary(g.gameId, players, winner, rounds, g.gameEndTime);
        }

        // New static factory method for SP DTO
        public static MatchSummary fromSPSinglePlayerGameSummary(SPSinglePlayerGameSummaryDTO g) {
            String players = String.join(", ", g.players);
            String winner = g.overallWinner != null ? g.overallWinner : "";
            String rounds = String.valueOf(g.totalRounds);
            return new MatchSummary(g.gameId != null ? g.gameId : "", players, winner, rounds, g.gameEndTime);
        }
    }

    // Removed the inner GameSummary DTO as we now use MultiplayerGameSummaryDTO and SPSinglePlayerGameSummaryDTO directly from server.dto
} 