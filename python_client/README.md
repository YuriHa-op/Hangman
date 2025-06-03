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