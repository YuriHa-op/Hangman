package server.game.exception;

public class AlreadyLoggedInException extends Exception {
    public AlreadyLoggedInException(String message) {
        super(message);
    }
} 