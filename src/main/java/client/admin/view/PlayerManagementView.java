package client.admin.view;

import AdminModule.AdminService;
import client.admin.controller.PlayerManagementController;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;
import java.util.function.Consumer;

public class PlayerManagementView {
    private Stage stage;
    private PlayerManagementController controller;
    private AdminService adminService;
    private Consumer<String> outputCallback;
    private Runnable onSuccessfulActionCallback;

    public PlayerManagementView(AdminService adminService, Consumer<String> outputCallback, Runnable onSuccessfulActionCallback) {
        this.adminService = adminService;
        this.outputCallback = outputCallback;
        this.onSuccessfulActionCallback = onSuccessfulActionCallback;
    }

    public PlayerManagementView(AdminService adminService, Consumer<String> outputCallback) {
        this(adminService, outputCallback, null);
    }

    public void showAddPlayer() {
        try {
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/client/admin/view/AddPlayerView.fxml"));
            Parent root = loader.load();
            controller = loader.getController();
            controller.setAdminService(adminService);
            controller.setOutputCallback(outputCallback);
            if (onSuccessfulActionCallback != null) {
                controller.setOnSuccessfulActionCallback(onSuccessfulActionCallback);
            }

            Stage newStage = new Stage();
            controller.setStage(newStage);
            Scene scene = new Scene(root);
            scene.getStylesheets().add(getClass().getResource("/client/admin/view/player-management.css").toExternalForm());
            newStage.setScene(scene);
            newStage.setTitle("Add Player");
            newStage.setResizable(false);
            newStage.show();
        } catch (Exception e) {
            outputCallback.accept("Error loading Add Player view: " + e.getMessage());
            e.printStackTrace();
        }
    }

    public void showUpdatePlayer() {
        try {
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/client/admin/view/UpdatePlayerView.fxml"));
            Parent root = loader.load();
            controller = loader.getController();
            controller.setAdminService(adminService);
            controller.setOutputCallback(outputCallback);
            if (onSuccessfulActionCallback != null) {
                controller.setOnSuccessfulActionCallback(onSuccessfulActionCallback);
            }

            Stage newStage = new Stage();
            controller.setStage(newStage);
            Scene scene = new Scene(root);
            scene.getStylesheets().add(getClass().getResource("/client/admin/view/player-management.css").toExternalForm());
            newStage.setScene(scene);
            newStage.setTitle("Update Player");
            newStage.setResizable(false);
            newStage.show();
        } catch (Exception e) {
            outputCallback.accept("Error loading Update Player view: " + e.getMessage());
            e.printStackTrace();
        }
    }

    public void showUpdatePlayerFor(String username) {
        try {
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/client/admin/view/UpdatePlayerView.fxml"));
            Parent root = loader.load();
            controller = loader.getController();
            controller.setAdminService(adminService);
            controller.setOutputCallback(outputCallback);
            controller.setUsernameForUpdate(username);
            if (onSuccessfulActionCallback != null) {
                controller.setOnSuccessfulActionCallback(onSuccessfulActionCallback);
            }

            Stage newStage = new Stage();
            controller.setStage(newStage);
            Scene scene = new Scene(root);
            scene.getStylesheets().add(getClass().getResource("/client/admin/view/player-management.css").toExternalForm());
            newStage.setScene(scene);
            newStage.setTitle("Update Player");
            newStage.setResizable(false);
            newStage.show();
        } catch (Exception e) {
            outputCallback.accept("Error loading Update Player view for " + username + ": " + e.getMessage());
            e.printStackTrace();
        }
    }

    public void showDeletePlayer() {
        try {
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/client/admin/view/DeletePlayerView.fxml"));
            Parent root = loader.load();
            controller = loader.getController();
            controller.setAdminService(adminService);
            controller.setOutputCallback(outputCallback);
            if (onSuccessfulActionCallback != null) {
                controller.setOnSuccessfulActionCallback(onSuccessfulActionCallback);
            }

            Stage newStage = new Stage();
            controller.setStage(newStage);
            Scene scene = new Scene(root);
            scene.getStylesheets().add(getClass().getResource("/client/admin/view/player-management.css").toExternalForm());
            newStage.setScene(scene);
            newStage.setTitle("Delete Player");
            newStage.setResizable(false);
            newStage.show();
        } catch (Exception e) {
            outputCallback.accept("Error loading Delete Player view: " + e.getMessage());
            e.printStackTrace();
        }
    }
} 