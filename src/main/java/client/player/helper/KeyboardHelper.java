package client.player.helper;

import javafx.scene.control.Button;
import javafx.scene.layout.GridPane;
import java.util.HashMap;
import java.util.Map;
import javafx.event.ActionEvent;
import javafx.event.EventHandler;

public class KeyboardHelper {
    private Map<String, Button> keyboardButtons = new HashMap<>();
    private GridPane keyboardGrid;
    private EventHandler<ActionEvent> keyPressHandler;

    public KeyboardHelper(GridPane keyboardGrid, EventHandler<ActionEvent> keyPressHandler) {
        this.keyboardGrid = keyboardGrid;
        this.keyPressHandler = keyPressHandler;
        initializeKeyboardButtons();
    }

    private void initializeKeyboardButtons() {
        for (javafx.scene.Node node : keyboardGrid.getChildren()) {
            if (node instanceof Button) {
                Button btn = (Button) node;
                keyboardButtons.put(btn.getText().toUpperCase(), btn);
                btn.setOnAction(keyPressHandler);
            }
        }
    }

    public void resetKeyboard() {
        for (Button button : keyboardButtons.values()) {
            button.setDisable(false);
            button.getStyleClass().removeAll("correct", "incorrect");
            button.setOnAction(keyPressHandler);
        }
    }

    public Map<String, Button> getKeyboardButtons() {
        return keyboardButtons;
    }
}