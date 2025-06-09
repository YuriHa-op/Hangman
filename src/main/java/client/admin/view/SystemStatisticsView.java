package client.admin.view;

import AdminModule.AdminService;
import client.admin.controller.SystemStatisticsController;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Modality;
import javafx.stage.Stage;

import java.io.IOException;
import java.util.function.Consumer;

public class SystemStatisticsView {
    private Stage stage;
    private SystemStatisticsController controller;
    private Consumer<String> outputCallback;
    private AdminService adminService;

    public SystemStatisticsView(AdminService adminService, Consumer<String> outputCallback) {
        this.adminService = adminService;
        this.outputCallback = outputCallback;
        this.stage = new Stage();
        stage.initModality(Modality.APPLICATION_MODAL);
        stage.setTitle("System Statistics");
        stage.setResizable(false);
    }

    public void initialize() {
        try {
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/client/admin/view/SystemStatisticsView.fxml"));
            Parent root = loader.load();
            controller = loader.getController();
            controller.setAdminService(adminService);
            controller.setOutputCallback(outputCallback);
            controller.setStage(stage);

            Scene scene = new Scene(root);
            scene.getStylesheets().add(getClass().getResource("/client/admin/view/SystemStatisticsView.css").toExternalForm());
            stage.setScene(scene);
            stage.setWidth(800);
            stage.setHeight(600);
        } catch (IOException e) {
            System.err.println("Error loading SystemStatisticsView: " + e.getMessage());
            e.printStackTrace();
        }
    }

    public void show() {
        controller.loadStatistics();
        stage.show();
    }

    public void close() {
        stage.close();
    }
}