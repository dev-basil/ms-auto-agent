from utils.logger import logger
from utils.docker_logs_extract import stream_container_logs
import os
from src.task_executor import run_agent

def main():
    for log in stream_container_logs("book-service"):
        print(log.decode('utf-8'), end='')
        run_agent(log.decode('utf-8'))
if __name__ == '__main__':
    main()