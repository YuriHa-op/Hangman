package client.player.helper;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;

public class SpectatorManager {
    private String spectatedPlayer;
    private final List<Consumer<String>> listeners = new ArrayList<>();

    public void setSpectatedPlayer(String playerName) {
        this.spectatedPlayer = playerName;
        notifyListeners();
    }

    public String getSpectatedPlayer() {
        return spectatedPlayer;
    }

    public void addListener(Consumer<String> listener) {
        listeners.add(listener);
    }

    private void notifyListeners() {
        for (Consumer<String> listener : listeners) {
            listener.accept(spectatedPlayer);
        }
    }
} 