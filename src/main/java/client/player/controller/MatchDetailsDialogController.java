package client.player.controller;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;
import javafx.application.Platform;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.layout.HBox;
import javafx.scene.layout.Region;
import javafx.scene.paint.Color;
import javafx.scene.text.Text;
import javafx.stage.Modality;
import javafx.stage.Stage;
import javafx.stage.StageStyle;
import java.lang.reflect.Type;
import java.util.List;

public class MatchDetailsDialogController {
    @FXML private Label gameIdLabel;
    @FXML private HBox playersBox;
    @FXML private Label winnerLabel;
    @FXML private TableView<RoundRow> roundsTable;
    @FXML private TableColumn<RoundRow, String> colRoundNum;
    @FXML private TableColumn<RoundRow, String> colWord;
    @FXML private TableColumn<RoundRow, String> colRoundWinner;
    @FXML private Button closeButton;
    @FXML private Text titleText;

    private final Gson gson = new Gson();
    private Stage dialogStage;

    public static void showDialog(Stage owner, String jsonDetails) {
        Platform.runLater(() -> {
            try {
                FXMLLoader loader = new FXMLLoader(MatchDetailsDialogController.class.getResource("/client/player/view/MatchDetailsDialog.fxml"));
                Region root = loader.load();
                MatchDetailsDialogController controller = loader.getController();
                controller.populateFromJson(jsonDetails);
                Stage dialog = new Stage(StageStyle.DECORATED);
                controller.dialogStage = dialog;
                dialog.initOwner(owner);
                dialog.initModality(Modality.APPLICATION_MODAL);
                dialog.setTitle("Match Details");
                dialog.setScene(new Scene(root));
                dialog.setResizable(false);
                dialog.showAndWait();
            } catch (Exception e) {
                e.printStackTrace();
            }
        });
    }

    public void populateFromJson(String json) {
        try {
            Type type = new TypeToken<GameDetails>(){}.getType();
            GameDetails details = gson.fromJson(json, type);
            gameIdLabel.setText("Game ID: " + details.gameId);
            winnerLabel.setText("Winner: " + (details.overallWinner != null ? details.overallWinner : "None"));
            playersBox.getChildren().clear();
            for (String player : details.players) {
                Label playerLabel = new Label(player);
                playerLabel.setStyle("-fx-background-color: #222; -fx-text-fill: #ffdd00; -fx-font-family: 'Minecraftia'; -fx-padding: 4 10 4 10; -fx-border-radius: 6; -fx-background-radius: 6; -fx-font-size: 15px; -fx-border-color: #42bd97; -fx-border-width: 1px; margin-right: 6px;");
                playersBox.getChildren().add(playerLabel);
            }
            ObservableList<RoundRow> roundRows = FXCollections.observableArrayList();
            for (RoundInfo round : details.rounds) {
                roundRows.add(new RoundRow(round.roundNumber, round.word, round.winner));
            }
            colRoundNum.setCellValueFactory(cellData -> cellData.getValue().roundNumProperty());
            colWord.setCellValueFactory(cellData -> cellData.getValue().wordProperty());
            colRoundWinner.setCellValueFactory(cellData -> cellData.getValue().winnerProperty());
            roundsTable.setItems(roundRows);
            if (closeButton != null) {
                closeButton.setOnAction(e -> {
                    if (dialogStage != null) dialogStage.close();
                });
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    // --- Data classes for JSON parsing and TableView ---
    public static class GameDetails {
        public String gameId;
        public int totalRounds;
        public String overallWinner;
        public List<String> players;
        public List<RoundInfo> rounds;
    }
    public static class RoundInfo {
        public int roundNumber;
        public String word;
        public String winner;
    }
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