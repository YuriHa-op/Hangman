package server.handler.core;

import GameModule.Bool;
import java.io.*;
import java.util.*;

public class WordManager {
    private List<String> words = new ArrayList<>();

    public WordManager() {
        loadWordsFromFile();
    }

    private void loadWordsFromFile() {
        try (BufferedReader br = new BufferedReader(new FileReader("words.txt"))) {
            String line;
            while ((line = br.readLine()) != null) {
                words.add(line.trim());
            }
        } catch (IOException e) {
            System.err.println("Error reading words from file: " + e.getMessage());
        }
    }

    public List<String> getWords() {
        return words;
    }


    public synchronized Bool addWord(String word) {
        if (word == null || word.trim().isEmpty()) return Bool.BOOL_FALSE;
        String trimmed = word.trim().toLowerCase();
        if (words.contains(trimmed)) return Bool.BOOL_FALSE;
        try (BufferedWriter writer = new BufferedWriter(new FileWriter("words.txt", true))) {
            writer.write(trimmed);
            writer.newLine();
            words.add(trimmed);
            return Bool.BOOL_TRUE;
        } catch (IOException e) {
            System.err.println("Error adding word: " + e.getMessage());
            return Bool.BOOL_FALSE;
        }
    }

    public synchronized Bool updateWord(String oldWord, String newWord) {
        if (oldWord == null || newWord == null || newWord.trim().isEmpty()) return Bool.BOOL_FALSE;
        String trimmedNew = newWord.trim().toLowerCase();
        if (!words.contains(oldWord) || (words.contains(trimmedNew) && !oldWord.equals(trimmedNew))) return Bool.BOOL_FALSE;
        List<String> updatedWords = new ArrayList<>();
        for (String w : words) {
            updatedWords.add(w.equals(oldWord) ? trimmedNew : w);
        }
        try (BufferedWriter writer = new BufferedWriter(new FileWriter("words.txt"))) {
            for (String w : updatedWords) {
                writer.write(w);
                writer.newLine();
            }
        } catch (IOException e) {
            System.err.println("Error updating word: " + e.getMessage());
            return Bool.BOOL_FALSE;
        }
        words = updatedWords;
        return Bool.BOOL_TRUE;
    }

    public synchronized Bool deleteWord(String word) {
        if (word == null || !words.contains(word)) return Bool.BOOL_FALSE;
        words.remove(word);
        try (BufferedWriter writer = new BufferedWriter(new FileWriter("words.txt"))) {
            for (String w : words) {
                writer.write(w);
                writer.newLine();
            }
        } catch (IOException e) {
            System.err.println("Error deleting word: " + e.getMessage());
            return Bool.BOOL_FALSE;
        }
        return Bool.BOOL_TRUE;
    }

} 