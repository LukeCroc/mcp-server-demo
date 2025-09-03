"""
FastMCP quickstart example.

cd to the `examples/snippets/clients` directory and run:
    uv run server fastmcp_quickstart stdio
"""

from mcp.server.fastmcp import FastMCP
import time
import json
import os
import subprocess
import uuid
from typing import Optional, Dict, Any

# Create an MCP server
mcp = FastMCP("Demo")

# # Add a dynamic greeting resource，返回只读，类似get
# @mcp.resource("greeting://{name}")
# def get_greeting(name: str) -> str:
#     """Get a personalized greeting"""
#     return f"Hello, {name}!"

# Add an addition tool，类似Post，可以修改和读取
@mcp.tool() #deco声明下面这个函数是mcp工具，注释和类型是必须写的，会传给llm
def remote_test(project_root: str, command: str) -> Dict[str, Any]:
    """Run a remote test and waiting for completion. The remote commands run in a Windows powershell.
    
    Args:
        project_root: Absolute path to the project root directory， for modifying files and git commands
        command: Command to execute remotely (use PowerShell syntax with semicolons, e.g., 'cd subdir; command', all subdir using relative dir)
        
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
    
    try:# try get results
        with open(job_file_path, 'w') as f:
            json.dump(job_data, f, indent=2)
        
        print(f"Job {job_id} created at {job_file_path}")
        
        # Commit and push to GitHub so the poller can detect the job
        try:
            # Change to project directory
            original_cwd = os.getcwd()
            os.chdir(project_root)
            
            # Git add and commit only the job file
            subprocess.run("git add remote_job.json", shell=True, check=True)
            subprocess.run(f'git commit -m "Add remote test job {job_id}"', shell=True, check=True)
            
            # Git push with better error handling - don't use capture_output
            # to allow interactive authentication if needed
            try:
                result = subprocess.run("git push origin main", shell=True, check=True, capture_output=True, text=True, timeout=30)
                print(f"✅ Job {job_id} committed and pushed to GitHub")
            except subprocess.CalledProcessError as e:
                print(f"⚠️  git push failed: {e}")
                if e.stderr:
                    print(f"Error details: {e.stderr}")
                print("Continuing with polling despite git push failure")
            except subprocess.TimeoutExpired:
                print("⚠️  git push timed out after 30 seconds")
                print("Continuing with polling despite timeout")
            
            # Restore original working directory
            os.chdir(original_cwd)
            
        except subprocess.CalledProcessError as e:
            print(f"Git operations failed: {e}")
            # Continue with polling even if git operations fail
        
        # Wait for job completion (polling)
        max_attempts = 60  # 5 minutes at 5 second intervals
        for attempt in range(max_attempts):
            time.sleep(5)  # Wait 5 seconds between checks
            
            try:
                with open(job_file_path, 'r') as f:
                    current_data = json.load(f)
                
                if current_data.get("status") == "completed":
                    return {
                        "job_id": job_id,
                        "status": "completed",
                        "result": current_data["result"]
                    }
                    
            except (FileNotFoundError, json.JSONDecodeError):
                continue
        
        return {
            "job_id": job_id,
            "status": "timeout",
            "error": "Job timed out after 5 minutes"
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
