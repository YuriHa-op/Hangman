package client.player.helper;

import javafx.scene.control.Label;
import javafx.scene.input.MouseEvent;
import javafx.scene.Cursor;

public class SpectatablePlayerLabel extends Label {
    public SpectatablePlayerLabel(String playerName, Runnable onClick) {
        super(playerName);
        setStyle("-fx-underline: true; -fx-text-fill: #00aaff; -fx-cursor: hand;");
        setCursor(Cursor.HAND);
        setOnMouseClicked((MouseEvent e) -> {
            if (onClick != null) onClick.run();
        });
    }
} 