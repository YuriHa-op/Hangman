package server.handler.core;

import java.sql.*;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import LoginModule.Bool;
import LoginModule.AlreadyLoggedInException;

public class LoginManager {
    private static final String DB_URL = "jdbc:mysql://localhost:3306/game";
    private static final String DB_USER = "root";
    private static final String DB_PASSWORD = "";
    
    // In-memory store of active sessions
    private final Map<String, String> activeSessions = new ConcurrentHashMap<>(); // username -> sessionId
    
    // Session notifier for invalidating sessions
    private final SessionNotifier sessionNotifier = SessionNotifier.getInstance();
    
    private Connection getConnection() throws SQLException {
        return DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
    }
    
    /**
     * Check if the session_id column exists in the players table
     */
    private boolean hasSessionIdColumn() {
        try (Connection conn = getConnection()) {
            DatabaseMetaData meta = conn.getMetaData();
            ResultSet rs = meta.getColumns(null, null, "players", "session_id");
            return rs.next(); // Column exists if there's a result
        } catch (SQLException e) {
            System.err.println("Error checking for session_id column: " + e.getMessage());
            return false;
        }
    }
    
    /**
     * Add the session_id column if it doesn't exist
     */
    private void ensureSessionIdColumn() {
        if (!hasSessionIdColumn()) {
            try (Connection conn = getConnection(); 
                 Statement stmt = conn.createStatement()) {
                
                System.out.println("Adding session_id column to players table...");
                stmt.executeUpdate("ALTER TABLE players ADD COLUMN session_id VARCHAR(255) DEFAULT NULL");
                
                // Reset any existing sessions
                stmt.executeUpdate("UPDATE players SET session_id = NULL WHERE currently_logged_in = 1");
                System.out.println("Session ID column added successfully");
            } catch (SQLException e) {
                System.err.println("Error adding session_id column: " + e.getMessage());
            }
        }
    }
    
    public Bool login(String username, String password) throws AlreadyLoggedInException {
        Connection conn = null;
        PreparedStatement ps = null;
        ResultSet rs = null;
        
        try {
            // Ensure session_id column exists
            ensureSessionIdColumn();
            
            conn = getConnection();
            
            // Check if credentials are valid
            ps = conn.prepareStatement("SELECT * FROM players WHERE username = ? AND password = ?");
            ps.setString(1, username);
            ps.setString(2, password);
            rs = ps.executeQuery();
            
            if (!rs.next()) {
                // Invalid credentials
                return Bool.BOOL_FALSE;
            }
            
            // Valid credentials - check current login status
            boolean isLoggedIn = rs.getBoolean("currently_logged_in");
            String currentSessionId = rs.getString("session_id");
            
            // If user is already logged in, throw exception
            if (isLoggedIn && currentSessionId != null && !currentSessionId.isEmpty()) {
                // For backward compatibility with existing clients, throw the exception
                // New clients can catch this and show the force login dialog
                throw new AlreadyLoggedInException("User already logged in");
            }
            
            // Generate new session ID
            String newSessionId = UUID.randomUUID().toString();
            
            // Update database with new session
            try (PreparedStatement updatePs = conn.prepareStatement(
                    "UPDATE players SET currently_logged_in = 1, session_id = ? WHERE username = ?")) {
                updatePs.setString(1, newSessionId);
                updatePs.setString(2, username);
                updatePs.executeUpdate();
            }
            
            // Store session in memory
            activeSessions.put(username, newSessionId);
            
            System.out.println("User " + username + " logged in with session ID: " + newSessionId);
            return Bool.BOOL_TRUE;
            
        } catch (SQLException e) {
            e.printStackTrace();
            return Bool.BOOL_FALSE;
        } finally {
            try { if (rs != null) rs.close(); } catch (Exception ignored) {}
            try { if (ps != null) ps.close(); } catch (Exception ignored) {}
            try { if (conn != null) conn.close(); } catch (Exception ignored) {}
        }
    }
    
    /**
     * Force login even if user is already logged in
     */
    public String forceLogin(String username, String password) {
        Connection conn = null;
        PreparedStatement ps = null;
        ResultSet rs = null;
        
        try {
            // Ensure session_id column exists
            ensureSessionIdColumn();
            
            conn = getConnection();
            
            // Check if credentials are valid
            ps = conn.prepareStatement("SELECT * FROM players WHERE username = ? AND password = ?");
            ps.setString(1, username);
            ps.setString(2, password);
            rs = ps.executeQuery();
            
            if (!rs.next()) {
                // Invalid credentials
                return null;
            }
            
            // Check if user is already logged in
            boolean isLoggedIn = rs.getBoolean("currently_logged_in");
            String oldSessionId = rs.getString("session_id");
            
            // Generate new session ID
            String newSessionId = UUID.randomUUID().toString();
            
            // Update database with new session, forcibly invalidating any existing session
            try (PreparedStatement updatePs = conn.prepareStatement(
                    "UPDATE players SET currently_logged_in = 1, session_id = ? WHERE username = ?")) {
                updatePs.setString(1, newSessionId);
                updatePs.setString(2, username);
                updatePs.executeUpdate();
            }
            
            // If user was already logged in, notify the previous session
            if (isLoggedIn && oldSessionId != null && !oldSessionId.isEmpty()) {
                // Notify the previous session that it's been invalidated
                sessionNotifier.notifySessionInvalidated(username, 
                    "Your account has been logged in from another location.");
                
                System.out.println("Invalidated previous session for user " + username + 
                    " (Old session: " + oldSessionId + ", New session: " + newSessionId + ")");
            }
            
            // Store session in memory, replacing any old one
            activeSessions.put(username, newSessionId);
            
            System.out.println("User " + username + " forced login with session ID: " + newSessionId);
            return newSessionId;
            
        } catch (SQLException e) {
            e.printStackTrace();
            return null;
        } finally {
            try { if (rs != null) rs.close(); } catch (Exception ignored) {}
            try { if (ps != null) ps.close(); } catch (Exception ignored) {}
            try { if (conn != null) conn.close(); } catch (Exception ignored) {}
        }
    }
    
    public void logout(String username) {
        try (Connection conn = getConnection();
             PreparedStatement ps = conn.prepareStatement(
                     "UPDATE players SET currently_logged_in = 0, session_id = NULL WHERE username = ?")) {
            ps.setString(1, username);
            ps.executeUpdate();
            
            // Remove from active sessions
            activeSessions.remove(username);
            
            // Unregister any session callback
            sessionNotifier.unregisterSessionCallback(username);
            
            System.out.println("User " + username + " logged out successfully");
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
    
    /**
     * Validates if a session is active and valid
     * @param username The username
     * @param sessionId The session ID to validate
     * @return true if session is valid, false otherwise
     */
    public boolean validateSession(String username, String sessionId) {
        if (username == null || sessionId == null || sessionId.isEmpty()) {
            return false;
        }
        
        try (Connection conn = getConnection();
             PreparedStatement ps = conn.prepareStatement(
                     "SELECT session_id FROM players WHERE username = ? AND currently_logged_in = 1")) {
            ps.setString(1, username);
            ResultSet rs = ps.executeQuery();
            
            if (rs.next()) {
                String dbSessionId = rs.getString("session_id");
                boolean isValid = sessionId.equals(dbSessionId);
                
                // Update in-memory cache if needed
                if (isValid) {
                    String cachedSessionId = activeSessions.get(username);
                    if (cachedSessionId == null || !cachedSessionId.equals(sessionId)) {
                        activeSessions.put(username, sessionId);
                    }
                } else {
                    // Session is invalid - notify the client
                    sessionNotifier.notifySessionInvalidated(username, "Your session is no longer valid.");
                }
                
                return isValid;
            }
            return false;
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
    }
    
    /**
     * Gets the current session ID for a user
     * @param username The username
     * @return The current session ID, or null if no active session
     */
    public String getSessionId(String username) {
        if (username == null) {
            return null;
        }
        
        // Try to get from cache first
        String cachedSessionId = activeSessions.get(username);
        if (cachedSessionId != null) {
            return cachedSessionId;
        }
        
        // Not in cache, check database
        try (Connection conn = getConnection();
             PreparedStatement ps = conn.prepareStatement(
                     "SELECT session_id FROM players WHERE username = ? AND currently_logged_in = 1")) {
            ps.setString(1, username);
            ResultSet rs = ps.executeQuery();
            
            if (rs.next()) {
                String dbSessionId = rs.getString("session_id");
                if (dbSessionId != null && !dbSessionId.isEmpty()) {
                    // Update cache
                    activeSessions.put(username, dbSessionId);
                    return dbSessionId;
                }
            }
            return null;
        } catch (SQLException e) {
            e.printStackTrace();
            return null;
        }
    }
    
    /**
     * Register a callback for session invalidation
     * @param username The username
     * @param callback The callback to invoke when session is invalidated
     * @return true if registration was successful
     */
    public boolean registerSessionCallback(String username, java.util.function.Consumer<String> callback) {
        return sessionNotifier.registerSessionCallback(username, callback);
    }
    
    /**
     * Logs out all currently logged in players.
     * Used during server shutdown or restart.
     */
    public void logoutAllPlayers() {
        try (Connection conn = getConnection();
             PreparedStatement ps = conn.prepareStatement(
                     "UPDATE players SET currently_logged_in = 0, session_id = NULL WHERE currently_logged_in = 1")) {
            int count = ps.executeUpdate();
            System.out.println("Logged out " + count + " active players");
            
            // Clear active sessions map
            activeSessions.clear();
            
            // Clear all session callbacks
            sessionNotifier.clearAllCallbacks();
        } catch (SQLException e) {
            System.err.println("Database error logging out all players: " + e.getMessage());
            e.printStackTrace();
        }
    }
} 