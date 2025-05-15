package client.admin.controller;

    import client.admin.model.WordManagementModel;
    import javafx.collections.FXCollections;
    import javafx.collections.ObservableList;
    import javafx.fxml.FXML;
    import javafx.fxml.FXMLLoader;
    import javafx.scene.Scene;
    import javafx.scene.control.*;
    import javafx.stage.Modality;
    import javafx.stage.Stage;
    import GameModule.GameService;

    import java.io.IOException;
    import java.util.List;
    import java.util.function.Consumer;

    public class WordManagementController {
        @FXML
        private Label titleLabel;
        @FXML
        private TextField searchField;
        @FXML
        private ListView<String> wordListView;
        @FXML
        private TextField newWordField;
        @FXML
        private TextField updatedWordField;
        @FXML
        private Label currentWordLabel;
        @FXML
        private Label wordToDeleteLabel;
        @FXML
        private Button closeButton;

        private Stage stage;
        private Consumer<String> outputCallback;
        private WordManagementModel model;
        private ObservableList<String> filteredWords = FXCollections.observableArrayList();
        private Stage currentDialogStage;
        private GameService gameService;

        @FXML
        public void initialize() {
            if (gameService != null) {
                model = new WordManagementModel(gameService);
            } else {
                model = new WordManagementModel();
            }
            wordListView.setItems(filteredWords);

            searchField.textProperty().addListener((observable, oldValue, newValue) -> {
                filterWords(newValue);
            });

            if (closeButton != null) {
                closeButton.setOnAction(event -> handleClose());
            }
        }

        public void setStage(Stage stage) {
            this.stage = stage;
        }

        public void setOutputCallback(Consumer<String> outputCallback) {
            this.outputCallback = outputCallback;
        }

        public void setGameService(GameService gameService) {
            this.gameService = gameService;
            this.model = new WordManagementModel(gameService);
        }

        public void loadWords() {
            model.loadWords();
            filterWords("");
            updateTitle();
        }

        private void updateTitle() {
            titleLabel.setText("Word Management - " + filteredWords.size() + " of " + model.getWordCount() + " words");
        }

        private void filterWords(String searchText) {
            List<String> filtered = model.searchWords(searchText);
            filteredWords.setAll(filtered);
            updateTitle();
        }

        @FXML
        public void prepareAddWord() {
            try {
                FXMLLoader loader = new FXMLLoader();
                loader.setLocation(getClass().getResource("/client/admin/view/AddWordDialog.fxml"));
                loader.setController(this);

                Scene scene = new Scene(loader.load());
                scene.getStylesheets().add(getClass().getResource("/client/admin/view/word-management.css").toExternalForm());

                currentDialogStage = new Stage();
                currentDialogStage.initModality(Modality.APPLICATION_MODAL);
                currentDialogStage.setTitle("Add Word");
                currentDialogStage.setScene(scene);
                currentDialogStage.showAndWait();
            } catch (IOException e) {
                showError("Error", "Could not open add word dialog: " + e.getMessage());
                e.printStackTrace();
            }
        }

        @FXML
        public void handleAddWord() {
            String newWord = newWordField.getText().trim();
            try {
                if (model.addWord(newWord)) {
                    if (outputCallback != null) {
                        outputCallback.accept("Added word: " + newWord);
                    }
                    closeDialog();
                    refreshWordList();
                }
            } catch (IllegalArgumentException e) {
                showError("Error", e.getMessage());
            } catch (IOException e) {
            } catch (Exception e) {
                showError("Error", "Failed to add word: " + e.getMessage());
            }
        }

        @FXML
        public void prepareUpdateWord() {
            String selectedWord = wordListView.getSelectionModel().getSelectedItem();
            if (selectedWord == null) {
                showError("Selection Required", "Please select a word to update");
                return;
            }

            try {
                FXMLLoader loader = new FXMLLoader();
                loader.setLocation(getClass().getResource("/client/admin/view/UpdateWordDialog.fxml"));
                loader.setController(this);

                Scene scene = new Scene(loader.load());
                scene.getStylesheets().add(getClass().getResource("/client/admin/view/word-management.css").toExternalForm());

                currentWordLabel.setText("Current word: " + selectedWord);
                updatedWordField.setText(selectedWord);

                currentDialogStage = new Stage();
                currentDialogStage.initModality(Modality.APPLICATION_MODAL);
                currentDialogStage.setTitle("Update Word");
                currentDialogStage.setScene(scene);
                currentDialogStage.showAndWait();
            } catch (IOException e) {
                showError("Error", "Could not open update word dialog: " + e.getMessage());
                e.printStackTrace();
            }
        }

        @FXML
        public void handleUpdateWord() {
            String oldWord = currentWordLabel.getText().replace("Current word: ", "");
            String newWord = updatedWordField.getText().trim();

            try {
                if (model.updateWord(oldWord, newWord)) {
                    if (outputCallback != null) {
                        outputCallback.accept("Updated word from '" + oldWord + "' to '" + newWord + "'");
                    }
                    closeDialog();
                    refreshWordList();
                }
            } catch (IllegalArgumentException e) {
                showError("Error", e.getMessage());
            } catch (IOException e) {
            } catch (Exception e) {
                showError("Error", "Failed to update word: " + e.getMessage());
            }
        }

        @FXML
        public void prepareDeleteWord() {
            String selectedWord = wordListView.getSelectionModel().getSelectedItem();
            if (selectedWord == null) {
                showError("Selection Required", "Please select a word to delete");
                return;
            }

            try {
                FXMLLoader loader = new FXMLLoader();
                loader.setLocation(getClass().getResource("/client/admin/view/DeleteWordDialog.fxml"));
                loader.setController(this);

                Scene scene = new Scene(loader.load());
                scene.getStylesheets().add(getClass().getResource("/client/admin/view/word-management.css").toExternalForm());

                wordToDeleteLabel.setText(selectedWord);

                currentDialogStage = new Stage();
                currentDialogStage.initModality(Modality.APPLICATION_MODAL);
                currentDialogStage.setTitle("Delete Word");
                currentDialogStage.setScene(scene);
                currentDialogStage.showAndWait();
            } catch (IOException e) {
                showError("Error", "Could not open delete word dialog: " + e.getMessage());
                e.printStackTrace();
            }
        }

        @FXML
        public void handleDeleteWord() {
            String wordToDelete = wordToDeleteLabel.getText();
            try {
                if (model.deleteWord(wordToDelete)) {
                    if (outputCallback != null) {
                        outputCallback.accept("Deleted word: " + wordToDelete);
                    }
                    closeDialog();
                    refreshWordList();
                }
            } catch (IllegalArgumentException e) {
                showError("Error", e.getMessage());
            } catch (IOException e) {
            } catch (Exception e) {
                showError("Error", "Failed to delete word: " + e.getMessage());
            }
        }

        @FXML
        public void handleCancel() {
            if (currentDialogStage != null) {
                currentDialogStage.close();
            }
        }

        @FXML
        public void handleClose() {
            if (stage != null) {
                stage.close();
            }
        }

        private void closeDialog() {
            if (currentDialogStage != null) {
                currentDialogStage.close();
            }
        }

        private void refreshWordList() {
            loadWords();
            if (outputCallback != null) {
                outputCallback.accept("Word list refreshed");
            }
        }

        private void showError(String title, String message) {
            Alert alert = new Alert(Alert.AlertType.ERROR);
            alert.setTitle(title);
            alert.setHeaderText(null);
            alert.setContentText(message);
            alert.getDialogPane().getStyleClass().add("error-dialog");
            alert.showAndWait();
        }
    }