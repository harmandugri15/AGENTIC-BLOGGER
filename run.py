#!/usr/bin/env python3
"""
Enterprise Agentic System Runner CLI
Replaces legacy batch scripts with a unified, cross-platform runner supporting:
- Concurrent backend + frontend development mode
- Process monitoring and graceful termination
- Test runner and build verification
- Environment validation and port checks
"""

import os
import sys
import time
import signal
import subprocess
import argparse
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = ROOT_DIR / "frontend"
BACKEND_DIR = ROOT_DIR / "backend"

# ANSI Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"

def log(tag: str, msg: str, color: str = CYAN):
    timestamp = time.strftime("%H:%M:%S")
    print(f"{color}{BOLD}[{timestamp}] [{tag}]{RESET} {msg}")

def check_environment():
    """Validates python, node, and .env file."""
    log("ENV", "Checking runtime prerequisites...", CYAN)
    
    # Check .env
    env_file = ROOT_DIR / ".env"
    if not env_file.exists():
        log("ENV", ".env file not found. Creating from .env.example...", YELLOW)
        example = ROOT_DIR / ".env.example"
        if example.exists():
            import shutil
            shutil.copy(example, env_file)
    else:
        log("ENV", ".env configuration detected.", GREEN)

    # Check node / npm
    try:
        npm_ver = subprocess.check_output(["npm", "--version"], text=True, shell=True).strip()
        log("ENV", f"Node/npm detected: v{npm_ver}", GREEN)
    except Exception:
        log("ENV", "Warning: npm not found in PATH.", RED)

    # Check python
    log("ENV", f"Python runtime: {sys.version.split()[0]} ({sys.executable})", GREEN)

def run_backend(host="127.0.0.1", port=8000, reload=True):
    """Starts FastAPI / Uvicorn backend server."""
    log("BACKEND", f"Starting server on http://{host}:{port} (reload={reload})...", MAGENTA)
    os.environ["PYTHONPATH"] = str(ROOT_DIR)
    cmd = [
        sys.executable, "-m", "uvicorn",
        "backend.app.main:app",
        "--host", host,
        "--port", str(port)
    ]
    if reload:
        cmd.append("--reload")

    try:
        return subprocess.Popen(cmd, cwd=str(ROOT_DIR))
    except Exception as e:
        log("BACKEND", f"Failed to start backend: {e}", RED)
        return None

def run_frontend(port=5173):
    """Starts Vite frontend dev server."""
    log("FRONTEND", f"Starting Vite dashboard on port {port}...", CYAN)
    cmd = ["npm", "run", "dev", "--", "--host", "--port", str(port)]
    try:
        return subprocess.Popen(cmd, cwd=str(FRONTEND_DIR), shell=True)
    except Exception as e:
        log("FRONTEND", f"Failed to start frontend: {e}", RED)
        return None

def run_dev():
    """Runs backend and frontend concurrently with unified logging and clean Ctrl+C shutdown."""
    print(f"\n{BOLD}{CYAN}======================================================={RESET}")
    print(f"{BOLD}{GREEN}  Enterprise Agentic Content Intelligence Platform{RESET}")
    print(f"{BOLD}{CYAN}======================================================={RESET}\n")

    check_environment()

    procs = []
    try:
        # Start backend on 8000
        p_backend = run_backend()
        if p_backend:
            procs.append(("Backend", p_backend))

        time.sleep(1.5)

        # Start frontend on 5173
        p_frontend = run_frontend()
        if p_frontend:
            procs.append(("Frontend", p_frontend))

        log("RUNNER", "All services running! Press Ctrl+C to stop all processes gracefully.", GREEN)

        # Monitor processes
        while True:
            time.sleep(1)
            for name, p in procs:
                if p.poll() is not None:
                    log("RUNNER", f"{name} exited unexpectedly with code {p.returncode}.", YELLOW)
                    return

    except KeyboardInterrupt:
        log("RUNNER", "\nGraceful shutdown signal received. Terminating all processes...", YELLOW)
    finally:
        for name, p in procs:
            log("RUNNER", f"Stopping {name} (PID {p.pid})...", CYAN)
            p.terminate()
            try:
                p.wait(timeout=3)
            except Exception:
                p.kill()
        log("RUNNER", "All processes stopped cleanly.", GREEN)

def run_tests():
    """Runs pytest test suite."""
    log("TEST", "Executing pytest test suite...", CYAN)
    cmd = [sys.executable, "-m", "pytest", "backend/tests", "-v"]
    result = subprocess.run(cmd, cwd=str(ROOT_DIR))
    sys.exit(result.returncode)

def run_build():
    """Runs frontend production build."""
    log("BUILD", "Compiling production frontend bundle...", CYAN)
    cmd = ["npm", "run", "build"]
    result = subprocess.run(cmd, cwd=str(FRONTEND_DIR), shell=True)
    sys.exit(result.returncode)

def run_status():
    """Checks the health of the services."""
    import urllib.request
    log("STATUS", "Checking services status...", CYAN)

    # Check backend
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/api/v1/campaigns", timeout=2) as r:
            log("STATUS", f"Backend (port 8000): ONLINE (HTTP {r.getcode()})", GREEN)
    except Exception as e:
        log("STATUS", f"Backend (port 8000): OFFLINE ({e})", RED)

    # Check frontend
    for port in [5173, 5174]:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}", timeout=2) as r:
                log("STATUS", f"Frontend (port {port}): ONLINE (HTTP {r.getcode()})", GREEN)
                break
        except Exception:
            pass

def main():
    parser = argparse.ArgumentParser(
        description="Enterprise Multi-Agent Platform CLI Runner",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "command",
        choices=["start", "dev", "backend", "frontend", "test", "build", "status"],
        nargs="?",
        default="start",
        help="Command to run:\n"
             "  start/dev : Run both backend and frontend concurrently (Default)\n"
             "  backend   : Run backend server only (port 8000)\n"
             "  frontend  : Run frontend dev server only (port 5173/5174)\n"
             "  test      : Execute pytest unit and integration tests\n"
             "  build     : Build frontend for production\n"
             "  status    : Check health of running services"
    )

    args = parser.parse_args()

    if args.command in ["start", "dev"]:
        run_dev()
    elif args.command == "backend":
        p = run_backend()
        if p:
            try:
                p.wait()
            except KeyboardInterrupt:
                p.terminate()
    elif args.command == "frontend":
        p = run_frontend()
        if p:
            try:
                p.wait()
            except KeyboardInterrupt:
                p.terminate()
    elif args.command == "test":
        run_tests()
    elif args.command == "build":
        run_build()
    elif args.command == "status":
        run_status()

if __name__ == "__main__":
    main()
