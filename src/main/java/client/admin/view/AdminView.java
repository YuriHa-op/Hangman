package client.admin.view;

import AdminModule.AdminService;
import client.admin.controller.AdminViewController;
import client.admin.model.AdminConnection;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;

public class AdminView {
    private Stage stage;
    private AdminViewController controller;

    public void start(Stage primaryStage, AdminService adminService, Runnable onLogout) {
        this.stage = primaryStage;
        try {
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/client/admin/view/AdminView.fxml"));
            Parent root = loader.load();
            controller = loader.getController();
            controller.setStage(stage);
            controller.setAdminService(adminService);
            controller.setOnLogout(() -> {
                this.close();
                if (onLogout != null) {
                    onLogout.run();
                }
            });

            Scene scene = new Scene(root);
            scene.getStylesheets().add(getClass().getResource("/client/admin/view/admin.css").toExternalForm());
            stage.setScene(scene);
            stage.setTitle("Admin Panel - What's The Word");
            stage.setResizable(true);
            stage.setMinWidth(600);
            stage.setMinHeight(850);
            stage.setWidth(800);
            stage.setHeight(950);
        } catch (Exception e) {
            System.err.println("Error loading AdminView: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    public void start(Stage primaryStage, AdminConnection adminConnection, Runnable onLogout) {
        this.stage = primaryStage;
        try {
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/client/admin/view/AdminView.fxml"));
            Parent root = loader.load();
            controller = loader.getController();
            controller.setStage(stage);
            controller.setAdminConnection(adminConnection);
            controller.setOnLogout(() -> {
                this.close();
                if (onLogout != null) {
                    onLogout.run();
                }
            });

            Scene scene = new Scene(root);
            scene.getStylesheets().add(getClass().getResource("/client/admin/view/admin.css").toExternalForm());
            stage.setScene(scene);
            stage.setTitle("Admin Panel - What's The Word");
            stage.setResizable(true);
            stage.setMinWidth(1000);
            stage.setMinHeight(950);
            stage.setWidth(1000);
            stage.setHeight(950);
        } catch (Exception e) {
            System.err.println("Error loading AdminView: " + e.getMessage());
            e.printStackTrace();
        }
    }

    public void show() {
        stage.show();
    }

    public void close() {
        if (stage != null) {
            stage.close();
        }
    }
}
