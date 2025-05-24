package server.handler;

import GameModule.GameServicePOA;
import java.util.function.Consumer;
import server.handler.GameManager;
import server.handler.PlayerManager;
import server.handler.WordManager;
import server.handler.MultiplayerGameManager;
import server.handler.MultiplayerLobby;
import server.handler.MultiplayerGameState;

import java.sql.*;
import java.util.*;
import java.util.Map;
import java.io.*;
import java.util.ArrayList;
import java.util.List;
import GameModule.GameStateDTO;
import client.admin.model.SystemStatisticsDTO;
import client.admin.model.LeaderboardEntryDTO;
import com.google.gson.Gson;

public class GameServiceImpl extends GameServicePOA {
    private final GameManager gameManager;
    private final PlayerManager playerManager;
    private final WordManager wordManager;
    private Consumer<String> logCallback;
    private MultiplayerGameManager multiplayerGameManager;
    private static final int MULTI_MIN_PLAYERS = 2;
    private static final int MULTI_MAX_PLAYERS = 8;
    private final MatchResultDAO matchResultDAO = new MatchResultDAO(
        "jdbc:mysql://localhost:3306/game",
        "root",
        ""
    );
    private final Gson gson = new Gson();

                //put this hotdog in you GameServiceImpl



    public GameServiceImpl() {
        this.wordManager = new WordManager();
        this.playerManager = new PlayerManager();
        this.gameManager = new GameManager(wordManager, playerManager);
        // Initialize multiplayer manager
        int waitingTime = playerManager.getWaitingTime();
        int minPlayers = 2;
        int maxPlayers = 8;
        this.multiplayerGameManager = new MultiplayerGameManager(wordManager, playerManager, minPlayers, maxPlayers, waitingTime);
    }

    public void setLogCallback(Consumer<String> callback) {
        this.logCallback = callback;
        gameManager.setLogCallback(callback);
    }


    public int getActivePlayers() {
        return gameManager.getActivePlayers();
    }

    public int getActiveGames() {
        return gameManager.getActiveGames();
    }


    @Override
    public boolean login(String username, String password) throws GameModule.AlreadyLoggedInException {
        return playerManager.login(username, password);
    }

    public void logout(String username) {
        playerManager.logout(username);
    }

    @Override
    public boolean sendGuess(String username, char letter) {
        return gameManager.sendGuess(username, letter);
    }

    @Override
    public String viewLeaderboard() {
        java.util.List<LeaderboardEntryDTO> entries = playerManager.getLeaderboardEntries();
        StringBuilder leaderboard = new StringBuilder("LEADERBOARD:\n");
        for (LeaderboardEntryDTO entry : entries) {
            leaderboard.append(entry.getUsername())
                    .append(": ")
                    .append(entry.getWins())
                    .append(" wins\n");
        }
        return leaderboard.toString();
    }

    @Override
    public String getMaskedWord(String username) {
        return gameManager.getMaskedWord(username);
    }

    @Override
    public boolean createPlayer(String username, String password) {
        return playerManager.createPlayer(username, password);
    }

    @Override
    public boolean deletePlayer(String username) {
        return playerManager.deletePlayer(username);
    }

    public String viewPlayers() {
        return playerManager.viewPlayers();
    }

    @Override
    public String startGame(String username) {
        return gameManager.startGame(username);
    }

    @Override
    public boolean updatePlayerPassword(String username, String newPassword) {
        return playerManager.updatePlayerPassword(username, newPassword);
    }

    @Override
    public boolean updateSettings(int waitingTime, int roundTime) {
        return playerManager.updateSettings(waitingTime, roundTime);
    }

    private void endGame(String username, boolean recordStats) {
        gameManager.endGame(username, recordStats);
    }

    @Override
    public boolean updatePlayerUsername(String username, String newUsername) {
        return playerManager.updatePlayerUsername(username, newUsername);
    }

    @Override
    public boolean updatePlayerWins(String username, int wins) {
        return playerManager.updatePlayerWins(username, wins);
    }

    @Override
    public int getRoundTime() {
        return playerManager.getRoundTime();
    }

    @Override
    public int getWaitingTime() {
        return playerManager.getWaitingTime();
    }

    @Override
    public int getRemainingTime(String username) {
        return gameManager.getRemainingTime(username);
    }

    @Override
    public int getIncorrectGuesses(String username) {
        return gameManager.getIncorrectGuesses(username);
    }

    @Override
    public void endGameSession(String username) {
        gameManager.endGameSession(username);
    }

    @Override
    public int getCurrentRound(String username) {
        return gameManager.getCurrentRound(username);
    }

    @Override
    public int getPlayerWins(String username) {
        return gameManager.getPlayerWins(username);
    }

    @Override
    public boolean startNewRound(String username) {
        return gameManager.startNewRound(username);
    }

    @Override
    public boolean isRoundOver(String username) {
        return gameManager.isRoundOver(username);
    }

    @Override
    public boolean isGameSessionOver(String username) {
        return gameManager.isGameSessionOver(username);
    }

    public boolean isGameSessionWinner(String username) {
        return gameManager.isGameSessionWinner(username);
    }

    public String getGameSessionResult(String username) {
        return gameManager.getGameSessionResult(username);
    }

    @Override
    public GameStateDTO getGameState(String username) {
        server.dto.GameStateDTO internal = gameManager.getGameState(username);
        GameStateDTO corbaDto = new GameStateDTO();
        corbaDto.maskedWord = (internal.maskedWord != null) ? internal.maskedWord : "";
        corbaDto.incorrectGuesses = internal.incorrectGuesses;
        corbaDto.currentRound = internal.currentRound;
        corbaDto.totalRounds = internal.totalRounds;
        corbaDto.playerWins = internal.playerWins;
        corbaDto.roundOver = internal.roundOver;
        corbaDto.gameOver = internal.gameOver;
        corbaDto.sessionResult = (internal.sessionResult != null) ? internal.sessionResult : "";
        corbaDto.remainingTime = internal.remainingTime;
        corbaDto.roundWinner = (internal.roundWinner != null) ? internal.roundWinner : "";
        corbaDto.finishedTime = internal.finishedTime;
        return corbaDto;
    }

    @Override
    public void finishRound(String username, int clientRemainingTime, boolean guessedWord) {
        gameManager.finishRound(username, (long)clientRemainingTime, guessedWord);
    }

    @Override
    public boolean addWord(String word) {
        return wordManager.addWord(word);
    }

    @Override
    public boolean updateWord(String oldWord, String newWord) {
        return wordManager.updateWord(oldWord, newWord);
    }

    @Override
    public boolean deleteWord(String word) {
        return wordManager.deleteWord(word);
    }

    @Override
    public String[] getAllWords() {
        List<String> words = wordManager.getWords();
        return words.toArray(new String[0]);
    }

    @Override
    public GameModule.SystemStatisticsDTO getSystemStatistics() {
        SystemStatisticsDTO stats = playerManager.getSystemStatistics();
        GameModule.SystemStatisticsDTO corbaDto = new GameModule.SystemStatisticsDTO();
        corbaDto.totalGames = stats.getTotalGames();
        corbaDto.wins = stats.getWins();
        corbaDto.losses = stats.getLosses();
        corbaDto.winRate = stats.getWinRate();
        corbaDto.waitingTime = stats.getWaitingTime();
        corbaDto.roundTime = stats.getRoundTime();
        return corbaDto;
    }

    @Override
    public GameModule.LeaderboardEntryDTO[] getLeaderboardEntries() {
        java.util.List<LeaderboardEntryDTO> entries = playerManager.getLeaderboardEntries();
        GameModule.LeaderboardEntryDTO[] corbaEntries = new GameModule.LeaderboardEntryDTO[entries.size()];
        for (int i = 0; i < entries.size(); i++) {
            LeaderboardEntryDTO entry = entries.get(i);
            GameModule.LeaderboardEntryDTO corbaEntry = new GameModule.LeaderboardEntryDTO();
            corbaEntry.username = entry.getUsername();
            corbaEntry.wins = entry.getWins();
            corbaEntries[i] = corbaEntry;
        }
        return corbaEntries;
    }

    public void cleanupPlayerSession(String username) {
        gameManager.cleanupPlayerSession(username);
    }

    public void initMultiplayerManager(int queueTimeSeconds) {
        this.multiplayerGameManager = new MultiplayerGameManager(wordManager, playerManager, MULTI_MIN_PLAYERS, MULTI_MAX_PLAYERS, queueTimeSeconds);
    }

    public String startMultiplayerGame(String username) {
        MultiplayerLobby lobby = multiplayerGameManager.joinOrCreateLobby(username);
        return lobby.getLobbyId();
    }

    public String getMultiplayerLobbyState(String username) {
        MultiplayerLobby lobby = multiplayerGameManager.getLobbyByPlayer(username);
        if (lobby == null) return "{\"state\":\"NOMATCH\"}";

        MultiplayerGameState gameState = multiplayerGameManager.getGameState(username);

        // Schedule cleanup if game is over and winner is declared
        if (lobby.isStarted() && gameState != null && gameState.getGameWinner() != null) {
            multiplayerGameManager.scheduleCleanupIfGameOver(lobby.getLobbyId());
        }

        StringBuilder sb = new StringBuilder();
        sb.append("{\"state\":\"")
          .append(lobby.isStarted() ? "STARTED" : "WAITING")
          .append("\",");
        
        // Add basic lobby info
        sb.append("\"players\":[");
        for (int i = 0; i < lobby.getPlayers().size(); i++) {
            sb.append("\"").append(lobby.getPlayers().get(i)).append("\"");
            if (i < lobby.getPlayers().size() - 1) sb.append(",");
        }
        sb.append("],");
        sb.append("\"maxPlayers\":").append(lobby.getMaxPlayers()).append(",");
        sb.append("\"creationTime\":").append(lobby.getCreationTime()).append(",");
        sb.append("\"queueTimeSeconds\":").append(multiplayerGameManager.getQueueTimeSeconds());

        // Add game state if game has started
        if (gameState != null) {
            sb.append(",\"gameState\":{");
            sb.append("\"currentRound\":").append(gameState.getCurrentRound()).append(",");
            sb.append("\"roundInProgress\":").append(gameState.isRoundInProgress()).append(",");
            sb.append("\"remainingTime\":").append(gameState.getRemainingTime()).append(",");
            sb.append("\"maskedWord\":\"").append(gameState.getMaskedWord(username)).append("\",");
            
            // Add scores
            sb.append("\"scores\":{");
            Map<String, Integer> scores = gameState.getScores();
            Iterator<Map.Entry<String, Integer>> it = scores.entrySet().iterator();
            while (it.hasNext()) {
                Map.Entry<String, Integer> entry = it.next();
                sb.append("\"").append(entry.getKey()).append("\":")
                  .append(entry.getValue());
                if (it.hasNext()) sb.append(",");
            }
            sb.append("},");

            // Add player guesses
            sb.append("\"guesses\":[");
            Set<Character> guesses = gameState.getPlayerGuesses(username);
            Iterator<Character> guessIt = guesses.iterator();
            while (guessIt.hasNext()) {
                sb.append("\"").append(guessIt.next()).append("\"");
                if (guessIt.hasNext()) sb.append(",");
            }
            sb.append("],");

            // Add round winner
            sb.append("\"roundWinner\":\"").append(gameState.getRoundWinner()).append("\",");

            // Add player round wins
            sb.append("\"playerRoundWins\":{");
            List<String> allPlayers = lobby.getPlayers();
            for (int i = 0; i < allPlayers.size(); i++) {
                String p = allPlayers.get(i);
                sb.append("\"").append(p).append("\":").append(gameState.getPlayerRoundWins(p));
                if (i < allPlayers.size() - 1) sb.append(",");
            }
            sb.append("},");

            // Add game winner
            sb.append("\"gameWinner\":\"").append(gameState.getGameWinner() != null ? gameState.getGameWinner() : "").append("\",");

            // Add sessionResult for this player
            String sessionResult = "";
            String gameWinner = gameState.getGameWinner();
            if (gameWinner != null && !gameWinner.isEmpty()) {
                if (gameWinner.equals(username)) {
                    sessionResult = "WIN";
                } else {
                    sessionResult = "LOSE";
                }
            } else {
                sessionResult = "ONGOING";
            }
            sb.append("\"sessionResult\":\"").append(sessionResult).append("\"");
            sb.append("}");
        }
        
        sb.append("}");
        return sb.toString();
    }

    public boolean sendMultiplayerGuess(String username, char letter) {
        return multiplayerGameManager.makeGuess(username, letter);
    }

    // Expose a method to start the next round in multiplayer
    public boolean startMultiplayerNextRound(String username) {
        return multiplayerGameManager.startNextRound(username);
    }

    // --- Match History Service Methods ---
    public String getMatchHistory(String username) {
        java.util.List<MatchResultDAO.GameSummary> games = matchResultDAO.getGamesForPlayer(username);
        return gson.toJson(games);
    }

    public String getMatchDetails(String gameId) {
        MatchResultDAO.GameDetails details = matchResultDAO.getGameDetails(gameId);
        return gson.toJson(details);
    }

}
