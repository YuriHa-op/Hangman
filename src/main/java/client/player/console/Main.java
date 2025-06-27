package client.player;

import client.player.model.LoginModel;
import client.player.model.GameModel;
import client.player.model.MultiplayerGameModel;
import GameModule.GameService;
import GameModule.GameStateDTO;
import GameModule.LeaderboardEntryDTO;
import LoginModule.Bool;
import LoginModule.AlreadyLoggedInException;
import org.omg.CORBA.ORB;
import java.util.Scanner;
import java.util.HashSet;
import java.util.Set;
import java.util.Map;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.Executors;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.TimeUnit;
import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;

public class Main {
    private static LoginModel loginModel;
    private static Scanner scanner = new Scanner(System.in);
    private static AtomicBoolean sessionValid = new AtomicBoolean(true);
    private static ExecutorService sessionChecker = Executors.newSingleThreadExecutor();
    private static Gson gson = new Gson();

    public static void main(String[] args) {
        // Default CORBA params
        String host = "localhost";
        String port = "900";
        for (int i = 0; i < args.length; i++) {
            if (args[i].equals("-ORBInitialHost") && i + 1 < args.length) host = args[i + 1];
            if (args[i].equals("-ORBInitialPort") && i + 1 < args.length) port = args[i + 1];
        }
        String[] orbArgs = {"-ORBInitialHost", host, "-ORBInitialPort", port};
        ORB orb = ORB.init(orbArgs, null);
        try {
            loginModel = new LoginModel(orb);
            if (loginModel.getGameService() == null || loginModel.getLoginService() == null) {
                System.err.println("\nCould not connect to the server. Please make sure the server and ORB are running, then try again.");
                System.exit(1);
            }
        } catch (Exception e) {
            System.err.println("\nFatal error: Unable to connect to the server.\n" + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
        while (true) {
            System.out.println("\nWelcome to Hangman Multiplayer!");
            System.out.println("1. Login");
            System.out.println("2. Sign Up");
            System.out.println("3. Exit");
            System.out.print("Select option: ");
            String choice = scanner.nextLine();
            if (choice.equals("1")) {
                if (login()) homeMenu();
            } else if (choice.equals("2")) {
                signUp();
            } else if (choice.equals("3")) {
                System.out.println("Goodbye!");
                break;
            } else {
                System.out.println("Invalid option.");
            }
        }
    }

    private static boolean login() {
        System.out.print("Username: ");
        String username = scanner.nextLine();
        System.out.print("Password: ");
        String password = scanner.nextLine();
        try {
            Bool result = loginModel.login(username, password);
            if (result == Bool.BOOL_TRUE) {
                System.out.println("Login successful!");
                startSessionChecker();
                return true;
            } else {
                System.out.println("Login failed. Check your credentials.");
            }
        } catch (AlreadyLoggedInException e) {
            System.out.println("Account already logged in elsewhere.");
            System.out.print("Do you want to force logout the previous session and login here? (y/n): ");
            String ans = scanner.nextLine();
            if (ans.trim().equalsIgnoreCase("y")) {
                Bool forceResult = loginModel.forceLogin(username, password);
                if (forceResult == Bool.BOOL_TRUE) {
                    System.out.println("Force login successful!");
                    startSessionChecker();
                    return true;
                } else {
                    System.out.println("Force login failed.");
                }
            }
        } catch (Exception e) {
            System.out.println("Login error: " + e.getMessage());
        }
        return false;
    }

    private static void signUp() {
        System.out.print("Choose a username: ");
        String username = scanner.nextLine();
        System.out.print("Choose a password: ");
        String password = scanner.nextLine();
        try {
            Bool result = loginModel.createPlayer(username, password);
            if (result == Bool.BOOL_TRUE) {
                System.out.println("Account created! You can now log in.");
            } else {
                System.out.println("Account creation failed. Username may already exist.");
            }
        } catch (Exception e) {
            System.out.println("Sign up error: " + e.getMessage());
        }
    }

    private static void homeMenu() {
        String username = loginModel.getLoggedInUser();
        GameService gameService = loginModel.getGameService();
        while (sessionValid.get()) {
            System.out.println("\nHome Menu");
            System.out.println("1. Play Multiplayer");
            System.out.println("2. View Leaderboard");
            System.out.println("3. View Match History");
            System.out.println("4. Logout");
            System.out.print("Select option: ");
            String choice = scanner.nextLine();
            if (!sessionValid.get()) break;
            if (choice.equals("1")) {
                try {
                    playMultiplayer(username, gameService);
                } catch (Exception e) {
                    System.out.println("Error during multiplayer: " + e.getMessage());
                }
            } else if (choice.equals("2")) {
                try {
                    showLeaderboard(gameService);
                } catch (Exception e) {
                    System.out.println("Error loading leaderboard: " + e.getMessage());
                }
            } else if (choice.equals("3")) {
                try {
                    showMatchHistory(username, gameService);
                } catch (Exception e) {
                    System.out.println("Error loading match history: " + e.getMessage());
                }
            } else if (choice.equals("4")) {
                loginModel.logout();
                sessionValid.set(false);
                System.out.println("Logged out.");
                break;
            } else {
                System.out.println("Invalid option.");
            }
        }
    }

    private static void playMultiplayer(String username, GameService gameService) {
        MultiplayerGameModel multiModel = new MultiplayerGameModel(gameService, username);
        multiModel.startGame();
        System.out.println("Waiting for other players to join the lobby...");
        // Wait for enough players and lobby to start
        while (true) {
            multiModel.updateLobbyState();
            MultiplayerGameModel.LobbyState state = multiModel.getLastLobbyState();
            if (state != null && state.getPlayers() != null) {
                System.out.println("Players in lobby: " + state.getPlayers());
                if (state.getPlayers().size() > 1 && "STARTED".equalsIgnoreCase(state.getState())) {
                    System.out.println("Game starting!");
                    multiModel.playerReadyForFirstRound();
                    // Wait for the first round to actually start
                    while (true) {
                        multiModel.updateLobbyState();
                        MultiplayerGameModel.LobbyState roundState = multiModel.getLastLobbyState();
                        String maskedWord = roundState.getPlayerMaskedWord(username);
                        Boolean roundInProgress = roundState.getGameState() != null && Boolean.TRUE.equals(roundState.getGameState().get("roundInProgress"));
                        if (maskedWord != null && !maskedWord.isEmpty() && maskedWord.contains("_ ") && roundInProgress != null && roundInProgress) {
                            break;
                        }
                        try { Thread.sleep(500); } catch (InterruptedException ignored) {}
                    }
                    break;
                }
            }
            try { Thread.sleep(1000); } catch (InterruptedException ignored) {}
        }
        // Main game loop: handle rounds until game over
        while (true) {
            multiModel.updateLobbyState();
            MultiplayerGameModel.LobbyState state = multiModel.getLastLobbyState();
            if (state == null) {
                System.out.println("Lost connection to server or lobby. Returning to menu.");
                break;
            }
            // Check for game over
            String gameResult = state.getStringFromGameState("sessionResult", null);
            Boolean isGameOver = state.getGameState() != null && Boolean.TRUE.equals(state.getGameState().get("gameOver"));
            if (isGameOver || (gameResult != null && !gameResult.isEmpty() && !"ONGOING".equalsIgnoreCase(gameResult))) {
                System.out.println("\nGame Over! Result: " + gameResult);
                Map<String, Integer> scores = state.getScoresFromGameState();
                if (scores != null && !scores.isEmpty()) {
                    System.out.println("Final Scores:");
                    for (Map.Entry<String, Integer> entry : scores.entrySet()) {
                        System.out.println(entry.getKey() + ": " + entry.getValue());
                    }
                }
                String winner = state.getStringFromGameState("gameWinner", "");
                if (winner != null && !winner.isEmpty()) {
                    System.out.println("Winner: " + winner);
                }
                break;
            }
            // Wait for round to be in progress
            Boolean roundInProgress = state.getGameState() != null && Boolean.TRUE.equals(state.getGameState().get("roundInProgress"));
            if (roundInProgress == null || !roundInProgress) {
                // Wait for the next round to start
                System.out.println("Waiting for next round to start...");
                while (true) {
                    multiModel.updateLobbyState();
                    MultiplayerGameModel.LobbyState nextState = multiModel.getLastLobbyState();
                    Boolean nextRoundInProgress = nextState.getGameState() != null && Boolean.TRUE.equals(nextState.getGameState().get("roundInProgress"));
                    if (nextRoundInProgress != null && nextRoundInProgress) {
                        break;
                    }
                    try { Thread.sleep(500); } catch (InterruptedException ignored) {}
                }
                continue;
            }
            // Show current round state
            String maskedWord = state.getPlayerMaskedWord(username);
            int incorrectGuesses = state.getPlayerIncorrectGuesses(username);
            Set<Character> alreadyGuessed = state.getPlayerGuesses(username);
            int maxGuesses = state.getIntFromGameState("maxIncorrectGuesses", 5);
            int timeLeft = state.getIntFromGameState("remainingTime", 0);
            System.out.println("\n--- Round " + (state.getIntFromGameState("currentRound", 0) + 1) + " ---");
            System.out.println("Word: " + maskedWord);
            System.out.println("Incorrect guesses: " + incorrectGuesses + "/" + maxGuesses);
            System.out.println("Time left: " + timeLeft + " seconds");
            System.out.print("Guessed letters: ");
            for (char c : alreadyGuessed) System.out.print(c + " ");
            System.out.println();
            // Accept guess
            System.out.print("Enter a letter: ");
            String input = scanner.nextLine();
            if (input.length() != 1 || !Character.isLetter(input.charAt(0))) {
                System.out.println("Please enter a single letter.");
                continue;
            }
            char guess = Character.toLowerCase(input.charAt(0));
            if (alreadyGuessed.contains(guess)) {
                System.out.println("You already guessed that letter.");
                continue;
            }
            boolean correct = multiModel.makeGuess(guess);
            if (correct) {
                System.out.println("Correct!");
            } else {
                System.out.println("Incorrect!");
            }
            // Check for round over
            Boolean isRoundOver = state.getGameState() != null && Boolean.TRUE.equals(state.getGameState().get("roundOver"));
            if (isRoundOver != null && isRoundOver) {
                String roundWinner = state.getStringFromGameState("roundWinner", "");
                System.out.println("\nRound Over!");
                if (roundWinner != null && !roundWinner.isEmpty()) {
                    System.out.println("Winner: " + roundWinner);
                } else {
                    System.out.println("No winner this round.");
                }
                System.out.println("Press Enter to continue to the next round...");
                scanner.nextLine();
                multiModel.playerReadyForFirstRound(); // Signal ready for next round
            }
        }
        System.out.println("Returning to home menu.");
    }

    private static void showLeaderboard(GameService gameService) {
        try {
            LeaderboardEntryDTO[] entries = gameService.getLeaderboardEntries();
            System.out.println("\nLeaderboard:");
            System.out.printf("%-5s %-20s %-5s\n", "Rank", "Username", "Wins");
            for (int i = 0; i < entries.length; i++) {
                System.out.printf("%-5d %-20s %-5d\n", i + 1, entries[i].username, entries[i].wins);
            }
        } catch (Exception e) {
            System.out.println("Could not load leaderboard: " + e.getMessage());
        }
    }

    private static void showMatchHistory(String username, GameService gameService) {
        try {
            String history = gameService.getMatchHistory(username);
            System.out.println("\nMatch History:");
            if (history == null || history.trim().isEmpty()) {
                System.out.println("No match history found.");
                return;
            }
            // Try to parse as JSON array of objects
            try {
                java.lang.reflect.Type listType = new TypeToken<java.util.List<java.util.Map<String, Object>>>(){}.getType();
                java.util.List<java.util.Map<String, Object>> matches = gson.fromJson(history, listType);
                int idx = 1;
                for (java.util.Map<String, Object> match : matches) {
                    System.out.println("Match " + idx + ":");
                    for (Map.Entry<String, Object> entry : match.entrySet()) {
                        System.out.printf("  %s: %s\n", entry.getKey(), entry.getValue());
                    }
                    System.out.println();
                    idx++;
                }
            } catch (Exception e) {
                // Fallback: print raw string
                System.out.println(history);
            }
        } catch (Exception e) {
            System.out.println("Could not load match history: " + e.getMessage());
        }
    }

    private static void startSessionChecker() {
        sessionValid.set(true);
        sessionChecker.shutdownNow();
        sessionChecker = Executors.newSingleThreadExecutor();
        sessionChecker.submit(() -> {
            while (sessionValid.get()) {
                try {
                    TimeUnit.SECONDS.sleep(5);
                    if (!loginModel.validateSession()) {
                        sessionValid.set(false);
                        System.out.println("\nSession invalidated (possibly logged in elsewhere or server disconnected). Returning to login screen.");
                        loginModel.logout();
                        break;
                    }
                } catch (InterruptedException ignored) {
                    break;
                } catch (Exception e) {
                    System.out.println("\nSession check error: " + e.getMessage());
                }
            }
        });
    }
} 