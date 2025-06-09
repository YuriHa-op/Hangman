package client.admin.model;

import javafx.beans.property.SimpleStringProperty;
import javafx.beans.property.StringProperty;

public class Word {
    private final StringProperty word;
    
    public Word(String word) {
        this.word = new SimpleStringProperty(word);
    }

    public String getWord() {
        return word.get();
    }

    public void setWord(String word) {
        this.word.set(word);
    }
    
    public StringProperty wordProperty() {
        return word;
    }
    
    @Override
    public String toString() {
        return getWord();
    }
    
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        
        Word other = (Word) obj;
        return getWord().equals(other.getWord());
    }
    
    @Override
    public int hashCode() {
        return getWord().hashCode();
    }
}