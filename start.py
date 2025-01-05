import subprocess
import sys
import os

def main():
    # Install dependencies
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Run Streamlit
    os.environ["STREAMLIT_SERVER_PORT"] = "8501"
    os.environ["STREAMLIT_SERVER_ADDRESS"] = "0.0.0.0"
    subprocess.check_call([sys.executable, "-m", "streamlit", "run", "app.py"])

if __name__ == "__main__":
    main()
