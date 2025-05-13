package client.admin.view;

import GameModule.GameService;
import GameModule.GameServiceHelper;
import client.admin.view.AdminView;
import javafx.application.Application;
import javafx.application.Platform;
import javafx.scene.control.Alert;
import javafx.scene.control.TextInputDialog;
import javafx.stage.Stage;
import org.omg.CORBA.ORB;
import org.omg.CosNaming.NamingContextExt;
import org.omg.CosNaming.NamingContextExtHelper;

import java.util.Optional;
import java.util.Properties;

public class AdminApplication extends Application {
    private ORB orb;
    private GameService gameService;
    private Stage primaryStage;
    private AdminView adminView;

    @Override
    public void start(Stage primaryStage) {
        this.primaryStage = primaryStage;
        primaryStage.setTitle("What's The Word - Admin");

        // Initialize CORBA connection
        initializeConnection();

        // Show login dialog
        showLoginDialog();
    }

    private void initializeConnection() {
        try {
            // Initialize ORB
            Properties props = new Properties();
<<<<<<< HEAD
            props.put("org.omg.CORBA.ORBInitialHost", "localhost");
=======
            props.put("org.omg.CORBA.ORBInitialHost", "192.168.254.125");
>>>>>>> main
            props.put("org.omg.CORBA.ORBInitialPort", "900");

            String[] args = {};
            orb = ORB.init(args, props);

            // Get reference to naming service
            org.omg.CORBA.Object objRef = orb.resolve_initial_references("NameService");
            NamingContextExt ncRef = NamingContextExtHelper.narrow(objRef);

            // Get reference to GameService
            String name = "GameService";
            gameService = GameServiceHelper.narrow(ncRef.resolve_str(name));

            System.out.println("Connected to GameService");
        } catch (Exception e) {
            showError("Connection Error", "Failed to connect to the game server: " + e.getMessage());
            Platform.exit();
        }
    }

    private void showLoginDialog() {
        TextInputDialog usernameDialog = new TextInputDialog();
        usernameDialog.setTitle("Admin Login");
        usernameDialog.setHeaderText("Please enter admin credentials");
        usernameDialog.setContentText("Username:");

        Optional<String> usernameResult = usernameDialog.showAndWait();
        if (usernameResult.isPresent()) {
            String username = usernameResult.get();

            TextInputDialog passwordDialog = new TextInputDialog();
            passwordDialog.setTitle("Admin Login");
            passwordDialog.setHeaderText("Enter password");
            passwordDialog.setContentText("Password:");

            Optional<String> passwordResult = passwordDialog.showAndWait();
            if (passwordResult.isPresent()) {
                String password = passwordResult.get();

                // Here we would normally verify admin credentials
                // For this, we'll just proceed to the admin view
                showAdminView();
            } else {
                Platform.exit();
            }
        } else {
            Platform.exit();
        }
    }

    private void showAdminView() {
        adminView = new AdminView();
        adminView.start(primaryStage, gameService, this::handleLogout);
        adminView.show();
    }

    private void handleLogout() {
        Platform.exit();
    }

    private void showError(String title, String message) {
        Alert alert = new Alert(Alert.AlertType.ERROR);
        alert.setTitle(title);
        alert.setHeaderText(null);
        alert.setContentText(message);
        alert.showAndWait();
    }

    @Override
    public void stop() {
        if (orb != null) {
            orb.shutdown(true);
        }
    }

    public static void main(String[] args) {
        launch(args);
    }
}