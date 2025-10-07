#!/usr/bin/env python3
"""
Simple daemon test script for HPC environment
This creates a basic daemon that writes to a log file every 30 seconds
"""

import time
import os
import sys
from datetime import datetime
from pathlib import Path


class SimpleDaemon:
    """Very simple daemon for testing on HPC"""
    
    def __init__(self, log_file='daemon_test.log', check_interval=30):
        """
        Args:
            log_file: Path to log file
            check_interval: Seconds between checks
        """
        self.log_file = Path(log_file)
        self.check_interval = check_interval
        self.pid_file = Path('daemon_test.pid')
        
    def log(self, message):
        """Write message to log file with timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] {message}\n")
        print(f"[{timestamp}] {message}")
    
    def write_pid(self):
        """Write current process ID to file"""
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))
        self.log(f"Daemon started with PID: {os.getpid()}")
    
    def remove_pid(self):
        """Remove PID file"""
        if self.pid_file.exists():
            self.pid_file.unlink()
    
    def is_running(self):
        """Check if daemon is already running"""
        if not self.pid_file.exists():
            return False
        
        # Read PID from file
        with open(self.pid_file, 'r') as f:
            pid = int(f.read().strip())
        
        # Check if process exists
        try:
            os.kill(pid, 0)  # Doesn't actually kill, just checks if exists
            return True
        except OSError:
            # Process doesn't exist, remove stale PID file
            self.remove_pid()
            return False
    
    def run(self):
        """Main daemon loop"""
        # Check if already running
        if self.is_running():
            print(f"ERROR: Daemon is already running (PID file: {self.pid_file})")
            sys.exit(1)
        
        # Write PID file
        self.write_pid()
        
        # Initialize counter
        counter = 0
        
        self.log("="*60)
        self.log("Simple Daemon Test Started")
        self.log(f"Check interval: {self.check_interval} seconds")
        self.log(f"Log file: {self.log_file.absolute()}")
        self.log(f"PID file: {self.pid_file.absolute()}")
        self.log("="*60)
        
        try:
            while True:
                counter += 1
                
                # Simulate checking something
                self.log(f"Check #{counter}: Daemon is alive and working!")

                # Sleep until next check
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.log("\nReceived interrupt signal, shutting down...")
            self.remove_pid()
            self.log("Daemon stopped gracefully")
        except Exception as e:
            self.log(f"ERROR: {str(e)}")
            self.remove_pid()
            raise


def stop_daemon(pid_file='daemon_test.pid'):
    """Stop the running daemon"""
    pid_path = Path(pid_file)
    
    if not pid_path.exists():
        print("No daemon running (PID file not found)")
        return
    
    with open(pid_path, 'r') as f:
        pid = int(f.read().strip())
    
    try:
        print(f"Stopping daemon with PID {pid}...")
        os.kill(pid, 15)
        time.sleep(2)
        
        # Check if still running
        try:
            os.kill(pid, 0)
            print("Warning: Process still running, forcing kill...")
            os.kill(pid, 9)  # SIGKILL
        except OSError:
            print("Daemon stopped successfully")
        
        # Remove PID file
        if pid_path.exists():
            pid_path.unlink()
            
    except OSError as e:
        print(f"Error stopping daemon: {e}")
        # Remove stale PID file
        if pid_path.exists():
            pid_path.unlink()


def status_daemon(pid_file='daemon_test.pid'):
    """Check daemon status"""
    pid_path = Path(pid_file)
    
    if not pid_path.exists():
        print("Daemon is NOT running (no PID file)")
        return
    
    with open(pid_path, 'r') as f:
        pid = int(f.read().strip())
    
    try:
        os.kill(pid, 0)
        print(f"Daemon is RUNNING with PID {pid}")
        
        # Show last few log entries
        log_file = Path('daemon_test.log')
        if log_file.exists():
            print("\nLast 5 log entries:")
            print("-" * 60)
            with open(log_file, 'r') as f:
                lines = f.readlines()
                for line in lines[-5:]:
                    print(line.rstrip())
    except OSError:
        print(f"Daemon is NOT running (stale PID {pid})")
        pid_path.unlink()


# ==============================================================================
# MAIN - Command Line Interface
# ==============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple daemon test for HPC')
    parser.add_argument('action', choices=['start', 'stop', 'restart', 'status'],
                       help='Action to perform')
    parser.add_argument('--interval', type=int, default=30,
                       help='Check interval in seconds (default: 30)')
    parser.add_argument('--log', default='daemon_test.log',
                       help='Log file path (default: daemon_test.log)')
    
    args = parser.parse_args()
    
    if args.action == 'start':
        daemon = SimpleDaemon(log_file=args.log, check_interval=args.interval)
        daemon.run()
        
    elif args.action == 'stop':
        stop_daemon()
        
    elif args.action == 'restart':
        print("Stopping daemon...")
        stop_daemon()
        time.sleep(2)
        print("Starting daemon...")
        daemon = SimpleDaemon(log_file=args.log, check_interval=args.interval)
        daemon.run()
        
    elif args.action == 'status':
        status_daemon()