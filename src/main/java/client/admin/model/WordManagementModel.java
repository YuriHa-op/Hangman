 package client.admin.model;

        import java.io.*;
        import java.util.ArrayList;
        import java.util.List;
        import java.util.stream.Collectors;
        import GameModule.GameService;

        public class WordManagementModel {
            private List<String> words = new ArrayList<>();
            private static final String WORDS_FILE = "words.txt";
            private GameService gameService;

            // Local file mode
            public WordManagementModel() {
                this.gameService = null;
                loadWords();
            }

            // Remote mode
            public WordManagementModel(GameService gameService) {
                this.gameService = gameService;
                loadWords();
            }

            public void loadWords() {
                words.clear();
                if (gameService != null) {
                    try {
                        String[] serverWords = gameService.getAllWords();
                        for (String word : serverWords) {
                            words.add(word.trim());
                        }
                    } catch (Exception e) {
                        System.err.println("Error loading words from server: " + e.getMessage());
                    }
                } else {
                    try (BufferedReader br = new BufferedReader(new FileReader(WORDS_FILE))) {
                        String line;
                        while ((line = br.readLine()) != null) {
                            words.add(line.trim());
                        }
                    } catch (IOException e) {
                        System.err.println("Error loading words: " + e.getMessage());
                    }
                }
            }

            public List<String> getAllWords() {
                return new ArrayList<>(words);
            }

            public List<String> searchWords(String searchText) {
                if (searchText == null || searchText.trim().isEmpty()) {
                    return getAllWords();
                }
                String lowerCaseSearch = searchText.toLowerCase().trim();
                return words.stream()
                        .filter(word -> word.toLowerCase().contains(lowerCaseSearch))
                        .collect(Collectors.toList());
            }

            public boolean addWord(String word) throws Exception {
                if (word == null || word.trim().isEmpty()) {
                    throw new IllegalArgumentException("Word cannot be empty");
                }
                String trimmedWord = word.trim().toLowerCase();
                if (words.contains(trimmedWord)) {
                    throw new IllegalArgumentException("Word already exists in dictionary");
                }

                if (gameService != null) {
                    boolean result = gameService.addWord(trimmedWord);
                    if (!result) throw new IllegalArgumentException("Word already exists or failed to add");
                } else {
                    try (BufferedWriter writer = new BufferedWriter(new FileWriter(WORDS_FILE, true))) {
                        writer.write(trimmedWord);
                        writer.newLine();
                    }
                }
                loadWords();
                return true;
            }

            public boolean updateWord(String oldWord, String newWord) throws Exception {
                if (newWord == null || newWord.trim().isEmpty()) {
                    throw new IllegalArgumentException("Word cannot be empty");
                }
                String trimmedNewWord = newWord.trim().toLowerCase();
                if (!oldWord.equals(trimmedNewWord) && words.contains(trimmedNewWord)) {
                    throw new IllegalArgumentException("Word already exists in dictionary");
                }

                if (gameService != null) {
                    boolean result = gameService.updateWord(oldWord, trimmedNewWord);
                    if (!result) throw new IllegalArgumentException("Word already exists or failed to update");
                } else {
                    List<String> updatedWords = new ArrayList<>();
                    for (String word : words) {
                        updatedWords.add(word.equals(oldWord) ? trimmedNewWord : word);
                    }
                    try (BufferedWriter writer = new BufferedWriter(new FileWriter(WORDS_FILE))) {
                        for (String word : updatedWords) {
                            writer.write(word);
                            writer.newLine();
                        }
                    }
                }
                loadWords();
                return true;
            }

            public boolean deleteWord(String word) throws Exception {
                if (!words.contains(word)) {
                    throw new IllegalArgumentException("Word does not exist in dictionary");
                }

                if (gameService != null) {
                    boolean result = gameService.deleteWord(word);
                    if (!result) throw new IllegalArgumentException("Word does not exist or failed to delete");
                } else {
                    words.remove(word);
                    try (BufferedWriter writer = new BufferedWriter(new FileWriter(WORDS_FILE))) {
                        for (String w : words) {
                            writer.write(w);
                            writer.newLine();
                        }
                    }
                }
                loadWords();
                return true;
            }

            public int getWordCount() {
                return words.size();
            }
        }