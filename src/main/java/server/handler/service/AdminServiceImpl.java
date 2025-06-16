package server.handler.service;

import AdminModule.AdminServicePOA;
import AdminModule.Bool;
import AdminModule.LeaderboardEntryDTO;
import AdminModule.SystemStatisticsDTO;
import java.util.function.Consumer;
import java.util.List;
import com.google.gson.Gson;
import server.handler.data.MatchResultDAO;
import server.handler.data.SinglePlayerMatchResultDAO;
import server.handler.core.PlayerManager;
import server.handler.core.WordManager;

public class AdminServiceImpl extends AdminServicePOA {
   private final WordManager wordManager;
    private final PlayerManager playerManager;
    private Consumer<String> logCallback;
    private final MatchResultDAO matchResultDAO;
    private final SinglePlayerMatchResultDAO singlePlayerMatchResultDAO;
    private final Gson gson = new Gson();
    private boolean isPaused = false;

    public AdminServiceImpl() {
        this.wordManager = new WordManager();
        this.playerManager = new PlayerManager();
        this.matchResultDAO = new MatchResultDAO(
            "jdbc:mysql://localhost:3306/game",
           "root",
            ""
        );
        this.singlePlayerMatchResultDAO = new SinglePlayerMatchResultDAO(
            "jdbc:mysql://localhost:3306/game",
            "root",
            ""
        );
    }

    public AdminServiceImpl(WordManager wordManager, PlayerManager playerManager,
                            MatchResultDAO matchResultDAO, SinglePlayerMatchResultDAO singlePlayerMatchResultDAO) {
        this.wordManager = wordManager;
        this.playerManager = playerManager;
        this.matchResultDAO = matchResultDAO;
        this.singlePlayerMatchResultDAO = singlePlayerMatchResultDAO;
    }

    public void setLogCallback(Consumer<String> callback) {
        this.logCallback = callback;
    }

    /**
     * Sets the paused state of this service.
     * When paused, the service will reject new admin operations
     * but maintain existing ones.
     *
     * @param paused true to pause, false to resume
     */
    public void setPaused(boolean paused) {
        this.isPaused = paused;
        if (logCallback != null) {
            logCallback.accept("AdminService " + (paused ? "paused" : "resumed"));
        }
    }

    /**
     * Checks if the service is currently paused.
     *
     * @return true if paused, false otherwise
     */
    public boolean isPaused() {
        return isPaused;
    }

    // Player Management Methods
    @Override
    public Bool createPlayer(String username, String password) {
        return playerManager.createPlayer(username, password) == LoginModule.Bool.BOOL_TRUE ?
                Bool.BOOL_TRUE : Bool.BOOL_FALSE;
    }

    @Override
    public Bool deletePlayer(String username) {
        return playerManager.deletePlayer(username) == LoginModule.Bool.BOOL_TRUE ?
                Bool.BOOL_TRUE : Bool.BOOL_FALSE;
    }

    @Override
    public Bool updatePlayerPassword(String username, String newPassword) {
        return playerManager.updatePlayerPassword(username, newPassword) == LoginModule.Bool.BOOL_TRUE ?
                Bool.BOOL_TRUE : Bool.BOOL_FALSE;
    }

    @Override
    public Bool updatePlayerUsername(String username, String newUsername) {
        return playerManager.updatePlayerUsername(username, newUsername) == LoginModule.Bool.BOOL_TRUE ?
                Bool.BOOL_TRUE : Bool.BOOL_FALSE;
    }

    @Override
    public Bool updatePlayerWins(String username, int wins) {
        return playerManager.updatePlayerWins(username, wins) == LoginModule.Bool.BOOL_TRUE ?
                Bool.BOOL_TRUE : Bool.BOOL_FALSE;
    }

    @Override
    public String viewPlayers() {
        return playerManager.viewPlayers();
    }

    // System Settings
    @Override
    public Bool updateSettings(int waitingTime, int roundTime) {
        return playerManager.updateSettings(waitingTime, roundTime) == LoginModule.Bool.BOOL_TRUE ?
                Bool.BOOL_TRUE : Bool.BOOL_FALSE;
    }

    // Word Management Methods
    @Override
    public Bool addWord(String word) {
        return wordManager.addWord(word) == GameModule.Bool.BOOL_TRUE ?
                Bool.BOOL_TRUE : Bool.BOOL_FALSE;
    }

    @Override
    public Bool updateWord(String oldWord, String newWord) {
        return wordManager.updateWord(oldWord, newWord) == GameModule.Bool.BOOL_TRUE ?
                Bool.BOOL_TRUE : Bool.BOOL_FALSE;
    }

    @Override
    public Bool deleteWord(String word) {
        return wordManager.deleteWord(word) == GameModule.Bool.BOOL_TRUE ?
                Bool.BOOL_TRUE : Bool.BOOL_FALSE;
    }

    @Override
    public String[] getAllWords() {
        List<String> words = wordManager.getWords();
        return words.toArray(new String[0]);
    }

    // Statistics Methods
    @Override
    public SystemStatisticsDTO getSystemStatistics() {
        client.admin.model.SystemStatisticsDTO stats = playerManager.getSystemStatistics();
        SystemStatisticsDTO corbaDto = new SystemStatisticsDTO();
        corbaDto.totalGames = stats.getTotalGames();
        corbaDto.wins = stats.getWins();
        corbaDto.losses = stats.getLosses();
        corbaDto.winRate = stats.getWinRate();
        corbaDto.waitingTime = stats.getWaitingTime();
        corbaDto.roundTime = stats.getRoundTime();
        return corbaDto;
    }

    @Override
    public LeaderboardEntryDTO[] getLeaderboardEntries() {
        java.util.List<client.admin.model.LeaderboardEntryDTO> entries = playerManager.getLeaderboardEntries();
        LeaderboardEntryDTO[] corbaEntries = new LeaderboardEntryDTO[entries.size()];
        for (int i = 0; i < entries.size(); i++) {
            client.admin.model.LeaderboardEntryDTO entry = entries.get(i);
            LeaderboardEntryDTO corbaEntry = new LeaderboardEntryDTO();
            corbaEntry.username = entry.getUsername();
            corbaEntry.wins = entry.getWins();
            corbaEntries[i] = corbaEntry;
        }
        return corbaEntries;
    }

    // Match History Methods
    @Override
    public String getMatchHistory(String username) {
        java.util.List<server.dto.MultiplayerGameSummaryDTO> games = matchResultDAO.getGamesForPlayer(username);
        return gson.toJson(games);
    }

    @Override
    public String getMatchDetails(String gameId) {
        server.dto.MultiplayerGameDetailsDTO details = matchResultDAO.getGameDetails(gameId);
        return gson.toJson(details);
    }

    @Override
    public String getSinglePlayerMatchHistory(String username) {
        List<server.dto.SPSinglePlayerGameSummaryDTO> games = singlePlayerMatchResultDAO.getGamesForPlayer(username);
        return gson.toJson(games);
    }

    @Override
    public String getSinglePlayerMatchDetails(String gameId) {
        server.dto.SPSinglePlayerGameDetailsDTO details = singlePlayerMatchResultDAO.getGameDetails(gameId);
        return gson.toJson(details);
    }
}