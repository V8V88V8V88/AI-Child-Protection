import os
import sys
import platform
import tempfile
import subprocess
import time
import argparse
import signal
import logging
from .host_blocker import block_sites, is_admin, hosts_path, test_site_blocking


log_dir = os.path.join(tempfile.gettempdir(), "ai_child_protection_logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "block_service.log")

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


running = True
CHECK_INTERVAL = 300  

def signal_handler(sig, frame):
    """Handle termination signals"""
    global running
    logging.info(f"Received signal {sig}, shutting down...")
    running = False

def create_windows_service():
    """Create a Windows service to run the blocker on startup"""
    if not is_admin():
        logging.error("Admin privileges required to create Windows service")
        return "❌ Admin privileges required to create Windows service"
    
    try:
        
        python_exe = sys.executable
        script_path = os.path.abspath(__file__)
        
        
        batch_dir = os.path.join(tempfile.gettempdir(), "ai_child_protection")
        os.makedirs(batch_dir, exist_ok=True)
        batch_path = os.path.join(batch_dir, "run_blocker.bat")
        
        with open(batch_path, 'w') as f:
            f.write(f'@echo off\n"{python_exe}" "{script_path}" --daemon')
        
        
        task_name = "AIChildProtectionBlocker"
        
        
        subprocess.run(
            ["schtasks", "/delete", "/tn", task_name, "/f"], 
            shell=True, 
            stderr=subprocess.DEVNULL, 
            stdout=subprocess.DEVNULL
        )
        
        
        result = subprocess.run(
            [
                "schtasks", "/create", "/tn", task_name, 
                "/tr", batch_path, 
                "/sc", "onstart", 
                "/ru", "SYSTEM",
                "/rl", "HIGHEST"
            ],
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logging.info("Windows service created successfully")
            return "✅ Windows service created successfully"
        else:
            logging.error(f"Failed to create Windows service: {result.stderr}")
            return f"❌ Failed to create Windows service: {result.stderr}"
    
    except Exception as e:
        logging.exception("Error creating Windows service")
        return f"❌ Error creating Windows service: {e}"

def create_linux_service():
    """Create a Linux systemd service to run the blocker on startup"""
    if not is_admin():
        logging.error("Root privileges required to create Linux service")
        return "❌ Root privileges required to create Linux service"
    
    try:
        
        python_exe = sys.executable
        script_path = os.path.abspath(__file__)
        
        
        service_content = f"""[Unit]
Description=AI Child Protection Website Blocker
After=network.target

[Service]
Type=simple
ExecStart={python_exe} {script_path} --daemon
Restart=on-failure
User=root

[Install]
WantedBy=multi-user.target
"""
        
        service_path = "/etc/systemd/system/aichildprotection.service"
        
        with open(service_path, 'w') as f:
            f.write(service_content)
        
        
        subprocess.run(["systemctl", "daemon-reload"], check=True)
        subprocess.run(["systemctl", "enable", "aichildprotection"], check=True)
        subprocess.run(["systemctl", "start", "aichildprotection"], check=True)
        
        logging.info("Linux service created successfully")
        return "✅ Linux service created successfully"
    
    except Exception as e:
        logging.exception("Error creating Linux service")
        return f"❌ Error creating Linux service: {e}"

def remove_windows_service():
    """Remove the Windows service"""
    if not is_admin():
        return "❌ Admin privileges required to remove Windows service"
    
    try:
        task_name = "AIChildProtectionBlocker"
        result = subprocess.run(
            ["schtasks", "/delete", "/tn", task_name, "/f"],
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logging.info("Windows service removed successfully")
            return "✅ Windows service removed successfully"
        else:
            logging.error(f"Failed to remove Windows service: {result.stderr}")
            return f"❌ Failed to remove Windows service: {result.stderr}"
    
    except Exception as e:
        logging.exception("Error removing Windows service")
        return f"❌ Error removing Windows service: {e}"

def remove_linux_service():
    """Remove the Linux systemd service"""
    if not is_admin():
        return "❌ Root privileges required to remove Linux service"
    
    try:
        service_name = "aichildprotection"
        
        
        try:
            subprocess.run(["systemctl", "stop", service_name], check=False, capture_output=True)
        except Exception as e:
            logging.warning(f"Error stopping service: {e}")
            
        try:
            subprocess.run(["systemctl", "disable", service_name], check=False, capture_output=True)
        except Exception as e:
            logging.warning(f"Error disabling service: {e}")
        
        
        service_path = f"/etc/systemd/system/{service_name}.service"
        if os.path.exists(service_path):
            try:
                os.remove(service_path)
            except Exception as e:
                logging.warning(f"Error removing service file: {e}")
        
        
        try:
            subprocess.run(["systemctl", "daemon-reload"], check=False, capture_output=True)
        except Exception as e:
            logging.warning(f"Error reloading systemd: {e}")
        
        logging.info("Linux service removal attempted")
        
        
        return "✅ Linux service removal attempted - check logs for detailed status"
    except Exception as e:
        logging.exception("Error removing Linux service")
        return f"❌ Error removing Linux service: {e}"

def is_service_running():
    """Check if the service is already running"""
    system = platform.system().lower()
    
    try:
        if system == "windows":
            result = subprocess.run(
                ["schtasks", "/query", "/tn", "AIChildProtectionBlocker"],
                shell=True,
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        elif system == "linux":
            result = subprocess.run(
                ["systemctl", "is-active", "aichildprotection"],
                capture_output=True,
                text=True
            )
            return "active" in result.stdout
        else:
            return False
    except Exception:
        return False

def run_daemon():
    """Run as a daemon process, periodically checking and enforcing site blocking"""
    global running
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logging.info("Starting AI Child Protection block service daemon")
    
    if not is_admin():
        logging.error("Admin/root privileges required to run the service")
        return "❌ Admin/root privileges required to run the service"
    
    while running:
        try:
            
            logging.info("Checking and enforcing site blocking")
            result = block_sites()
            logging.info(f"Block result: {result}")
            
            
            test_result = test_site_blocking("pornhub.com")
            logging.info(f"Block test: {test_result}")
            
            
            for _ in range(CHECK_INTERVAL):
                if not running:
                    break
                time.sleep(1)
        
        except Exception as e:
            logging.exception(f"Error in daemon loop: {e}")
            
            time.sleep(60)
    
    logging.info("Block service daemon shutting down")
    return "✅ Service stopped"

def create_service():
    """Create the appropriate service for the current OS"""
    system = platform.system().lower()
    
    if system == "windows":
        return create_windows_service()
    elif system == "linux":
        return create_linux_service()
    else:
        return f"❌ Unsupported OS for service creation: {system}"

def remove_service():
    """Remove the service for the current OS"""
    system = platform.system().lower()
    
    if system == "windows":
        return remove_windows_service()
    elif system == "linux":
        return remove_linux_service()
    else:
        return f"❌ Unsupported OS for service removal: {system}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Child Protection Block Service")
    parser.add_argument("--daemon", action="store_true", help="Run as a daemon process")
    parser.add_argument("--install", action="store_true", help="Install as a service")
    parser.add_argument("--uninstall", action="store_true", help="Uninstall the service")
    
    args = parser.parse_args()
    
    if args.daemon:
        run_daemon()
    elif args.install:
        print(create_service())
    elif args.uninstall:
        print(remove_service())
    else:
        parser.print_help() 