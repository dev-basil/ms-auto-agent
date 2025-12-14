from dotenv import load_dotenv
load_dotenv()

from .utils.logger import logger
from .utils.docker_logs_extract import get_logs_since
from .task_executor import run_agent
from .task_extractor2 import task_extractor
import time
from datetime import datetime, timezone

def parse_docker_timestamp(ts_str):
    try:
        ts_clean = ts_str.replace("Z", "+00:00")
        if "." in ts_clean:
            head, tail = ts_clean.split(".", 1)
            f, z = tail.split("+", 1)
            if len(f) > 6:
                f = f[:6]
            ts_clean = f"{head}.{f}+{z}"
        
        dt = datetime.fromisoformat(ts_clean)
        return dt.timestamp()
    except Exception:
        # Fallback: return current time to avoid stuck loop? 
        # Or just 0 if invalid?
        return 0.0


def main():
    # Start checking from now
    last_ts = time.time()
    print(f"Starting log monitor from timestamp {last_ts}...")
    
    while True:
        time.sleep(5)
        # Fetch logs since the last timestamp
        logs_bytes = get_logs_since("book-service", last_ts)
        
        if not logs_bytes:
            continue
            
        logs_decoded = logs_bytes.decode("utf-8").strip()
        if not logs_decoded:
            continue
            
        lines = logs_decoded.splitlines()
        batch_content = []
        max_ts_in_batch = last_ts

        for line in lines:
            parts = line.split(" ", 1)
            if len(parts) < 2:
                continue
            
            ts_str, content = parts[0], parts[1]
            
            # Parse timestamp
            current_log_ts = parse_docker_timestamp(ts_str)
            
            if current_log_ts > last_ts:
                batch_content.append(content)
                if current_log_ts > max_ts_in_batch:
                    max_ts_in_batch = current_log_ts
        
        # update last_ts to the latest one seen
        last_ts = max_ts_in_batch
        
        if not batch_content:
            continue

        log_string = "\n".join(batch_content)
        print(f"--- Batch Logs (New) ---\n{log_string}\n------------------")
            
        task = task_extractor(log_string)
        if task is None:
            continue
        run_agent(task)

if __name__ == "__main__":
    main()
