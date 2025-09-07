"""
Simple MCP server for testing - modifies job file and does git add
"""

from mcp.server.fastmcp import FastMCP
import json
import os
import uuid
from typing import Dict, Any

# Create an MCP server
mcp = FastMCP("Demo")

@mcp.tool()
def remote_test(project_root: str, command: str) -> Dict[str, Any]:
    """Run a remote test - modifies job file and does git add
    
    Args:
        project_root: Absolute path to the project root directory
        command: Command to execute remotely
        
    Returns:
        Dictionary containing the test results
    """
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    # Create job data structure
    job_data = {
        "status": "pending",
        "job": {
            "id": job_id,
            "command": command
        },
        "result": {
            "stdout": None,
            "stderr": None,
            "return_code": None
        }
    }
    
    # Write to remote_job.json in the specified project root directory
    job_file_path = os.path.join(project_root, "remote_job.json")
    
    try:
        with open(job_file_path, 'w') as f:
            json.dump(job_data, f, indent=2)
        
        # Write to debug log file instead of print - clear log file first
        debug_log_path = os.path.join(project_root, "mcp_debug.log")
        with open(debug_log_path, 'w') as log_file:  # 'w' mode to clear file
            log_file.write(f"Job {job_id} created at {job_file_path}\n")
        
        # Add timestamp for debugging
        import time
        start_time = time.time()
        with open(debug_log_path, 'a') as log_file:
            log_file.write(f"DEBUG: Starting git add at {time.time()}\n")
        
        # Run git add synchronously (single thread as requested)
        try:
            # Change to project directory before running git add
            original_cwd = os.getcwd()
            os.chdir(project_root)
            
            # Use subprocess for better control and error handling
            import subprocess
            with open(debug_log_path, 'a') as log_file:
                log_file.write(f"DEBUG: Before subprocess at {time.time()}\n")
            
            result = subprocess.run(["git", "add", "remote_job.json"],
                                  capture_output=True, text=True, timeout=30)
            return_code = result.returncode
            
            # Log detailed git output for debugging
            with open(debug_log_path, 'a') as log_file:
                log_file.write(f"DEBUG: After subprocess at {time.time()}\n")
                if result.stdout:
                    log_file.write(f"Git stdout: {result.stdout}\n")
                if result.stderr:
                    log_file.write(f"Git stderr: {result.stderr}\n")
            
            os.chdir(original_cwd)  # Restore original directory
            
            git_success = return_code == 0
            status_symbol = "SUCCESS" if git_success else "WARNING"
            
            with open(debug_log_path, 'a') as log_file:
                log_file.write(f"{status_symbol} Git add completed (return code: {return_code}) at {time.time()}\n")
                
        except subprocess.TimeoutExpired:
            with open(debug_log_path, 'a') as log_file:
                log_file.write("ERROR: Git add timed out after 30 seconds\n")
            return_code = -1
        except Exception as e:
            with open(debug_log_path, 'a') as log_file:
                log_file.write(f"ERROR: Git add error: {e}\n")
            return_code = -1
        
        # Add final timestamp
        with open(debug_log_path, 'a') as log_file:
            log_file.write(f"DEBUG: Function completed at {time.time()}, total time: {time.time() - start_time:.2f}s\n")
        
        # Return response after git add completes
        return {
            "job_id": job_id,
            "status": "success",
            "message": f"Job {job_id} created, git add completed",
            "file_path": job_file_path,
            "debug_log": debug_log_path,
            "git_add": {
                "status": "completed",
                "message": "Git add operation finished"
            }
        }
        
    except Exception as e:
        return {
            "job_id": job_id,
            "status": "error",
            "error": f"Failed to create job file: {str(e)}"
        }

# main func
def main():
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
