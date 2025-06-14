package client.player.controller;

import client.player.model.LoginModel;
import GameModule.GameService;
import GameModule.Bool;
import GameModule.AlreadyLoggedInException;

import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.scene.control.Button;
import javafx.scene.control.PasswordField;
import javafx.scene.control.TextField;
import javafx.scene.control.Hyperlink;
import javafx.scene.paint.Color;
import javafx.scene.text.Text;
import javafx.stage.Stage;

public class LoginViewController {
    @FXML private TextField usernameField;
    @FXML private PasswordField passwordField;
    @FXML private Button loginButton;
    @FXML private Text statusText;
    @FXML private Button retryButton;
    @FXML private Hyperlink signUpLink;

    private LoginModel model;
    private GameService gameService;
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
        this.gameService = model.getGameService();
    }

    public void setStage(Stage stage) {
        this.stage = stage;
    }

    public void setShowLoginViewAgain(Runnable showLoginViewAgain) {
        this.showLoginViewAgain = showLoginViewAgain;
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
            GameModule.Bool success = gameService.login(username, password);
            if (success == GameModule.Bool.BOOL_TRUE) {
                setStatus("Login successful!", false);
                // Launch HomeView and close login window
                javafx.application.Platform.runLater(() -> {
                    close();
                    Stage homeStage = new Stage();
                    client.player.view.HomeView homeView = new client.player.view.HomeView();
                    homeView.start(homeStage, gameService, username, () -> {
                        // On logout, show login again
                        if (showLoginViewAgain != null) showLoginViewAgain.run();
                    });
                    homeView.show();
                });
            } else {
                setStatus("Invalid username or password", true);
            }
        } catch (GameModule.AlreadyLoggedInException ex) {
            setStatus("User is already logged in elsewhere.", true);
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
            GameModule.Bool success = gameService.createPlayer(username, password);
            if (success == GameModule.Bool.BOOL_TRUE) {
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
