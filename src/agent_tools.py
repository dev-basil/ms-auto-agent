from pydantic import BaseModel, Field
from langchain_core.tools import tool

import docker
import time
from docker.errors import NotFound, APIError


class ServiceInput(BaseModel):
    a: str = Field(description="name of the service to restart")


@tool("restart-service-tool", args_schema=ServiceInput, return_direct=True)
def restart_service(a: str) -> str:
    """Restart the given service (Docker container) by name."""
    try:
        client = docker.from_env()
        try:
            container = client.containers.get(a)
        except NotFound:
            msg = f"Container '{a}' not found."
            print(msg)
            return f"Error: {msg}"

        print(f"Restarting service {a} ...")
        container.restart(timeout=10)
        # Wait until the container is running again
        deadline = time.time() + 30
        while time.time() < deadline:
            container.reload()
            if container.status == "running":
                msg = f"Service {a} restarted successfully."
                print(msg)
                return f"Success: {msg}"
            time.sleep(0.5)
        
        msg = f"Service {a} restart timed out (status: {container.status})."
        print(msg)
        return f"Error: {msg}"
    except APIError as e:
        msg = f"Docker API error while restarting '{a}': {e}"
        print(msg)
        return f"Error: {msg}"
    except Exception as e:
        msg = f"Error restarting '{a}': {e}"
        print(msg)
        return f"Error: {msg}"


tools = [restart_service]