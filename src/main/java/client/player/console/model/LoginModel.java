package client.player.console.model;

import GameModule.GameService;
import GameModule.GameServiceHelper;
import LoginModule.Bool;
import LoginModule.LoginResponse;
import LoginModule.AlreadyLoggedInException;
import LoginModule.LoginService;
import LoginModule.LoginServiceHelper;
import org.omg.CORBA.ORB;

public class LoginModel {
    private GameService gameService;
    private LoginService loginService;
    private String sessionId;  // Store the session ID for the logged-in user
    private String loggedInUser;  // Store the currently logged-in username
    
    // Singleton instance
    private static LoginModel instance;

    public LoginModel(ORB orb) {
        try {
            // Get the naming context - use the correct helper class
            org.omg.CORBA.Object objRef = orb.resolve_initial_references("NameService");
            org.omg.CosNaming.NamingContextExt ncRef = org.omg.CosNaming.NamingContextExtHelper.narrow(objRef);

            // Resolve the game service
            org.omg.CosNaming.NameComponent gamePath[] = ncRef.to_name("GameService");
            org.omg.CORBA.Object gameObj = ncRef.resolve(gamePath);
            gameService = GameServiceHelper.narrow(gameObj);
            System.out.println("Successfully connected to GameService");

            // Resolve the login service
            org.omg.CosNaming.NameComponent loginPath[] = ncRef.to_name("LoginService");
            org.omg.CORBA.Object loginObj = ncRef.resolve(loginPath);
            loginService = LoginServiceHelper.narrow(loginObj);
            System.out.println("Successfully connected to LoginService");
            
            // Store the singleton instance
            instance = this;
        } catch (Exception e) {
            System.err.println("Error connecting to the server: " + e.getMessage());
            e.printStackTrace();
        }
    }

    // Get the singleton instance
    public static LoginModel getInstance() {
        return instance;
    }

    public GameService getGameService() {
        return gameService;
    }

    public LoginService getLoginService() {
        return loginService;
    }
    
    public String getSessionId() {
        return sessionId;
    }
    
    public String getLoggedInUser() {
        return loggedInUser;
    }

    public Bool login(String username, String password) throws AlreadyLoggedInException {
        try {
            // Try to use the new loginWithSession method if available
            try {
                LoginResponse response = loginService.loginWithSession(username, password);
                if (response.success == Bool.BOOL_TRUE) {
                    this.loggedInUser = username;
                    this.sessionId = response.sessionId;
                }
                return response.success;
            } catch (org.omg.CORBA.BAD_OPERATION e) {
                // If the method doesn't exist, fall back to the old method
                System.out.println("Server doesn't support session-based login, using regular login");
                Bool result = loginService.login(username, password);
                if (result == Bool.BOOL_TRUE) {
                    this.loggedInUser = username;
                }
                return result;
            }
        } catch (AlreadyLoggedInException e) {
            throw e;
        } catch (Exception e) {
            System.err.println("Error during login: " + e.getMessage());
            throw e;
        }
    }
    
    public void logout() {
        if (loggedInUser != null) {
            try {
                loginService.logout(loggedInUser);
                this.loggedInUser = null;
                this.sessionId = null;
            } catch (Exception e) {
                System.err.println("Error during logout: " + e.getMessage());
            }
        }
    }

    public Bool createPlayer(String username, String password) {
        try {
            return loginService.createPlayer(username, password);
        } catch (Exception e) {
            System.err.println("Error during player creation: " + e.getMessage());
            throw e;
        }
    }

    // Force login method for when account is already logged in elsewhere
    public Bool forceLogin(String username, String password) {
        try {
            // Try to use loginWithSession again to force a new session
            LoginResponse response = loginService.loginWithSession(username, password);
            if (response.success == Bool.BOOL_TRUE) {
                this.loggedInUser = username;
                this.sessionId = response.sessionId;
            }
            return response.success;
        } catch (Exception e) {
            System.err.println("Error during force login: " + e.getMessage());
            return Bool.BOOL_FALSE;
        }
    }

    // Validate the current session (returns true if valid, false if invalid)
    public boolean validateSession() {
        if (loggedInUser == null || sessionId == null) return false;
        try {
            // Try validateSession(username, sessionId) if available
            try {
                return loginService.validateSession(loggedInUser, sessionId) == Bool.BOOL_TRUE;
            } catch (org.omg.CORBA.BAD_OPERATION e) {
                // Fallback to checkSessionValid(username)
                return loginService.checkSessionValid(loggedInUser) == Bool.BOOL_TRUE;
            }
        } catch (Exception e) {
            System.err.println("Session validation error: " + e.getMessage());
            return false;
        }
    }
}