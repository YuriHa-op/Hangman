Hangman Python Client - Installation Instructions
================================================

Requirements:
- Python 3.x
- omniORB and omniORBpy (CORBA libraries for Python)
- The generated Python stubs from your GameService.idl (GameModule.py, etc.)

Installation Steps:

1. Install omniORB and omniORBpy:
   - Windows: Download and run the installers from https://sourceforge.net/projects/omniorb/files/
   - Linux: sudo apt-get install python3-omniorb omniidl python3-omniorb-omg

2. Generate Python stubs from the IDL:
   - Open a terminal in the CORBA_IDLs folder.
   - Run: omniidl -bpython GameService.idl
   - Copy the generated GameModule.py and any related files into Client_Python/

3. Install Python dependencies:
   - Open a terminal in Python_Installer.
   - Run: pip install -r requirements.txt

4. Run the client:
   - Open a terminal in Client_Python.
   - Run: python hangman_client.py

Troubleshooting:
- If you get "No module named omniORB", make sure omniORBpy is installed and in your PYTHONPATH.
- If you get CORBA connection errors, ensure the Java server is running and accessible. 



https://github.com/YuriHa-op/Hangman