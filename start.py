import subprocess
import os
import sys
import time

def main():
    # Set environment variables
    os.environ["STREAMLIT_SERVER_PORT"] = "8501"
    os.environ["STREAMLIT_SERVER_ADDRESS"] = "0.0.0.0"
    os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
    os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    os.environ["STREAMLIT_SERVER_BASE_URL"] = "/_app"
    os.environ["STREAMLIT_SERVER_ENABLE_CORS"] = "true"
    os.environ["STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION"] = "false"

    # Create public directory if it doesn't exist
    if not os.path.exists("public"):
        os.makedirs("public")

    # Install dependencies
    print("Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements-build.txt"])

    # Run the Streamlit app
    print("Starting Streamlit app...")
    process = subprocess.Popen([
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "app.py",
        "--server.port=8501",
        "--server.address=0.0.0.0",
        "--server.headless=true",
        "--server.baseUrlPath=_app",
        "--server.enableCORS=true",
        "--server.enableXsrfProtection=false",
        "--browser.gatherUsageStats=false"
    ])

    # Keep the script running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        process.terminate()
        process.wait()

if __name__ == "__main__":
    main()
