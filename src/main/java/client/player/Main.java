package client.player;

import client.player.model.LoginModel;
import client.player.view.LoginView;
import javafx.application.Application;
import javafx.stage.Stage;

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

     // Create model and view
     loginModel = new LoginModel(host, port);
     loginView = new LoginView();
     loginView.start(primaryStage);
     loginView.setModel(loginModel);

     loginView.setShowLoginViewAgain(() -> {
         javafx.application.Platform.runLater(() -> {
             loginView.getStage().show();
         });
     });

     loginView.setVisible(true);
 }

    public static void main(String[] args) {
        launch(args);
    }
} 