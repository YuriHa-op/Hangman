package server.handler;

import GameModule.GameService;
import GameModule.GameServiceHelper;
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

public class ServerMain extends Application {
    private ORB orb;
    private POA rootPOA;
    private GameServiceImpl gameService;
    private ServerMainController controller;

    @Override
    public void start(Stage primaryStage) throws Exception {
        FXMLLoader loader = new FXMLLoader(getClass().getResource("/server/view/ServerMainView.fxml"));
        Parent root = loader.load();
        controller = loader.getController();
        controller.setServerMain(this);
        
        Scene scene = new Scene(root);
        scene.getStylesheets().add(getClass().getResource("/server/view/ServerMainView.css").toExternalForm());
        
        primaryStage.setTitle("Hanger Man At Your Service");
        primaryStage.setScene(scene);
        primaryStage.getIcons().add(
                new Image(getClass().getResourceAsStream("/server/view/icon.png"))
        );
        primaryStage.setMinWidth(800);
        primaryStage.setMinHeight(600);
        primaryStage.show();
    }

    public void startServer() {
        try {
            String[] args = new String[0];
            orb = ORB.init(args, null);
            rootPOA = POAHelper.narrow(orb.resolve_initial_references("RootPOA"));
            rootPOA.the_POAManager().activate();

            gameService = new GameServiceImpl();
            gameService.setLogCallback(controller::logMessage);

            org.omg.CORBA.Object ref = rootPOA.servant_to_reference(gameService);
            GameService href = GameServiceHelper.narrow(ref);

            org.omg.CORBA.Object objRef = orb.resolve_initial_references("NameService");
            NamingContextExt ncRef = NamingContextExtHelper.narrow(objRef);

            String name = "GameService";
            NameComponent path[] = ncRef.to_name(name);
            ncRef.rebind(path, href);

            controller.logMessage("Server initialized and ready to start");
            new Thread(() -> {
                try {
                    orb.run();
                    controller.logMessage("Server started successfully");
                } catch (Exception e) {
                    controller.logMessage("ORB stopped: " + e.getMessage());
                }
            }).start();
        } catch (Exception e) {
            controller.logMessage("Error starting server: " + e.getMessage());
            throw new RuntimeException("Failed to start server", e);
        }
    }

    public void stopServer() {
        try {
            orb.shutdown(true);
            controller.logMessage("Server stopped successfully");
        } catch (Exception e) {
            controller.logMessage("Error stopping server: " + e.getMessage());
            throw new RuntimeException("Failed to stop server", e);
        }
    }

    public GameServiceImpl getGameService() {
        return gameService;
    }

    @Override
    public void stop() {
        if (controller != null) {
            controller.cleanup();
        }
        if (orb != null) {
            orb.shutdown(true);
        }
    }

    public static void main(String[] args) {
        launch(args);
    }
} 