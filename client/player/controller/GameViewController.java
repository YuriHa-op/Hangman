public void onMatchFound(String maskedWord) {
    try {
        showGameUI();
        if (maskedWord != null) {
            wordDisplay.setText(maskedWord);
            updateHangmanImage(0);
            stopTimerIfRunning(); // Good
            String opponent = getOpponentUsername(); 
            if (opponent == null || opponent.isEmpty()) opponent = "Opponent";
            
            MatchFoundDialogController.showDialog(stage, username, opponent, () -> { // Callback for when dialog closes
                stopTimerIfRunning(); 
                GameStateDTO stateAfterDialog = model.getGameState(); // <-- FETCH LATEST STATE HERE
                gameTimerHelper = new GameTimerHelper(timerLabel, this::handleTimeUp);
                if (stateAfterDialog != null) { // Check if state is not null
                    gameTimerHelper.startRoundTimer(gameService.getRoundTime(), stateAfterDialog.remainingTime);
                } else {
                    // Handle case where state is null, perhaps log an error or default
                    System.err.println("Error: GameStateDTO was null after match found dialog.");
                    gameTimerHelper.startRoundTimer(gameService.getRoundTime(), gameService.getRoundTime()); // Fallback to full time
                }
                GameViewHelper.animateWordDisplay(wordDisplay);
            });
        }
    } catch (Exception e) {
        // ... existing code ...
    }
} 