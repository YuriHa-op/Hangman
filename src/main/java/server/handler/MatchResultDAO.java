package server.handler;

import java.sql.*;
import java.util.*;

public class MatchResultDAO {
    private final String dbUrl;
    private final String dbUser;
    private final String dbPassword;

    public MatchResultDAO(String dbUrl, String dbUser, String dbPassword) {
        this.dbUrl = dbUrl;
        this.dbUser = dbUser;
        this.dbPassword = dbPassword;
    }

    private Connection getConnection() throws SQLException {
        return DriverManager.getConnection(dbUrl, dbUser, dbPassword);
    }

    public void saveMatchResult(MultiplayerGameState.MatchResult result) {
        try (Connection conn = getConnection()) {
            // Insert into games
            String insertGame = "INSERT INTO games (game_id, total_rounds, overall_winner) VALUES (?, ?, ?)";
            try (PreparedStatement ps = conn.prepareStatement(insertGame)) {
                ps.setString(1, result.gameId);
                ps.setInt(2, result.totalRounds);
                ps.setString(3, result.overallWinner);
                ps.executeUpdate();
            }
            // Insert players
            String insertPlayer = "INSERT INTO game_players (game_id, player_name) VALUES (?, ?)";
            try (PreparedStatement ps = conn.prepareStatement(insertPlayer)) {
                for (String player : result.players) {
                    ps.setString(1, result.gameId);
                    ps.setString(2, player);
                    ps.addBatch();
                }
                ps.executeBatch();
            }
            // Insert rounds
            String insertRound = "INSERT INTO rounds (game_id, round_number, word, winner) VALUES (?, ?, ?, ?)";
            try (PreparedStatement ps = conn.prepareStatement(insertRound)) {
                for (MultiplayerGameState.RoundResult round : result.rounds) {
                    ps.setString(1, result.gameId);
                    ps.setInt(2, round.roundNumber);
                    ps.setString(3, round.word);
                    ps.setString(4, round.winner);
                    ps.addBatch();
                }
                ps.executeBatch();
            }
        } catch (SQLException e) {
            System.err.println("Error saving match result: " + e.getMessage());
            e.printStackTrace();
        }
    }

    // --- Match History Data Classes ---
    public static class GameSummary {
        public final String gameId;
        public final int totalRounds;
        public final String overallWinner;
        public final List<String> players;
        public GameSummary(String gameId, int totalRounds, String overallWinner, List<String> players) {
            this.gameId = gameId;
            this.totalRounds = totalRounds;
            this.overallWinner = overallWinner;
            this.players = players;
        }
    }
    public static class GameDetails {
        public final String gameId;
        public final int totalRounds;
        public final String overallWinner;
        public final List<String> players;
        public final List<RoundInfo> rounds;
        public GameDetails(String gameId, int totalRounds, String overallWinner, List<String> players, List<RoundInfo> rounds) {
            this.gameId = gameId;
            this.totalRounds = totalRounds;
            this.overallWinner = overallWinner;
            this.players = players;
            this.rounds = rounds;
        }
    }
    public static class RoundInfo {
        public final int roundNumber;
        public final String word;
        public final String winner;
        public RoundInfo(int roundNumber, String word, String winner) {
            this.roundNumber = roundNumber;
            this.word = word;
            this.winner = winner;
        }
    }

    // --- Fetch all games a player participated in ---
    public List<GameSummary> getGamesForPlayer(String username) {
        List<GameSummary> result = new ArrayList<>();
        String sql = "SELECT g.game_id, g.total_rounds, g.overall_winner " +
                     "FROM games g JOIN game_players gp ON g.game_id = gp.game_id " +
                     "WHERE gp.player_name = ? ORDER BY g.game_id DESC";
        try (Connection conn = getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, username);
            ResultSet rs = ps.executeQuery();
            while (rs.next()) {
                String gameId = rs.getString("game_id");
                int totalRounds = rs.getInt("total_rounds");
                String overallWinner = rs.getString("overall_winner");
                // Fetch players for this game
                List<String> players = new ArrayList<>();
                try (PreparedStatement ps2 = conn.prepareStatement("SELECT player_name FROM game_players WHERE game_id = ?")) {
                    ps2.setString(1, gameId);
                    ResultSet rs2 = ps2.executeQuery();
                    while (rs2.next()) {
                        players.add(rs2.getString("player_name"));
                    }
                }
                result.add(new GameSummary(gameId, totalRounds, overallWinner, players));
            }
        } catch (SQLException e) {
            System.err.println("Error fetching match history: " + e.getMessage());
        }
        return result;
    }

    // --- Fetch details for a specific game ---
    public GameDetails getGameDetails(String gameId) {
        String sqlGame = "SELECT total_rounds, overall_winner FROM games WHERE game_id = ?";
        String sqlPlayers = "SELECT player_name FROM game_players WHERE game_id = ?";
        String sqlRounds = "SELECT round_number, word, winner FROM rounds WHERE game_id = ? ORDER BY round_number ASC";
        try (Connection conn = getConnection()) {
            int totalRounds = 0;
            String overallWinner = null;
            try (PreparedStatement ps = conn.prepareStatement(sqlGame)) {
                ps.setString(1, gameId);
                ResultSet rs = ps.executeQuery();
                if (rs.next()) {
                    totalRounds = rs.getInt("total_rounds");
                    overallWinner = rs.getString("overall_winner");
                }
            }
            List<String> players = new ArrayList<>();
            try (PreparedStatement ps = conn.prepareStatement(sqlPlayers)) {
                ps.setString(1, gameId);
                ResultSet rs = ps.executeQuery();
                while (rs.next()) {
                    players.add(rs.getString("player_name"));
                }
            }
            List<RoundInfo> rounds = new ArrayList<>();
            try (PreparedStatement ps = conn.prepareStatement(sqlRounds)) {
                ps.setString(1, gameId);
                ResultSet rs = ps.executeQuery();
                while (rs.next()) {
                    int roundNumber = rs.getInt("round_number");
                    String word = rs.getString("word");
                    String winner = rs.getString("winner");
                    rounds.add(new RoundInfo(roundNumber, word, winner));
                }
            }
            return new GameDetails(gameId, totalRounds, overallWinner, players, rounds);
        } catch (SQLException e) {
            System.err.println("Error fetching match details: " + e.getMessage());
            return null;
        }
    }
} 