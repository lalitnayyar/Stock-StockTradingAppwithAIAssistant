import os
import signal
import subprocess
import sys
import time
from pathlib import Path

def set_environment():
    """Set required environment variables"""
    os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    os.environ['PIP_DISABLE_PIP_VERSION_CHECK'] = '1'
    os.environ['PYTHONWARNINGS'] = 'ignore'

def kill_process_on_port(port):
    """Kill any process running on the specified port"""
    try:
        if sys.platform == 'win32':
            subprocess.run(['taskkill', '/F', '/PID', 
                          subprocess.check_output(['netstat', '-ano', '|', 'findstr', f':{port}']).decode().split()[-1]], 
                         capture_output=True)
        else:
            subprocess.run(['lsof', '-ti', f':{port}', '|', 'xargs', 'kill', '-9'], shell=True)
    except:
        pass

def run_streamlit():
    """Run the Streamlit application with timeout"""
    try:
        # Kill any existing process on port 8501
        kill_process_on_port(8501)
        
        # Set environment variables
        set_environment()
        
        # Get the absolute path to app.py
        app_path = Path(__file__).parent / 'app.py'
        
        # Start Streamlit with a timeout
        process = subprocess.Popen(['streamlit', 'run', str(app_path)],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 text=True)
        
        # Wait for a short time to check if the process starts successfully
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is None:
            print("Streamlit application started successfully")
            process.wait()
        else:
            stdout, stderr = process.communicate()
            print("Error starting Streamlit:", stderr)
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            process.kill()
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    # Set up signal handler for graceful shutdown
    if sys.platform != 'win32':
        signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    
    run_streamlit()
