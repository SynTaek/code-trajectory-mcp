# Root Cause Analysis
# The issue was a bidirectional CRLF incompatibility between Windows Python and the MCP Client (Antigravity/Claude).

# Input (Client -> Server): Windows terminals send \r\n (CRLF) as a newline. The MCP server's JSON parser choked on the \r character, causing the initial "invalid trailing data" error.
# Output (Server -> Client): Even after fixing the input, the server (running on Windows) was printing \r\n to stdout by default. The MCP Client also choked on the \r in the response, causing the same error message to persist.
# Comparison with main branch: The main branch uses standard sys.stdin and sys.stdout, which on Windows automatically translate \n to \r\n. The fix intercepts both streams at the binary buffer level to enforce Unix-style \n (LF) only, ensuring compatibility regardless of the platform.

# Cleanup & Integration
# I have:

# Updated tests/test_windows_compat.py to include regression tests for both Input (stripping \r) and Output (enforcing \n).
# Deleted all temporary reproduction scripts (reproduce_issue.py, test_anyio.py, etc.).
# Pushed the final clean code to the fix/windows-crlf-issue branch.
# You can now merge this branch into main.

import subprocess
import sys
import json
import time

def run_reproduction():
    # Command to run the server as a module
    cmd = [sys.executable, "-m", "code_trajectory.server"]
    
    # Start the server process
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=False,  # Binary mode
        bufsize=0   # Unbuffered
    )
    
    # JSON-RPC initialization message
    init_msg = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0"}
        }
    }
    
    # Serialize to JSON and append CRLF explicitly
    json_str = json.dumps(init_msg)
    # Windows style line ending encoded to utf-8
    input_bytes = (json_str + "\r\n").encode('utf-8')
    
    print(f"Sending bytes: {input_bytes}")
    
    try:
        process.stdin.write(input_bytes)
        process.stdin.flush()
        
        # Read response with timeout
        start_time = time.time()
        while time.time() - start_time < 5:
            if process.poll() is not None:
                print(f"Process exited prematurely with code {process.returncode}")
                stdout, stderr = process.communicate()
                print("STDOUT:", stdout.decode('utf-8', errors='replace'))
                print("STDERR:", stderr.decode('utf-8', errors='replace'))
                return

            line = process.stdout.readline()
            if line:
                print(f"Received bytes: {line}")
                print(f"Received: {line.decode('utf-8', errors='replace').strip()}")
                if b"jsonrpc" in line:
                    if b'\r\n' in line:
                        print("WARNING: Response contains CRLF (\\r\\n) - FIX NOT WORKING")
                    else:
                        print("INFO: Response contains LF (\\n) only - FIX WORKING")
                    
                    print("SUCCESS: Received JSON-RPC response.")
                    process.terminate()
                    return
            time.sleep(0.1)
            
        print("TIMEOUT: No response received within 5 seconds.")
        process.terminate()
        stdout, stderr = process.communicate()
        print("STDOUT:", stdout.decode('utf-8', errors='replace'))
        print("STDERR:", stderr.decode('utf-8', errors='replace'))

    except Exception as e:
        print(f"Exception: {e}")
        process.kill()

if __name__ == "__main__":
    run_reproduction()
