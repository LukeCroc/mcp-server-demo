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
            
            # Run git push synchronously for debugging
            try:
                result = subprocess.run("git push origin main", shell=True, check=True, capture_output=True, text=True, timeout=30)
                print(f"✅ Job {job_id} committed and pushed to GitHub")
                print(f"git push stdout: {result.stdout}")
                print(f"git push stderr: {result.stderr}")
            except subprocess.CalledProcessError as e:
                print(f"⚠️  git push failed: {e}")
                print(f"git push stdout: {e.stdout}")
                print(f"git push stderr: {e.stderr}")
                # Re-raise to see detailed error
                raise
            except subprocess.TimeoutExpired:
                print("⚠️  git push timed out after 30 seconds")
                raise
            except Exception as e:
                print(f"⚠️  git push unexpected error: {e}")
                raise
            
            # Restore original working directory
            os.chdir(original_cwd)
            
        except subprocess.CalledProcessError as e:
            print(f"Git operations failed: {e}")
            return {
                "job_id": job_id,
                "status": "git_error",
                "error": f"Git operation failed: {str(e)}",
                "stdout": e.stdout,
                "stderr": e.stderr
            }
        except Exception as e:
            print(f"Unexpected error: {e}")
            return {
                "job_id": job_id,
                "status": "error",
                "error": f"Unexpected error: {str(e)}"
            }
        
        # Return success
        return {
            "job_id": job_id,
            "status": "success",
            "message": f"Job {job_id} created, committed, and pushed successfully"
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
