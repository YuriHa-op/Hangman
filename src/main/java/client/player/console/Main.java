package client.player.console;

import client.player.console.model.LoginModel;
import client.player.console.model.GameModel;
import client.player.console.model.MultiplayerGameModel;
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

    // Helper method for Java 8 compatibility (replaces String.repeat())
    private static String repeat(String str, int count) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < count; i++) {
            sb.append(str);
        }
        return sb.toString();
    }

    // ASCII Art for Hangman
    private static final String[] HANGMAN_ART = {
            "  +---+\n  |   |\n      |\n      |\n      |\n      |\n=========",
            "  +---+\n  |   |\n  O   |\n      |\n      |\n      |\n=========",
            "  +---+\n  |   |\n  O   |\n  |   |\n      |\n      |\n=========",
            "  +---+\n  |   |\n  O   |\n /|   |\n      |\n      |\n=========",
            "  +---+\n  |   |\n  O   |\n /|\\  |\n      |\n      |\n=========",
            "  +---+\n  |   |\n  O   |\n /|\\  |\n /    |\n      |\n=========",
            "  +---+\n  |   |\n  O   |\n /|\\  |\n / \\  |\n      |\n========="
    };

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

        showWelcomeScreen();

        while (true) {
            System.out.println("\n" + repeat("=", 50));
            System.out.println("🎮 HANGMAN MULTIPLAYER GAME 🎮");
            System.out.println(repeat("=", 50));
            System.out.println("1. Login");
            System.out.println("2. Sign Up");
            System.out.println("3. Exit");
            System.out.println(repeat("-", 50));
            System.out.print("Select option: ");
            String choice = scanner.nextLine();
            if (choice.equals("1")) {
                if (login()) homeMenu();
            } else if (choice.equals("2")) {
                signUp();
            } else if (choice.equals("3")) {
                System.out.println("👋 Goodbye! Thanks for playing!");
                break;
            } else {
                System.out.println("❌ Invalid option. Please try again.");
            }
        }
    }

    private static void showWelcomeScreen() {
        System.out.println("\n" + repeat("🎯", 25));
        System.out.println("    WELCOME TO HANGMAN MULTIPLAYER!");
        System.out.println(repeat("🎯", 25));
        System.out.println("\n" + HANGMAN_ART[0]);
        System.out.println("\n🎮 Features:");
        System.out.println("  • Single Player 1v1 Mode");
        System.out.println("  • Multiplayer Mode");
        System.out.println("  • Real-time Leaderboards");
        System.out.println("  • Match History");
        System.out.println("  • Session Management");
        System.out.println("\n" + repeat("🎯", 25));
    }

    private static boolean login() {
        System.out.println("\n" + repeat("🔐", 20));
        System.out.println("        LOGIN");
        System.out.println(repeat("🔐", 20));
        System.out.print("Username: ");
        String username = scanner.nextLine();
        System.out.print("Password: ");
        String password = scanner.nextLine();
        try {
            Bool result = loginModel.login(username, password);
            if (result == Bool.BOOL_TRUE) {
                System.out.println("✅ Login successful!");
                startSessionChecker();
                return true;
            } else {
                System.out.println("❌ Login failed. Check your credentials.");
            }
        } catch (AlreadyLoggedInException e) {
            System.out.println("⚠️  Account already logged in elsewhere.");
            System.out.print("Do you want to force logout the previous session and login here? (y/n): ");
            String ans = scanner.nextLine();
            if (ans.trim().equalsIgnoreCase("y")) {
                Bool forceResult = loginModel.forceLogin(username, password);
                if (forceResult == Bool.BOOL_TRUE) {
                    System.out.println("✅ Force login successful!");
                    startSessionChecker();
                    return true;
                } else {
                    System.out.println("❌ Force login failed.");
                }
            }
        } catch (Exception e) {
            System.out.println("❌ Login error: " + e.getMessage());
        }
        return false;
    }

    private static void signUp() {
        System.out.println("\n" + repeat("📝", 20));
        System.out.println("        CREATE ACCOUNT");
        System.out.println(repeat("📝", 20));
        System.out.print("Choose a username: ");
        String username = scanner.nextLine();
        System.out.print("Choose a password: ");
        String password = scanner.nextLine();
        try {
            Bool result = loginModel.createPlayer(username, password);
            if (result == Bool.BOOL_TRUE) {
                System.out.println("✅ Account created! You can now log in.");
            } else {
                System.out.println("❌ Account creation failed. Username may already exist.");
            }
        } catch (Exception e) {
            System.out.println("❌ Sign up error: " + e.getMessage());
        }
    }

    private static void homeMenu() {
        String username = loginModel.getLoggedInUser();
        GameService gameService = loginModel.getGameService();
        while (sessionValid.get()) {
            System.out.println("\n" + repeat("🏠", 20));
            System.out.println("        HOME MENU");
            System.out.println(repeat("🏠", 20));
            System.out.println("👤 Welcome, " + username + "!");
            System.out.println(repeat("-", 40));
            System.out.println("1. 🎯 Play Single Player (1v1)");
            System.out.println("2. 🌐 Play Multiplayer");
            System.out.println("3. 🏆 View Leaderboard");
            System.out.println("4. 📊 View Match History");
            System.out.println("5. ⚙️  Game Settings");
            System.out.println("6. 🚪 Logout");
            System.out.println(repeat("-", 40));
            System.out.print("Select option: ");
            String choice = scanner.nextLine();
            if (!sessionValid.get()) break;
            if (choice.equals("1")) {
                try {
                    playSinglePlayer1v1(username, gameService);
                } catch (Exception e) {
                    System.out.println("❌ Error during single player: " + e.getMessage());
                }
            } else if (choice.equals("2")) {
                try {
                    playMultiplayer(username, gameService);
                } catch (Exception e) {
                    System.out.println("❌ Error during multiplayer: " + e.getMessage());
                }
            } else if (choice.equals("3")) {
                try {
                    showLeaderboard(gameService);
                } catch (Exception e) {
                    System.out.println("❌ Error loading leaderboard: " + e.getMessage());
                }
            } else if (choice.equals("4")) {
                try {
                    showMatchHistory(username, gameService);
                } catch (Exception e) {
                    System.out.println("❌ Error loading match history: " + e.getMessage());
                }
            } else if (choice.equals("5")) {
                showGameSettings(gameService);
            } else if (choice.equals("6")) {
                loginModel.logout();
                sessionValid.set(false);
                System.out.println("👋 Logged out successfully.");
                break;
            } else {
                System.out.println("❌ Invalid option.");
            }
        }
    }

    private static void playSinglePlayer1v1(String username, GameService gameService) {
        System.out.println("\n" + repeat("🎯", 25));
        System.out.println("    SINGLE PLAYER 1v1 MODE");
        System.out.println(repeat("🎯", 25));
        System.out.println("🔍 Searching for opponent...");

        GameModel gameModel = new GameModel(gameService, username);
        gameModel.setMatchListener(new GameModel.MatchListener() {
            @Override
            public void onMatchFound(String maskedWord) {
                System.out.println("✅ Match found! Game starting...");
                System.out.println("🎯 Your word: " + maskedWord);
                gameModel.playerReadyForFirstRound();
                startSinglePlayerGameLoop(gameModel, username);
            }

            @Override
            public void onMatchTimeout() {
                System.out.println("⏰ No opponent found within the waiting time.");
                System.out.println("Returning to main menu...");
            }
        });

        gameModel.startNewGame();

        // Wait for match result
        try {
            Thread.sleep(1000);
            while (true) {
                GameStateDTO gameState = gameService.getGameState(username);
                if (gameState != null && gameState.gameOver.value() == GameModule.Bool.BOOL_TRUE.value()) {
                    break;
                }
                Thread.sleep(500);
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    private static void startSinglePlayerGameLoop(GameModel gameModel, String username) {
        GameService gameService = gameModel.getGameService();
        Set<Character> guessedLetters = new HashSet<>();
        int roundNumber = 1;

        while (true) {
            try {
                GameStateDTO gameState = gameService.getGameState(username);
                if (gameState == null) {
                    System.out.println("❌ Lost connection to server.");
                    break;
                }

                if (gameState.gameOver.value() == GameModule.Bool.BOOL_TRUE.value()) {
                    showSinglePlayerGameResults(gameState);
                    break;
                }

                if (gameState.roundOver.value() == GameModule.Bool.BOOL_TRUE.value()) {
                    showRoundResults(gameState, roundNumber);
                    roundNumber++;
                    gameModel.playerReadyForFirstRound();
                    guessedLetters.clear();
                    continue;
                }

                // Check if player has reached maximum incorrect guesses (5/5)
                if (gameState.incorrectGuesses >= 5) {
                    System.out.println("\n💀 You've reached the maximum incorrect guesses (5/5)!");
                    System.out.println("🏁 Round ending automatically...");
                    // Signal to server that round should end
                    gameModel.finishRound(0, GameModule.Bool.BOOL_FALSE);
                    // Wait a moment for server to process
                    try { Thread.sleep(1000); } catch (InterruptedException ignored) {}
                    continue;
                }

                // Display current game state
                displaySinglePlayerGameState(gameState, guessedLetters);

                // Get player input
                System.out.print("🎯 Enter a letter: ");
                String input = scanner.nextLine();

                if (input.length() != 1 || !Character.isLetter(input.charAt(0))) {
                    System.out.println("❌ Please enter a single letter.");
                    continue;
                }

                char guess = Character.toLowerCase(input.charAt(0));
                if (guessedLetters.contains(guess)) {
                    System.out.println("⚠️  You already guessed that letter.");
                    continue;
                }

                guessedLetters.add(guess);
                GameModule.Bool correctBool = gameService.sendGuess(username, guess);
                boolean correct = correctBool.value() == GameModule.Bool.BOOL_TRUE.value();

                if (correct) {
                    System.out.println("✅ Correct!");
                } else {
                    System.out.println("❌ Incorrect!");
                }

                // Small delay to let server process the guess
                try { Thread.sleep(500); } catch (InterruptedException ignored) {}

            } catch (Exception e) {
                System.out.println("❌ Error during game: " + e.getMessage());
                break;
            }
        }
    }

    private static void displaySinglePlayerGameState(GameStateDTO gameState, Set<Character> guessedLetters) {
        System.out.println("\n" + repeat("🎮", 30));
        System.out.println("        ROUND " + gameState.currentRound + "/" + gameState.totalRounds);
        System.out.println(repeat("🎮", 30));

        // Show hangman art based on incorrect guesses
        int incorrectGuesses = (int) gameState.incorrectGuesses;
        System.out.println(HANGMAN_ART[Math.min(incorrectGuesses, HANGMAN_ART.length - 1)]);

        System.out.println("🎯 Word: " + gameState.maskedWord);
        System.out.println("⏰ Time left: " + gameState.remainingTime + " seconds");
        System.out.println("❌ Incorrect guesses: " + gameState.incorrectGuesses + "/5");
        System.out.println("🏆 Your Score: " + gameState.playerWins);
        System.out.println("👥 Opponent: " + gameState.opponentUsername);

        if (!guessedLetters.isEmpty()) {
            System.out.print("🔤 Guessed letters: ");
            for (char c : guessedLetters) {
                System.out.print(c + " ");
            }
            System.out.println();
        }
        System.out.println(repeat("-", 40));
    }

    private static void showRoundResults(GameStateDTO gameState, int roundNumber) {
        System.out.println("\n" + repeat("🏁", 25));
        System.out.println("        ROUND " + (roundNumber - 1) + " COMPLETE");
        System.out.println(repeat("🏁", 25));

        if (gameState.roundWinner != null && !gameState.roundWinner.isEmpty()) {
            System.out.println("🏆 Round Winner: " + gameState.roundWinner);
        } else {
            System.out.println("🤝 Round ended in a tie");
        }

        System.out.println("⏱️  Time taken: " + (30 - gameState.finishedTime) + " seconds");
        System.out.println("Press Enter to continue to next round...");
        scanner.nextLine();
    }

    private static void showSinglePlayerGameResults(GameStateDTO gameState) {
        System.out.println("\n" + repeat("🏆", 30));
        System.out.println("        GAME COMPLETE!");
        System.out.println(repeat("🏆", 30));

        System.out.println("📊 Final Result: " + gameState.sessionResult);
        System.out.println("🏆 Your wins: " + gameState.playerWins);
        System.out.println("👥 Opponent wins: " + (gameState.totalRounds - gameState.playerWins));

        if (gameState.sessionResult != null && gameState.sessionResult.contains("WIN")) {
            System.out.println("🎉 Congratulations! You won!");
        } else if (gameState.sessionResult != null && gameState.sessionResult.contains("LOSE")) {
            System.out.println("😔 Better luck next time!");
        } else {
            System.out.println("🤝 It's a tie!");
        }

        System.out.println("Press Enter to return to main menu...");
        scanner.nextLine();
    }

    private static void showGameSettings(GameService gameService) {
        System.out.println("\n" + repeat("⚙️", 20));
        System.out.println("        GAME SETTINGS");
        System.out.println(repeat("⚙️", 20));

        try {
            int roundTime = gameService.getRoundTime();
            int waitingTime = gameService.getWaitingTime();

            System.out.println("⏰ Round Time: " + roundTime + " seconds");
            System.out.println("⏳ Waiting Time: " + waitingTime + " seconds");
            System.out.println("🎯 Max Incorrect Guesses: 5");
            System.out.println("🏆 Total Rounds: 3");

        } catch (Exception e) {
            System.out.println("❌ Error loading settings: " + e.getMessage());
        }

        System.out.println("Press Enter to return to main menu...");
        scanner.nextLine();
    }

    private static void playMultiplayer(String username, GameService gameService) {
        System.out.println("\n" + repeat("🌐", 25));
        System.out.println("    MULTIPLAYER MODE");
        System.out.println(repeat("🌐", 25));

        MultiplayerGameModel multiModel = new MultiplayerGameModel(gameService, username);
        multiModel.startGame();
        System.out.println("🔍 Waiting for other players to join the lobby...");

        // Wait for enough players and lobby to start
        while (true) {
            multiModel.updateLobbyState();
            MultiplayerGameModel.LobbyState state = multiModel.getLastLobbyState();
            if (state != null && state.getPlayers() != null) {
                System.out.println("👥 Players in lobby: " + state.getPlayers());
                if (state.getPlayers().size() > 1 && "STARTED".equalsIgnoreCase(state.getState())) {
                    System.out.println("🎮 Game starting!");
                    multiModel.playerReadyForNextRound();
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
                System.out.println("❌ Lost connection to server or lobby. Returning to menu.");
                break;
            }

            // Check for game over
            String gameResult = state.getStringFromGameState("sessionResult", null);
            Boolean isGameOver = state.getGameState() != null && Boolean.TRUE.equals(state.getGameState().get("gameOver"));
            if (isGameOver || (gameResult != null && !gameResult.isEmpty() && !"ONGOING".equalsIgnoreCase(gameResult))) {
                System.out.println("\n🏁 Game Over! Result: " + gameResult);
                Map<String, Integer> scores = state.getScoresFromGameState();
                if (scores != null && !scores.isEmpty()) {
                    System.out.println("📊 Final Scores:");
                    for (Map.Entry<String, Integer> entry : scores.entrySet()) {
                        System.out.println("  " + entry.getKey() + ": " + entry.getValue());
                    }
                }
                String winner = state.getStringFromGameState("gameWinner", "");
                if (winner != null && !winner.isEmpty()) {
                    System.out.println("🏆 Winner: " + winner);
                }
                break;
            }

            // Wait for round to be in progress
            Boolean roundInProgress = state.getGameState() != null && Boolean.TRUE.equals(state.getGameState().get("roundInProgress"));
            if (roundInProgress == null || !roundInProgress) {
                // Additional check: make sure we're not in the middle of a round
                String maskedWord = state.getPlayerMaskedWord(username);
                int timeLeft = state.getIntFromGameState("remainingTime", 0);

                // If we have a valid masked word and time left, the round is still active
                if (maskedWord != null && !maskedWord.isEmpty() && maskedWord.contains("_") && timeLeft > 0) {
                    // Round is still active, just continue
                    continue;
                }

                // Automatically start the next round instead of waiting
                System.out.println("⏳ Starting next round...");
                multiModel.startNextRound(); // Automatically start next round instead of waiting for input
                // Small delay to prevent rapid successive calls
                try { Thread.sleep(1000); } catch (InterruptedException ignored) {}
                continue;
            }

            // Show current round state
            String maskedWord = state.getPlayerMaskedWord(username);
            int incorrectGuesses = state.getPlayerIncorrectGuesses(username);
            Set<Character> alreadyGuessed = state.getPlayerGuesses(username);
            int maxGuesses = state.getIntFromGameState("maxIncorrectGuesses", 5);
            int timeLeft = state.getIntFromGameState("remainingTime", 0);

            // Validate that we have a proper masked word before proceeding
            if (maskedWord == null || maskedWord.isEmpty() || !maskedWord.contains("_")) {
                System.out.println("\n⏳ Waiting for round to be properly initialized...");
                try { Thread.sleep(1000); } catch (InterruptedException ignored) {}
                continue;
            }

            // Check for round over first (server-side round completion)
            Boolean isRoundOver = state.getGameState() != null && Boolean.TRUE.equals(state.getGameState().get("roundOver"));
            if (isRoundOver != null && isRoundOver) {
                // Handle round completion for ALL players
                String roundWinner = state.getStringFromGameState("roundWinner", "");
                System.out.println("\n🏁 Round Over!");
                if (roundWinner != null && !roundWinner.isEmpty()) {
                    System.out.println("🏆 Winner: " + roundWinner);
                } else {
                    System.out.println("🤝 No winner this round.");
                }
                System.out.println("⏳ Starting next round...");
                multiModel.startNextRound(); // Automatically start next round instead of waiting for input
                // Small delay to prevent rapid successive calls
                try { Thread.sleep(1000); } catch (InterruptedException ignored) {}
                continue;
            }

            // Check if this player has reached max incorrect guesses
            if (incorrectGuesses >= maxGuesses) {
                System.out.println("\n" + repeat("🎮", 30));
                System.out.println("        ROUND " + (state.getIntFromGameState("currentRound", 0) + 1));
                System.out.println(repeat("🎮", 30));

                // Show hangman art
                System.out.println(HANGMAN_ART[Math.min(incorrectGuesses, HANGMAN_ART.length - 1)]);

                System.out.println("🎯 Word: " + maskedWord);
                System.out.println("❌ Incorrect guesses: " + incorrectGuesses + "/" + maxGuesses);
                System.out.println("⏰ Time left: " + timeLeft + " seconds");
                System.out.print("🔤 Guessed letters: ");
                for (char c : alreadyGuessed) System.out.print(c + " ");
                System.out.println();

                System.out.println("\n💀 You've reached the maximum incorrect guesses!");
                System.out.println("⏳ Waiting for other players to finish their turns...");

                // Wait for round to end (other players still playing)
                try { Thread.sleep(2000); } catch (InterruptedException ignored) {}
                continue;
            }

            System.out.println("\n" + repeat("🎮", 30));
            System.out.println("        ROUND " + (state.getIntFromGameState("currentRound", 0) + 1));
            System.out.println(repeat("🎮", 30));

            // Show hangman art
            System.out.println(HANGMAN_ART[Math.min(incorrectGuesses, HANGMAN_ART.length - 1)]);

            System.out.println("🎯 Word: " + maskedWord);
            System.out.println("❌ Incorrect guesses: " + incorrectGuesses + "/" + maxGuesses);
            System.out.println("⏰ Time left: " + timeLeft + " seconds");
            System.out.println("🏆 Your Score: " + state.getScoresFromGameState().get(username));
            System.out.print("🔤 Guessed letters: ");
            for (char c : alreadyGuessed) System.out.print(c + " ");
            System.out.println();

            // Accept guess
            System.out.print("🎯 Enter a letter: ");
            String input = scanner.nextLine();
            if (input.length() != 1 || !Character.isLetter(input.charAt(0))) {
                System.out.println("❌ Please enter a single letter.");
                continue;
            }
            char guess = Character.toLowerCase(input.charAt(0));
            if (alreadyGuessed.contains(guess)) {
                System.out.println("⚠️  You already guessed that letter.");
                continue;
            }
            boolean correct = multiModel.makeGuess(guess);
            if (correct) {
                System.out.println("✅ Correct!");
            } else {
                System.out.println("❌ Incorrect!");
            }

            // Small delay to let server process the guess
            try { Thread.sleep(500); } catch (InterruptedException ignored) {}
        }
        System.out.println("🏠 Returning to home menu.");
    }

    private static void showLeaderboard(GameService gameService) {
        System.out.println("\n" + repeat("🏆", 25));
        System.out.println("        LEADERBOARD");
        System.out.println(repeat("🏆", 25));
        try {
            LeaderboardEntryDTO[] entries = gameService.getLeaderboardEntries();
            System.out.printf("%-5s %-20s %-5s\n", "Rank", "Username", "Wins");
            System.out.println(repeat("-", 35));
            for (int i = 0; i < entries.length; i++) {
                String rankSymbol = i == 0 ? "🥇" : i == 1 ? "🥈" : i == 2 ? "🥉" : "  ";
                System.out.printf("%-5s %-20s %-5d\n", rankSymbol + (i + 1), entries[i].username, entries[i].wins);
            }
        } catch (Exception e) {
            System.out.println("❌ Could not load leaderboard: " + e.getMessage());
        }
        System.out.println("Press Enter to return to main menu...");
        scanner.nextLine();
    }

    private static void showMatchHistory(String username, GameService gameService) {
        System.out.println("\n" + repeat("📊", 25));
        System.out.println("        MATCH HISTORY");
        System.out.println(repeat("📊", 25));
        try {
            String history = gameService.getMatchHistory(username);
            if (history == null || history.trim().isEmpty()) {
                System.out.println("📝 No match history found.");
                System.out.println("Press Enter to return to main menu...");
                scanner.nextLine();
                return;
            }
            // Try to parse as JSON array of objects
            try {
                java.lang.reflect.Type listType = new TypeToken<java.util.List<java.util.Map<String, Object>>>(){}.getType();
                java.util.List<java.util.Map<String, Object>> matches = gson.fromJson(history, listType);
                int idx = 1;
                for (java.util.Map<String, Object> match : matches) {
                    System.out.println("🎮 Match " + idx + ":");
                    System.out.println(repeat("-", 30));
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
            System.out.println("❌ Could not load match history: " + e.getMessage());
        }
        System.out.println("Press Enter to return to main menu...");
        scanner.nextLine();
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
                        System.out.println("\n⚠️  Session invalidated (possibly logged in elsewhere or server disconnected). Returning to login screen.");
                        loginModel.logout();
                        break;
                    }
                } catch (InterruptedException ignored) {
                    break;
                } catch (Exception e) {
                    System.out.println("\n❌ Session check error: " + e.getMessage());
                }
            }
        });
    }
} 