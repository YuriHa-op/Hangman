package client.admin.model;

import AdminModule.AdminService;
import AdminModule.AdminServiceHelper;
import org.omg.CORBA.ORB;
import org.omg.CosNaming.NamingContextExt;
import org.omg.CosNaming.NamingContextExtHelper;

/**
 * Manages the connection to the AdminService
 */
public class AdminConnection {
    private ORB orb;
    private AdminService adminService;
    private String host;
    private String port;
    private boolean connected = false;

    public AdminConnection(String host, String port) {
        this.host = host;
        this.port = port;
    }

    public void connect() throws Exception {
        String[] args = {"-ORBInitialHost", host, "-ORBInitialPort", port};
        orb = ORB.init(args, null);

        org.omg.CORBA.Object objRef = orb.resolve_initial_references("NameService");
        NamingContextExt ncRef = NamingContextExtHelper.narrow(objRef);

        adminService = AdminServiceHelper.narrow(ncRef.resolve_str("AdminService"));
        connected = true;
    }

    public void disconnect() {
        if (orb != null) {
            orb.shutdown(true);
        }
        connected = false;
    }

    public AdminService getAdminService() {
        if (!connected) {
            throw new IllegalStateException("Not connected to AdminService");
        }
        return adminService;
    }

    public boolean isConnected() {
        return connected;
    }
} 