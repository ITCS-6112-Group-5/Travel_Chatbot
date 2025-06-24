# Temporary web server to launch website contents locally

# TODO: create a server (Flask or other) that can serve both website and API calls

import os
import webbrowser
import subprocess
import sys

PORT = 8080 # Modify port if needed

def launch_website():
    os.chdir("website")
    print(f"NaviBlu at http://localhost:{PORT}")
    webbrowser.open(f"http://localhost:{PORT}")
    
    # Execute python's built-in server module (terminal command to run website locally)
    subprocess.run([sys.executable, "-m", "http.server", str(PORT)])

if __name__ == "__main__":
    launch_website()