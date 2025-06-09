package server.bootstrap;

import org.omg.CORBA.ORB;
import org.omg.CosNaming.NameComponent;
import org.omg.CosNaming.NamingContextExt;
import org.omg.CosNaming.NamingContextExtHelper;
import org.omg.PortableServer.POA;
import org.omg.PortableServer.POAHelper;

import server.handler.service.AdminServiceImpl;
import server.handler.service.GameServiceImpl;
import server.handler.data.MatchResultDAO;
import server.handler.core.PlayerManager;
import server.handler.data.SinglePlayerMatchResultDAO;
import server.handler.core.WordManager;

// Generated IDL bindings
import GameModule.GameService;
import GameModule.GameServiceHelper;
import AdminModule.AdminService;
import AdminModule.AdminServiceHelper;

public class ServerBootstrap {
    public static void main(String[] args) {
        try {
            // Initialize ORB
            ORB orb = ORB.init(args, null);
            
            // Get reference to RootPOA
            POA rootPOA = POAHelper.narrow(orb.resolve_initial_references("RootPOA"));
            rootPOA.the_POAManager().activate();
            
            // Create shared resources
            WordManager wordManager = new WordManager();
            PlayerManager playerManager = new PlayerManager();
            MatchResultDAO matchResultDAO = new MatchResultDAO(
                "jdbc:mysql://localhost:3306/game",
                "root",
                ""
            );
            SinglePlayerMatchResultDAO singlePlayerMatchResultDAO = new SinglePlayerMatchResultDAO(
                "jdbc:mysql://localhost:3306/game",
                "root",
                ""
            );
            
            // Create service implementations with shared resources
            GameServiceImpl gameImpl = new GameServiceImpl();
            AdminServiceImpl adminImpl = new AdminServiceImpl(
                wordManager,
                playerManager,
                matchResultDAO,
                singlePlayerMatchResultDAO
            );
            
            // Get object references
            org.omg.CORBA.Object gameRef = rootPOA.servant_to_reference(gameImpl);
            GameService gameService = GameServiceHelper.narrow(gameRef);
            
            org.omg.CORBA.Object adminRef = rootPOA.servant_to_reference(adminImpl);
            AdminService adminService = AdminServiceHelper.narrow(adminRef);
            
            // Get the root naming context
            org.omg.CORBA.Object objRef = orb.resolve_initial_references("NameService");
            NamingContextExt ncRef = NamingContextExtHelper.narrow(objRef);
            
            // Bind the object references in naming
            NameComponent[] gameName = ncRef.to_name("GameService");
            NameComponent[] adminName = ncRef.to_name("AdminService");
            ncRef.rebind(gameName, gameService);
            ncRef.rebind(adminName, adminService);
            
            System.out.println("Server ready...");
            
            // Wait for invocations
            orb.run();
            
        } catch (Exception e) {
            System.err.println("ERROR: " + e);
            e.printStackTrace(System.out);
        }
    }
} 