# Python CORBA Hangman Client

This Python client allows users to connect to the Java CORBA Hangman server to play the game. It provides a graphical user interface using Tkinter and follows an MVC (Model-View-Controller) pattern.

## Features

*   Login and Account Creation (interfacing with the server's player management).
*   Single-Player Mode.
*   Multiplayer Mode:
    *   Join or create game lobbies.
    *   Real-time gameplay with other players (Java or Python clients).
    *   View scores and game state updates.
    *   Spectator mode.
    *   AFK/Stall handling.
*   View Leaderboard.

## Requirements

*   Python 3.7 or newer.
*   **omniORB and omniORBpy:** For CORBA communication.
*   **Pillow:** For image processing, potentially used by the Tkinter GUI.
    ```bash
    pip install omniORB omniORBpy Pillow
    ```
*   **(Potentially) CustomTkinter or other GUI libraries:** Check `requirements.txt` if present in the `python_client` directory, or install as needed if import errors occur.

## Setup and Running

### 1. Ensure Java Server is Running

The Java Hangman server (including its CORBA Naming Service) must be running and accessible over the network. Refer to the main project `README.md` for instructions on building and running the server.

### 2. Generate Python Stubs from IDL

CORBA communication requires Python stub files generated from the `GameService.idl` (Interface Definition Language) file provided by the Java server.

1.  **Locate the IDL file:** The `GameService.idl` file is typically located within the Java server's source code, often in a path like `src/main/java/idl/GameService.idl` relative to the project root.
2.  **Navigate to the `python_client` directory** in your terminal.
3.  **Run `omniidl`:** Execute the following command, adjusting the path to `GameService.idl` as necessary:
    ```bash
    omniidl -bpython ../src/main/java/idl/GameService.idl
    ```
    *   If your project structure is different, change `../src/main/java/idl/GameService.idl` to the correct relative or absolute path to the IDL file.
4.  **Verify `GameModule`:** This command should create a `GameModule` directory within your `python_client` directory. This module contains the generated Python stubs. If it appears elsewhere, move it into `python_client/`.

### 3. Run the Python Client

Once the server is running and the Python stubs (`GameModule/`) are correctly placed in the `python_client` directory:

1.  Navigate to the `python_client` directory in your terminal.
2.  Execute the main application file (assumed to be `app.py` based on common structure; adjust if your entry point is different, e.g., `hangman_client.py`):
    ```bash
    python app.py
    ```
3.  The client GUI should appear, allowing you to log in, create an account, and play Hangman.

## Development Notes

*   **Client-Server Interaction:** The client uses CORBA to invoke methods on the remote `GameService` object hosted by the Java server.
*   **Game Logic:** All core game logic resides on the server. The Python client is responsible for UI, user input, and relaying actions to/from the server.
*   **IDL Changes:** If the `GameService.idl` interface is ever modified on the server side, you **must** regenerate the Python stubs (Step 2) and replace the old `GameModule` directory in `python_client/` to maintain compatibility.
*   **Configuration:** CORBA client configuration (e.g., Naming Service host/port) is typically handled implicitly by omniORB based on how the server registers its services, or potentially through an `omniorb.cfg` file if specific overrides are needed (though usually not required for basic client operation if the server uses standard Naming Service ports).

## Session Management System

This client implements an improved session management system to fix the "lockout pattern" issue where accounts would become inaccessible if a previous session crashed without properly logging out.

### Key Features

1. **Session ID Tracking**: Each login generates a unique session ID that is stored both in-memory and in the database.

2. **Session Validation**: The client periodically validates the session with the server to ensure it's still active.

3. **Force Login Capability**: If a user tries to log in while their account is already logged in elsewhere, they can choose to force login, which will invalidate the previous session.

4. **Real-time Session Invalidation**: If a user logs in from a second client, the first client will detect the invalidated session and log out.

5. **Custom Minecraft-themed Dialogs**: Both session invalidation and force-login confirmation use custom styled dialogs with animations.

### Implementation Details

#### Model Layer (GameModel)
- Stores the session ID after login
- Implements `validate_session()` method to check if the session is still valid
- Implements `keep_alive()` method to ping the server and maintain the session
- Implements `force_login()` method to force login when account is already logged in elsewhere

#### Controller Layer (BaseController)
- Implements session checking in a background thread
- Handles session invalidation by showing a dialog and redirecting to login

#### View Layer
- Implements custom styled dialogs for force login and session invalidation
- Includes animations like fade-in and shake effects

### How to Use

1. **Compile IDL**: Run `python compile_idl.py` to generate the necessary Python bindings.

2. **Run the Client**: Start the client with `python app.py`.

3. **Login**: If your account is already logged in elsewhere, you'll see a force login dialog.

4. **Session Validation**: The client automatically validates your session every second.

### Troubleshooting

- If you're experiencing issues with session validation, ensure the server supports the new session management methods.
- If you're unable to log in, try restarting the client and the server.
- If you're still experiencing issues, check the server logs for more information.

## Session Management Fixes

The following issues were fixed in the session management system:

### 1. Thread Management
- Fixed thread joining in `stop_session_checking()` to prevent "cannot join current thread" errors
- Added proper thread variable naming (`_session_check_thread` and `_session_check_running`)
- Added safety checks to avoid joining the current thread

### 2. Session Invalidation Dialog
- Enhanced the `SessionInvalidatedDialog` with attention-grabbing features:
  - Red border and styling
  - Shake animation
  - System beep sound
  - Fade-in effect
- Fixed QPoint import in the ShakeAnimation class
- Added proper error handling with try/except blocks
- Forced dialog to be application modal and stay on top

### 3. Cross-Thread Communication
- Replaced QMetaObject.invokeMethod with QTimer.singleShot for reliable cross-thread UI updates
- Added QApplication.processEvents() calls to ensure UI updates
- Fixed case sensitivity in view names (e.g., "MainMenu" vs "main_menu")

### 4. Error Handling
- Added comprehensive error handling and logging
- Implemented fallback mechanisms for session validation
- Added timeout for thread joining

### 5. Dialog Display
- Fixed dialog centering on screen
- Added @pyqtSlot() decoration to the handle_session_invalidated method
- Created a _show_session_invalidated_dialog helper method
- Added fallback to Login view if current view doesn't support showing the dialog

### 6. Multiple Invalidation Prevention
- Added a class-level flag to prevent multiple simultaneous session invalidation handlers
- Implemented checks to skip redundant invalidation attempts
- Created a dedicated method to reset the flag after invalidation is complete
- Added checks in the session check worker to stop if invalidation is already in progress

## Testing
Three test scripts were created to verify the fixes:
- `test_invalidation.py`: Tests session invalidation from both main thread and background thread
- `test_session_dialog.py`: Tests the session invalidated dialog directly
- `test_multiple_invalidation.py`: Tests prevention of multiple simultaneous invalidations

## How to Test
1. Run `py test_invalidation.py` to test session invalidation
2. Run `py test_session_dialog.py` to test the session invalidated dialog directly
3. Run `py test_multiple_invalidation.py` to test multiple invalidation prevention 