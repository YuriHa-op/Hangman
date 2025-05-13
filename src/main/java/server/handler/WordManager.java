package server.handler;

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
<<<<<<< HEAD
=======

    public synchronized boolean addWord(String word) {
        if (word == null || word.trim().isEmpty()) return false;
        String trimmed = word.trim().toLowerCase();
        if (words.contains(trimmed)) return false;
        try (BufferedWriter writer = new BufferedWriter(new FileWriter("words.txt", true))) {
            writer.write(trimmed);
            writer.newLine();
            words.add(trimmed);
            return true;
        } catch (IOException e) {
            System.err.println("Error adding word: " + e.getMessage());
            return false;
        }
    }

    public synchronized boolean updateWord(String oldWord, String newWord) {
        if (oldWord == null || newWord == null || newWord.trim().isEmpty()) return false;
        String trimmedNew = newWord.trim().toLowerCase();
        if (!words.contains(oldWord) || (words.contains(trimmedNew) && !oldWord.equals(trimmedNew))) return false;
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
            return false;
        }
        words = updatedWords;
        return true;
    }

    public synchronized boolean deleteWord(String word) {
        if (word == null || !words.contains(word)) return false;
        words.remove(word);
        try (BufferedWriter writer = new BufferedWriter(new FileWriter("words.txt"))) {
            for (String w : words) {
                writer.write(w);
                writer.newLine();
            }
        } catch (IOException e) {
            System.err.println("Error deleting word: " + e.getMessage());
            return false;
        }
        return true;
    }
>>>>>>> main
} 