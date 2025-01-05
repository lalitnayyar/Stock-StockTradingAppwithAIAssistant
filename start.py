import os
import sys
import subprocess
import time

def suppress_warnings():
    """Configure environment to suppress common warnings"""
    os.environ["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"  # Suppress pip upgrade warning
    os.environ["PYTHONWARNINGS"] = "ignore"  # Suppress Python warnings
    os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    os.environ["PYTHONUNBUFFERED"] = "1"

def upgrade_pip_silently():
    """Upgrade pip without showing warnings"""
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
            check=True,
            capture_output=True,
            env={**os.environ, "PIP_DISABLE_PIP_VERSION_CHECK": "1"}
        )
        return True
    except subprocess.CalledProcessError:
        return False

def install_requirements():
    """Install dependencies with error handling and retries"""
    max_retries = 3
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            print(f"Installing dependencies (attempt {attempt + 1}/{max_retries})...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "requirements-build.txt"],
                check=True,
                capture_output=True,
                text=True,
                env={**os.environ, "PIP_DISABLE_PIP_VERSION_CHECK": "1"}
            )
            print("Dependencies installed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies (attempt {attempt + 1}):")
            if e.stderr:
                print(e.stderr)
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Failed to install dependencies after multiple attempts")
                return False

def start_streamlit():
    """Start Streamlit with proper error handling"""
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
            bufsize=1,
            env={**os.environ, "STREAMLIT_BROWSER_GATHER_USAGE_STATS": "false"}
        )
        
        start_time = time.time()
        timeout = 300  # 5 minutes
        success_message_seen = False
        error_count = 0
        max_errors = 5
        
        while True:
            if time.time() - start_time > timeout:
                print("Startup timed out after 5 minutes")
                process.kill()
                return False
            
            # Handle stdout
            output = process.stdout.readline()
            if output:
                # Filter out reshimming message
                if "Reshimming asdf python" not in output:
                    print(output.strip())
                if "You can now view your Streamlit app in your browser" in output:
                    success_message_seen = True
                    print("Streamlit app started successfully!")
                    break
            
            # Handle stderr
            error = process.stderr.readline()
            if error:
                error_text = error.strip()
                # Filter out common warnings
                if not any(warning in error_text for warning in [
                    "new release of pip",
                    "Reshimming asdf python"
                ]):
                    print(f"Error: {error_text}")
                    error_count += 1
                    if error_count >= max_errors:
                        print("Too many errors encountered")
                        process.kill()
                        return False
            
            # Check if process has ended
            if output == '' and error == '' and process.poll() is not None:
                break
        
        if not success_message_seen:
            print("Failed to start Streamlit app")
            return False
        
        # Keep the process running
        process.wait()
        return True
        
    except Exception as e:
        print(f"Error starting Streamlit: {e}")
        return False

def main():
    # Suppress warnings and configure environment
    suppress_warnings()
    
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
    
    # Upgrade pip silently
    upgrade_pip_silently()
    
    # Install dependencies
    if not install_requirements():
        sys.exit(1)
    
    # Start Streamlit
    print("Starting Streamlit app...")
    if not start_streamlit():
        sys.exit(1)

if __name__ == "__main__":
    main()
