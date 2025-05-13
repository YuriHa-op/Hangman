# What's The Word - Multiplayer Hangman Game

 Multiplayer Hangman game using Java, JavaFX, and CORBA for client-server communication.
//not yet multiplayer
## Features

- **User Login:** Secure login with session management.
- **Game Play:** Classic Hangman with timer and visual feedback.
- **Leaderboard:** View top players and their win counts.
- **Admin Functions:** Create/delete users, update settings. //not yet implemented


## Technologies

- Java 1.8
- JavaFX
- CORBA (IDL, Naming Service)
- MySQL (for server-side data)
- FXML/CSS for UI

## Project Structure

- `src/main/java/`
    - `client/` - JavaFX client application
    - `server/` - Server-side logic and database access
    - `GameModule/` - CORBA-generated interfaces and stubs
- `src/main/resources/`
    - FXML, CSS, images, and fonts

## Setup

### Prerequisites

- Java 1.8 or newer
- MySQL server
- [JavaFX SDK](https://openjfx.io/)
- CORBA libraries (e.g., JacORB or OpenJDK ORB)
- IntelliJ IDEA (recommended)

### Database

1. Import the SQL schema from `src/main/java/server/db/game.sql` into your MySQL server.
2. Update your server's database connection settings as needed.

## Build & Run

#### Server

### 1. In you cmd orbd -ORBInitialPort 900 -ORBInitialHost localhost
### 2. Run ServerMain class:  
   `java server.ServerMain`
### 3. Then Run LoginController class:  
   `java client.player.controller.LoginController$LoginApplication`
### 4. Run the server main class (not shown here, but typically in `server/`).
### 5. Assuming youve already created an account in the database or set up the database, you can now login to the game.



#### Client

1. Compile the client code.
2. Run the client main class:  
   `java client.player.controller.LoginController$LoginApplication`
3. Use the login window to connect and play.

### Configuration

- Change CORBA host/port in `LoginModel.java` or via command-line args.
- UI resources (images, fonts) are in `src/main/resources/client/player/view/`.

## Usage

- **Login:** Enter your username and password.
- **Start Game:** Play Hangman, guess letters, and beat the timer.
- **Leaderboard:** View top players.
- **Logout:** End your session safely.

## Notes

<h2>- Only one session per user is allowed at a time.</h2>
<h2>- Create Account in the data base. via phpmyadmin</h2>
<h2>- Always logout if you fortgot to logout and you are not able to login again. unless you edit the database in players table edit you account and set the currently loggein value to zero.</h2>
<h2>- Admin features are available for users with the `admin` role. Comingsoon!</h2>

## License

Team02-IT-222

---

*This project is for educational purposes and demonstrates JavaFX, CORBA, and client-server architecture.*

## Python Client for Hangman (CORBA)

A Python client is available in the `python_client/` folder. This client can connect to the Java CORBA server and play Hangman with other Java or Python clients.

### Requirements
- Python 3.7+
- omniORB (`pip install omniORB omniORBpy`)

### Setup
1. Make sure the Java server is running and accessible.
2. Generate Python stubs from the `GameService.idl` file using omniORB's `omniidl` tool:
   ```sh
   omniidl -bpython src/main/java/idl/GameService.idl
   ```
   Place the generated `GameModule` Python package inside `python_client/`.
3. Run the Python client:
   ```sh
   cd python_client
   python hangman_client.py
   ```

### Features
- Login, create account, and play Hangman with matchmaking (just like the Java client)
- View leaderboard
- Play against other Java or Python clients

See `python_client/README.md` for more details.