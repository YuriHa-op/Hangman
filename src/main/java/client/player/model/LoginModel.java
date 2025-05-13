package client.player.model;

import GameModule.GameService;
import GameModule.GameServiceHelper;
import org.omg.CORBA.ORB;

public class LoginModel {
    private GameService gameService;

    public LoginModel() {
        this("localhost", "900");
    }

    public LoginModel(String host, String port) {
        try {
            // Define proper initialization parameters
            String[] args = {"-ORBInitialHost", host, "-ORBInitialPort", port};
            ORB orb = ORB.init(args, null);

            // Get the naming context - use the correct helper class
            org.omg.CORBA.Object objRef = orb.resolve_initial_references("NameService");
            org.omg.CosNaming.NamingContextExt ncRef = org.omg.CosNaming.NamingContextExtHelper.narrow(objRef);

            // Resolve the game service
            org.omg.CosNaming.NameComponent path[] = ncRef.to_name("GameService");
            org.omg.CORBA.Object obj = ncRef.resolve(path);

            gameService = GameServiceHelper.narrow(obj);
            System.out.println("Successfully connected to GameService");
        } catch (Exception e) {
            System.err.println("Error connecting to the server: " + e.getMessage());
            e.printStackTrace();
        }
    }

    public GameService getGameService() {
        return gameService;
    }

    public boolean login(String username, String password) throws GameModule.AlreadyLoggedInException {
        try {
            return gameService.login(username, password); // Send plain password
        } catch (GameModule.AlreadyLoggedInException e) {
            throw e;
        } catch (Exception e) {
            System.err.println("Error during login: " + e.getMessage());
            throw e;
        }
    }
}