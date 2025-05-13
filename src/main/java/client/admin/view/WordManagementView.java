  package client.admin.view;

        import client.admin.controller.WordManagementController;
        import javafx.fxml.FXMLLoader;
        import javafx.scene.Parent;
        import javafx.scene.Scene;
        import javafx.stage.Modality;
        import javafx.stage.Stage;
        import GameModule.GameService;

        import java.io.IOException;
        import java.util.function.Consumer;

        public class WordManagementView {
            private Stage stage;
            private WordManagementController controller;
            private Consumer<String> outputCallback;
            private GameService gameService;

            public WordManagementView(GameService gameService, Consumer<String> outputCallback) {
                this.gameService = gameService;
                this.outputCallback = outputCallback;
                this.stage = new Stage();
                stage.initModality(Modality.APPLICATION_MODAL);
                stage.setTitle("Word Management");
                stage.setResizable(false);
            }

            public void initialize() {
                try {
                    FXMLLoader loader = new FXMLLoader(getClass().getResource("/client/admin/view/WordManagementView.fxml"));
                    Parent root = loader.load();
                    controller = loader.getController();
                    controller.setOutputCallback(outputCallback);
                    controller.setStage(stage);
                    controller.setGameService(gameService);
                    Scene scene = new Scene(root);
                    scene.getStylesheets().add(getClass().getResource("/client/admin/view/admin.css").toExternalForm());
                    stage.setScene(scene);
                    stage.setWidth(800);
                    stage.setHeight(600);
                } catch (IOException e) {
                    System.err.println("Error loading WordManagementView: " + e.getMessage());
                    e.printStackTrace();
                }
            }

            public void showViewWords() {
                controller.loadWords();
                stage.show();
            }

            public void showAddWord() {
                controller.prepareAddWord();
                stage.show();
            }

            public void showUpdateWord() {
                controller.prepareUpdateWord();
                stage.show();
            }

            public void showDeleteWord() {
                controller.prepareDeleteWord();
                stage.show();
            }

            public void close() {
                stage.close();
            }
        }