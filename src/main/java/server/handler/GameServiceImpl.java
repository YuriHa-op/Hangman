package server.handler;

import GameModule.GameServicePOA;
import GameModule.Bool;
import GameModule.AlreadyLoggedInException;
import java.util.function.Consumer;
import server.handler.GameManager;
import server.handler.PlayerManager;
import server.handler.WordManager;
import server.handler.MultiplayerGameManager;
import server.handler.MultiplayerLobby;
import server.handler.MultiplayerGameState;
import server.handler.SinglePlayerMatchResultDAO;

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
    private final SinglePlayerMatchResultDAO singlePlayerMatchResultDAO = new SinglePlayerMatchResultDAO(
        "jdbc:mysql://localhost:3306/game",
        "root",
        ""
    );
    private final Gson gson = new Gson();

                //put this hotdog in you GameServiceImpl


    public GameServiceImpl() {
        this.wordManager = new WordManager();
        this.playerManager = new PlayerManager();
        this.gameManager = new GameManager(wordManager, playerManager, singlePlayerMatchResultDAO);
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
    public Bool login(String username, String password) throws GameModule.AlreadyLoggedInException {
        return playerManager.login(username, password);
    }

    public void logout(String username) {
        playerManager.logout(username);
    }

    @Override
    public Bool sendGuess(String username, char letter) {
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
    public Bool createPlayer(String username, String password) {
        return playerManager.createPlayer(username, password);
    }

    @Override
    public Bool deletePlayer(String username) {
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
    public Bool updatePlayerPassword(String username, String newPassword) {
        return playerManager.updatePlayerPassword(username, newPassword);
    }

    @Override
    public Bool updateSettings(int waitingTime, int roundTime) {
        return playerManager.updateSettings(waitingTime, roundTime);
    }

    private void endGame(String username, boolean recordStats) {
        gameManager.endGame(username, recordStats);
    }

    @Override
    public Bool updatePlayerUsername(String username, String newUsername) {
        return playerManager.updatePlayerUsername(username, newUsername);
    }

    @Override
    public Bool updatePlayerWins(String username, int wins) {
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
    public Bool startNewRound(String username) {
        return gameManager.startNewRound(username) ? Bool.BOOL_TRUE : Bool.BOOL_FALSE;
    }

    @Override
    public Bool isRoundOver(String username) {
        return gameManager.isRoundOver(username) ? Bool.BOOL_TRUE : Bool.BOOL_FALSE;
    }

    @Override
    public Bool isGameSessionOver(String username) {
        return gameManager.isGameSessionOver(username) ? Bool.BOOL_TRUE : Bool.BOOL_FALSE;
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
        corbaDto.opponentUsername = internal.opponentUsername;
        return corbaDto;
    }

    @Override
    public void finishRound(String username, int clientRemainingTime, Bool guessedWord) {
        gameManager.finishRound(username, clientRemainingTime, guessedWord);
    }

    @Override
    public Bool addWord(String word) {
        return wordManager.addWord(word);
    }

    @Override
    public Bool updateWord(String oldWord, String newWord) {
        return wordManager.updateWord(oldWord, newWord);
    }

    @Override
    public Bool deleteWord(String word) {
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
        if (lobby == null) {
            return "{\"state\":\"NOMATCH\"}";
        }

        MultiplayerGameState gameState = multiplayerGameManager.getGameState(username);

        // Schedule cleanup if game is over and winner is declared
        if (lobby.isStarted() && gameState != null && gameState.getGameWinner() != null) {
            multiplayerGameManager.scheduleCleanupIfGameOver(lobby.getLobbyId());
        }

        Map<String, Object> stateMap = new LinkedHashMap<>();
        stateMap.put("state", lobby.isStarted() ? "STARTED" : "WAITING");
        stateMap.put("players", lobby.getPlayers());
        stateMap.put("maxPlayers", lobby.getMaxPlayers());
        stateMap.put("creationTime", lobby.getCreationTime());
        stateMap.put("queueTimeSeconds", multiplayerGameManager.getQueueTimeSeconds());

        if (gameState != null) {
            if (!gameState.isRoundPotentiallyStalled()) {
                multiplayerGameManager.cancelStallCheckTimer(lobby.getLobbyId());
            }

            Map<String, Object> gameStateMap = new LinkedHashMap<>();
            gameStateMap.put("gameId", gameState.getGameId());
            gameStateMap.put("currentRound", gameState.getCurrentRound());
            gameStateMap.put("roundInProgress", gameState.isRoundInProgress());
            gameStateMap.put("remainingTime", gameState.getRemainingTime());
            gameStateMap.put("maskedWord", gameState.getMaskedWord(username));
            gameStateMap.put("maskedWords", gameState.getAllMaskedWords());
            gameStateMap.put("incorrectGuessesMap", gameState.getAllIncorrectGuesses());
            gameStateMap.put("scores", gameState.getScores());
            gameStateMap.put("guesses", gameState.getPlayerGuesses(username));
            gameStateMap.put("roundWinner", gameState.getRoundWinner());
            
            Map<String, Integer> playerRoundWins = new HashMap<>();
            for(String p : lobby.getPlayers()) {
                playerRoundWins.put(p, gameState.getPlayerRoundWins(p));
            }
            gameStateMap.put("playerRoundWins", playerRoundWins);

            String gameWinner = gameState.getGameWinner();
            gameStateMap.put("gameWinner", gameWinner != null ? gameWinner : "");
            
            String sessionResult = "ONGOING";
            if (gameWinner != null && !gameWinner.isEmpty()) {
                sessionResult = gameWinner.equals(username) ? "WIN" : "LOSE";
            }
            gameStateMap.put("sessionResult", sessionResult);
            
            gameStateMap.put("playerGuessesMap", gameState.getAllPlayerGuesses());
            gameStateMap.put("allCurrentWords", gameState.getAllCurrentWords());
            gameStateMap.put("playerWinStreaks", gameState.getPlayerWinStreaks());
            gameStateMap.put("allPlayerFinishTimes", gameState.getAllPlayerFinishTimes());
            gameStateMap.put("gameEvents", gameState.getGameEvents());
            gameStateMap.put("allPlayersEver", gameState.getAllPlayersEver());

            stateMap.put("gameState", gameStateMap);
        }

        return gson.toJson(stateMap);
    }

    public Bool sendMultiplayerGuess(String username, char letter) {
        return multiplayerGameManager.makeGuess(username, letter) ? Bool.BOOL_TRUE : Bool.BOOL_FALSE;
    }

    // Expose a method to start the next round in multiplayer
    public Bool startMultiplayerNextRound(String username) {
        return multiplayerGameManager.startNextRound(username) ? Bool.BOOL_TRUE : Bool.BOOL_FALSE;
    }

    // --- Match History Service Methods ---
    public String getMatchHistory(String username) {
        java.util.List<server.dto.MultiplayerGameSummaryDTO> games = matchResultDAO.getGamesForPlayer(username);
        return gson.toJson(games);
    }

    public String getMatchDetails(String gameId) {
        server.dto.MultiplayerGameDetailsDTO details = matchResultDAO.getGameDetails(gameId);
        return gson.toJson(details);
    }

    // --- Single Player Match History Service Methods ---
    public String getSinglePlayerMatchHistory(String username) {
        List<server.dto.SPSinglePlayerGameSummaryDTO> games = singlePlayerMatchResultDAO.getGamesForPlayer(username);
        return gson.toJson(games);
    }

    public String getSinglePlayerMatchDetails(String gameId) {
        server.dto.SPSinglePlayerGameDetailsDTO details = singlePlayerMatchResultDAO.getGameDetails(gameId);
        return gson.toJson(details);
    }

    @Override
    public void playerReadyForFirstRound(String username) {
        if (multiplayerGameManager.isPlayerInMultiplayer(username)) {
            multiplayerGameManager.playerReadyForFirstRound(username);
        } else {
            gameManager.signalPlayerReadyAndPotentiallyStartFirstRound(username);
        }
    }

    @Override
    public void leaveMultiplayerGame(String username) {
        multiplayerGameManager.leaveMultiplayerGame(username);
    }

}
