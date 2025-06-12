class QtMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hangman")
        self.resize(800, 600)
        # Other initialization code...
        self.views = {}
        self.current_view = None
        self.username = None
        
        # Create a stacked widget to hold different views
        self.stacked_widget = QStackedWidget(self)
        self.setCentralWidget(self.stacked_widget)
        
        # Dictionary to track active visual effects
        self._active_effects = {}

    def show_view(self, view_name):
        """Switch to the specified view"""
        # First clean up any visual effects
        self.cleanup_all_visual_effects()
        
        # If we have the view, show it
        if view_name in self.views:
            # Hide the current view
            if self.current_view is not None:
                # Call on_hide if available
                if hasattr(self.views[self.current_view], 'on_hide'):
                    self.views[self.current_view].on_hide()
            
            # Set and show the new view
            self.stacked_widget.setCurrentWidget(self.views[view_name])
            self.current_view = view_name
            
            # Call on_show if available
            if hasattr(self.views[view_name], 'on_show'):
                self.views[view_name].on_show()
                
            # Resize window if view specifies dimensions
            if view_name == "MultiplayerGame" and hasattr(self, 'multiplayer_game_view'):
                self.resize(950, 950)  # Set size for multiplayer game
            elif view_name == "SinglePlayer1v1Game" and hasattr(self, 'sp_1v1_game_view'):
                self.resize(1000, 700)  # Set size for 1v1 game
            else:
                self.resize(800, 600)  # Default size
            
            # Center the window on the screen
            self._center_on_screen()

    def cleanup_all_visual_effects(self):
        """Centralized method to clean up all visual effects across the app"""
        try:
            # Clean up confetti effects
            from .effects.confetti_effect import ConfettiEffect
            if hasattr(ConfettiEffect, 'cleanup_all_instances'):
                ConfettiEffect.cleanup_all_instances()
            
            # Clean up round transition effects
            from .effects.round_transition_effect import RoundTransitionEffect
            if hasattr(RoundTransitionEffect, 'cleanup_all_instances'):
                RoundTransitionEffect.cleanup_all_instances()
                
            # Clean any view-specific effects
            if hasattr(self, 'multiplayer_game_view') and self.multiplayer_game_view:
                if hasattr(self.multiplayer_game_view, 'cleanup_all_effects'):
                    self.multiplayer_game_view.cleanup_all_effects()
                    
            if hasattr(self, 'sp_1v1_game_view') and self.sp_1v1_game_view:
                if hasattr(self.sp_1v1_game_view, 'cleanup_all_effects'):
                    self.sp_1v1_game_view.cleanup_all_effects()
        except Exception as e:
            print(f"Error cleaning up visual effects: {e}")
            
    def _center_on_screen(self):
        """Center the window on the screen"""
        available_geometry = QApplication.desktop().availableGeometry()
        frame_geometry = self.frameGeometry()
        frame_geometry.moveCenter(available_geometry.center())
        self.move(frame_geometry.topLeft()) 