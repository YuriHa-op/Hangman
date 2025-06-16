package client.player.controller;

import client.player.model.LoginModel;
import LoginModule.LoginService;
import LoginModule.Bool;
import LoginModule.LoginResponse;
import LoginModule.AlreadyLoggedInException;

import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.scene.control.Button;
import javafx.scene.control.PasswordField;
import javafx.scene.control.TextField;
import javafx.scene.control.Hyperlink;
import javafx.scene.control.Alert;
import javafx.scene.control.Alert.AlertType;
import javafx.scene.control.ButtonType;
import javafx.scene.control.Label;
import javafx.scene.paint.Color;
import javafx.scene.text.Text;
import javafx.stage.Stage;
import javafx.scene.layout.VBox;
import javafx.scene.layout.HBox;
import javafx.geometry.Pos;
import javafx.geometry.Insets;
import javafx.scene.Scene;

import java.util.Optional;

public class LoginViewController {
    @FXML private TextField usernameField;
    @FXML private PasswordField passwordField;
    @FXML private Button loginButton;
    @FXML private Text statusText;
    @FXML private Button retryButton;
    @FXML private Hyperlink signUpLink;

    private LoginModel model;
    private LoginService loginService;
    private Stage stage;
    private Runnable showLoginViewAgain;

    public void initialize() {
        // Initial setup when FXML is loaded
        statusText.setText("Please enter your credentials");
        statusText.setFill(Color.BLACK);
        
        // Set character limits: 10 for username and 15 for password
        usernameField.textProperty().addListener((observable, oldValue, newValue) -> {
            if (newValue.length() > 10) {
                usernameField.setText(oldValue);
            }
        });
        
        passwordField.textProperty().addListener((observable, oldValue, newValue) -> {
            if (newValue.length() > 15) {
                passwordField.setText(oldValue);
            }
        });
    }

    public void setModel(LoginModel model) {
        this.model = model;
        this.loginService = model.getLoginService();
    }

    public void setStage(Stage stage) {
        this.stage = stage;
    }

    public void setShowLoginViewAgain(Runnable showLoginViewAgain) {
        this.showLoginViewAgain = showLoginViewAgain;
    }

    /**
     * Handle successful login and launch home view
     */
    private void handleSuccessfulLogin(String username, String sessionId) {
        setStatus("Login successful!", false);
        
        // Make sure the session ID is stored in the login model for future reference
        if (model != null && sessionId != null && !sessionId.isEmpty()) {
            try {
                java.lang.reflect.Field sessionIdField = model.getClass().getDeclaredField("sessionId");
                sessionIdField.setAccessible(true);
                sessionIdField.set(model, sessionId);
                
                java.lang.reflect.Field loggedInUserField = model.getClass().getDeclaredField("loggedInUser");
                loggedInUserField.setAccessible(true);
                loggedInUserField.set(model, username);
                
                System.out.println("Stored session ID in LoginModel: " + sessionId);
            } catch (Exception e) {
                System.err.println("Could not store session ID in model: " + e.getMessage());
            }
        }
        
        // Launch HomeView and close login window
        javafx.application.Platform.runLater(() -> {
            close();
            
            Stage homeStage = new Stage();
            client.player.view.HomeView homeView = new client.player.view.HomeView();
            
            // Try to use the init method with session ID if possible
            boolean useInitMethod = false;
            
            if (sessionId != null && !sessionId.isEmpty()) {
                try {
                    // Check if the init method exists
                    java.lang.reflect.Method initMethod = homeView.getClass().getMethod(
                        "init", Stage.class, LoginService.class, String.class, String.class, Runnable.class);
                    
                    if (initMethod != null) {
                        // Use the init method that accepts sessionId
                        initMethod.invoke(homeView, homeStage, loginService, username, sessionId, (Runnable)(() -> {
                            if (showLoginViewAgain != null) showLoginViewAgain.run();
                        }));
                        useInitMethod = true;
                    }
                } catch (Exception e) {
                    System.err.println("Could not use init method: " + e.getMessage());
                    // Fall back to standard start method
                }
            }
            
            // If we couldn't use the init method, use the standard start method
            if (!useInitMethod) {
                homeView.start(homeStage, model.getGameService(), username, () -> {
                    // On logout, show login again
                    if (showLoginViewAgain != null) showLoginViewAgain.run();
                });
            }
            
            homeView.show();
        });
    }

    /**
     * Show a custom styled confirmation dialog for forcing logout of another session
     */
    private boolean showForceLogoutConfirmationDialog() {
        // Create a custom dialog stage
        Stage dialogStage = new Stage();
        dialogStage.initModality(javafx.stage.Modality.APPLICATION_MODAL);
        dialogStage.setTitle("Account In Use");
        dialogStage.initStyle(javafx.stage.StageStyle.UNDECORATED);
        dialogStage.setResizable(false);
        
        // Atomic reference to store the result
        java.util.concurrent.atomic.AtomicBoolean resultRef = new java.util.concurrent.atomic.AtomicBoolean(false);
        
        // Create root container with border
        VBox root = new VBox(15);
        root.setPadding(new javafx.geometry.Insets(20));
        root.setAlignment(javafx.geometry.Pos.CENTER);
        root.setStyle("-fx-background-color: #c6c6c6; " + 
                     "-fx-border-color: #555555; " +
                     "-fx-border-width: 4px; " +
                     "-fx-effect: dropshadow(three-pass-box, rgba(0,0,0,0.6), 10, 0, 0, 0);");
        
        // Dialog header
        Label titleLabel = new Label("Account Already In Use");
        titleLabel.setStyle("-fx-font-size: 22px; " +
                           "-fx-font-weight: bold; " +
                           "-fx-font-family: 'Minecraft', sans-serif; " +
                           "-fx-text-fill: #E64A19;"); // Orange color
        
        // Message
        Label messageLabel = new Label("This account is already logged in elsewhere.\nDo you want to force logout the previous session and login here?");
        messageLabel.setStyle("-fx-font-size: 14px; " +
                             "-fx-font-family: 'Minecraft', sans-serif; " +
                             "-fx-text-alignment: center;");
        messageLabel.setWrapText(true);
        messageLabel.setAlignment(javafx.geometry.Pos.CENTER);
        
        // Buttons container
        HBox buttonBox = new HBox(20);
        buttonBox.setAlignment(javafx.geometry.Pos.CENTER);
        
        // Yes button (minecraft style)
        Button yesButton = new Button("Yes, Force Logout");
        yesButton.setPrefWidth(150);
        yesButton.setPrefHeight(30);
        yesButton.setStyle("-fx-font-size: 12px; " +
                          "-fx-font-family: 'Minecraft', sans-serif; " +
                          "-fx-background-color: #43A047, linear-gradient(#66BB6A, #43A047); " +
                          "-fx-background-radius: 0; " +
                          "-fx-border-color: #2d2d2d; " +
                          "-fx-border-width: 2px; " +
                          "-fx-text-fill: white; " +
                          "-fx-cursor: hand;");
        
        // No button (minecraft style)
        Button noButton = new Button("No, Cancel");
        noButton.setPrefWidth(150);
        noButton.setPrefHeight(30);
        noButton.setStyle("-fx-font-size: 12px; " +
                         "-fx-font-family: 'Minecraft', sans-serif; " +
                         "-fx-background-color: #5c5c5c, linear-gradient(#9e9e9e, #707070); " +
                         "-fx-background-radius: 0; " +
                         "-fx-border-color: #2d2d2d; " +
                         "-fx-border-width: 2px; " +
                         "-fx-text-fill: white; " +
                         "-fx-cursor: hand;");
        
        // Button hover effects
        yesButton.setOnMouseEntered(e -> 
            yesButton.setStyle("-fx-font-size: 12px; " +
                              "-fx-font-family: 'Minecraft', sans-serif; " +
                              "-fx-background-color: #2E7D32, linear-gradient(#66BB6A, #2E7D32); " +
                              "-fx-background-radius: 0; " +
                              "-fx-border-color: #2d2d2d; " +
                              "-fx-border-width: 2px; " +
                              "-fx-text-fill: white; " +
                              "-fx-cursor: hand;"));
        
        yesButton.setOnMouseExited(e -> 
            yesButton.setStyle("-fx-font-size: 12px; " +
                              "-fx-font-family: 'Minecraft', sans-serif; " +
                              "-fx-background-color: #43A047, linear-gradient(#66BB6A, #43A047); " +
                              "-fx-background-radius: 0; " +
                              "-fx-border-color: #2d2d2d; " +
                              "-fx-border-width: 2px; " +
                              "-fx-text-fill: white; " +
                              "-fx-cursor: hand;"));
        
        noButton.setOnMouseEntered(e -> 
            noButton.setStyle("-fx-font-size: 12px; " +
                             "-fx-font-family: 'Minecraft', sans-serif; " +
                             "-fx-background-color: #707070, linear-gradient(#9e9e9e, #8a8a8a); " +
                             "-fx-background-radius: 0; " +
                             "-fx-border-color: #2d2d2d; " +
                             "-fx-border-width: 2px; " +
                             "-fx-text-fill: white; " +
                             "-fx-cursor: hand;"));
        
        noButton.setOnMouseExited(e -> 
            noButton.setStyle("-fx-font-size: 12px; " +
                             "-fx-font-family: 'Minecraft', sans-serif; " +
                             "-fx-background-color: #5c5c5c, linear-gradient(#9e9e9e, #707070); " +
                             "-fx-background-radius: 0; " +
                             "-fx-border-color: #2d2d2d; " +
                             "-fx-border-width: 2px; " +
                             "-fx-text-fill: white; " +
                             "-fx-cursor: hand;"));
        
        // Button actions
        yesButton.setOnAction(e -> {
            resultRef.set(true);
            dialogStage.close();
        });
        
        noButton.setOnAction(e -> {
            resultRef.set(false);
            dialogStage.close();
        });
        
        buttonBox.getChildren().addAll(yesButton, noButton);
        
        // Add components to root
        root.getChildren().addAll(titleLabel, messageLabel, buttonBox);
        
        // Set scene
        javafx.scene.Scene scene = new javafx.scene.Scene(root);
        dialogStage.setScene(scene);
        dialogStage.setWidth(450);
        dialogStage.setHeight(250);
        
        // Center on screen
        dialogStage.setOnShown(e -> {
            dialogStage.setX((javafx.stage.Screen.getPrimary().getVisualBounds().getWidth() - dialogStage.getWidth()) / 2);
            dialogStage.setY((javafx.stage.Screen.getPrimary().getVisualBounds().getHeight() - dialogStage.getHeight()) / 2);
        });
        
        // Show and wait for result
        dialogStage.showAndWait();
        
        return resultRef.get();
    }

    @FXML
    protected void handleLoginAction(ActionEvent event) {
        String username = usernameField.getText();
        String password = passwordField.getText();

        if (username.isEmpty() || password.isEmpty()) {
            setStatus("Username and password cannot be empty", true);
            return;
        }

        try {
            // First, try session-based login
            try {
                LoginResponse response = loginService.loginWithSession(username, password);
                if (response.success == Bool.BOOL_TRUE) {
                    System.out.println("Logged in with session ID: " + response.sessionId);
                    handleSuccessfulLogin(username, response.sessionId);
                } else {
                    setStatus("Invalid username or password", true);
                }
                return;
            } catch (org.omg.CORBA.BAD_OPERATION e) {
                // Server doesn't support session-based login, fall back to regular login
                System.out.println("Server doesn't support loginWithSession, falling back to regular login");
            } catch (AlreadyLoggedInException ex) {
                // Show custom confirmation dialog for force logout
                if (showForceLogoutConfirmationDialog()) {
                    // User chose to force logout - use special force login path
                    forceLogin(username, password);
                } else {
                    setStatus("Login canceled. The account is in use elsewhere.", true);
                }
                return;
            }
            
            // If we get here, we need to try regular login
            Bool success = loginService.login(username, password);
            if (success == Bool.BOOL_TRUE) {
                handleSuccessfulLogin(username, null);
            } else {
                setStatus("Invalid username or password", true);
            }
        } catch (AlreadyLoggedInException ex) {
            // Show custom confirmation dialog for force logout
            if (showForceLogoutConfirmationDialog()) {
                // User chose to force logout - use special force login path
                forceLogin(username, password);
            } else {
                setStatus("Login canceled. The account is in use elsewhere.", true);
            }
        } catch (Exception ex) {
            ex.printStackTrace();
            setStatus("Cannot connect to server. Please check your connection.", true);
        }
    }
    
    /**
     * Attempt a force login for an already logged in user
     */
    private void forceLogin(String username, String password) {
        try {
            // Try session login with force flag
            try {
                LoginResponse response = loginService.loginWithSession(username, password);
                if (response.success == Bool.BOOL_TRUE) {
                    System.out.println("Force logged in with session ID: " + response.sessionId);
                    
                    // Store the session ID in the model
                    if (model != null) {
                        java.lang.reflect.Field sessionIdField = model.getClass().getDeclaredField("sessionId");
                        sessionIdField.setAccessible(true);
                        sessionIdField.set(model, response.sessionId);
                        
                        java.lang.reflect.Field loggedInUserField = model.getClass().getDeclaredField("loggedInUser");
                        loggedInUserField.setAccessible(true);
                        loggedInUserField.set(model, username);
                    }
                    
                    setStatus("Login successful! (Previous session was closed)", false);
                    handleSuccessfulLogin(username, response.sessionId);
                } else {
                    setStatus("Failed to force login. Please try again later.", true);
                }
            } catch (org.omg.CORBA.BAD_OPERATION e) {
                // Server doesn't support session login, this is a problem for force login
                setStatus("Force login not supported by server. Please try again later.", true);
            } catch (Exception e) {
                setStatus("Error forcing login: " + e.getMessage(), true);
            }
        } catch (Exception ex) {
            ex.printStackTrace();
            setStatus("Cannot connect to server. Please check your connection.", true);
        }
    }

    @FXML
    protected void handleSignUpAction(ActionEvent event) {
        String username = usernameField.getText();
        String password = passwordField.getText();

        if (username.isEmpty() || password.isEmpty()) {
            setStatus("Username and password cannot be empty", true);
            return;
        }
        
        // Check username and password length constraints
        if (username.length() > 10) {
            setStatus("Username must be at most 10 characters", true);
            return;
        }
        
        if (password.length() > 15) {
            setStatus("Password must be at most 15 characters", true);
            return;
        }

        try {
            Bool success = loginService.createPlayer(username, password);
            if (success == Bool.BOOL_TRUE) {
                setStatus("Account created successfully! You can now login.", false);
            } else {
                setStatus("Username already exists. Please choose another.", true);
            }
        } catch (Exception ex) {
            ex.printStackTrace();
            setStatus("Cannot connect to server. Please check your connection.", true);
            retryButton.setVisible(true);
        }
    }

    @FXML
    protected void handleRetryAction(ActionEvent event) {
        setStatus("Retrying connection...", false);
        retryButton.setVisible(false);
        // Optionally, re-initialize the model or re-attempt login
    }

    public void setStatus(String message, boolean isError) {
        statusText.setText(message);
        statusText.setFill(isError ? Color.RED : Color.GREEN);
    }

    public String getUsername() {
        return usernameField.getText();
    }

    public String getPassword() {
        return passwordField.getText();
    }

    public void close() {
        if (stage != null) {
            stage.close();
        }
    }
}
