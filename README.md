# Hangman Game

Welcome to the **Hangman Game** project! This is a client-server application where players try to guess a word by suggesting letters, with support for both single-player and multiplayer modes.

## Architecture Overview

The Hangman game features a robust client-server architecture:

*   **Server:** A Java-based application built with Maven, responsible for all game logic (single-player and multiplayer), player account management, word management, and data persistence.
*   **Communication:** Clients and Server communicate using CORBA (Common Object Request Broker Architecture).
*   **Database:** MySQL is used to store player accounts, game statistics, and match history.
*   **Clients:**
    *   **JavaFX Player Client:** A graphical client built with JavaFX for playing the game.
    *   **JavaFX Admin Client:** A graphical client built with JavaFX for administrative tasks (e.g., word management, viewing server status).
    *   **Python Player Client:** A graphical client built with Python and Tkinter (using an MVC pattern) for playing the game.

## Features

*   **Single-Player Mode:** Play Hangman against the computer.
*   **Multiplayer Mode:** Compete against other players in real-time.
    *   Lobby system for matchmaking.
    *   Synchronized game state and timers.
    *   Spectator mode.
    *   AFK detection and handling.
*   **Cross-Platform Clients:** Play using either the JavaFX or Python client.
*   **User Accounts:** Secure login and account creation.
*   **Persistent Scores & Leaderboards:** Track player statistics and rankings.
*   **Administrative Interface:** Manage game words and server operations through a dedicated admin client.
*   **GUI:** User-friendly graphical interfaces for all client applications.

## How to Run

### Prerequisites
*   Java Development Kit (JDK) 8 or higher.
*   Apache Maven (for building the Java server/clients).
*   MySQL Server.
*   Python 3.7+ (for the Python client).
*   `omniORB` and `omniORBpy` (for the Python client's CORBA communication).
    ```bash
    pip install omniORB omniORBpy Pillow
    ```

### 1. Database Setup
1.  Ensure your MySQL server is running.
2.  Create a database (e.g., `game`).
3.  Import the SQL schema file located in `src/main/java/server/db/` (you'll need to create this file or ensure schema is auto-generated if using an ORM with DDL capabilities, otherwise adjust based on your actual DB setup process).
4.  Default server configuration expects the database `game` on `localhost:3306` with user `root` and an empty password. Adjust `GameServiceImpl.java` if your setup differs.

### 2. Build the Java Server and Clients
Navigate to the project root directory and run:
```bash
mvn clean package
```
This will compile the Java code and create necessary JAR files or prepare classes in the `target/classes` directory.

### 3. Start the Server
The server handles CORBA Naming Service initialization.
Open a terminal and execute the following command from the project root directory:
```bash
java -Djava.endorsed.dirs=./lib -cp ./lib/*;target/classes server.ServerMain
```
(Note: Ensure the `lib` directory with necessary CORBA and JDBC JARs is present in the root, or adjust the classpath. The `pom.xml` should download these, but they need to be in the classpath at runtime if not running an executable JAR that includes them.)

Leave this terminal open. The server must be running for clients to connect.

### 4. Start the JavaFX Player Application
Open a new terminal and execute the following command from the project root directory:
```bash
java -Djava.endorsed.dirs=./lib -cp ./lib/*;target/classes client.player.Main
```

### 5. Start the JavaFX Admin Application
The admin client allows you to manage words, etc.
To run it, open a new terminal and execute the following command from the project root directory:
```bash
java -Djava.endorsed.dirs=./lib -cp ./lib/*;target/classes client.admin.AdminApplication
```
For the admin client, username and password might not be required for initial access (press Enter if prompted), allowing direct access to admin functionalities. Create user accounts via this client or directly in the database for players.

### 6. Prepare and Run the Python Player Client

#### a. Generate Python Stubs from IDL
The Python client requires CORBA stubs generated from the `GameService.idl` file.
1.  Navigate to the `python_client` directory.
2.  Run the `omniidl` command (ensure `omniidl` is in your system's PATH):
    ```bash
    omniidl -bpython ../src/main/java/idl/GameService.idl
    ```
    (Adjust the path to `GameService.idl` if it's different. It is typically found in `src/main/java/idl/` or a similar location within your Java server source structure.)
3.  This will create a `GameModule` directory in `python_client/`. If it creates it elsewhere, move the `GameModule` directory into `python_client/`.

#### b. Run the Python Client
1.  Ensure the Java server is running.
2.  Navigate to the `python_client` directory.
3.  Run the client application (assuming `app.py` is the main entry point):
    ```bash
    python app.py
    ```

## Installation (from source)

1.  Clone this repository to your local machine:
    ```bash
    git clone https://github.com/YuriCrane13/Hangman.git
    ```
2.  Follow the Database Setup, Build, and Run instructions above.

## Contributing
Details on how to contribute to the project (e.g., coding standards, pull request process). *(To be added)*

## License
Specify the project license here (e.g., MIT, Apache 2.0). *(To be added)*

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
