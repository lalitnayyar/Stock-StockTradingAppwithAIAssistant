#!/usr/bin/env python3
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

def set_environment():
    """Set required environment variables"""
    env_vars = {
        'STREAMLIT_BROWSER_GATHER_USAGE_STATS': 'false',
        'PIP_DISABLE_PIP_VERSION_CHECK': '1',
        'PYTHONWARNINGS': 'ignore',
        'PYTHONUNBUFFERED': '1',
        'ASDF_PYTHON_QUIET_RESHIM': '1',
        'STREAMLIT_SERVER_PORT': '8501',
        'STREAMLIT_SERVER_ADDRESS': '0.0.0.0',
        'STREAMLIT_SERVER_HEADLESS': 'true',
        'STREAMLIT_SERVER_ENABLE_CORS': 'true',
        'STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION': 'false',
        'STREAMLIT_SERVER_FILE_WATCHER_TYPE': 'none',
        'STREAMLIT_SERVER_RUN_ON_SAVE': 'false',
        'STREAMLIT_THEME_BASE': 'dark',
        'STREAMLIT_LOGGER_LEVEL': 'error'
    }
    os.environ.update(env_vars)

def kill_process_on_port(port):
    """Kill any process running on the specified port"""
    try:
        if sys.platform == 'win32':
            cmd = f'netstat -ano | findstr :{port}'
            result = subprocess.check_output(cmd, shell=True).decode()
            if result:
                pid = result.split()[-1]
                subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True)
        else:
            # Try different commands to find and kill the process
            try:
                # Try ss command first (usually available on modern Linux)
                cmd = f"ss -lptn 'sport = :{port}'"
                output = subprocess.check_output(cmd, shell=True).decode()
                if output:
                    pid = output.split('pid=')[-1].split(',')[0]
                    if pid:
                        subprocess.run(['kill', '-9', pid], check=False)
            except:
                try:
                    # Try netstat as fallback
                    cmd = f"netstat -tlpn | grep :{port}"
                    output = subprocess.check_output(cmd, shell=True).decode()
                    if output:
                        pid = output.split()[-1].split('/')[0]
                        if pid:
                            subprocess.run(['kill', '-9', pid], check=False)
                except:
                    # If both fail, try fuser as last resort
                    try:
                        cmd = f"fuser -k {port}/tcp"
                        subprocess.run(cmd, shell=True, check=False)
                    except:
                        pass  # If all methods fail, continue anyway
    except Exception as e:
        print(f"Warning: Could not kill process on port {port}: {e}")

class StreamlitRunner:
    def __init__(self):
        self.process = None
        self.port = 8501
        
    def setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            print("\nReceived shutdown signal. Cleaning up...")
            self.cleanup()
            sys.exit(0)
            
        if sys.platform != 'win32':
            signal.signal(signal.SIGTERM, signal_handler)
            signal.signal(signal.SIGINT, signal_handler)
    
    def cleanup(self):
        """Clean up resources"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                try:
                    self.process.kill()
                except:
                    pass
    
    def run(self):
        """Run the Streamlit application"""
        try:
            # Set environment variables
            set_environment()
            
            # Kill any existing process
            kill_process_on_port(self.port)
            
            # Get the absolute path to app.py
            app_path = Path(__file__).parent / 'app.py'
            
            # Prepare Streamlit command
            cmd = [
                sys.executable,
                '-m', 'streamlit',
                'run',
                str(app_path),
                '--server.address=0.0.0.0',
                f'--server.port={self.port}',
                '--server.headless=true',
                '--server.enableCORS=true',
                '--server.enableXsrfProtection=false',
                '--server.fileWatcherType=none',
                '--server.runOnSave=false',
                '--theme.base=dark',
                '--browser.gatherUsageStats=false',
                '--logger.level=error'
            ]
            
            # Start Streamlit process
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                env=os.environ
            )
            
            print("Starting Streamlit application...")
            time.sleep(2)  # Give it a moment to start
            
            # Monitor the process
            while True:
                if self.process.poll() is not None:
                    stdout, stderr = self.process.communicate()
                    print("Streamlit process ended unexpectedly")
                    if stderr:
                        print(f"Error: {stderr}")
                    break
                    
                # Read output line by line
                while True:
                    line = self.process.stdout.readline()
                    if not line:
                        break
                    
                    # Filter out noise
                    if not any(msg in line for msg in [
                        'Reshimming asdf python',
                        'new release of pip',
                        'To update, run: pip',
                        'ASDF_PYTHON_VERSION'
                    ]):
                        print(line.strip())
                        
                    # Check for successful startup
                    if 'You can now view your Streamlit app in your browser' in line:
                        print("Streamlit application started successfully!")
                        
                time.sleep(0.1)  # Prevent CPU thrashing
                
        except KeyboardInterrupt:
            print("\nShutting down gracefully...")
            self.cleanup()
        except Exception as e:
            print(f"Error running Streamlit: {e}")
            self.cleanup()
            sys.exit(1)

if __name__ == '__main__':
    runner = StreamlitRunner()
    runner.setup_signal_handlers()
    runner.run()
