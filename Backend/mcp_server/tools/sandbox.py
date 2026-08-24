import docker
import tempfile
import os

async def execute_python_code(code: str) -> str:
    """
    Executes python code in an ephemeral docker container.
    Returns the stdout/stderr or error message.
    """
    client = docker.from_env()
    
    # Create a temporary directory to mount into the container
    with tempfile.TemporaryDirectory() as temp_dir:
        # Write the code to a file in the temp dir
        script_path = os.path.join(temp_dir, "script.py")
        with open(script_path, "w") as f:
            f.write(code)
            
        try:
            # Run the container
            # Using python:3.10-slim as a lightweight sandbox
            container = client.containers.run(
                "python:3.10-slim",
                command=["python", "/workspace/script.py"],
                volumes={temp_dir: {'bind': '/workspace', 'mode': 'ro'}},
                working_dir="/workspace",
                mem_limit="512m",  # Limit memory
                cpu_quota=50000,   # Limit CPU (50%)
                network_mode="none", # Air-gapped, no network access
                remove=True,       # Auto-remove container when done
                detach=False,      # Block until finished
                stdout=True,
                stderr=True
            )
            return container.decode('utf-8')
        except docker.errors.ContainerError as e:
            # Container exited with non-zero status
            return f"Error executing code:\n{e.stderr.decode('utf-8') if e.stderr else e.args}"
        except Exception as e:
            return f"Sandbox execution failed: {str(e)}"
