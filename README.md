# Hangman Game

Welcome to the **Hangman Game** project! This is a simple game where players try to guess a word by suggesting letters within a certain number of attempts.

## How to Run

set up the database first using wamp and import the sql file in the database folder src/main/java/server/db

then create account via admin client or phpmyadmin.

admin client don't have password and username just enter enter.

### 1. Start the CORBA ORB Daemon

Open a terminal and run:
```bash
orbd -ORBInitialHost localhost -ORBInitialPort 900
```
Leave this terminal open; the ORB must be running for the server and clients to communicate.

### 2. Start the Server

Run the server main class:
- **Class:** `server.handler.ServerMain`

  ```bash
  java -cp target/classes server.handler.ServerMain
  ```


### 3. Start the Player Application

Run the player main class:
- **Class:** `client.player.Main`

  ```bash
  java -cp target/classes client.player.Main
  ```
 

### 4. Start the Admin Application

Run the admin main class:
- **Class:** `client.admin.view.AdminApplication`

  ```bash
  java -cp target/classes client.admin.view.AdminApplication
  ```
  admin client don't have password and username just enter enter.
  *(Or run the built JAR if available.)*

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Features

....

## Installation

1. Clone this repository to your local machine:
   ```bash
   git clone https://github.com/YuriCrane13/Hangman.git
