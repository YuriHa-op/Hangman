package server.handler.data;

import server.dto.MultiplayerGameDetailsDTO;
import server.dto.MultiplayerRoundInfoDTO;
import server.dto.MultiplayerGameSummaryDTO;
import server.handler.model.MultiplayerGameState;

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
            String insertGame = "INSERT INTO games (game_id, total_rounds, overall_winner, game_end_time) VALUES (?, ?, ?, ?)";
            try (PreparedStatement ps = conn.prepareStatement(insertGame)) {
                ps.setString(1, result.gameId);
                ps.setInt(2, result.totalRounds);
                ps.setString(3, result.overallWinner);
                ps.setTimestamp(4, new Timestamp(result.gameEndTime));
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

    // --- Fetch all games a player participated in ---
    public List<MultiplayerGameSummaryDTO> getGamesForPlayer(String username) {
        List<MultiplayerGameSummaryDTO> result = new ArrayList<>();
        String sql = "SELECT g.game_id, g.total_rounds, g.overall_winner, g.game_end_time " +
                     "FROM games g JOIN game_players gp ON g.game_id = gp.game_id " +
                     "WHERE gp.player_name = ? ORDER BY g.game_end_time DESC";
        try (Connection conn = getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, username);
            ResultSet rs = ps.executeQuery();
            while (rs.next()) {
                String gameId = rs.getString("game_id");
                int totalRounds = rs.getInt("total_rounds");
                String overallWinner = rs.getString("overall_winner");
                Timestamp gameEndTimeStamp = rs.getTimestamp("game_end_time");
                long gameEndTime = (gameEndTimeStamp != null) ? gameEndTimeStamp.getTime() : 0L;

                List<String> players = new ArrayList<>();
                try (PreparedStatement ps2 = conn.prepareStatement("SELECT player_name FROM game_players WHERE game_id = ?")) {
                    ps2.setString(1, gameId);
                    ResultSet rs2 = ps2.executeQuery();
                    while (rs2.next()) {
                        players.add(rs2.getString("player_name"));
                    }
                }
                result.add(new MultiplayerGameSummaryDTO(gameId, totalRounds, overallWinner, players, gameEndTime));
            }
        } catch (SQLException e) {
            System.err.println("Error fetching match history: " + e.getMessage());
        }
        return result;
    }

    // --- Fetch details for a specific game ---
    public MultiplayerGameDetailsDTO getGameDetails(String gameId) {
        String sqlGame = "SELECT total_rounds, overall_winner, game_end_time FROM games WHERE game_id = ?";
        String sqlPlayers = "SELECT player_name FROM game_players WHERE game_id = ?";
        String sqlRounds = "SELECT round_number, word, winner FROM rounds WHERE game_id = ? ORDER BY round_number ASC";
        try (Connection conn = getConnection()) {
            int totalRounds = 0;
            String overallWinner = null;
            long gameEndTime = 0L;
            try (PreparedStatement ps = conn.prepareStatement(sqlGame)) {
                ps.setString(1, gameId);
                ResultSet rs = ps.executeQuery();
                if (rs.next()) {
                    totalRounds = rs.getInt("total_rounds");
                    overallWinner = rs.getString("overall_winner");
                    Timestamp gameEndTimeStamp = rs.getTimestamp("game_end_time");
                    gameEndTime = (gameEndTimeStamp != null) ? gameEndTimeStamp.getTime() : 0L;
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
            List<MultiplayerRoundInfoDTO> rounds = new ArrayList<>();
            try (PreparedStatement ps = conn.prepareStatement(sqlRounds)) {
                ps.setString(1, gameId);
                ResultSet rs = ps.executeQuery();
                while (rs.next()) {
                    int roundNumber = rs.getInt("round_number");
                    String word = rs.getString("word");
                    String winner = rs.getString("winner");
                    rounds.add(new MultiplayerRoundInfoDTO(roundNumber, word, winner));
                }
            }
            return new MultiplayerGameDetailsDTO(gameId, totalRounds, overallWinner, players, rounds, gameEndTime);
        } catch (SQLException e) {
            System.err.println("Error fetching match details: " + e.getMessage());
            return null;
        }
    }
} 