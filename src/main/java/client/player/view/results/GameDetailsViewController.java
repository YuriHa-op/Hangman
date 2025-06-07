package client.player.view.results;

import client.player.dto.MultiplayerGameDetailsDTO;
import client.player.dto.MultiplayerRoundInfoDTO;
import javafx.collections.FXCollections;
import javafx.fxml.FXML;
import javafx.scene.control.TableColumn;
import javafx.scene.control.TableView;
import javafx.scene.control.cell.PropertyValueFactory;

public class GameDetailsViewController {

    @FXML private TableView<MultiplayerRoundInfoDTO> detailsTable;
    @FXML private TableColumn<MultiplayerRoundInfoDTO, Integer> roundColumn;
    @FXML private TableColumn<MultiplayerRoundInfoDTO, String> wordColumn;
    @FXML private TableColumn<MultiplayerRoundInfoDTO, String> winnerColumn;

    public void initialize() {
        roundColumn.setCellValueFactory(new PropertyValueFactory<>("roundNumber"));
        wordColumn.setCellValueFactory(new PropertyValueFactory<>("word"));
        winnerColumn.setCellValueFactory(new PropertyValueFactory<>("winner"));
    }

    public void setDetails(MultiplayerGameDetailsDTO details) {
        if (details != null && details.getRounds() != null) {
            detailsTable.setItems(FXCollections.observableArrayList(details.getRounds()));
        }
    }
}