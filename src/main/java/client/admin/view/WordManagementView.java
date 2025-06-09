package client.admin.view;

import client.admin.controller.WordManagementController;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Modality;
import javafx.stage.Stage;
import AdminModule.AdminService;

import java.io.IOException;
import java.util.function.Consumer;

public class WordManagementView {
    private Stage stage;
    private WordManagementController controller;
    private Consumer<String> outputCallback;
    private AdminService adminService;
    private boolean initialized = false;

    public WordManagementView(AdminService adminService, Consumer<String> outputCallback) {
        this.adminService = adminService;
        this.outputCallback = outputCallback;
        this.stage = new Stage();
        stage.initModality(Modality.APPLICATION_MODAL);
        stage.setTitle("Word Management");
        stage.setResizable(false);
        initialize();
    }

    public void initialize() {
        if (initialized) return;
        try {
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/client/admin/view/WordManagementView.fxml"));
            Parent root = loader.load();
            controller = loader.getController();
            if (controller != null) {
                controller.setOutputCallback(outputCallback);
                controller.setStage(stage);
                controller.setAdminService(adminService);
            } else {
                System.err.println("Failed to get controller from FXML loader");
            }
            Scene scene = new Scene(root);
            scene.getStylesheets().add(getClass().getResource("/client/admin/view/word-management.css").toExternalForm());
            stage.setScene(scene);
            stage.setWidth(850);
            stage.setHeight(750);
            initialized = true;
        } catch (IOException e) {
            System.err.println("Error loading WordManagementView: " + e.getMessage());
            e.printStackTrace();
        }
    }

    public void showViewWords() {
        if (!initialized) initialize();
        if (controller != null) {
            controller.loadWords();
            stage.show();
        } else {
            System.err.println("Controller is null in showViewWords");
        }
    }

    public void showAddWord() {
        if (!initialized) initialize();
        if (controller != null) {
            controller.prepareAddWord();
            stage.show();
        } else {
            System.err.println("Controller is null in showAddWord");
        }
    }

    public void showUpdateWord() {
        if (!initialized) initialize();
        if (controller != null) {
            controller.prepareUpdateWord();
            stage.show();
        } else {
            System.err.println("Controller is null in showUpdateWord");
        }
    }

    public void showDeleteWord() {
        if (!initialized) initialize();
        if (controller != null) {
            controller.prepareDeleteWord();
            stage.show();
        } else {
            System.err.println("Controller is null in showDeleteWord");
        }
    }

    public void close() {
        stage.close();
    }
}