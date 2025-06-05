package server.handler;

import server.dto.SPSinglePlayerGameDetailsDTO;
import server.dto.SPSinglePlayerGameSummaryDTO;
import server.dto.SPSinglePlayerRoundInfoDTO;

import java.sql.*;
import java.util.ArrayList;
import java.util.List;

public class SinglePlayerMatchResultDAO {
    private final String dbUrl;
    private final String dbUser;
    private final String dbPassword;

    public SinglePlayerMatchResultDAO(String dbUrl, String dbUser, String dbPassword) {
        this.dbUrl = dbUrl;
        this.dbUser = dbUser;
        this.dbPassword = dbPassword;
    }

    private Connection getConnection() throws SQLException {
        return DriverManager.getConnection(dbUrl, dbUser, dbPassword);
    }

    // SinglePlayerMatchResult for saving, now uses SPSinglePlayerRoundInfoDTO
    public static class SinglePlayerMatchResult {
        public final String gameId;
        public final int totalRounds;
        public final String overallWinner;
        public final List<String> players;
        public final List<SPSinglePlayerRoundInfoDTO> rounds; // Updated
        public final long gameEndTime;

        public SinglePlayerMatchResult(String gameId, int totalRounds, String overallWinner, List<String> players, List<SPSinglePlayerRoundInfoDTO> rounds, long gameEndTime) {
            this.gameId = gameId;
            this.totalRounds = totalRounds;
            this.overallWinner = overallWinner;
            this.players = players;
            this.rounds = rounds;
            this.gameEndTime = gameEndTime;
        }
    }

    public void saveMatchResult(SinglePlayerMatchResult result) {
        try (Connection conn = getConnection()) {
            conn.setAutoCommit(false); // Start transaction

            String insertGame = "INSERT INTO sp_games (game_id, total_rounds, overall_winner, game_end_time) VALUES (?, ?, ?, ?)";
            try (PreparedStatement psGame = conn.prepareStatement(insertGame)) {
                psGame.setString(1, result.gameId);
                psGame.setInt(2, result.totalRounds);
                psGame.setString(3, result.overallWinner);
                psGame.setTimestamp(4, new Timestamp(result.gameEndTime));
                psGame.executeUpdate();
            }

            String insertPlayer = "INSERT INTO sp_game_players (game_id, player_name) VALUES (?, ?)";
            try (PreparedStatement psPlayer = conn.prepareStatement(insertPlayer)) {
                for (String player : result.players) {
                    psPlayer.setString(1, result.gameId);
                    psPlayer.setString(2, player);
                    psPlayer.addBatch();
                }
                psPlayer.executeBatch();
            }

            String insertRound = "INSERT INTO sp_rounds (game_id, round_number, word, winner) VALUES (?, ?, ?, ?)";
            try (PreparedStatement psRound = conn.prepareStatement(insertRound)) {
                for (SPSinglePlayerRoundInfoDTO round : result.rounds) { // Updated
                    psRound.setString(1, result.gameId);
                    psRound.setInt(2, round.roundNumber);
                    psRound.setString(3, round.word);
                    psRound.setString(4, round.winner);
                    psRound.addBatch();
                }
                psRound.executeBatch();
            }

            conn.commit(); // Commit transaction
        } catch (SQLException e) {
            System.err.println("Error saving single player match result: " + e.getMessage());
            // Consider rolling back if an error occurs, though with auto-close resources it might be complex.
            e.printStackTrace();
        }
    }

    public List<SPSinglePlayerGameSummaryDTO> getGamesForPlayer(String username) {
        List<SPSinglePlayerGameSummaryDTO> result = new ArrayList<>();
        String sql = "SELECT g.game_id, g.total_rounds, g.overall_winner, g.game_end_time " +
                     "FROM sp_games g JOIN sp_game_players gp ON g.game_id = gp.game_id " +
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
                // Fetch players for this game
                try (PreparedStatement psPlayers = conn.prepareStatement("SELECT player_name FROM sp_game_players WHERE game_id = ?")) {
                    psPlayers.setString(1, gameId);
                    ResultSet rsPlayers = psPlayers.executeQuery();
                    while (rsPlayers.next()) {
                        players.add(rsPlayers.getString("player_name"));
                    }
                }
                result.add(new SPSinglePlayerGameSummaryDTO(gameId, totalRounds, overallWinner, players, gameEndTime));
            }
        } catch (SQLException e) {
            System.err.println("Error fetching single player match history: " + e.getMessage());
        }
        return result;
    }

    public SPSinglePlayerGameDetailsDTO getGameDetails(String gameId) {
        String sqlGame = "SELECT total_rounds, overall_winner, game_end_time FROM sp_games WHERE game_id = ?";
        String sqlPlayers = "SELECT player_name FROM sp_game_players WHERE game_id = ?";
        String sqlRounds = "SELECT round_number, word, winner FROM sp_rounds WHERE game_id = ? ORDER BY round_number ASC";

        try (Connection conn = getConnection()) {
            int totalRounds = 0;
            String overallWinner = null;
            long gameEndTime = 0L;

            try (PreparedStatement psGame = conn.prepareStatement(sqlGame)) {
                psGame.setString(1, gameId);
                ResultSet rsGame = psGame.executeQuery();
                if (rsGame.next()) {
                    totalRounds = rsGame.getInt("total_rounds");
                    overallWinner = rsGame.getString("overall_winner");
                    Timestamp gameEndTimeStamp = rsGame.getTimestamp("game_end_time");
                    gameEndTime = (gameEndTimeStamp != null) ? gameEndTimeStamp.getTime() : 0L;
                }
            }

            List<String> players = new ArrayList<>();
            try (PreparedStatement psPlayers = conn.prepareStatement(sqlPlayers)) {
                psPlayers.setString(1, gameId);
                ResultSet rsPlayers = psPlayers.executeQuery();
                while (rsPlayers.next()) {
                    players.add(rsPlayers.getString("player_name"));
                }
            }

            List<SPSinglePlayerRoundInfoDTO> rounds = new ArrayList<>();
            try (PreparedStatement psRounds = conn.prepareStatement(sqlRounds)) {
                psRounds.setString(1, gameId);
                ResultSet rsRounds = psRounds.executeQuery();
                while (rsRounds.next()) {
                    rounds.add(new SPSinglePlayerRoundInfoDTO(
                            rsRounds.getInt("round_number"),
                            rsRounds.getString("word"),
                            rsRounds.getString("winner")
                    ));
                }
            }
            return new SPSinglePlayerGameDetailsDTO(gameId, totalRounds, overallWinner, players, rounds, gameEndTime);
        } catch (SQLException e) {
            System.err.println("Error fetching single player match details: " + e.getMessage());
            return null;
        }
    }
} 