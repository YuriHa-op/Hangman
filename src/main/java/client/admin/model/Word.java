package client.admin.model;

public class Word {
    private String value;
    private String category;
    private int difficulty;

    public Word(String value, String category, int difficulty) {
        this.value = value;
        this.category = category;
        this.difficulty = difficulty;
    }

    public String getValue() {
        return value;
    }

    public void setValue(String value) {
        this.value = value;
    }

    public String getCategory() {
        return category;
    }

    public void setCategory(String category) {
        this.category = category;
    }

    public int getDifficulty() {
        return difficulty;
    }

    public void setDifficulty(int difficulty) {
        this.difficulty = difficulty;
    }

    @Override
    public String toString() {
        return value + " (" + category + ", " + difficultyToString() + ")";
    }

    private String difficultyToString() {
        switch (difficulty) {
            case 1: return "Easy";
            case 2: return "Medium";
            case 3: return "Hard";
            default: return "Unknown";
        }
    }
}