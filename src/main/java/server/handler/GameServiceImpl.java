package server.handler;

import GameModule.GameServicePOA;
import java.util.function.Consumer;
import server.handler.GameManager;
import server.handler.PlayerManager;
import server.handler.WordManager;

import java.sql.*;
import java.util.Random;
import java.util.HashMap;
import java.util.Map;
import java.io.*;
import java.util.ArrayList;
import java.util.List;
import GameModule.GameStateDTO;

public class GameServiceImpl extends GameServicePOA {
    private final GameManager gameManager;
    private final PlayerManager playerManager;
    private final WordManager wordManager;
    private Consumer<String> logCallback;

                //put this hotdog in you GameServiceImpl



    public GameServiceImpl() {
        this.wordManager = new WordManager();
        this.playerManager = new PlayerManager();
        this.gameManager = new GameManager(wordManager, playerManager);
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
        return gameManager.viewLeaderboard();
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

}
