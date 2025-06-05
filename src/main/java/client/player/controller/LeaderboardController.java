package client.player.controller;

import GameModule.GameService;
import GameModule.LeaderboardEntryDTO;
import javafx.animation.KeyFrame;
import javafx.animation.KeyValue;
import javafx.animation.Timeline;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.fxml.FXML;
import javafx.geometry.Pos;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.control.ListCell;
import javafx.scene.control.ListView;
import javafx.scene.effect.DropShadow;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.layout.HBox;
import javafx.scene.layout.Pane;
import javafx.scene.layout.Priority;
import javafx.scene.paint.Color;
import javafx.stage.Stage;
import javafx.util.Callback;
import javafx.util.Duration;

import java.util.Arrays;
import java.util.List;

public class LeaderboardController {
    @FXML private ListView<PlayerEntry> leaderboardListView;
    @FXML private Button closeButton; // For the 'X' button

    private Stage stage;
    private GameService gameService;
    private Runnable onBackToMenu;

    // Define a simple class or record to hold player entry data
    public static class PlayerEntry {
        private final int rank;
        private final String name;
        private final int wins;
        // Assuming a default avatar
        private final String avatarPath = "/avat.png"; // Default avatar
        private final String crownPath = "/crown.png";

        public PlayerEntry(int rank, String name, int wins) {
            this.rank = rank;
            this.name = name;
            this.wins = wins;
        }

        public int getRank() { return rank; }
        public String getName() { return name; }
        public int getWins() { return wins; }
        public String getAvatarPath() { return avatarPath; }
        public String getCrownPath() { return crownPath; }
    }

    public void setStage(Stage stage) {
        this.stage = stage;
    }

    public void setGameService(GameService gameService) {
        this.gameService = gameService;
        loadLeaderboardData(); // Load data when service is set
    }

    public void setOnBackToMenu(Runnable onBackToMenu) {
        this.onBackToMenu = onBackToMenu;
    }

    @FXML
    public void initialize() {
        // Set up the cell factory for the ListView
        leaderboardListView.setCellFactory(listView -> new LeaderboardListCell());
    }

    private void loadLeaderboardData() {
        if (gameService == null) {
            System.err.println("GameService is null, cannot load leaderboard.");
            leaderboardListView.setPlaceholder(new Label("Leaderboard service unavailable."));
            return;
        }
        try {
            // GameService.getLeaderboardEntries() returns GameModule.LeaderboardEntryDTO[]
            GameModule.LeaderboardEntryDTO[] dtoArray = gameService.getLeaderboardEntries(); 
            ObservableList<PlayerEntry> entries = FXCollections.observableArrayList();

            if (dtoArray != null) {
                // No need for Arrays.asList if iterating directly
                int rank = 1;
                for (GameModule.LeaderboardEntryDTO dto : dtoArray) { // Iterate over GameModule.LeaderboardEntryDTO
                    // Manually create the internal PlayerEntry type using public fields
                    entries.add(new PlayerEntry(rank++, dto.username, dto.wins));
                }
                leaderboardListView.setItems(entries);

                // Adjust ListView height to show all items
                double cellHeight = 70; // Approximate height of a single cell - Increased
                int numItems = entries.size();
                if (numItems > 0) {
                    leaderboardListView.setPrefHeight(numItems * cellHeight + 10); // +10 for a little padding/border
                } else {
                    leaderboardListView.setPrefHeight(100); // Default height for empty placeholder
                }

                if (dtoArray.length == 0) {
                    leaderboardListView.setPlaceholder(new Label("Leaderboard is empty."));
                }
            } else {
                 leaderboardListView.setPlaceholder(new Label("Leaderboard data is unavailable (null)."));
                 System.err.println("Received null array from gameService.getLeaderboardEntries()");
            }

        } catch (Exception e) {
            System.err.println("Error loading leaderboard data: " + e.getMessage());
            e.printStackTrace();
            leaderboardListView.setPlaceholder(new Label("Could not load leaderboard."));
        }
    }

    @FXML
    private void handleBackToMenu() {
        if (onBackToMenu != null) {
            onBackToMenu.run();
        }
        if (stage != null) {
            stage.close();
        }
    }

    // Custom ListCell implementation
    private static class LeaderboardListCell extends ListCell<PlayerEntry> {
        private final HBox contentBox = new HBox();
        private final Label rankLabel = new Label();
        private final ImageView avatarImageView = new ImageView();
        private final Label nameLabel = new Label();
        private final HBox winsBox = new HBox();
        private final ImageView crownImageView = new ImageView();
        private final Label winsLabel = new Label();
        private final Pane spacer = new Pane(); // For pushing wins to the right

        private Timeline glowAnimation; // Timeline for the glow animation
        private DropShadow glowEffect;  // DropShadow effect for the glow

        public LeaderboardListCell() {
            super();
            // Structure: [Rank] [Avatar] [Name] <---Spacer---> [Crown Icon] [Wins]
            avatarImageView.setFitHeight(30);
            avatarImageView.setFitWidth(30);
            avatarImageView.setPreserveRatio(true);

            crownImageView.setFitHeight(20);
            crownImageView.setFitWidth(20);
            crownImageView.setPreserveRatio(true);

            rankLabel.getStyleClass().add("rank-label");
            nameLabel.getStyleClass().add("player-name-label");
            winsBox.getStyleClass().add("wins-container");
            winsBox.setAlignment(Pos.CENTER_LEFT);
            winsLabel.getStyleClass().add("wins-text");

            winsBox.getChildren().addAll(crownImageView, winsLabel);
            HBox.setHgrow(spacer, Priority.ALWAYS); // Spacer takes available horizontal space

            contentBox.getChildren().addAll(rankLabel, avatarImageView, nameLabel, spacer, winsBox);
            contentBox.getStyleClass().add("leaderboard-row"); // For overall row styling
            contentBox.setAlignment(Pos.CENTER_LEFT);
            contentBox.setSpacing(10); // Spacing between elements in the row
            
            // Remove default padding from ListCell to use HBox padding
            setPadding(javafx.geometry.Insets.EMPTY);
        }

        @Override
        protected void updateItem(PlayerEntry item, boolean empty) {
            super.updateItem(item, empty);

            // Stop any existing animation and remove effect before processing new item
            if (glowAnimation != null) {
                glowAnimation.stop();
                glowAnimation = null;
            }
            contentBox.setEffect(null);
            // Clear any dynamic style classes if we were using them previously for static glow
            contentBox.getStyleClass().removeIf(s -> s.startsWith("leaderboard-row-rank")); 

            if (empty || item == null) {
                setText(null);
                setGraphic(null);
            } else {
                rankLabel.setText(String.valueOf(item.getRank()));
                rankLabel.getStyleClass().removeIf(s -> s.startsWith("rank-label-"));
                if (item.getRank() >= 1 && item.getRank() <= 4) {
                    rankLabel.getStyleClass().add("rank-label-" + item.getRank());
                }

                Color glowColor = null;
                if (item.getRank() == 1) glowColor = Color.rgb(0, 123, 255, 0.9); // Blue
                else if (item.getRank() == 2) glowColor = Color.rgb(255, 215, 0, 0.9); // Gold
                else if (item.getRank() == 3) glowColor = Color.rgb(160, 82, 45, 0.9); // Brown (Sienna)

                if (glowColor != null) {
                    glowEffect = new DropShadow();
                    glowEffect.setColor(glowColor);
                    glowEffect.setSpread(0.6); // How much the shadow spreads
                    // Initial radius, will be animated
                    glowEffect.setRadius(10); 
                    contentBox.setEffect(glowEffect);

                    glowAnimation = new Timeline(
                        new KeyFrame(Duration.ZERO, new KeyValue(glowEffect.radiusProperty(), 10)),
                        new KeyFrame(Duration.seconds(1), new KeyValue(glowEffect.radiusProperty(), 20)), // Expand glow
                        new KeyFrame(Duration.seconds(2), new KeyValue(glowEffect.radiusProperty(), 10))  // Contract glow
                    );
                    glowAnimation.setCycleCount(Timeline.INDEFINITE);
                    glowAnimation.play();
                } else {
                    contentBox.setEffect(null); // Ensure no glow for other ranks
                }

                try {
                    Image avatarImg = new Image(getClass().getResourceAsStream(item.getAvatarPath()));
                    avatarImageView.setImage(avatarImg);
                } catch (Exception e) {
                    System.err.println("Failed to load avatar image: " + item.getAvatarPath() + " - " + e.getMessage());
                    avatarImageView.setImage(null); // Clear or set placeholder
                }
                nameLabel.setText(item.getName());
                try {
                    Image crownImg = new Image(getClass().getResourceAsStream(item.getCrownPath()));
                    crownImageView.setImage(crownImg);
                } catch (Exception e) {
                    System.err.println("Failed to load crown image: " + item.getCrownPath() + " - " + e.getMessage());
                    crownImageView.setImage(null); // Clear or set placeholder
                }
                winsLabel.setText(String.format("%,d", item.getWins())); // Format wins with commas

                setGraphic(contentBox);
            }
        }
    }
}