# Session Management System Installation Guide

This guide walks through the implementation of improved session management for the Hangman game. This system addresses the issue where users would be locked out if their previous session ended improperly.

## Overview

The new system adds:
1. Session tracking with unique session IDs
2. A force login capability that invalidates previous sessions
3. A separated login management system
4. Database schema updates

## Installation Steps

### 1. Database Update

Run the SQL script to add the session_id column:

```sql
-- Run this in your MySQL database
ALTER TABLE players ADD COLUMN session_id VARCHAR(255) DEFAULT NULL;

-- Update any existing players to have NULL session_id
UPDATE players SET session_id = NULL WHERE session_id IS NULL;

-- Make sure any currently logged in players have session_id reset
UPDATE players SET session_id = NULL WHERE currently_logged_in = 1;

-- Optional: Add index on session_id for faster lookups
ALTER TABLE players ADD INDEX idx_session_id (session_id);
```

### 2. Deploy Updated Java Files

The following files have been updated:
- `LoginManager.java` (new file)
- `PlayerManager.java` (updated)
- `LoginViewController.java` (updated)
- `LoginModel.java` (updated)
- `GameServiceImpl.java` (updated)

### 3. Verify Installation

To verify the installation:
1. Start the server
2. Login with an account
3. Without logging out, try to login again with the same account from a different client
4. You should see a dialog asking if you want to force logout the previous session
5. Choosing "OK" should allow you to login, invalidating the previous session

## Technical Details

### Session Management

The system uses a combination of:
- Database tracking via the `session_id` column
- In-memory tracking in `LoginManager`
- Client-side handling in `LoginViewController`

### Security Considerations

- Session IDs are generated using UUID for uniqueness
- Previous sessions are properly invalidated when force-login occurs
- Database connections are properly closed to prevent leaks

### Improving Future Versions

For a more robust implementation:
1. Add session timeout functionality
2. Implement heartbeats to detect inactive sessions
3. Add a notification mechanism for users when their session is invalidated
4. Enhance logging for security auditing

## Troubleshooting

If users still experience login issues:
1. Check if the `session_id` column was added correctly
2. Verify the `currently_logged_in` status in the database
3. Ensure the LoginManager is being initialized properly
4. Check server logs for any exceptions during login/logout operations 