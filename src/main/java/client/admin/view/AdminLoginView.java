package client.admin.view;

import client.admin.model.AdminConnection;
import javafx.application.Application;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.layout.*;
import javafx.stage.Stage;

public class AdminLoginView extends Application {
    private TextField hostField;
    private TextField portField;
    private TextField usernameField;
    private PasswordField passwordField;
    private Button loginButton;
    private Label statusLabel;
    private AdminConnection adminConnection;
    private AdminView adminView;

    @Override
    public void start(Stage primaryStage) throws Exception {
        // Setup UI components
        VBox root = new VBox(10);
        root.setPadding(new Insets(20));
        root.setAlignment(Pos.CENTER);
        
        Label titleLabel = new Label("Admin Console Login");
        titleLabel.setStyle("-fx-font-size: 20px; -fx-font-weight: bold;");
        
        GridPane grid = new GridPane();
        grid.setHgap(10);
        grid.setVgap(10);
        grid.setAlignment(Pos.CENTER);
        
        hostField = new TextField("localhost");
        portField = new TextField("900");
        usernameField = new TextField("admin");
        passwordField = new PasswordField();
        loginButton = new Button("Login");
        statusLabel = new Label();
        statusLabel.setStyle("-fx-text-fill: red;");
        
        grid.add(new Label("Host:"), 0, 0);
        grid.add(hostField, 1, 0);
        grid.add(new Label("Port:"), 0, 1);
        grid.add(portField, 1, 1);
        grid.add(new Label("Username:"), 0, 2);
        grid.add(usernameField, 1, 2);
        grid.add(new Label("Password:"), 0, 3);
        grid.add(passwordField, 1, 3);
        
        loginButton.setOnAction(e -> handleLogin(primaryStage));
        
        root.getChildren().addAll(titleLabel, grid, loginButton, statusLabel);
        
        Scene scene = new Scene(root, 400, 300);
        scene.getStylesheets().add(getClass().getResource("/client/admin/view/admin.css").toExternalForm());
        
        primaryStage.setTitle("Admin Login");
        primaryStage.setScene(scene);
        primaryStage.setResizable(false);
        primaryStage.show();
    }
    
    private void handleLogin(Stage primaryStage) {
        String host = hostField.getText().trim();
        String port = portField.getText().trim();
        String username = usernameField.getText().trim();
        String password = passwordField.getText();
        
        if (host.isEmpty() || port.isEmpty() || username.isEmpty() || password.isEmpty()) {
            statusLabel.setText("All fields are required");
            return;
        }
        
        try {
            adminConnection = new AdminConnection(host, port);
            adminConnection.connect();
            
            // Validate admin credentials ( need to implement this in AdminService)
            
            // Create and use AdminView class
            Stage adminStage = new Stage();
            adminView = new AdminView();
            adminView.start(adminStage, adminConnection, () -> {
                primaryStage.show();
                passwordField.clear();
                statusLabel.setText("");
                if (adminConnection != null) {
                    adminConnection.disconnect();
                }
            });
            
            adminStage.setOnCloseRequest(e -> {
                if (adminConnection != null) {
                    adminConnection.disconnect();
                }
                primaryStage.show();
            });
            
            adminView.show();
            primaryStage.hide();
            
        } catch (Exception e) {
            statusLabel.setText("Connection error: " + e.getMessage());
            e.printStackTrace();
            
            if (adminConnection != null) {
                adminConnection.disconnect();
            }
        }
    }
    
    @Override
    public void stop() {
        if (adminConnection != null) {
            adminConnection.disconnect();
        }
        if (adminView != null) {
            adminView.close();
        }
    }
    
    public static void main(String[] args) {
        launch(args);
    }
} 