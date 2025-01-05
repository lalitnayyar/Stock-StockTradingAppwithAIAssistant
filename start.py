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

    # Create public directory if it doesn't exist
    if not os.path.exists("public"):
        os.makedirs("public")

    # Install dependencies
    print("Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements-build.txt"])

    # Run the Streamlit app
    print("Starting Streamlit app...")
    os.execv(sys.executable, [sys.executable, '-m', 'streamlit', 'run', 'app.py'])

if __name__ == "__main__":
    main()
