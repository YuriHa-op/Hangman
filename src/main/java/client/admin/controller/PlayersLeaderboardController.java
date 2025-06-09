package client.admin.controller;

import client.admin.model.Player;
import client.admin.view.PlayerManagementView;
import client.admin.view.AdminMatchHistoryView;
import AdminModule.AdminService;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.fxml.FXML;
import javafx.scene.control.ListCell;
import javafx.scene.control.ListView;
import javafx.scene.control.TextField;
import javafx.scene.control.Alert;
import javafx.scene.control.Button;
import javafx.scene.control.ButtonType;
import javafx.scene.control.SelectionMode;
import javafx.scene.control.ComboBox;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.layout.HBox;
import javafx.scene.layout.StackPane;
import javafx.scene.layout.Priority;
import javafx.scene.layout.Region;
import javafx.scene.paint.Color;
import javafx.scene.shape.Circle;
import javafx.scene.text.Text;
import javafx.util.Callback;
import javafx.application.Platform;
import javafx.animation.KeyFrame;
import javafx.animation.Timeline;
import javafx.util.Duration;
import javafx.stage.Window;
import javafx.stage.Stage;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.Optional;
import java.util.function.Consumer;
import java.util.stream.Collectors;

public class PlayersLeaderboardController {
    @FXML
    private ListView<Player> playersListView;

    @FXML
    private TextField searchField;

    @FXML
    private ComboBox<String> statusFilterComboBox;

    @FXML
    private ComboBox<String> sortOrderComboBox;

    private List<Player> allPlayers = new ArrayList<>();
    private ObservableList<Player> filteredPlayers;
    private AdminService adminService;
    private Consumer<String> outputCallback;
    private Timeline refreshTimeline;

    private static final String STATUS_ALL = "All";
    private static final String STATUS_ONLINE = "Online";
    private static final String STATUS_OFFLINE = "Offline";

    private static final String SORT_DEFAULT_RANK = "Default (Rank)";
    private static final String SORT_WINS_ASC = "Wins (Ascending)";
    private static final String SORT_WINS_DESC = "Wins (Descending)";
    private static final String SORT_USERNAME_ASC = "Username (Ascending)";
    private static final String SORT_USERNAME_DESC = "Username (Descending)";

    public void initialize() {
        filteredPlayers = FXCollections.observableArrayList();
        playersListView.getSelectionModel().setSelectionMode(SelectionMode.MULTIPLE);

        statusFilterComboBox.setItems(FXCollections.observableArrayList(STATUS_ALL, STATUS_ONLINE, STATUS_OFFLINE));
        statusFilterComboBox.setValue(STATUS_ALL);

        sortOrderComboBox.setItems(FXCollections.observableArrayList(
            SORT_DEFAULT_RANK, SORT_WINS_ASC, SORT_WINS_DESC, SORT_USERNAME_ASC, SORT_USERNAME_DESC
        ));
        sortOrderComboBox.setValue(SORT_DEFAULT_RANK);

        searchField.textProperty().addListener((observable, oldValue, newValue) -> filterPlayers());
        statusFilterComboBox.valueProperty().addListener((observable, oldValue, newValue) -> filterPlayers());
        sortOrderComboBox.valueProperty().addListener((observable, oldValue, newValue) -> filterPlayers());

        setupAutoRefresh();

        playersListView.sceneProperty().addListener((obs, oldScene, newScene) -> {
            if (newScene != null) {
                Window window = newScene.getWindow();
                if (window != null) {
                    window.showingProperty().addListener((observable, oldValue, isShowing) -> {
                        if (isShowing) {
                            if (refreshTimeline != null) {
                                refreshTimeline.play();
                                if (outputCallback != null) outputCallback.accept("Auto-refresh started.");
                            }
                        } else {
                            if (refreshTimeline != null) {
                                refreshTimeline.stop();
                                 if (outputCallback != null) outputCallback.accept("Auto-refresh stopped.");
                            }
                        }
                    });
                } else {
                    newScene.windowProperty().addListener((obsWindow, oldWindow, newWindowVal) -> {
                        if (newWindowVal != null) {
                             newWindowVal.showingProperty().addListener((observable, oldValue, isShowing) -> {
                                if (isShowing) {
                                    if (refreshTimeline != null) {
                                        refreshTimeline.play();
                                        if (outputCallback != null) outputCallback.accept("Auto-refresh started.");
                                    }
                                } else {
                                    if (refreshTimeline != null) {
                                        refreshTimeline.stop();
                                        if (outputCallback != null) outputCallback.accept("Auto-refresh stopped.");
                                    }
                                }
                            });
                        }
                    });
                }
            }
        });

        playersListView.setCellFactory(new Callback<ListView<Player>, ListCell<Player>>() {
            @Override
            public ListCell<Player> call(ListView<Player> listView) {
                return new ListCell<Player>() {
                    private final HBox contentBox = new HBox();
                    private final HBox playerInfoBox = new HBox(10);
                    private final Button historyButton = new Button("History");
                    private final Region spacer = new Region();

                    {
                        historyButton.getStyleClass().add("admin-button-small");
                        playerInfoBox.setAlignment(javafx.geometry.Pos.CENTER_LEFT);
                        contentBox.setAlignment(javafx.geometry.Pos.CENTER_LEFT);
                        HBox.setHgrow(spacer, Priority.ALWAYS);
                        contentBox.getChildren().addAll(playerInfoBox, spacer, historyButton);
                        contentBox.setSpacing(10);
                        contentBox.setStyle("-fx-padding: 8px;");

                        historyButton.setOnAction(event -> {
                            Player player = getItem();
                            if (player != null && adminService != null && outputCallback != null) {
                                AdminMatchHistoryView historyView = new AdminMatchHistoryView();
                                historyView.showPlayerHistory(adminService, player.getUsername(), outputCallback, (Stage) playersListView.getScene().getWindow());
                            } else {
                                if (outputCallback != null) outputCallback.accept("Cannot show history: Player, service or output not available.");
                            }
                        });
                    }

                    @Override
                    protected void updateItem(Player player, boolean empty) {
                        super.updateItem(player, empty);
                        if (empty || player == null) {
                            setGraphic(null);
                        } else {
                            playerInfoBox.getChildren().clear();
                            ImageView avatarView;
                            if (player.getAvatar() != null && !player.getAvatar().isEmpty()) {
                                avatarView = new ImageView(new Image(player.getAvatar(), 32, 32, true, true));
                            } else {
                                Circle circle = new Circle(16, Color.web("#5e5e5e"));
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
                            String roleText = (player.getRole() != null) ? player.getRole() : "Player";
                            Text role = new Text("[" + roleText + "]");
                            role.setStyle("-fx-font-family: 'Minecraftia'; -fx-font-size: 14px; -fx-fill: #ffaa00;");
                            playerInfoBox.getChildren().addAll(rank, avatarView, username, wins, status, role);
                            
                            setGraphic(contentBox);
                        }
                    }
                };
            }
        });
    }

    private void setupAutoRefresh() {
        refreshTimeline = new Timeline(
            new KeyFrame(Duration.seconds(5), event -> {
                if (playersListView.getScene() != null && playersListView.getScene().getWindow() != null && playersListView.getScene().getWindow().isShowing()) {
                    if (outputCallback != null) outputCallback.accept("Auto-refreshing player list...");
                    refreshPlayerList();
                }
            })
        );
        refreshTimeline.setCycleCount(Timeline.INDEFINITE);
    }

    public void setAdminService(AdminService adminService) {
        this.adminService = adminService;
    }

    public void setOutputCallback(Consumer<String> outputCallback) {
        this.outputCallback = outputCallback;
    }

    private List<Player> parsePlayers(String playersData) {
        List<Player> players = new ArrayList<>();
        if (playersData == null || playersData.isEmpty()) {
            return players;
        }
        String[] lines = playersData.split("\n");
        for (int i = 1; i < lines.length; i++) {
            String line = lines[i].trim();
            if (line.isEmpty()) continue;
            try {
                Player player = new Player();
                int usernameStart = line.indexOf("Username: ") + "Username: ".length();
                int usernameEnd = line.indexOf(" | Wins:");
                if (usernameStart >= "Username: ".length() && usernameEnd > usernameStart) {
                    player.setUsername(line.substring(usernameStart, usernameEnd).trim());
                } else continue; 

                int winsStart = line.indexOf("Wins: ") + "Wins: ".length();
                int winsEnd = line.indexOf(" | Status:");
                if (winsStart >= "Wins: ".length() && winsEnd > winsStart) {
                    player.setWins(Integer.parseInt(line.substring(winsStart, winsEnd).trim()));
                } else continue;

                int statusStart = line.indexOf("Status: ") + "Status: ".length();
                int statusEnd = line.indexOf(" | Role:");
                if (statusStart >= "Status: ".length() && statusEnd > statusStart) {
                    player.setOnline("Online".equalsIgnoreCase(line.substring(statusStart, statusEnd).trim()));
                } else continue;

                int roleStart = line.indexOf("Role: ") + "Role: ".length();
                if (roleStart >= "Role: ".length() && roleStart < line.length()) {
                    player.setRole(line.substring(roleStart).trim());
                } else continue;
                
                players.add(player);
            } catch (Exception e) {
                System.err.println("PL_CTRL: Error parsing player line: '" + line + "'. Error: " + e.getMessage());
                if (outputCallback != null) outputCallback.accept("Error parsing a player data line in leaderboard.");
            }
        }
        players.sort(Comparator.comparingInt(Player::getWins).reversed());
        for (int i = 0; i < players.size(); i++) {
            players.get(i).setRank(i + 1);
        }
        return players;
    }

    public void refreshPlayerList() {
        if (adminService == null) {
            if (outputCallback != null) outputCallback.accept("Cannot refresh player list: AdminService not available.");
            return;
        }
        try {
            String playersData = adminService.viewPlayers();
            this.allPlayers = parsePlayers(playersData);
            filterPlayers();
        } catch (Exception e) {
            System.err.println("PL_CTRL: Error refreshing player list: " + e.getMessage());
            if (outputCallback != null) outputCallback.accept("Error refreshing player list: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private void filterPlayers() {
        String searchText = searchField.getText();
        String statusFilter = statusFilterComboBox.getValue();
        String sortOrder = sortOrderComboBox.getValue();

        List<Player> toDisplay = new ArrayList<>(allPlayers);

        if (statusFilter != null && !statusFilter.equals(STATUS_ALL)) {
            boolean showOnline = statusFilter.equals(STATUS_ONLINE);
            toDisplay = toDisplay.stream()
                               .filter(player -> player.isOnline() == showOnline)
                               .collect(Collectors.toList());
        }

        if (searchText != null && !searchText.trim().isEmpty()) {
            String lowerCaseSearch = searchText.toLowerCase().trim();
            toDisplay = toDisplay.stream()
                    .filter(player -> (player.getUsername() != null && player.getUsername().toLowerCase().contains(lowerCaseSearch)) ||
                                     (player.getRole() != null && player.getRole().toLowerCase().contains(lowerCaseSearch)))
                    .collect(Collectors.toList());
        }
        
        if (sortOrder != null) {
            switch (sortOrder) {
                case SORT_WINS_ASC:
                    toDisplay.sort(Comparator.comparingInt(Player::getWins));
                    break;
                case SORT_WINS_DESC:
                    toDisplay.sort(Comparator.comparingInt(Player::getWins).reversed());
                    break;
                case SORT_USERNAME_ASC:
                    toDisplay.sort(Comparator.comparing(Player::getUsername, String.CASE_INSENSITIVE_ORDER));
                    break;
                case SORT_USERNAME_DESC:
                    toDisplay.sort(Comparator.comparing(Player::getUsername, String.CASE_INSENSITIVE_ORDER).reversed());
                    break;
                case SORT_DEFAULT_RANK:
                default:
                    toDisplay.sort(Comparator.comparingInt(Player::getRank));
                    break;
            }
        }
        
        final List<Player> finalToDisplay = toDisplay;
        Platform.runLater(() -> {
            filteredPlayers.setAll(finalToDisplay);
            playersListView.setItems(filteredPlayers);
        });
    }

    public void setPlayers(List<Player> players) {
        this.allPlayers = new ArrayList<>(players); 
        filterPlayers();
    }

    @FXML
    private void handleBack() {
        if (refreshTimeline != null) {
            refreshTimeline.stop();
            if (outputCallback != null) outputCallback.accept("Auto-refresh stopped via Back button.");
        }
        playersListView.getScene().getWindow().hide();
    }

    @FXML
    private void handleAddPlayer() {
        if (adminService == null || outputCallback == null) {
             showAlertDialog(Alert.AlertType.ERROR, "Error", "Cannot add player: Service or output not ready."); return;
        }
        PlayerManagementView playerManagementView = new PlayerManagementView(adminService, outputCallback, this::refreshPlayerList);
        playerManagementView.showAddPlayer();
    }

    @FXML
    private void handleUpdatePlayer() {
        ObservableList<Player> selectedPlayers = playersListView.getSelectionModel().getSelectedItems();
        if (selectedPlayers.size() == 1) {
            Player selectedPlayer = selectedPlayers.get(0);
            if (adminService == null || outputCallback == null) {
                showAlertDialog(Alert.AlertType.ERROR, "Error", "Cannot update player: Service or output not ready."); return;
            }
            PlayerManagementView playerManagementView = new PlayerManagementView(adminService, outputCallback, this::refreshPlayerList);
            playerManagementView.showUpdatePlayerFor(selectedPlayer.getUsername()); 
        } else {
            showAlertDialog(Alert.AlertType.WARNING, "Update Player", "Please select exactly one player to update.");
        }
    }

    @FXML
    private void handleDeletePlayer() {
        ObservableList<Player> selectedPlayers = playersListView.getSelectionModel().getSelectedItems();

        if (selectedPlayers.isEmpty()) {
            showAlertDialog(Alert.AlertType.WARNING, "Delete Player", "Please select one or more players to delete.");
            return;
        }
        if (adminService == null || outputCallback == null) {
            showAlertDialog(Alert.AlertType.ERROR, "Error", "Cannot delete player: Service or output not ready."); return;
        }

        StringBuilder confirmationMessage = new StringBuilder("Are you sure you want to delete the following player(s)?\n");
        selectedPlayers.forEach(player -> confirmationMessage.append("- ").append(player.getUsername()).append("\n"));

        Optional<ButtonType> result = showConfirmationDialog("Confirm Deletion", confirmationMessage.toString());

        if (result.isPresent() && result.get() == ButtonType.OK) {
            List<String> successfullyDeletedUsernames = new ArrayList<>();
            List<String> failedToDeleteUsernames = new ArrayList<>();

            for (Player player : selectedPlayers) {
                try {
                    if (adminService.deletePlayer(player.getUsername()) == AdminModule.Bool.BOOL_TRUE) {
                        successfullyDeletedUsernames.add(player.getUsername());
                    } else {
                        failedToDeleteUsernames.add(player.getUsername() + " (failed by service)");
                    }
                } catch (Exception e) {
                    failedToDeleteUsernames.add(player.getUsername() + " (error: " + e.getMessage() + ")");
                }
            }
            
            refreshPlayerList();
            
            StringBuilder summaryMessage = new StringBuilder();
            if (!successfullyDeletedUsernames.isEmpty()) {
                summaryMessage.append("Successfully deleted ").append(successfullyDeletedUsernames.size()).append(" player(s):\n");
                for (String name : successfullyDeletedUsernames) {
                    summaryMessage.append("- ").append(name).append("\n");
                }
                outputCallback.accept(successfullyDeletedUsernames.size() + " player(s) deleted.");
            }
            if (!failedToDeleteUsernames.isEmpty()) {
                summaryMessage.append("Failed to delete ").append(failedToDeleteUsernames.size()).append(" player(s):\n");
                failedToDeleteUsernames.forEach(name -> summaryMessage.append("- ").append(name).append("\n"));
            }
            if (summaryMessage.length() > 0) {
                showAlertDialog(Alert.AlertType.INFORMATION, "Delete Player Results", summaryMessage.toString());
            }
        }
    }

    private void showAlertDialog(Alert.AlertType alertType, String title, String content) {
        Alert alert = new Alert(alertType);
        alert.setTitle(title);
        alert.setHeaderText(null);
        alert.setContentText(content);
        alert.showAndWait();
    }

    private Optional<ButtonType> showConfirmationDialog(String title, String content) {
        Alert alert = new Alert(Alert.AlertType.CONFIRMATION);
        alert.setTitle(title);
        alert.setHeaderText(null);
        alert.setContentText(content);
        return alert.showAndWait();
    }
}