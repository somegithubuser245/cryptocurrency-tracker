#!/usr/bin/env python3
"""
Cryptocurrency Tracker - Development Runner
System-agnostic script to run the entire application stack
"""

import os
import sys
import subprocess
import signal
import time
import argparse
import json
from pathlib import Path
from typing import List, Optional
import threading
import platform

# Import the build output processor helper
from build_utils import BuildOutputProcessor

class Colors:
    """ANSI color codes for cross-platform terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class AppRunner:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.frontend_dir = self.root_dir / "frontend"
        self.backend_dir = self.root_dir / "backend"
        self.processes: List[subprocess.Popen] = []
        self.docker_compose_file = self.root_dir / "docker-compose.yml"
        self.is_windows = platform.system() == "Windows"
        
        # Initialize build output processor helper - ELIMINATES DUPLICATION
        self.build_processor = BuildOutputProcessor()
        
    def log(self, message: str, level: str = "INFO"):
        """Colored logging output"""
        color = {
            "INFO": Colors.OKBLUE,
            "SUCCESS": Colors.OKGREEN,
            "WARNING": Colors.WARNING,
            "ERROR": Colors.FAIL,
            "HEADER": Colors.HEADER
        }.get(level, Colors.ENDC)
        
        timestamp = time.strftime("%H:%M:%S")
        print(f"{color}[{timestamp}] {level}: {message}{Colors.ENDC}")
    
    def check_prerequisites(self) -> bool:
        """Check if required tools are available"""
        self.log("Checking prerequisites...", "HEADER")
        
        # Check Docker
        try:
            result = subprocess.run(["docker", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.log(f"[OK] Docker: {result.stdout.strip()}", "SUCCESS")
            else:
                self.log("[FAIL] Docker not found", "ERROR")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.log("[FAIL] Docker not found or not responding", "ERROR")
            return False
        
        # Check Docker Compose
        try:
            result = subprocess.run(["docker", "compose", "version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.log(f"[OK] Docker Compose: {result.stdout.strip()}", "SUCCESS")
            else:
                # Try legacy docker-compose
                result = subprocess.run(["docker-compose", "--version"], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    self.log(f"[OK] Docker Compose (legacy): {result.stdout.strip()}", "SUCCESS")
                else:
                    self.log("[FAIL] Docker Compose not found", "ERROR")
                    return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.log("[FAIL] Docker Compose not found", "ERROR")
            return False
        
        # Check Node.js (for local development)
        try:
            result = subprocess.run(["node", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.log(f"[OK] Node.js: {result.stdout.strip()}", "SUCCESS")
            else:
                self.log("[WARN] Node.js not found (Docker will be used)", "WARNING")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.log("[WARN] Node.js not found (Docker will be used)", "WARNING")
        
        # Check Python
        try:
            result = subprocess.run([sys.executable, "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.log(f"[OK] Python: {result.stdout.strip()}", "SUCCESS")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.log("[FAIL] Python not found", "ERROR")
            return False
        
        return True
    
    def run_docker_dev(self):
        """Run the full stack using Docker Compose with development settings"""
        self.log("Starting development environment with Docker...", "HEADER")
        
        if not self.docker_compose_file.exists():
            self.log("docker-compose.yml not found!", "ERROR")
            return False
        
        try:
            # Stop any existing containers
            self.log("Stopping existing containers...", "INFO")
            subprocess.run(["docker", "compose", "down"], 
                          cwd=self.root_dir, check=False)
            
            # Build and start services
            self.log("Building and starting services...", "INFO")
            cmd = ["docker", "compose", "up", "--build"]
            
            process = subprocess.Popen(cmd, cwd=self.root_dir)
            self.processes.append(process)
            
            self.log("[STARTED] Development environment started!", "SUCCESS")
            self.log("Frontend: http://localhost:5173", "INFO")
            self.log("Backend: http://localhost:8000", "INFO")
            self.log("Redis: localhost:6379", "INFO")
            self.log("Press Ctrl+C to stop", "WARNING")
            
            # Wait for process to complete
            process.wait()
            
        except KeyboardInterrupt:
            self.log("Received interrupt signal...", "WARNING")
            self.cleanup()
        except Exception as e:
            self.log(f"Error running Docker: {e}", "ERROR")
            return False
        
        return True
    
    def run_docker_prod(self):
        """Run production build with Docker"""
        self.log("Starting production environment...", "HEADER")
        
        try:
            # Build production images
            self.log("Building production images...", "INFO")
            subprocess.run(["docker", "compose", "build", "--no-cache"], 
                          cwd=self.root_dir, check=True)
            
            # Run production stack
            subprocess.run(["docker", "compose", "up", "-d"], 
                          cwd=self.root_dir, check=True)
            
            self.log("[STARTED] Production environment started!", "SUCCESS")
            self.log("Application: http://localhost:5173", "INFO")
            self.log("API: http://localhost:8000", "INFO")
            
        except subprocess.CalledProcessError as e:
            self.log(f"Error starting production environment: {e}", "ERROR")
            return False
        
        return True
    
    def run_local_dev(self):
        """Run development environment locally (without Docker)"""
        self.log("Starting local development environment...", "HEADER")
        
        # Check if npm is available
        try:
            subprocess.run(["npm", "--version"], 
                          capture_output=True, check=True, timeout=10, shell=self.is_windows)
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log("npm not found. Please install Node.js or use Docker mode.", "ERROR")
            return False
        
        try:
            # Install frontend dependencies
            if not (self.frontend_dir / "node_modules").exists():
                self.log("Installing frontend dependencies...", "INFO")
                subprocess.run(["npm", "install"], 
                              cwd=self.frontend_dir, check=True, shell=self.is_windows)
            
            # Install backend dependencies
            if not (self.backend_dir / "venv").exists():
                self.log("Setting up Python virtual environment...", "INFO")
                subprocess.run([sys.executable, "-m", "venv", "venv"], 
                              cwd=self.backend_dir, check=True)
            
            # Activate venv and install requirements
            venv_python = self.backend_dir / "venv" / ("Scripts" if self.is_windows else "bin") / "python"
            if (self.backend_dir / "requirements.txt").exists():
                self.log("Installing backend dependencies...", "INFO")
                subprocess.run([str(venv_python), "-m", "pip", "install", "-r", "requirements.txt"], 
                              cwd=self.backend_dir, check=True)
            
            # Start Redis (if available)
            redis_process = None
            try:
                self.log("Starting Redis server...", "INFO")
                redis_process = subprocess.Popen(["redis-server"], 
                                               stdout=subprocess.DEVNULL, 
                                               stderr=subprocess.DEVNULL)
                self.processes.append(redis_process)
                time.sleep(2)  # Give Redis time to start
            except FileNotFoundError:
                self.log("Redis not found locally. Using Docker for Redis...", "WARNING")
                subprocess.Popen(["docker", "run", "-d", "--name", "crypto-redis", 
                                "-p", "6379:6379", "redis:alpine"], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Start backend
            self.log("Starting backend server...", "INFO")
            backend_cmd = [str(venv_python), "-m", "uvicorn", "src.routes.main:app", 
                          "--host", "0.0.0.0", "--port", "8000", "--reload"]
            backend_process = subprocess.Popen(backend_cmd, cwd=self.backend_dir)
            self.processes.append(backend_process)
            
            # Start frontend
            self.log("Starting frontend development server...", "INFO")
            frontend_process = subprocess.Popen(["npm", "run", "dev"], 
                                               cwd=self.frontend_dir, shell=self.is_windows)
            self.processes.append(frontend_process)
            
            self.log("[STARTED] Local development environment started!", "SUCCESS")
            self.log("Frontend: http://localhost:5173", "INFO")
            self.log("Backend: http://localhost:8000", "INFO")
            self.log("Press Ctrl+C to stop", "WARNING")
            
            # Wait for processes
            for process in self.processes:
                process.wait()
                
        except KeyboardInterrupt:
            self.log("Received interrupt signal...", "WARNING")
            self.cleanup()
        except subprocess.CalledProcessError as e:
            self.log(f"Error in local development: {e}", "ERROR")
            return False
        except Exception as e:
            self.log(f"Unexpected error: {e}", "ERROR")
            return False
        
        return True
    
    def build_frontend(self, watch=False, docker=False):
        """Build frontend for production with optional watch mode and Docker support"""
        mode = "watch mode" if watch else "production"
        method = "Docker" if docker else "local"
        self.log(f"Building frontend for {mode} using {method}...", "HEADER")
        
        if docker:
            return self._build_frontend_docker(watch)
        else:
            return self._build_frontend_local(watch)
    
    def _build_frontend_docker(self, watch=False):
        """Build frontend using Docker with helper - ELIMINATES DUPLICATION"""
        try:
            if watch:
                # Run development mode with HMR through Docker
                self.log("Starting Docker development build with HMR...", "INFO")
                cmd = ["docker", "compose", "up", "--build", "frontend"]
            else:
                # Build production version
                self.log("Building production frontend in Docker...", "INFO")
                cmd = ["docker", "compose", "run", "--rm", "frontend", "npm", "run", "build"]
            
            # Use helper to monitor build process - ELIMINATES DUPLICATION
            process = self.build_processor.create_monitored_process(cmd, cwd=self.root_dir)
            success, build_errors, build_warnings = self.build_processor.process_build_output(process)
            
            # Use helper to log results - ELIMINATES DUPLICATION
            self.build_processor.log_build_results(
                success, build_errors, build_warnings, "Docker frontend build"
            )
            
            return success
                
        except subprocess.CalledProcessError as e:
            self.log(f"Docker frontend build failed: {e}", "ERROR")
            return False
        except Exception as e:
            self.log(f"Unexpected error during Docker build: {e}", "ERROR")
            return False
    
    def _build_frontend_local(self, watch=False):
        """Build frontend locally with helper - ELIMINATES DUPLICATION"""
        try:
            # Install dependencies if needed
            if not (self.frontend_dir / "node_modules").exists():
                self.log("Installing frontend dependencies...", "INFO")
                install_result = subprocess.run(
                    ["npm", "install"], 
                    cwd=self.frontend_dir, 
                    capture_output=True, 
                    text=True,
                    shell=self.is_windows
                )
                if install_result.returncode != 0:
                    self.log("Failed to install dependencies:", "ERROR")
                    self.log(install_result.stderr, "ERROR")
                    return False
            
            # Build frontend
            build_cmd = ["npm", "run", "dev"] if watch else ["npm", "run", "build"]
            self.log(f"Running: {' '.join(build_cmd)}", "INFO")
            
            if watch:
                # For watch mode, run in background
                process = subprocess.Popen(build_cmd, cwd=self.frontend_dir, shell=self.is_windows)
                self.processes.append(process)
                self.log("[SUCCESS] Frontend development server started with HMR!", "SUCCESS")
                self.log("Press Ctrl+C to stop", "WARNING")
                try:
                    process.wait()
                except KeyboardInterrupt:
                    self.cleanup()
                return True
            else:
                # Use helper to monitor build process - ELIMINATES DUPLICATION
                process = self.build_processor.create_monitored_process(
                    build_cmd, cwd=self.frontend_dir, shell=self.is_windows
                )
                success, build_errors, build_warnings = self.build_processor.process_build_output(process)
                
                # Use helper to log results - ELIMINATES DUPLICATION
                self.build_processor.log_build_results(
                    success, build_errors, build_warnings, "Local frontend build"
                )
                
                return success
            
        except subprocess.CalledProcessError as e:
            self.log(f"Local frontend build failed: {e}", "ERROR")
            return False
        except Exception as e:
            self.log(f"Unexpected error during local build: {e}", "ERROR")
            return False
    
    def cleanup(self):
        """Clean up running processes"""
        self.log("Cleaning up processes...", "WARNING")
        
        # Terminate local processes
        for process in self.processes:
            try:
                if process.poll() is None:  # Process is still running
                    process.terminate()
                    time.sleep(2)
                    if process.poll() is None:  # Still running, force kill
                        process.kill()
            except Exception as e:
                self.log(f"Error terminating process: {e}", "ERROR")
        
        # Stop Docker containers
        try:
            subprocess.run(["docker", "compose", "down"], 
                          cwd=self.root_dir, check=False, 
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass
        
        self.log("Cleanup completed", "INFO")
    
    def status(self):
        """Show status of running services"""
        self.log("Checking service status...", "HEADER")
        
        try:
            # Check Docker containers
            result = subprocess.run(["docker", "compose", "ps"], 
                                  cwd=self.root_dir, capture_output=True, text=True)
            if result.stdout.strip():
                self.log("Docker services:", "INFO")
                print(result.stdout)
            else:
                self.log("No Docker services running", "INFO")
                
        except Exception as e:
            self.log(f"Error checking Docker status: {e}", "ERROR")

def main():
    parser = argparse.ArgumentParser(description="Cryptocurrency Tracker Development Runner")
    parser.add_argument("command", choices=["dev", "prod", "local", "build", "status", "stop"], 
                       help="Command to run")
    parser.add_argument("--check", action="store_true", 
                       help="Check prerequisites only")
    parser.add_argument("--watch", action="store_true",
                       help="Enable watch mode for build command (HMR)")
    parser.add_argument("--docker", action="store_true",
                       help="Use Docker for build command")
    
    args = parser.parse_args()
    
    runner = AppRunner()
    
    # Always check prerequisites first
    if not runner.check_prerequisites():
        runner.log("Prerequisites check failed. Please install missing tools.", "ERROR")
        sys.exit(1)
    
    if args.check:
        runner.log("Prerequisites check passed!", "SUCCESS")
        sys.exit(0)
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        runner.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        if args.command == "dev":
            success = runner.run_docker_dev()
        elif args.command == "prod":
            success = runner.run_docker_prod()
        elif args.command == "local":
            success = runner.run_local_dev()
        elif args.command == "build":
            success = runner.build_frontend(watch=args.watch, docker=args.docker)
        elif args.command == "status":
            runner.status()
            success = True
        elif args.command == "stop":
            runner.cleanup()
            success = True
        else:
            parser.print_help()
            success = False
        
        if not success:
            sys.exit(1)
            
    except KeyboardInterrupt:
        runner.cleanup()
        sys.exit(0)
    except Exception as e:
        runner.log(f"Unexpected error: {e}", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()