package client.player.session;

/**
 * Singleton class to manage player session data
 */
public class PlayerSession {
    private static PlayerSession instance;
    private String username;

    private PlayerSession() {
        // Private constructor to prevent external instantiation
    }

    public static synchronized PlayerSession getInstance() {
        if (instance == null) {
            instance = new PlayerSession();
        }
        return instance;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public void clearSession() {
        username = null;
    }
}