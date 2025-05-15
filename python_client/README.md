# Python CORBA Hangman Client

This is a Python client for the Hangman game that connects to the Java CORBA server. It supports login, account creation, matchmaking, and playing against other Java or Python clients.

## Requirements
- Python 3.7+
- omniORB and omniORBpy

Install dependencies:
```sh
pip install omniORB omniORBpy
```

## Generating Python Stubs from IDL
You need to generate Python stubs from the `GameService.idl` file using omniORB's `omniidl` tool:

```sh
omniidl -bpython ../src/main/java/idl/GameService.idl
```
This will create a `GameModule` directory. Move it into `python_client/`.

## Usage
1. Make sure the Java server is running.
2. Run the Python client:
   ```sh
   python hangman_client.py
   ```
3. Follow the prompts to login, create an account, or play the game.

## Features
- Login and account creation
- Matchmaking and playing Hangman
- View leaderboard
- Play against Java or Python clients

## Notes
- The client uses CORBA to communicate with the Java server. Ensure the server is accessible and the ORB host/port are correct.
- If you change the IDL, regenerate the stubs and replace the `GameModule` directory. 