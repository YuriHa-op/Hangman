package client.player.controller;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;
import javafx.application.Platform;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.layout.HBox;
import javafx.scene.layout.Region;
import javafx.scene.layout.VBox;
import javafx.scene.text.Text;
import javafx.stage.Modality;
import javafx.stage.Stage;
import javafx.stage.StageStyle;
import server.dto.MultiplayerGameDetailsDTO;
import server.dto.MultiplayerRoundInfoDTO;
import server.dto.SPSinglePlayerGameDetailsDTO;
import server.dto.SPSinglePlayerRoundInfoDTO;
import java.io.IOException;
import java.lang.reflect.Type;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.stream.Collectors;

public class MatchDetailsDialogController {
    @FXML private Label gameIdLabel;
    @FXML private Label dateTimeLabel;
    @FXML private Label overallWinnerLabel;
    @FXML private Label totalRoundsLabel;
    @FXML private ListView<String> playersListView;
    @FXML private VBox roundsContainer; // VBox to hold round details labels
    @FXML private HBox playersBox;
    @FXML private Label winnerLabel;
    @FXML private TableView<RoundRow> roundsTable;
    @FXML private TableColumn<RoundRow, String> colRoundNum;
    @FXML private TableColumn<RoundRow, String> colWord;
    @FXML private TableColumn<RoundRow, String> colRoundWinner;
    @FXML private Button closeButton;
    @FXML private Text titleText;

    private Stage dialogStage;
    private final Gson gson = new Gson();
    private static final SimpleDateFormat DATE_FORMAT = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
    private ObservableList<RoundRow> roundData = FXCollections.observableArrayList();

    @FXML
    public void initialize() {
        if (colRoundNum != null) colRoundNum.setCellValueFactory(cellData -> cellData.getValue().roundNumProperty());
        if (colWord != null) colWord.setCellValueFactory(cellData -> cellData.getValue().wordProperty());
        if (colRoundWinner != null) colRoundWinner.setCellValueFactory(cellData -> cellData.getValue().winnerProperty());
        if (roundsTable != null) roundsTable.setItems(roundData);

        // Ensure closeButton action is set if FXML doesn't have it (belt and suspenders)
        // However, the primary fix is in the FXML's onAction.
        // if (closeButton != null) closeButton.setOnAction(event -> closeDialog());
    }

    public void setDialogStage(Stage dialogStage) {
        this.dialogStage = dialogStage;
    }

    public void setMatchDetails(String jsonDetails, String mode) {
        if ("singleplayer".equals(mode)) {
            Type spDetailsType = new TypeToken<SPSinglePlayerGameDetailsDTO>(){}.getType();
            SPSinglePlayerGameDetailsDTO spDetails = gson.fromJson(jsonDetails, spDetailsType);
            if (spDetails != null) {
                if (gameIdLabel != null) gameIdLabel.setText("Game ID: " + (spDetails.gameId != null ? spDetails.gameId : "N/A"));
                if (dateTimeLabel != null) dateTimeLabel.setText("Date/Time: " + (spDetails.gameEndTime > 0 ? DATE_FORMAT.format(new Date(spDetails.gameEndTime)) : "N/A"));
                if (overallWinnerLabel != null) overallWinnerLabel.setText("Overall Winner: " + (spDetails.overallWinner != null ? spDetails.overallWinner : "N/A"));
                if (totalRoundsLabel != null) totalRoundsLabel.setText("Total Rounds: " + spDetails.totalRounds);
                if (playersListView != null) {
                    if (spDetails.players != null) {
                        playersListView.getItems().setAll(spDetails.players);
                    } else {
                        playersListView.getItems().clear();
                    }
                }
                roundData.clear();
                if (spDetails.rounds != null) {
                    for (SPSinglePlayerRoundInfoDTO round : spDetails.rounds) {
                        roundData.add(new RoundRow(round.roundNumber, round.word, round.winner));
                    }
                }
                if (roundsContainer != null) {
                    roundsContainer.getChildren().clear();
                }
            } else {
                // Handle case where spDetails is null (e.g., bad JSON or no data)
                if (titleText != null) titleText.setText("Details Unavailable");
                if (gameIdLabel != null) gameIdLabel.setText("Game ID: Error");
                if (dateTimeLabel != null) dateTimeLabel.setText("Date/Time: Error");
                if (overallWinnerLabel != null) overallWinnerLabel.setText("Overall Winner: Error");
                if (totalRoundsLabel != null) totalRoundsLabel.setText("Total Rounds: Error");
                if (playersListView != null) playersListView.getItems().clear();
                if (roundsContainer != null) roundsContainer.getChildren().clear();
            }
        } else { // Multiplayer mode
            Type detailsType = new TypeToken<MultiplayerGameDetailsDTO>(){}.getType();
            MultiplayerGameDetailsDTO details = gson.fromJson(jsonDetails, detailsType);
            if (details != null) {
                if (gameIdLabel != null) gameIdLabel.setText("Game ID: " + (details.gameId != null ? details.gameId : "N/A"));
                if (dateTimeLabel != null) dateTimeLabel.setText("Date/Time: " + (details.gameEndTime > 0 ? DATE_FORMAT.format(new Date(details.gameEndTime)) : "N/A"));
                if (overallWinnerLabel != null) overallWinnerLabel.setText("Overall Winner: " + (details.overallWinner != null ? details.overallWinner : "N/A"));
                if (totalRoundsLabel != null) totalRoundsLabel.setText("Total Rounds: " + details.totalRounds);
                if (playersListView != null) {
                    if (details.players != null) {
                        playersListView.getItems().setAll(details.players);
                    } else {
                        playersListView.getItems().clear();
                    }
                }
                roundData.clear();
                if (details.rounds != null) {
                    for (MultiplayerRoundInfoDTO round : details.rounds) {
                        roundData.add(new RoundRow(round.roundNumber, round.word, round.winner));
                    }
                }
                if (roundsContainer != null) {
                    roundsContainer.getChildren().clear();
                }
            } else {
                // Handle case where details is null
                if (titleText != null) titleText.setText("Details Unavailable");
                if (gameIdLabel != null) gameIdLabel.setText("Game ID: Error");
                if (dateTimeLabel != null) dateTimeLabel.setText("Date/Time: Error");
                if (overallWinnerLabel != null) overallWinnerLabel.setText("Overall Winner: Error");
                if (totalRoundsLabel != null) totalRoundsLabel.setText("Total Rounds: Error");
                if (playersListView != null) playersListView.getItems().clear();
                if (roundsContainer != null) roundsContainer.getChildren().clear();
            }
        }
    }

    @FXML
    private void closeDialog() {
        if (dialogStage != null) {
            dialogStage.close();
        }
    }

    public static void showDialog(Stage ownerStage, String jsonDetails, String mode) {
        try {
            FXMLLoader loader = new FXMLLoader(MatchDetailsDialogController.class.getResource("/client/player/view/MatchDetailsDialog.fxml"));
            Parent page = loader.load();

            Stage dialogStage = new Stage();
            dialogStage.setTitle("Match Details");
            dialogStage.initModality(Modality.WINDOW_MODAL);
            dialogStage.initOwner(ownerStage);
            dialogStage.initStyle(StageStyle.UTILITY);
            Scene scene = new Scene(page);
            dialogStage.setScene(scene);

            MatchDetailsDialogController controller = loader.getController();
            controller.setDialogStage(dialogStage);
            controller.setMatchDetails(jsonDetails, mode);

            dialogStage.showAndWait();

        } catch (IOException e) {
            e.printStackTrace();
            Alert alert = new Alert(Alert.AlertType.ERROR, "Could not load match details dialog.");
            alert.initOwner(ownerStage);
            alert.showAndWait();
        }
    }

    // --- Data classes for JSON parsing and TableView ---
    public static class RoundRow {
        private final javafx.beans.property.SimpleStringProperty roundNum;
        private final javafx.beans.property.SimpleStringProperty word;
        private final javafx.beans.property.SimpleStringProperty winner;
        public RoundRow(int roundNum, String word, String winner) {
            this.roundNum = new javafx.beans.property.SimpleStringProperty(String.valueOf(roundNum));
            this.word = new javafx.beans.property.SimpleStringProperty(word);
            this.winner = new javafx.beans.property.SimpleStringProperty(winner != null ? winner : "");
        }
        public javafx.beans.property.SimpleStringProperty roundNumProperty() { return roundNum; }
        public javafx.beans.property.SimpleStringProperty wordProperty() { return word; }
        public javafx.beans.property.SimpleStringProperty winnerProperty() { return winner; }
    }
} 