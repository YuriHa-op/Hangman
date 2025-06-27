package client.player;

import client.player.model.LoginModel;
import client.player.view.LoginView;
import javafx.application.Application;
import javafx.stage.Stage;
import org.omg.CORBA.ORB;

public class Main extends Application {
    private LoginView loginView;
    private LoginModel loginModel;

    @Override
    public void start(Stage primaryStage) {
        // Default CORBA params
        String host = "localhost";
        String port = "900";

        // Parse command line args
        Parameters params = getParameters();
        for (String param : params.getRaw()) {
            if (param.startsWith("-ORBInitialHost")) {
                String[] split = param.split(" ");
                if (split.length > 1) host = split[1];
            } else if (param.startsWith("-ORBInitialPort")) {
                String[] split = param.split(" ");
                if (split.length > 1) port = split[1];
            }
        }

        try {
            // Initialize the ORB here
            String[] orbArgs = {"-ORBInitialHost", host, "-ORBInitialPort", port};
            ORB orb = ORB.init(orbArgs, null);

            // Create model and view with initialized ORB
            loginModel = new LoginModel(orb);
            loginView = new LoginView();
            loginView.start(primaryStage);
            loginView.setModel(loginModel);

            loginView.setShowLoginViewAgain(() -> {
                javafx.application.Platform.runLater(() -> {
                    loginView.getStage().show();
                });
            });

            loginView.setVisible(true);
        } catch (Exception e) {
            System.err.println("Error initializing ORB: " + e.getMessage());
            e.printStackTrace();
        }
    }

    public static void main(String[] args) {
        launch(args);
    }
} 