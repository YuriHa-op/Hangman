package client.player.model;

import GameModule.GameService;
import GameModule.GameStateDTO;

public class GameModel {
    public interface MatchListener {
        void onMatchFound(String maskedWord);
        void onMatchTimeout();
    }


    private GameService gameService;
    private String username;
    private MatchListener matchListener;

    public GameModel(GameService gameService, String username) {
        this.gameService = gameService;
        this.username = username;
    }

    public GameStateDTO getGameState() {
        return gameService.getGameState(username);
    }

    public void startNewGame() {
        gameService.startGame(username);
        waitForMatch();
    }

    private void waitForMatch() {
        Thread matchWaitThread = new Thread(() -> {
            boolean matched = false;
            long startTime = System.currentTimeMillis();
            int waitingTimeSeconds = gameService.getWaitingTime();
            long waitingTimeMillis = waitingTimeSeconds * 1000;

            while (!matched && (System.currentTimeMillis() - startTime) < waitingTimeMillis) {
                try {
                    Thread.sleep(500);
                    String currentMaskedWord = gameService.getMaskedWord(username);

                    if (currentMaskedWord != null && !currentMaskedWord.isEmpty() &&
                            !currentMaskedWord.equals("WAITING_FOR_MATCH")) {
                        matched = true;
                        if (matchListener != null) {
                            javafx.application.Platform.runLater(() -> {
                                matchListener.onMatchFound(currentMaskedWord);
                            });
                        }
                    }
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    break;
                }
            }

            if (!matched) {
                gameService.endGameSession(username);
                if (matchListener != null) {
                    javafx.application.Platform.runLater(() -> {
                        matchListener.onMatchTimeout();
                    });
                }
            }
        });

        matchWaitThread.setDaemon(true);
        matchWaitThread.start();
    }

    public boolean makeGuess(char letter, int clientRemainingTime) {
        boolean correct = gameService.sendGuess(username, letter);
        GameStateDTO state = gameService.getGameState(username);
        // If the round is over after this guess, call finishRound
        if (state.roundOver) {
            boolean guessedWord = !state.maskedWord.contains("_");
            finishRound(clientRemainingTime, guessedWord);
        }
        return correct;
    }

    public void finishRound(int clientRemainingTime, boolean guessedWord) {
        gameService.finishRound(username, clientRemainingTime, guessedWord);
    }

    // Listener setters
    public void setMatchListener(MatchListener listener) {
        this.matchListener = listener;
    }


    public GameService getGameService() {
        return gameService;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }
}
