import os
import sys
import subprocess

def main():
    # Set environment variables
    os.environ["PORT"] = os.environ.get("PORT", "8501")
    os.environ["STREAMLIT_SERVER_PORT"] = os.environ.get("PORT", "8501")
    os.environ["STREAMLIT_SERVER_ADDRESS"] = "0.0.0.0"
    os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
    os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    os.environ["STREAMLIT_SERVER_ENABLE_CORS"] = "true"
    os.environ["STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION"] = "false"
    os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"
    os.environ["STREAMLIT_SERVER_RUN_ON_SAVE"] = "false"
    os.environ["STREAMLIT_THEME_BASE"] = "dark"
    os.environ["PYTHONUNBUFFERED"] = "1"

    # Create public directory if it doesn't exist
    if not os.path.exists("public"):
        os.makedirs("public")

    # Install dependencies
    print("Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements-build.txt"], check=True)

    # Start Streamlit
    print("Starting Streamlit app...")
    streamlit_cmd = [
        sys.executable,
        "-m", "streamlit",
        "run",
        "app.py",
        "--server.address=0.0.0.0",
        f"--server.port={os.environ['PORT']}",
        "--server.headless=true",
        "--server.enableCORS=true",
        "--server.enableXsrfProtection=false",
        "--server.fileWatcherType=none",
        "--server.runOnSave=false",
        "--theme.base=dark",
        "--browser.gatherUsageStats=false"
    ]
    
    try:
        process = subprocess.Popen(
            streamlit_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1
        )
        
        # Monitor the process output
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
                # If we see the success message, we can stop monitoring
                if "You can now view your Streamlit app in your browser" in output:
                    break
        
        # Keep the process running
        process.wait()
        
    except Exception as e:
        print(f"Error starting Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
