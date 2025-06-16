package client.player.view;

import GameModule.GameService;
import LoginModule.LoginService;
import client.player.controller.HomeViewController;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;
import javafx.stage.StageStyle;

public class HomeView {
    private Stage stage;
    private HomeViewController controller;

    public void start(Stage primaryStage, GameService gameService, String username, Runnable onLogout) {
        this.stage = primaryStage;
        try {
            // Remove default window decorations (no title bar/buttons)
            stage.initStyle(StageStyle.UNDECORATED);

            // Load FXML
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/client/player/view/HomeView.fxml"));
            Parent root = loader.load();

            // Get and configure controller
            controller = loader.getController();
            controller.setStage(stage);
            controller.setGameService(gameService);
            controller.setUsername(username);
            controller.setOnLogout(onLogout);
            
            // Try to start session validation if the method exists
            try {
                java.lang.reflect.Method startSessionValidation = 
                    controller.getClass().getDeclaredMethod("startSessionValidation");
                if (startSessionValidation != null) {
                    startSessionValidation.setAccessible(true);
                    startSessionValidation.invoke(controller);
                }
            } catch (Exception e) {
                // Method doesn't exist, ignore
            }

            // Make window draggable
            final double[] xOffset = {0};
            final double[] yOffset = {0};

            root.setOnMousePressed(event -> {
                xOffset[0] = event.getSceneX();
                yOffset[0] = event.getSceneY();
            });

            root.setOnMouseDragged(event -> {
                stage.setX(event.getScreenX() - xOffset[0]);
                stage.setY(event.getScreenY() - yOffset[0]);
            });

            // Set up scene
            Scene scene = new Scene(root);
            
            // Try to apply CSS if it exists
            try {
                String cssPath = "/client/player/view/home.css";
                if (getClass().getResource(cssPath) != null) {
                    scene.getStylesheets().add(getClass().getResource(cssPath).toExternalForm());
                }
            } catch (Exception e) {
                System.err.println("Could not load CSS: " + e.getMessage());
            }
            
            stage.setScene(scene);
            stage.setTitle("Home - What's The Word");
            stage.setResizable(false);
            stage.setWidth(750);
            stage.setHeight(650);
        } catch (Exception e) {
            System.err.println("Error loading HomeView: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    /**
     * Alternative initialization method that accepts session ID
     */
    public void init(Stage primaryStage, LoginService loginService, String username, String sessionId, Runnable onLogout) {
        if (primaryStage == null || loginService == null || username == null) {
            System.err.println("Cannot initialize HomeView with null parameters");
            if (primaryStage != null && onLogout != null) {
                // Try standard initialization as fallback
                // This part is tricky because we don't have a GameService instance here.
                // For now, we'll just log an error. A better solution might involve
                // getting the GameService from the LoginModel singleton.
            }
            return;
        }
        
        this.stage = primaryStage;
        try {
            // Remove default window decorations (no title bar/buttons)
            stage.initStyle(StageStyle.UNDECORATED);

            // Load FXML
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/client/player/view/HomeView.fxml"));
            Parent root = loader.load();

            // Get and configure controller
            controller = loader.getController();
            controller.setStage(stage);
            
            // We need both LoginService and GameService. Get them from the LoginModel singleton.
            try {
                Object loginModel = client.player.model.LoginModel.getInstance();
                GameService gameService = (GameService) loginModel.getClass().getMethod("getGameService").invoke(loginModel);
                controller.setGameService(gameService);
            } catch (Exception e) {
                System.err.println("Failed to get GameService from LoginModel singleton: " + e.getMessage());
            }

            controller.setLoginService(loginService);
            controller.setUsername(username);
            controller.setOnLogout(onLogout);
            
            // Set the session ID if the field exists
            try {
                if (sessionId != null && !sessionId.isEmpty()) {
                    java.lang.reflect.Field sessionIdField = controller.getClass().getDeclaredField("sessionId");
                    if (sessionIdField != null) {
                        sessionIdField.setAccessible(true);
                        sessionIdField.set(controller, sessionId);
                        
                        System.out.println("Successfully set session ID: " + sessionId);
                    }
                }
            } catch (Exception e) {
                // Field doesn't exist or can't be accessed, continue without setting it
                System.out.println("Could not set session ID directly: " + e.getMessage());
            }
            
            // Try to start the session validation timer if it exists
            try {
                java.lang.reflect.Method startSessionValidation = 
                    controller.getClass().getDeclaredMethod("startSessionValidation");
                if (startSessionValidation != null) {
                    startSessionValidation.setAccessible(true);
                    startSessionValidation.invoke(controller);
                    System.out.println("Started session validation");
                }
            } catch (Exception e) {
                // Method doesn't exist or can't be invoked
                System.out.println("Could not start session validation: " + e.getMessage());
            }

            // Make window draggable
            final double[] xOffset = {0};
            final double[] yOffset = {0};

            root.setOnMousePressed(event -> {
                xOffset[0] = event.getSceneX();
                yOffset[0] = event.getSceneY();
            });

            root.setOnMouseDragged(event -> {
                stage.setX(event.getScreenX() - xOffset[0]);
                stage.setY(event.getScreenY() - yOffset[0]);
            });

            // Set up scene
            Scene scene = new Scene(root);
            
            // Try to apply CSS if it exists
            try {
                String cssPath = "/client/player/view/home.css";
                if (getClass().getResource(cssPath) != null) {
                    scene.getStylesheets().add(getClass().getResource(cssPath).toExternalForm());
                }
            } catch (Exception e) {
                System.err.println("Could not load CSS: " + e.getMessage());
            }
            
            stage.setScene(scene);
            stage.setTitle("Home - What's The Word");
            stage.setResizable(false);
            stage.setWidth(750);
            stage.setHeight(650);
        } catch (Exception e) {
            System.err.println("Error initializing HomeView with session ID: " + e.getMessage());
            e.printStackTrace();
            
            // Fall back to standard initialization without session ID
            start(primaryStage, null, username, onLogout); // Passing null for GameService as we can't easily get it here
        }
    }

    public void show() {
        stage.show();
    }

    public void close() {
        stage.close();
    }
}
