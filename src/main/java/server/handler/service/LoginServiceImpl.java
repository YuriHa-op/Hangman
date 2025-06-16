package server.handler.service;

import LoginModule.AlreadyLoggedInException;
import LoginModule.Bool;
import LoginModule.LoginResponse;
import LoginModule.LoginServicePOA;
import server.handler.core.LoginManager;

import java.util.function.Consumer;

public class LoginServiceImpl extends LoginServicePOA {
    private final LoginManager loginManager;
    private Consumer<String> logCallback;

    public LoginServiceImpl(LoginManager loginManager) {
        this.loginManager = loginManager;
    }

    public void setLogCallback(Consumer<String> callback) {
        this.logCallback = callback;
    }

    @Override
    public LoginResponse loginWithSession(String username, String password) throws AlreadyLoggedInException {
        LoginResponse response = new LoginResponse();
        
        try {
            Bool loginResult = loginManager.login(username, password);
            response.success = loginResult;
            
            if (loginResult == Bool.BOOL_TRUE) {
                String sessionId = loginManager.getSessionId(username);
                response.sessionId = sessionId != null ? sessionId : "";
                if (logCallback != null) {
                    logCallback.accept("User " + username + " logged in successfully with session ID: " + sessionId);
                }
            } else {
                response.sessionId = "";
            }
        } catch (AlreadyLoggedInException e) {
            if (logCallback != null) {
                logCallback.accept("User " + username + " is already logged in. Attempting forced login.");
            }
            
            String sessionId = loginManager.forceLogin(username, password);
            
            if (sessionId != null) {
                response.success = Bool.BOOL_TRUE;
                response.sessionId = sessionId;
                if (logCallback != null) {
                    logCallback.accept("User " + username + " forced login with new session ID: " + sessionId);
                }
            } else {
                response.success = Bool.BOOL_FALSE;
                response.sessionId = "";
                throw e;
            }
        }
        
        return response;
    }

    @Override
    public Bool login(String username, String password) throws AlreadyLoggedInException {
        Bool result = loginManager.login(username, password);
        if (result == Bool.BOOL_TRUE) {
            if (logCallback != null) {
                logCallback.accept("User " + username + " logged in successfully.");
            }
        }
        return result;
    }

    @Override
    public void logout(String username) {
        loginManager.logout(username);
        if (logCallback != null) {
            logCallback.accept("User " + username + " logged out.");
        }
    }

    @Override
    public Bool createPlayer(String username, String password) {
        // Since createPlayer is not in LoginManager, we can call it from a new PlayerManager instance
        return new server.handler.core.PlayerManager().createPlayer(username, password);
    }

    @Override
    public Bool validateSession(String username, String sessionId) {
        return loginManager.validateSession(username, sessionId) ? Bool.BOOL_TRUE : Bool.BOOL_FALSE;
    }

    @Override
    public Bool checkSessionValid(String username) {
        if (username == null) {
            return Bool.BOOL_FALSE;
        }
        String sessionId = loginManager.getSessionId(username);
        if (sessionId == null) {
            if (logCallback != null) {
                logCallback.accept("Session validation failed for " + username + ": No active session found");
            }
            return Bool.BOOL_FALSE;
        }
        boolean isValid = loginManager.validateSession(username, sessionId);
        if (!isValid) {
            if (logCallback != null) {
                logCallback.accept("Session validation failed for " + username + ": Session is invalid");
            }
        }
        return isValid ? Bool.BOOL_TRUE : Bool.BOOL_FALSE;
    }

    @Override
    public Bool keepAlive(String username, String sessionId) {
        if (username == null || sessionId == null || sessionId.isEmpty()) {
            return Bool.BOOL_FALSE;
        }
        Bool isValid = validateSession(username, sessionId);
        if (isValid == Bool.BOOL_TRUE) {
            if (logCallback != null && Math.random() < 0.05) { // Only log 5% of keepalives to avoid spam
                logCallback.accept("Keep-alive for user " + username);
            }
        } else {
            if (logCallback != null) {
                logCallback.accept("Keep-alive failed for user " + username + ": Invalid session");
            }
        }
        return isValid;
    }
} 