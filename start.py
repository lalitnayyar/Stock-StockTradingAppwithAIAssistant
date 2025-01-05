import os
import sys
import subprocess
import time

def upgrade_pip():
    """Upgrade pip to avoid warnings"""
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, 
                      capture_output=True)
        return True
    except subprocess.CalledProcessError:
        print("Warning: Could not upgrade pip, continuing with installation...")
        return False

def install_requirements():
    """Install dependencies with error handling"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"Installing dependencies (attempt {attempt + 1}/{max_retries})...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements-build.txt"],
                         check=True,
                         capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                print("Retrying in 5 seconds...")
                time.sleep(5)
            else:
                print("Failed to install dependencies after multiple attempts")
                return False

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
    
    # Suppress pip warnings in output
    os.environ["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"

    # Upgrade pip silently (avoid warnings)
    upgrade_pip()

    # Install dependencies with retry mechanism
    if not install_requirements():
        sys.exit(1)

    # Create public directory if it doesn't exist
    if not os.path.exists("public"):
        os.makedirs("public")

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
        
        # Monitor the process output with timeout
        start_time = time.time()
        timeout = 300  # 5 minutes timeout
        success_message_seen = False
        
        while True:
            if time.time() - start_time > timeout:
                print("Startup timed out after 5 minutes")
                process.kill()
                sys.exit(1)
                
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
                
            if output:
                print(output.strip())
                if "You can now view your Streamlit app in your browser" in output:
                    success_message_seen = True
                    print("Streamlit app started successfully!")
                    break
            
            # Check for common error patterns
            error = process.stderr.readline()
            if error:
                print(f"Error: {error.strip()}")
                if "Address already in use" in error:
                    print("Port is already in use. Trying to kill existing process...")
                    process.kill()
                    sys.exit(1)
        
        if not success_message_seen:
            print("Failed to start Streamlit app")
            process.kill()
            sys.exit(1)
            
        # Keep the process running
        process.wait()
        
    except Exception as e:
        print(f"Error starting Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
