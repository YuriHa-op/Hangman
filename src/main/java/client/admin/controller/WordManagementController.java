package client.admin.controller;

import AdminModule.AdminService;
import client.admin.model.WordManagementModel;
import client.admin.model.Word;
import javafx.application.Platform;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.control.cell.PropertyValueFactory;
import javafx.stage.Modality;
import javafx.stage.Stage;
import javafx.util.Callback;
import AdminModule.Bool;

import java.io.IOException;
import java.util.List;
import java.util.function.Consumer;

public class WordManagementController {
    @FXML private TableView<Word> wordsTable;
    @FXML private TableColumn<Word, String> wordColumn;
    @FXML private TableColumn<Word, Void> updateColumn;
    @FXML private TableColumn<Word, Void> deleteColumn;
    @FXML private TextField newWordField;
    @FXML private TextField wordToUpdateField;
    @FXML private TextField updatedWordField;
    @FXML private Button addButton;
    @FXML private Button updateButton;
    @FXML private TextField searchField;
    @FXML private Label statusLabel;
    @FXML private TabPane tabPane;

    private WordManagementModel model;
    private AdminService adminService;
    private ObservableList<Word> wordsList = FXCollections.observableArrayList();
    private Consumer<String> outputCallback;
    private Stage stage;

    @FXML
    public void initialize() {
        wordColumn.setCellValueFactory(new PropertyValueFactory<>("word"));
        wordsTable.setItems(wordsList);
        setupTableColumns();

        searchField.textProperty().addListener((observable, oldValue, newValue) -> {
            filterWords(newValue);
        });
    }

    public void setAdminService(AdminService adminService) {
        this.adminService = adminService;
        this.model = new WordManagementModel(adminService);
        loadWords(); // Reload words whenever adminService is set or changed
    }

    public void setOutputCallback(Consumer<String> outputCallback) {
        this.outputCallback = outputCallback;
    }

    public void setStage(Stage stage) {
        this.stage = stage;
    }

    public void loadWords() {
        try {
            List<String> words = model.getAllWords();
            updateWordsList(words);
            showStatus("Loaded " + words.size() + " words");
        } catch (Exception e) {
            showError("Error loading words: " + e.getMessage());
        }
    }

    private void updateWordsList(List<String> words) {
        Platform.runLater(() -> {
            wordsList.clear();
            for (String word : words) {
                wordsList.add(new Word(word));
            }
        });
    }

    private void filterWords(String searchText) {
        try {
            List<String> filteredWords = model.searchWords(searchText);
            updateWordsList(filteredWords);
            showStatus("Found " + filteredWords.size() + " words");
        } catch (Exception e) {
            showError("Error filtering words: " + e.getMessage());
        }
    }

    @FXML
    private void handleAddWord() {
        String word = newWordField.getText().trim();
        if (word.isEmpty()) {
            showError("Word cannot be empty");
            return;
        }

        try {
            Bool result = model.addWord(word);
            if (result == Bool.BOOL_TRUE) {
                newWordField.clear();
                loadWords();
                showStatus("Word '" + word + "' added successfully");
                if (outputCallback != null) {
                    outputCallback.accept("Word added: " + word);
                }
                tabPane.getSelectionModel().select(0); // Switch to view tab
            } else {
                showError("Failed to add word");
            }
        } catch (Exception e) {
            showError("Error adding word: " + e.getMessage());
        }
    }

    @FXML
    private void handleUpdateWord() {
        String oldWord = wordToUpdateField.getText().trim();
        String newWord = updatedWordField.getText().trim();

        if (oldWord.isEmpty() || newWord.isEmpty()) {
            showError("Both fields must be filled");
            return;
        }

        try {
            Bool result = model.updateWord(oldWord, newWord);
            if (result == Bool.BOOL_TRUE) {
                wordToUpdateField.clear();
                updatedWordField.clear();
                loadWords();
                showStatus("Word updated successfully");
                if (outputCallback != null) {
                    outputCallback.accept("Word updated: " + oldWord + " -> " + newWord);
                }
                tabPane.getSelectionModel().select(0); // Switch to view tab
            } else {
                showError("Failed to update word");
            }
        } catch (Exception e) {
            showError("Error updating word: " + e.getMessage());
        }
    }

    private void setupTableColumns() {
        // Add update button column
        updateColumn.setCellFactory(param -> new TableCell<Word, Void>() {
            private final Button updateBtn = new Button("Update");

            {
                updateBtn.setOnAction(event -> {
                    Word word = getTableView().getItems().get(getIndex());
                    wordToUpdateField.setText(word.getWord());
                    updatedWordField.clear();
                    updatedWordField.requestFocus();
                    tabPane.getSelectionModel().select(2); // Switch to update tab (index 2)
                });
                updateBtn.getStyleClass().add("action-button");
                updateBtn.setPrefWidth(90);
                updateBtn.setPrefHeight(30);
            }

            @Override
            protected void updateItem(Void item, boolean empty) {
                super.updateItem(item, empty);
                if (empty) {
                    setGraphic(null);
                } else {
                    setGraphic(updateBtn);
                }
            }
        });

        // Add delete button column
        deleteColumn.setCellFactory(param -> new TableCell<Word, Void>() {
            private final Button deleteBtn = new Button("Delete");

            {
                deleteBtn.setOnAction(event -> {
                    Word word = getTableView().getItems().get(getIndex());
                    Alert alert = new Alert(Alert.AlertType.CONFIRMATION,
                            "Are you sure you want to delete the word '" + word.getWord() + "'?",
                            ButtonType.YES, ButtonType.NO);
                    alert.showAndWait().ifPresent(response -> {
                        if (response == ButtonType.YES) {
                            try {
                                Bool result = model.deleteWord(word.getWord());
                                if (result == Bool.BOOL_TRUE) {
                                    loadWords();
                                    showStatus("Word '" + word.getWord() + "' deleted successfully");
                                    if (outputCallback != null) {
                                        outputCallback.accept("Word deleted: " + word.getWord());
                                    }
                                } else {
                                    showError("Failed to delete word");
                                }
                            } catch (Exception e) {
                                showError("Error deleting word: " + e.getMessage());
                            }
                        }
                    });
                });
                deleteBtn.getStyleClass().add("dialog-button-delete");
                deleteBtn.setPrefWidth(90);
                deleteBtn.setPrefHeight(30);
            }

            @Override
            protected void updateItem(Void item, boolean empty) {
                super.updateItem(item, empty);
                if (empty) {
                    setGraphic(null);
                } else {
                    setGraphic(deleteBtn);
                }
            }
        });
    }

    public void prepareAddWord() {
        if (tabPane != null) {
            tabPane.getSelectionModel().select(1); // Switch to Add Word tab
        }
    }

    public void prepareUpdateWord() {
        if (tabPane != null) {
            tabPane.getSelectionModel().select(2); // Switch to Update Word tab
        }
    }

    public void prepareDeleteWord() {
        if (tabPane != null && wordsTable != null) {
            tabPane.getSelectionModel().select(0); // Switch to View Words tab
        }
    }

    private void showStatus(String message) {
        Platform.runLater(() -> {
            statusLabel.setText(message);
            statusLabel.setStyle("-fx-text-fill: green;");
        });
    }

    private void showError(String message) {
        Platform.runLater(() -> {
            statusLabel.setText(message);
            statusLabel.setStyle("-fx-text-fill: red;");
        });
    }

    @FXML
    public void handleCancel() {
        if (stage != null) {
            stage.close();
        }
    }
}