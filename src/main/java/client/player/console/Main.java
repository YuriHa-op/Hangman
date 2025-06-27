package client.player.console;

import client.player.console.model.LoginModel;
import client.player.console.model.MultiplayerGameModel;
import GameModule.GameService;
import GameModule.LeaderboardEntryDTO;
import LoginModule.Bool;
import LoginModule.AlreadyLoggedInException;
import org.omg.CORBA.ORB;
import java.util.Scanner;
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
        long lobbyStartTime = System.currentTimeMillis();
        while (sessionValid.get()) {
            multiModel.updateLobbyState();
            MultiplayerGameModel.LobbyState state = multiModel.getLastLobbyState();
            if (state == null) {
                System.out.println("Lost connection to server or lobby disbanded. Returning to menu.");
                return;
            }

            if ("CANCELLED".equalsIgnoreCase(state.getState())) {
                System.out.println("Lobby was cancelled. Returning to home menu.");
                return;
            }

                System.out.println("Players in lobby: " + state.getPlayers());
                if (state.getPlayers().size() > 1 && "STARTED".equalsIgnoreCase(state.getState())) {
                    System.out.println("Game starting!");
                multiModel.playerReadyForNextRound();
                    break; // Exit lobby wait loop
                }

            // Use server-provided queue time for timeout
            if (state.getQueueTimeSeconds() > 0 && (System.currentTimeMillis() - lobbyStartTime) / 1000 > state.getQueueTimeSeconds()) {
                System.out.println("Lobby timed out. Not enough players joined within the allowed time. Returning to home menu.");
                multiModel.leaveGame(); // Signal server that client is leaving
                return;
            }

            try { Thread.sleep(1000); } catch (InterruptedException ignored) {}
        }

        if (!sessionValid.get()) return;

        // Main game loop
        while (sessionValid.get()) {
            multiModel.updateLobbyState();
            MultiplayerGameModel.LobbyState state = multiModel.getLastLobbyState();

            if (state == null) {
                System.out.println("Lost connection to server. Returning to menu.");
                break;
            }

            // Check for game over using sessionResult (highest priority)
            String sessionResult = state.getStringFromGameState("sessionResult", "");
            if (sessionResult != null && !sessionResult.isEmpty() && !sessionResult.equalsIgnoreCase("ONGOING")) {
                System.out.println("\nGame Over!");
                String winner = state.getStringFromGameState("gameWinner", "");

                if ("WIN".equalsIgnoreCase(sessionResult)) {
                    System.out.println("Congratulations, you won the game!");
                } else if ("LOSE".equalsIgnoreCase(sessionResult)) {
                    System.out.println("Sorry, you lost the game.");
                    if (!winner.isEmpty()) {
                        System.out.println("Winner: " + winner);
                    }
                } else if ("DRAW".equalsIgnoreCase(sessionResult)) {
                    System.out.println("The game is a draw!");
                } else {
                    // Fallback for other states
                    if (!winner.isEmpty()) {
                    System.out.println("Winner: " + winner);
                    }
                }

                Map<String, Integer> scores = state.getScoresFromGameState();
                if (scores != null && !scores.isEmpty()) {
                    System.out.println("Final Scores:");
                    scores.forEach((player, score) -> System.out.println(player + ": " + score));
                }
                break; // Exit game loop
            }

            // --- Detect if the round has ended ---
            int currentRoundNum = state.getIntFromGameState("currentRound", -1);
            Boolean roundInProgressFlag = state.getGameState() != null && Boolean.TRUE.equals(state.getGameState().get("roundInProgress"));

            boolean isRoundOver = currentRoundNum >= 0 && !roundInProgressFlag;

            if (isRoundOver) {
                String roundWinner = state.getStringFromGameState("roundWinner", "");
                System.out.println("\nRound Over!");
                if (roundWinner != null && !roundWinner.isEmpty()) {
                    System.out.println("Winner: " + roundWinner);
                } else {
                    System.out.println("No winner this round.");
                }
                System.out.println("Press Enter to advance to the next round...");
                scanner.nextLine();
                multiModel.playerReadyForNextRound(); // Signal ready for next round

                // Wait for the server to transition to the next round
                long waitStartTime = System.currentTimeMillis();
                final long MAX_WAIT_FOR_NEXT_ROUND_MS = 10 * 1000; // Wait up to 10 seconds

                while (sessionValid.get()) {
                    multiModel.updateLobbyState();
                    MultiplayerGameModel.LobbyState newState = multiModel.getLastLobbyState();

                    if (newState == null) {
                        System.out.println("Lost connection to server while waiting for next round. Returning to menu.");
                        return; // Exit playMultiplayer method
                    }

                    // Detect if the next round has begun
                    Boolean newRoundInProgress = newState.getGameState() != null && Boolean.TRUE.equals(newState.getGameState().get("roundInProgress"));
                    int nextRoundNum = newState.getIntFromGameState("currentRound", -1);

                    // If round is in progress AND it's a different round number, we can proceed
                    if (Boolean.TRUE.equals(newRoundInProgress) && nextRoundNum != currentRoundNum) {
                        System.out.println("New round detected. Proceeding...");
                        break; // Exit wait loop, continue main game loop
                    }

                    if (System.currentTimeMillis() - waitStartTime > MAX_WAIT_FOR_NEXT_ROUND_MS) {
                        System.out.println("Timed out waiting for next round to start. Returning to home menu.");
                        return; // Exit playMultiplayer method
                    }

                    try { Thread.sleep(500); } catch (InterruptedException ignored) {} // Shorter sleep for faster polling
                }
                continue;
            }

            // Check if waiting for round to start
            Boolean roundInProgress = state.getGameState() != null && Boolean.TRUE.equals(state.getGameState().get("roundInProgress"));
            if (!roundInProgress) {
                System.out.println("Waiting for next round to start...");
                try { Thread.sleep(1000); } catch (InterruptedException ignored) {}
                continue;
            }

            // --- Round is in progress ---
            int timeLeft = state.getIntFromGameState("remainingTime", 0);
            System.out.println("\n--- Round " + (state.getIntFromGameState("currentRound", 0) + 1) + " ---");
            System.out.println("Word: " + state.getPlayerMaskedWord(username));
            System.out.println("Incorrect guesses: " + state.getPlayerIncorrectGuesses(username) + "/" + state.getIntFromGameState("maxIncorrectGuesses", 5));
            System.out.println("Time left: " + timeLeft + " seconds");
            System.out.print("Guessed letters: ");
            state.getPlayerGuesses(username).forEach(c -> System.out.print(c + " "));
            System.out.println();

            // If time is up, don't ask for input, just wait for server to end the round
            if (timeLeft <= 0) {
                try { Thread.sleep(1000); } catch (InterruptedException ignored) {}
                continue;
            }

            // Accept guess
            System.out.print("Enter a letter: ");
            String input = scanner.nextLine();
            if (!sessionValid.get()) break;

            if (input.length() != 1 || !Character.isLetter(input.charAt(0))) {
                System.out.println("Please enter a single letter.");
                continue;
            }
            char guess = Character.toLowerCase(input.charAt(0));
            if (state.getPlayerGuesses(username).contains(guess)) {
                System.out.println("You already guessed that letter.");
                continue;
            }

            boolean correct = multiModel.makeGuess(guess);
            System.out.println(correct ? "Correct!" : "Incorrect!");
        }
        System.out.println("Returning to home menu.");
    }

    private static void showLeaderboard(GameService gameService) {
        try {
            LeaderboardEntryDTO[] entries = gameService.getLeaderboardEntries();
            System.out.println("\n--- Leaderboard ---");
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
            String historyJson = gameService.getMatchHistory(username);
            System.out.println("\n--- Multiplayer Match History ---");
            if (historyJson == null || historyJson.trim().isEmpty() || historyJson.trim().equals("[]")) {
                System.out.println("No match history found.");
                return;
            }

            java.lang.reflect.Type listType = new TypeToken<java.util.List<java.util.Map<String, Object>>>(){}.getType();
            java.util.List<java.util.Map<String, Object>> matches = gson.fromJson(historyJson, listType);

            if (matches.isEmpty()) {
                System.out.println("No match history found.");
                return;
            }

            for (int i = 0; i < matches.size(); i++) {
                Map<String, Object> match = matches.get(i);
                String gameId = (String) match.get("gameId");
                long endTime = ((Double) match.get("gameEndTime")).longValue();
                String winner = (String) match.get("overallWinner");
                java.util.List<String> players = (java.util.List<String>) match.get("players");

                String result = "DRAW";
                if (winner != null) {
                    result = winner.equals(username) ? "WIN" : "LOSE";
                }

                System.out.printf("%d. Game ID: %s\n", i + 1, gameId);
                System.out.printf("   Date: %s\n", new java.util.Date(endTime));
                System.out.printf("   Players: %s\n", String.join(", ", players));
                System.out.printf("   Winner: %s\n", winner != null ? winner : "Unknown");
                System.out.printf("   Your Result: %s\n\n", result);
            }

            while (true) {
                System.out.print("Enter game number to view details (or 0 to return): ");
                String choice = scanner.nextLine();
                if (!sessionValid.get()) break;
                try {
                    int gameNum = Integer.parseInt(choice);
                    if (gameNum == 0) {
                        break;
                    }
                    if (gameNum > 0 && gameNum <= matches.size()) {
                        String gameId = (String) matches.get(gameNum - 1).get("gameId");
                        showMatchDetails(gameId, gameService);
                        // After viewing, re-display the list header for clarity
                        System.out.println("\n--- Multiplayer Match History ---");
                        for (int i = 0; i < matches.size(); i++) {
                            Map<String, Object> match = matches.get(i);
                            String mGameId = (String) match.get("gameId");
                            long mEndTime = ((Double) match.get("gameEndTime")).longValue();
                            String mWinner = (String) match.get("overallWinner");
                            java.util.List<String> mPlayers = (java.util.List<String>) match.get("players");
                            String mResult = "DRAW";
                            if (mWinner != null) {
                                mResult = mWinner.equals(username) ? "WIN" : "LOSE";
                            }
                            System.out.printf("%d. Game ID: %s\n", i + 1, mGameId);
                            System.out.printf("   Date: %s\n", new java.util.Date(mEndTime));
                            System.out.printf("   Players: %s\n", String.join(", ", mPlayers));
                            System.out.printf("   Winner: %s\n", mWinner != null ? mWinner : "Unknown");
                            System.out.printf("   Your Result: %s\n\n", mResult);
                        }
                    } else {
                        System.out.println("Invalid number.");
                    }
                } catch (NumberFormatException e) {
                    System.out.println("Invalid input. Please enter a number.");
                }
            }
        } catch (Exception e) {
            System.out.println("Could not load match history: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private static void showMatchDetails(String gameId, GameService gameService) {
        System.out.println("\n--- Match Details ---");
        try {
            String detailsJson = gameService.getMatchDetails(gameId);
            if (detailsJson == null || detailsJson.trim().isEmpty()) {
                System.out.println("Could not retrieve details for game " + gameId);
                return;
            }

            java.lang.reflect.Type mapType = new TypeToken<java.util.Map<String, Object>>(){}.getType();
            Map<String, Object> details = gson.fromJson(detailsJson, mapType);

            long endTime = ((Double) details.get("gameEndTime")).longValue();
            java.util.List<String> players = (java.util.List<String>) details.get("players");
            String winner = (String) details.get("overallWinner");
            int totalRounds = ((Double) details.get("totalRounds")).intValue();

            System.out.printf("Game ID: %s\n", details.get("gameId"));
            System.out.printf("Date: %s\n", new java.util.Date(endTime));
            System.out.printf("Players: %s\n", String.join(", ", players));
            System.out.printf("Winner: %s\n", winner != null ? winner : "None");
            System.out.printf("Total Rounds: %d\n", totalRounds);

            System.out.println("\nRounds:");
            java.util.List<Map<String, Object>> rounds = (java.util.List<Map<String, Object>>) details.get("rounds");
            if (rounds != null) {
                for (Map<String, Object> round : rounds) {
                    int roundNum = ((Double) round.get("roundNumber")).intValue();
                    String word = (String) round.get("word");
                    String roundWinner = (String) round.get("winner");
                    System.out.printf("  Round %d: Word = %s, Winner = %s\n", roundNum, word, roundWinner != null ? roundWinner : "None");
                }
            }

            System.out.print("\nPress Enter to return...");
            scanner.nextLine();

        } catch (Exception e) {
            System.out.println("Error retrieving match details: " + e.getMessage());
            e.printStackTrace();
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