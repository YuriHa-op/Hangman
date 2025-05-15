package server.dto;

import java.io.Serializable;

public class GameStateDTO implements Serializable {
    public String maskedWord;
    public int incorrectGuesses;
    public int currentRound;
    public int totalRounds;
    public int playerWins;
    public boolean roundOver;
    public boolean gameOver;
    public String sessionResult; // "WIN", "LOSE", "DRAW", "ONGOING", etc.
    public int remainingTime;
    public String roundWinner; // Usernam
    public int finishedTime; // Time left
} 