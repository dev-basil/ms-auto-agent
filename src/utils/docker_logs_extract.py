import docker
import sys

def get_logs_since(container_name, since_ts):
    client = docker.from_env()
    try:
        container = client.containers.get(container_name)
        # return logs with timestamps for deduplication
        return container.logs(stream=False, follow=False, since=since_ts, timestamps=True)
    except docker.errors.NotFound:
        print(f"Container '{container_name}' not found.")
        return b""
    except Exception as e:
        print(f"Error: {e}")
        return b""
