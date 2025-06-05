import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QListWidget, QTextEdit, QMessageBox, QSplitter, QListWidgetItem
)
from PyQt5.QtCore import Qt

class QtMatchHistoryView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.controller = None # Will be set by MainWindow
        self.current_match_list_data = [] # Store full JSON objects for each match
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle('Match History - Hangman')
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        title_label = QLabel('Match History')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(title_label)

        # Splitter for match list and details
        splitter = QSplitter(Qt.Horizontal)

        # Left side: Match List
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0,0,0,0)
        self.match_list_widget = QListWidget()
        self.match_list_widget.setAlternatingRowColors(True)
        self.match_list_widget.itemClicked.connect(self.on_match_selected)
        left_layout.addWidget(QLabel("Matches:"))
        left_layout.addWidget(self.match_list_widget)
        left_panel.setLayout(left_layout)
        splitter.addWidget(left_panel)

        # Right side: Match Details
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0,0,0,0)
        self.match_details_area = QTextEdit()
        self.match_details_area.setReadOnly(True)
        self.match_details_area.setPlaceholderText("Select a match to view details.")
        right_layout.addWidget(QLabel("Details:"))
        right_layout.addWidget(self.match_details_area)
        right_panel.setLayout(right_layout)
        splitter.addWidget(right_panel)
        
        splitter.setSizes([250, 350]) # Initial size distribution, adjusted for typical content

        main_layout.addWidget(splitter)

        self.back_button = QPushButton('Back to Main Menu')
        self.back_button.setStyleSheet("padding: 8px 15px; font-size: 14px; margin-top: 10px;")
        main_layout.addWidget(self.back_button, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)

    def set_controller(self, controller):
        self.controller = controller
        if self.controller:
            self.back_button.clicked.connect(self.controller.go_back_to_main_menu)

    def on_match_selected(self, item):
        if not self.controller:
            self.show_error_message("Controller not available.")
            return
        
        selected_index = self.match_list_widget.row(item)
        if 0 <= selected_index < len(self.current_match_list_data):
            match_data = self.current_match_list_data[selected_index]
            game_id = match_data.get('gameId') # Corrected: 'gameId'
            if game_id is not None:
                self.controller.fetch_match_details(str(game_id))
            else:
                self.display_match_details_error("Error: 'gameId' not found in selected match data.")
        else:
            self.display_match_details_error("Error: Selected match index out of bounds.")

    def display_match_history(self, matches_json_string):
        self.match_list_widget.clear()
        self.match_details_area.clear()
        self.match_details_area.setPlaceholderText("Select a match to view details.")
        self.current_match_list_data = [] # Clear previous data
        try:
            matches = json.loads(matches_json_string)
            self.current_match_list_data = matches # Store the parsed list of dicts
            if not matches:
                self.match_list_widget.addItem("No match history found.")
                return

            for i, match_info in enumerate(matches):
                game_id = match_info.get('gameId', 'N/A') # Corrected: 'gameId'
                display_text = f"Game ID: {game_id}"
                
                # Add overall winner if available
                overall_winner = match_info.get('overallWinner')
                if overall_winner:
                    display_text += f" - Winner: {overall_winner}"
                
                # Add game end time if available (requires datetime conversion for readability)
                game_end_time_ms = match_info.get('gameEndTime')
                if game_end_time_ms:
                    try:
                        # Assuming gameEndTime is milliseconds since epoch
                        from datetime import datetime
                        dt_object = datetime.fromtimestamp(game_end_time_ms / 1000)
                        display_text += f" - Date: {dt_object.strftime('%Y-%m-%d %H:%M')}"
                    except Exception as e:
                        print(f"Error formatting gameEndTime: {e}")
                        display_text += f" - Date: (raw {game_end_time_ms})"
                
                list_item = QListWidgetItem(display_text)
                # Store the index or full gameId if needed for direct lookup, 
                # but self.current_match_list_data[row_index] is better.
                # list_item.setData(Qt.UserRole, game_id) # Example if storing ID directly in item
                self.match_list_widget.addItem(list_item)

        except json.JSONDecodeError:
            self.match_list_widget.addItem("Error: Could not parse match history data.")
        except Exception as e:
            self.match_list_widget.addItem(f"Error displaying history: {type(e).__name__} - {e}")

    def display_match_details(self, details_string):
        try:
            details_obj = json.loads(details_string)
            pretty_details = json.dumps(details_obj, indent=4)
            self.match_details_area.setText(pretty_details)
        except json.JSONDecodeError:
            self.match_details_area.setText(details_string)
        except Exception as e:
             self.match_details_area.setText(f"Error displaying details: {type(e).__name__}\nRaw: {details_string}")

    def display_match_details_error(self, message):
        self.match_details_area.setText(message)

    def show_error_message(self, message):
        QMessageBox.warning(self, 'Match History Error', message) 