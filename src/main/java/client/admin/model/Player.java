package client.admin.model;

public class Player {
    private int rank;
    private String username;
    private int wins;
    private boolean online;
    private String avatar; // Could be a path or initials

    private String role;



    public void setRole(String role) {
        this.role = role;
    }

    public int getRank() {
        return rank;
    }

    public void setRank(int rank) {
        this.rank = rank;
    }

    public boolean isOnline() {
        return online;
    }

    public void setOnline(boolean online) {
        this.online = online;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public int getWins() {
        return wins;
    }

    public void setWins(int wins) {
        this.wins = wins;
    }

    public String getAvatar() {
        return avatar;
    }
    public String getRole() {
        return role;
    }
    public void setAvatar(String avatar) {
        this.avatar = avatar;
    }
}