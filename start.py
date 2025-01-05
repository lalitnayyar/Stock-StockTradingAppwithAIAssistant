import os
import sys
import subprocess

def main():
    # Set environment variables
    os.environ["STREAMLIT_SERVER_PORT"] = os.environ.get("PORT", "8501")
    os.environ["STREAMLIT_SERVER_ADDRESS"] = "0.0.0.0"
    os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
    os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    os.environ["STREAMLIT_SERVER_ENABLE_CORS"] = "true"
    os.environ["STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION"] = "false"
    os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"
    os.environ["STREAMLIT_SERVER_RUN_ON_SAVE"] = "false"
    os.environ["STREAMLIT_THEME_BASE"] = "dark"

    # Create public directory if it doesn't exist
    if not os.path.exists("public"):
        os.makedirs("public")

    # Install dependencies
    print("Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements-build.txt"])

    # Run the Streamlit app directly
    print("Starting Streamlit app...")
    subprocess.check_call([sys.executable, "-m", "streamlit", "run", "app.py", "--server.address", "0.0.0.0"])

if __name__ == "__main__":
    main()
