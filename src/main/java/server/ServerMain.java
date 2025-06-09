package server;

import GameModule.GameService;
import GameModule.GameServiceHelper;
import AdminModule.AdminService;
import AdminModule.AdminServiceHelper;
import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;
import org.omg.CORBA.ORB;
import org.omg.CosNaming.NameComponent;
import org.omg.CosNaming.NamingContextExt;
import org.omg.CosNaming.NamingContextExtHelper;
import org.omg.PortableServer.POA;
import org.omg.PortableServer.POAHelper;
import server.controller.ServerMainController;
import javafx.scene.image.Image;
import server.handler.service.GameServiceImpl;
import server.handler.service.AdminServiceImpl;
import server.handler.core.WordManager;
import server.handler.core.PlayerManager;
import server.handler.data.MatchResultDAO;
import server.handler.data.SinglePlayerMatchResultDAO;

import java.io.IOException;

public class ServerMain extends Application {
    private ORB orb;
    private POA rootPOA;
    private GameServiceImpl gameService;
    private AdminServiceImpl adminService;
    private ServerMainController controller;
    private Thread orbThread;
    private boolean isPaused = false;
    
    // Database connection settings
    private static final String DB_URL = "jdbc:mysql://localhost:3306/game";
    private static final String DB_USER = "root";
    private static final String DB_PASSWORD = "";
    
    // Shared resources
    private WordManager wordManager;
    private PlayerManager playerManager;
    private MatchResultDAO matchResultDAO;
    private SinglePlayerMatchResultDAO singlePlayerMatchResultDAO;

    @Override
    public void start(Stage primaryStage) throws Exception {
        try {
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/server/view/ServerMainView.fxml"));
            Parent root = loader.load();
            controller = loader.getController();
            controller.setServerMain(this);
            
            Scene scene = new Scene(root);
            scene.getStylesheets().add(getClass().getResource("/server/view/ServerMainView.css").toExternalForm());
            
            primaryStage.setTitle("Hangman Game Server");
            primaryStage.setScene(scene);
            primaryStage.getIcons().add(
                    new Image(getClass().getResourceAsStream("/server/view/icon.png"))
            );
            primaryStage.setMinWidth(800);
            primaryStage.setMinHeight(600);
            primaryStage.show();
            
            // Set up handling for window close event
            primaryStage.setOnCloseRequest(event -> {
                if (orb != null) {
                    stop();
                }
            });
            
            controller.logInfo("Server GUI initialized successfully");
        } catch (IOException e) {
            System.err.println("Error initializing server UI: " + e.getMessage());
            e.printStackTrace();
            throw e;
        }
    }

    public void startServer() {
        try {
            isPaused = false;
            controller.logInfo("Initializing server components...");
            
            String[] args = new String[0];
            orb = ORB.init(args, null);
            
            controller.logInfo("ORB initialized");
            
            rootPOA = POAHelper.narrow(orb.resolve_initial_references("RootPOA"));
            rootPOA.the_POAManager().activate();
            
            controller.logInfo("POA Manager activated");

            // Initialize shared resources
            initializeSharedResources();

            // Initialize services with shared resources
            initializeServices();

            // Register services with naming service
            registerServices();

            controller.logInfo("Server initialized and ready to start");
            
            // Start the ORB in a separate thread
            orbThread = new Thread(() -> {
                try {
                    controller.logInfo("ORB running and accepting connections");
                    orb.run();
                } catch (Exception e) {
                    controller.logError("ORB stopped: " + e.getMessage());
                }
            });
            
            orbThread.setDaemon(true);
            orbThread.start();
            
            controller.logSuccess("Server started successfully");
        } catch (Exception e) {
            controller.logError("Error starting server: " + e.getMessage());
            e.printStackTrace();
            throw new RuntimeException("Failed to start server", e);
        }
    }
    
    /**
     * Pauses the server by putting services in a state that rejects new connections
     * but maintains existing ones.
     */
    public void pauseServer() {
        try {
            controller.logInfo("Pausing server...");
            
            if (gameService != null) {
                gameService.setPaused(true);
            }
            
            if (adminService != null) {
                adminService.setPaused(true);
            }
            
            isPaused = true;
            controller.logSuccess("Server paused successfully - new connections will be rejected");
        } catch (Exception e) {
            controller.logError("Error pausing server: " + e.getMessage());
            throw new RuntimeException("Failed to pause server", e);
        }
    }
    
    /**
     * Resumes the server to accept new connections again after being paused.
     */
    public void resumeServer() {
        try {
            controller.logInfo("Resuming server...");
            
            if (gameService != null) {
                gameService.setPaused(false);
            }
            
            if (adminService != null) {
                adminService.setPaused(false);
            }
            
            isPaused = false;
            controller.logSuccess("Server resumed successfully - now accepting connections");
        } catch (Exception e) {
            controller.logError("Error resuming server: " + e.getMessage());
            throw new RuntimeException("Failed to resume server", e);
        }
    }
    
    private void initializeSharedResources() {
        try {
            controller.logInfo("Initializing word manager...");
            wordManager = new WordManager();
            
            controller.logInfo("Initializing player manager...");
            playerManager = new PlayerManager();
            
            controller.logInfo("Connecting to database at " + DB_URL);
            matchResultDAO = new MatchResultDAO(DB_URL, DB_USER, DB_PASSWORD);
            singlePlayerMatchResultDAO = new SinglePlayerMatchResultDAO(DB_URL, DB_USER, DB_PASSWORD);
            
            controller.logSuccess("All shared resources initialized successfully");
        } catch (Exception e) {
            controller.logError("Failed to initialize shared resources: " + e.getMessage());
            throw e;
        }
    }
    
    private void initializeServices() {
        try {
            controller.logInfo("Initializing game service...");
            gameService = new GameServiceImpl(
                wordManager,
                playerManager,
                matchResultDAO,
                singlePlayerMatchResultDAO
            );
            gameService.setLogCallback(controller::logInfo);
            
            controller.logInfo("Initializing admin service...");
            adminService = new AdminServiceImpl(
                wordManager, 
                playerManager, 
                matchResultDAO, 
                singlePlayerMatchResultDAO
            );
            adminService.setLogCallback(controller::logInfo);
            
            controller.logSuccess("Services initialized successfully");
        } catch (Exception e) {
            controller.logError("Failed to initialize services: " + e.getMessage());
            throw e;
        }
    }
    
    private void registerServices() {
        try {
            controller.logInfo("Connecting to naming service...");
            org.omg.CORBA.Object objRef = orb.resolve_initial_references("NameService");
            NamingContextExt ncRef = NamingContextExtHelper.narrow(objRef);

            // Register GameService
            controller.logInfo("Registering GameService...");
            org.omg.CORBA.Object gameRef = rootPOA.servant_to_reference(gameService);
            GameService gameHref = GameServiceHelper.narrow(gameRef);
            String gameName = "GameService";
            NameComponent[] gamePath = ncRef.to_name(gameName);
            ncRef.rebind(gamePath, gameHref);
            
            // Register AdminService
            controller.logInfo("Registering AdminService...");
            org.omg.CORBA.Object adminRef = rootPOA.servant_to_reference(adminService);
            AdminService adminHref = AdminServiceHelper.narrow(adminRef);
            String adminName = "AdminService";
            NameComponent[] adminPath = ncRef.to_name(adminName);
            ncRef.rebind(adminPath, adminHref);
            
            controller.logSuccess("All services registered successfully");
        } catch (org.omg.CORBA.ORBPackage.InvalidName e) {
            controller.logError("InvalidName exception: " + e.getMessage());
            throw new RuntimeException("Failed to register services", e);
        } catch (org.omg.PortableServer.POAPackage.ServantNotActive e) {
            controller.logError("ServantNotActive exception: " + e.getMessage());
            throw new RuntimeException("Failed to register services", e);
        } catch (org.omg.PortableServer.POAPackage.WrongPolicy e) {
            controller.logError("WrongPolicy exception: " + e.getMessage());
            throw new RuntimeException("Failed to register services", e);
        } catch (org.omg.CosNaming.NamingContextPackage.InvalidName e) {
            controller.logError("NamingContext InvalidName exception: " + e.getMessage());
            throw new RuntimeException("Failed to register services", e);
        } catch (org.omg.CosNaming.NamingContextPackage.NotFound e) {
            controller.logError("NotFound exception: " + e.getMessage());
            throw new RuntimeException("Failed to register services", e);
        } catch (org.omg.CosNaming.NamingContextPackage.CannotProceed e) {
            controller.logError("CannotProceed exception: " + e.getMessage());
            throw new RuntimeException("Failed to register services", e);
        } catch (Exception e) {
            controller.logError("Failed to register services: " + e.getMessage());
            throw new RuntimeException("Failed to register services", e);
        }
    }

    public void stopServer() {
        try {
            controller.logInfo("Shutting down server...");
            
            // Reset game and player stats before stopping
            if (gameService != null) {
                gameService.resetAllGames();
            }
            
            if (playerManager != null) {
                playerManager.logoutAllPlayers();
            }
            
            if (orb != null) {
                orb.shutdown(false); // false means don't wait
                
                // Wait for the ORB thread to terminate
                if (orbThread != null && orbThread.isAlive()) {
                    orbThread.interrupt();
                    orbThread.join(3000); // Wait up to 3 seconds
                }
            }
            controller.logSuccess("Server stopped successfully");
        } catch (Exception e) {
            controller.logError("Error stopping server: " + e.getMessage());
            e.printStackTrace();
            throw new RuntimeException("Failed to stop server", e);
        }
    }

    public GameServiceImpl getGameService() {
        return gameService;
    }
    
    public AdminServiceImpl getAdminService() {
        return adminService;
    }
    
    public boolean isPaused() {
        return isPaused;
    }

    @Override
    public void stop() {
        if (controller != null) {
            controller.logInfo("Application is shutting down...");
            controller.cleanup();
        }
        
        if (orb != null) {
            try {
                if (gameService != null) {
                    gameService.resetAllGames();
                }
                
                if (playerManager != null) {
                    playerManager.logoutAllPlayers();
                }
                
                orb.shutdown(true);
                System.out.println("Server shut down successfully");
            } catch (Exception e) {
                System.err.println("Error shutting down server: " + e.getMessage());
            }
        }
    }

    public static void main(String[] args) {
        launch(args);
    }
} 