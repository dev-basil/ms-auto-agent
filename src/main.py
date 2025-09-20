from utils.logger import logger
from utils.docker_logs_extract import stream_container_logs
from task_executor import run_agent
from task_extractor2 import task_extractor


def main():
    for log in stream_container_logs("book-service"):
        log_string = log.decode("utf-8")
        print(log_string, end="")
        task = task_extractor(log_string)
        if task == None:
            continue
        run_agent(task)


if __name__ == "__main__":
    main()
