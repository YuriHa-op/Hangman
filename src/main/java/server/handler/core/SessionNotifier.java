package server.handler.core;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Consumer;

/**
 * Handles notifications for session events such as forced logouts
 */
public class SessionNotifier {
    // Singleton instance
    private static SessionNotifier instance;
    
    // Map of username to session invalidation callbacks
    private final Map<String, Consumer<String>> sessionInvalidationCallbacks = new ConcurrentHashMap<>();
    
    private SessionNotifier() {
        // Private constructor for singleton
    }
    
    public static synchronized SessionNotifier getInstance() {
        if (instance == null) {
            instance = new SessionNotifier();
        }
        return instance;
    }
    
    /**
     * Register a callback for a user's session
     * @param username The username
     * @param callback The callback to invoke when session is invalidated
     * @return true if registration was successful
     */
    public boolean registerSessionCallback(String username, Consumer<String> callback) {
        if (username == null || callback == null) {
            return false;
        }
        sessionInvalidationCallbacks.put(username, callback);
        System.out.println("Registered session callback for: " + username);
        return true;
    }
    
    /**
     * Unregister a callback for a user's session
     * @param username The username
     * @return true if unregistration was successful
     */
    public boolean unregisterSessionCallback(String username) {
        if (username == null) {
            return false;
        }
        Consumer<String> removed = sessionInvalidationCallbacks.remove(username);
        if (removed != null) {
            System.out.println("Unregistered session callback for: " + username);
            return true;
        }
        return false;
    }
    
    /**
     * Notify a user that their session has been invalidated
     * @param username The username
     * @param reason The reason for invalidation
     * @return true if notification was sent
     */
    public boolean notifySessionInvalidated(String username, String reason) {
        if (username == null) {
            return false;
        }
        
        Consumer<String> callback = sessionInvalidationCallbacks.get(username);
        if (callback != null) {
            try {
                System.out.println("Notifying session invalidation for: " + username + " Reason: " + reason);
                callback.accept(reason);
                return true;
            } catch (Exception e) {
                System.err.println("Error notifying session invalidation for " + username + ": " + e.getMessage());
            }
        }
        return false;
    }
    
    /**
     * Check if a session callback is registered for a user
     * @param username The username
     * @return true if a callback is registered
     */
    public boolean hasSessionCallback(String username) {
        return username != null && sessionInvalidationCallbacks.containsKey(username);
    }
    
    /**
     * Clear all registered callbacks
     */
    public void clearAllCallbacks() {
        sessionInvalidationCallbacks.clear();
        System.out.println("Cleared all session callbacks");
    }
} 