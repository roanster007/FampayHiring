#!/usr/bin/env python3

import subprocess
import time


class Colors:
    GREEN = "\033[92m"
    RESET = "\033[0m"


def start_redis():
    print(f"{Colors.GREEN}Starting Redis...{Colors.RESET}")
    redis_process = subprocess.Popen(["redis-server"])
    time.sleep(2)  # Wait for Redis to start
    return redis_process


def start_celery_worker():
    print(f"{Colors.GREEN}Starting Celery worker...{Colors.RESET}")
    celery_worker_process = subprocess.Popen(
        ["celery", "-A", "FampayHiring", "worker", "--loglevel=info"]
    )
    time.sleep(2)  # Wait for Celery worker to initialize
    return celery_worker_process


def start_django_server():
    print(f"{Colors.GREEN}Starting Django server...{Colors.RESET}")
    django_server_process = subprocess.Popen(["python", "manage.py", "runserver"])
    time.sleep(2)  # Wait for Django server to initialize
    return django_server_process


def start_celery_beat():
    print(f"{Colors.GREEN}Starting Celery Beat...{Colors.RESET}")
    celery_beat_process = subprocess.Popen(
        ["celery", "-A", "FampayHiring", "beat", "--loglevel=info"]
    )
    time.sleep(2)  # Wait for Celery Beat to initialize
    return celery_beat_process


def main():
    # Start services
    redis_process = start_redis()
    celery_worker_process = start_celery_worker()
    django_server_process = start_django_server()
    celery_beat_process = start_celery_beat()

    print(f"{Colors.GREEN}All services started successfully!{Colors.RESET}")

    try:
        # Keep the script running to keep services alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"{Colors.GREEN}Stopping services...{Colors.RESET}")
        # Terminate all subprocesses
        redis_process.terminate()
        celery_worker_process.terminate()
        django_server_process.terminate()
        celery_beat_process.terminate()
        print(f"{Colors.GREEN}All services stopped.{Colors.RESET}")


if __name__ == "__main__":
    main()
