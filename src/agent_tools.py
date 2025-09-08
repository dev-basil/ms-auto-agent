from pydantic import BaseModel, Field
from langchain_core.tools import tool

import docker
import time
from docker.errors import NotFound, APIError


class ServiceInput(BaseModel):
    a: str = Field(description="name of the service to restart")


@tool("restart-service-tool", args_schema=ServiceInput, return_direct=True)
def restart_service(a: str) -> bool:
    """Restart the given service (Docker container) by name."""
    try:
        client = docker.from_env()
        try:
            container = client.containers.get(a)
        except NotFound:
            print(f"Container '{a}' not found.")
            return False

        print(f"Restarting service {a} ...")
        container.restart(timeout=10)
        # Wait until the container is running again
        deadline = time.time() + 30
        while time.time() < deadline:
            container.reload()
            if container.status == "running":
                print(f"Service {a} restarted successfully.")
                return True
            time.sleep(0.5)
        print(f"Service {a} restart timed out (status: {container.status}).")
        return False
    except APIError as e:
        print(f"Docker API error while restarting '{a}': {e}")
        return False
    except Exception as e:
        print(f"Error restarting '{a}': {e}")
        return False


tools = [restart_service]