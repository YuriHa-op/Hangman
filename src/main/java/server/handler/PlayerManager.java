package server.handler;

import java.sql.*;
import client.admin.model.SystemStatisticsDTO;
import client.admin.model.LeaderboardEntryDTO;
import java.util.ArrayList;
import java.util.List;

public class PlayerManager {
    private static final String DB_URL = "jdbc:mysql://localhost:3306/game";
    private static final String DB_USER = "root";
    private static final String DB_PASSWORD = "";

    private Connection getConnection() throws SQLException {
        return DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
    }

    public boolean login(String username, String password) throws GameModule.AlreadyLoggedInException {
        Connection conn = null;
        PreparedStatement ps = null;
        ResultSet rs = null;
        try {
            conn = getConnection();
            ps = conn.prepareStatement("SELECT * FROM players WHERE username = ? AND password = ?");
            ps.setString(1, username);
            ps.setString(2, password);
            rs = ps.executeQuery();
            if (rs.next()) {
                if (rs.getBoolean("currently_logged_in")) {
                    throw new GameModule.AlreadyLoggedInException("User already logged in");
                }
                try (PreparedStatement updatePs = conn.prepareStatement(
                        "UPDATE players SET currently_logged_in = 1 WHERE username = ?")) {
                    updatePs.setString(1, username);
                    updatePs.executeUpdate();
                }
                return true;
            }
            return false;
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        } finally {
            try { if (rs != null) rs.close(); } catch (Exception ignored) {}
            try { if (ps != null) ps.close(); } catch (Exception ignored) {}
            try { if (conn != null) conn.close(); } catch (Exception ignored) {}
        }
    }

    public void logout(String username) {
        try (Connection conn = getConnection();
             PreparedStatement ps = conn.prepareStatement(
                     "UPDATE players SET currently_logged_in = 0 WHERE username = ?")) {
            ps.setString(1, username);
            ps.executeUpdate();
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    public boolean createPlayer(String username, String password) {
        try (Connection conn = getConnection();
             PreparedStatement ps = conn.prepareStatement(
                     "INSERT INTO players (username, password) VALUES (?, ?)")) {
            ps.setString(1, username);
            ps.setString(2, password);
            ps.executeUpdate();
            return true;
        } catch (SQLException e) {
            System.err.println("Database error creating player: " + e.getMessage());
            return false;
        }
    }

    public boolean deletePlayer(String username) {
        try (Connection conn = getConnection();
             PreparedStatement ps = conn.prepareStatement(
                     "DELETE FROM players WHERE TRIM(LOWER(username)) = ?")) {
            ps.setString(1, username.trim().toLowerCase());
            int rowsAffected = ps.executeUpdate();
            return rowsAffected > 0;
        } catch (SQLException e) {
            System.err.println("Database error deleting player: " + e.getMessage());
            return false;
        }
    }

    public String viewPlayers() {
        StringBuilder playersList = new StringBuilder("ALL PLAYERS:\n");
        try (Connection conn = getConnection();
             Statement stmt = conn.createStatement()) {
            ResultSet rs = stmt.executeQuery(
                    "SELECT id, username, wins, currently_logged_in, role FROM players ORDER BY username ASC");
            while (rs.next()) {
                playersList.append("ID: ").append(rs.getInt("id"))
                        .append(" | Username: ").append(rs.getString("username"))
                        .append(" | Wins: ").append(rs.getInt("wins"))
                        .append(" | Status: ").append(rs.getBoolean("currently_logged_in") ? "Online" : "Offline")
                        .append(" | Role: ").append(rs.getString("role"))
                        .append("\n");
            }
        } catch (SQLException e) {
            System.err.println("Database error retrieving players: " + e.getMessage());
            return "Error retrieving players list.";
        }
        return playersList.toString();
    }

    public boolean updatePlayerPassword(String username, String newPassword) {
        try (Connection conn = getConnection();
             PreparedStatement ps = conn.prepareStatement(
                     "UPDATE players SET password = ? WHERE username = ?")) {
            ps.setString(1, newPassword);
            ps.setString(2, username);
            int rowsAffected = ps.executeUpdate();
            return rowsAffected > 0;
        } catch (SQLException e) {
            System.err.println("Database error updating password: " + e.getMessage());
            return false;
        }
    }

    public boolean updatePlayerUsername(String username, String newUsername) {
        try (Connection conn = getConnection()) {
            PreparedStatement checkPs = conn.prepareStatement(
                    "SELECT * FROM players WHERE TRIM(LOWER(username)) = ?");
            checkPs.setString(1, username.trim().toLowerCase());
            ResultSet rs = checkPs.executeQuery();
            if (!rs.next()) {
                return false;
            }
            checkPs = conn.prepareStatement(
                    "SELECT * FROM players WHERE TRIM(LOWER(username)) = ?");
            checkPs.setString(1, newUsername.trim().toLowerCase());
            rs = checkPs.executeQuery();
            if (rs.next()) {
                return false;
            }
            PreparedStatement ps = conn.prepareStatement(
                    "UPDATE players SET username = ? WHERE TRIM(LOWER(username)) = ?");
            ps.setString(1, newUsername.trim());
            ps.setString(2, username.trim().toLowerCase());
            int rowsAffected = ps.executeUpdate();
            return rowsAffected > 0;
        } catch (SQLException e) {
            System.err.println("Database error updating username: " + e.getMessage());
            return false;
        }
    }

    public boolean updatePlayerWins(String username, int wins) {
        try (Connection conn = getConnection();
             PreparedStatement ps = conn.prepareStatement(
                     "UPDATE players SET wins = ? WHERE username = ?")) {
            ps.setInt(1, wins);
            ps.setString(2, username);
            int rowsAffected = ps.executeUpdate();
            return rowsAffected > 0;
        } catch (SQLException e) {
            System.err.println("Database error updating wins: " + e.getMessage());
            return false;
        }
    }

    public int getTotalWins(String username) {
        try (Connection conn = getConnection();
             PreparedStatement ps = conn.prepareStatement(
                     "SELECT wins FROM players WHERE username = ?")) {
            ps.setString(1, username);
            ResultSet rs = ps.executeQuery();
            if (rs.next()) {
                return rs.getInt("wins");
            }
        } catch (SQLException e) {
            System.err.println("Database error getting total wins: " + e.getMessage());
        }
        return 0;
    }

    public int getRoundTime() {
        int roundTime = 0;
        try (Connection conn = getConnection();
             PreparedStatement stmt = conn.prepareStatement("SELECT round_time_seconds FROM settings WHERE id = 1")) {
            ResultSet rs = stmt.executeQuery();
            if (rs.next()) {
                roundTime = rs.getInt("round_time_seconds");
            }
        } catch (SQLException e) {
            System.err.println("Error getting round time: " + e.getMessage());
        }
        return roundTime;
    }

    public int getWaitingTime() {
        int waitingTime = 10;
        try (Connection conn = getConnection();
             PreparedStatement stmt = conn.prepareStatement("SELECT waiting_time_seconds FROM settings WHERE id = 1")) {
            ResultSet rs = stmt.executeQuery();
            if (rs.next()) {
                waitingTime = rs.getInt("waiting_time_seconds");
            }
        } catch (SQLException e) {
            System.err.println("Error getting waiting time: " + e.getMessage());
        }
        return waitingTime;
    }

    public boolean updateSettings(int waitingTime, int roundTime) {
        try (Connection conn = getConnection();
             PreparedStatement ps = conn.prepareStatement(
                     "UPDATE settings SET waiting_time_seconds = ?, round_time_seconds = ? WHERE id = 1")) {
            ps.setInt(1, waitingTime);
            ps.setInt(2, roundTime);
            int rowsAffected = ps.executeUpdate();
            return rowsAffected > 0;
        } catch (SQLException e) {
            System.err.println("Database error updating settings: " + e.getMessage());
            return false;
        }
    }

    public SystemStatisticsDTO getSystemStatistics() {
        int totalGames = 0;
        int wins = 0;
        int losses = 0;
        double winRate = 0;
        int waitingTime = 10;
        int roundTime = 30;
        try (Connection conn = getConnection();
             PreparedStatement totalGamesStmt = conn.prepareStatement("SELECT COUNT(*) FROM game_results");
             PreparedStatement winsStmt = conn.prepareStatement("SELECT COUNT(*) FROM game_results WHERE win_status = 1");
             PreparedStatement settingsStmt = conn.prepareStatement("SELECT waiting_time_seconds, round_time_seconds FROM settings WHERE id = 1")) {
            ResultSet totalGamesRs = totalGamesStmt.executeQuery();
            if (totalGamesRs.next()) {
                totalGames = totalGamesRs.getInt(1);
            }
            ResultSet winsRs = winsStmt.executeQuery();
            if (winsRs.next()) {
                wins = winsRs.getInt(1);
            }
            losses = totalGames - wins;
            winRate = totalGames > 0 ? (double) wins / totalGames * 100 : 0;
            ResultSet settingsRs = settingsStmt.executeQuery();
            if (settingsRs.next()) {
                waitingTime = settingsRs.getInt("waiting_time_seconds");
                roundTime = settingsRs.getInt("round_time_seconds");
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return new SystemStatisticsDTO(totalGames, wins, losses, winRate, waitingTime, roundTime);
    }

    public List<LeaderboardEntryDTO> getLeaderboardEntries() {
        List<LeaderboardEntryDTO> leaderboard = new ArrayList<>();
        try (Connection conn = getConnection();
             PreparedStatement stmt = conn.prepareStatement("SELECT username, wins FROM players ORDER BY wins DESC, username ASC LIMIT 5")) {
            ResultSet rs = stmt.executeQuery();
            while (rs.next()) {
                leaderboard.add(new LeaderboardEntryDTO(rs.getString("username"), rs.getInt("wins")));
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return leaderboard;
    }
} 