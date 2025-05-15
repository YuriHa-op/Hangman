package client.admin.controller;

import client.admin.model.Player;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.fxml.FXML;
import javafx.scene.control.ListCell;
import javafx.scene.control.ListView;
import javafx.scene.control.TextField;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.layout.HBox;
import javafx.scene.layout.StackPane;
import javafx.scene.paint.Color;
import javafx.scene.shape.Circle;
import javafx.scene.text.Text;
import javafx.util.Callback;

import java.util.List;
import java.util.stream.Collectors;

public class PlayersLeaderboardController {
    @FXML
    private ListView<Player> playersListView;

    @FXML
    private TextField searchField;

    private List<Player> allPlayers;
    private ObservableList<Player> filteredPlayers;

    public void initialize() {
        // Initialize filtered list
        filteredPlayers = FXCollections.observableArrayList();

        // Set up search field listener for real-time filtering
        searchField.textProperty().addListener((observable, oldValue, newValue) -> {
            filterPlayers(newValue);
        });

        playersListView.setCellFactory(new Callback<ListView<Player>, ListCell<Player>>() {
            @Override
            public ListCell<Player> call(ListView<Player> listView) {
                return new ListCell<Player>() {

                    @Override
                    protected void updateItem(Player player, boolean empty) {
                        super.updateItem(player, empty);
                        if (empty || player == null) {
                            setGraphic(null);
                        } else {
                            // Avatar: use static image or initials in a circle
                            ImageView avatarView;
                            if (player.getAvatar() != null && !player.getAvatar().isEmpty()) {
                                avatarView = new ImageView(new Image(player.getAvatar(), 32, 32, true, true));
                            } else {
                                Circle circle = new Circle(16, Color.web("#5e5e5e"));

                                // Safely extract initial with null/empty check
                                String initialText = "?";
                                if (player.getUsername() != null && !player.getUsername().isEmpty()) {
                                    initialText = player.getUsername().substring(0, 1).toUpperCase();
                                }

                                Text initials = new Text(initialText);
                                initials.setFill(Color.BROWN);
                                initials.setStyle("-fx-font-family: 'Minecraftia'; -fx-font-size: 18px;");
                                StackPane avatarPane = new StackPane(circle, initials);
                                avatarPane.setPrefSize(32, 32);
                                avatarView = new ImageView();
                                avatarView.setImage(avatarPane.snapshot(null, null));
                            }

                            // Ensure username isn't null
                            String usernameText = (player.getUsername() != null) ? player.getUsername() : "Unknown";

                            Text rank = new Text("#" + player.getRank());
                            rank.setStyle("-fx-font-family: 'Minecraftia'; -fx-font-size: 16px; -fx-fill: #ffdd00;");
                            Text username = new Text(usernameText);
                            username.setStyle("-fx-font-family: 'Minecraftia'; -fx-font-size: 16px; -fx-fill: #ad0000;");
                            Text wins = new Text(player.getWins() + " wins");
                            wins.setStyle("-fx-font-family: 'Minecraftia'; -fx-font-size: 14px; -fx-fill: #55aaff;");
                            Text status = new Text(player.isOnline() ? "Online" : "Offline");
                            status.setStyle("-fx-font-family: 'Minecraftia'; -fx-font-size: 14px; -fx-fill: " +
                                    (player.isOnline() ? "#42bd97;" : "#888888;"));

                            // Ensure role isn't null
                            String roleText = (player.getRole() != null) ? player.getRole() : "Player";
                            Text role = new Text("[" + roleText + "]");
                            role.setStyle("-fx-font-family: 'Minecraftia'; -fx-font-size: 14px; -fx-fill: #ffaa00;");

                            HBox hbox = new HBox(10, rank, avatarView, username, wins, status, role);
                            hbox.setStyle("-fx-padding: 8px; -fx-alignment: center-left;");
                            setGraphic(hbox);
                        }
                    }
                };
            }
        });
    }

    @FXML
    private void handleSearch() {
        filterPlayers(searchField.getText());
    }

    private void filterPlayers(String searchText) {
        if (allPlayers == null) return;

        if (searchText == null || searchText.trim().isEmpty()) {
            // Show all players if search is empty
            filteredPlayers.setAll(allPlayers);
        } else {
            // Filter players by username
            String lowerCaseSearch = searchText.toLowerCase().trim();
            List<Player> filtered = allPlayers.stream()
                    .filter(player -> player.getUsername().toLowerCase().contains(lowerCaseSearch) ||
                            player.getRole().toLowerCase().contains(lowerCaseSearch))
                    .collect(Collectors.toList());
            filteredPlayers.setAll(filtered);
        }

        playersListView.setItems(filteredPlayers);
    }

    public void setPlayers(List<Player> players) {
        this.allPlayers = players;
        filteredPlayers.setAll(players);
        playersListView.setItems(filteredPlayers);
    }

    @FXML
    private void handleBack() {
        // Close or hide this view
        playersListView.getScene().getWindow().hide();
    }
}