package client.player.helper;

import javafx.event.ActionEvent;
import javafx.event.EventHandler;
import javafx.scene.Node;
import javafx.scene.control.Button;
import javafx.scene.layout.Pane;

import java.util.HashMap;
import java.util.Map;

public class KeyboardHelper {
    private final Map<String, Button> keyboardButtons = new HashMap<>();
    private final EventHandler<ActionEvent> keyPressHandler;

    public KeyboardHelper(Pane keyboardPane, EventHandler<ActionEvent> keyPressHandler) {
        this.keyPressHandler = keyPressHandler;
        initializeKeyboardButtons(keyboardPane);
    }

    private void initializeKeyboardButtons(Pane pane) {
        for (Node node : pane.getChildren()) {
            if (node instanceof Button) {
                Button btn = (Button) node;
                keyboardButtons.put(btn.getText().toUpperCase(), btn);
                btn.setOnAction(keyPressHandler);
            } else if (node instanceof Pane) {
                initializeKeyboardButtons((Pane) node); // Recurse for nested panes
            }
        }
    }

    public void resetKeyboard() {
        for (Button button : keyboardButtons.values()) {
            button.setDisable(false);
            button.getStyleClass().removeAll("correct", "incorrect");
        }
    }

    public Map<String, Button> getKeyboardButtons() {
        return keyboardButtons;
    }
}