package client.player.console.model;

import GameModule.GameService;
import GameModule.GameStateDTO;
import GameModule.Bool;

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
                            matchListener.onMatchFound(currentMaskedWord);
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
                    matchListener.onMatchTimeout();
                }
            }
        });

        matchWaitThread.setDaemon(true);
        matchWaitThread.start();
    }

    public boolean makeGuess(char letter, int clientRemainingTime) {
        GameModule.Bool correctBool = gameService.sendGuess(username, letter);
        return correctBool.value() == GameModule.Bool.BOOL_TRUE.value();
    }

    public void finishRound(int clientRemainingTime, GameModule.Bool guessedWord) {
        gameService.finishRound(username, clientRemainingTime, guessedWord);
    }

    // Listener setters
    public void setMatchListener(MatchListener listener) {
        this.matchListener = listener;
    }

    public void playerReadyForFirstRound() {
        if (username != null && !username.isEmpty()) {
            try {
                gameService.playerReadyForFirstRound(username);
            } catch (Exception e) {
                System.err.println("Error signaling player ready for first round: " + e.getMessage());
                // Optionally, notify the user or handle the error in a way that makes sense for the UI
            }
        }
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
