import docker
import sys

def stream_container_logs(container_name):
    client = docker.from_env()
    print(client.containers.list()[0])
    try:
        container = client.containers.get(container_name)
        return container.logs(stream=True, follow=True, tail=0)
    except docker.errors.NotFound:
        print(f"Container '{container_name}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
