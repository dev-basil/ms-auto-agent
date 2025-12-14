from pydantic import BaseModel, Field
from langchain_core.tools import tool

import docker
import time
from docker.errors import NotFound, APIError


class ServiceInput(BaseModel):
    service_name: str = Field(description="name of the service to restart")


@tool("restart-service-tool", args_schema=ServiceInput, return_direct=True)
def restart_service(service_name: str) -> str:
    """Restart the given service (Docker container) by name."""
    try:
        client = docker.from_env()
        try:
            container = client.containers.get(service_name)
        except NotFound:
            msg = f"Container '{service_name}' not found."
            print(msg)
            return f"Error: {msg}"

        print(f"Restarting service {service_name} ...")
        container.restart(timeout=10)
        # Wait until the container is running again
        deadline = time.time() + 30
        while time.time() < deadline:
            container.reload()
            if container.status == "running":
                msg = f"Service {service_name} restarted successfully."
                print(msg)
                return f"Success: {msg}"
            time.sleep(0.5)
        
        msg = f"Service {service_name} restart timed out (status: {container.status})."
        print(msg)
        return f"Error: {msg}"
    except APIError as e:
        msg = f"Docker API error while restarting '{service_name}': {e}"
        print(msg)
        return f"Error: {msg}"
    except Exception as e:
        msg = f"Error restarting '{service_name}': {e}"
        print(msg)
        return f"Error: {msg}"


tools = [restart_service]