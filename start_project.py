import subprocess
import threading
import os
import sys

def run_in_conda_env(command):
    conda_env_name = "Albadah"  # Replace with the name of your conda environment
    if os.name == 'nt':
        # For Windows
        activate_cmd = f"conda activate {conda_env_name} && {command}"
        subprocess.run(["cmd", "/c", activate_cmd], shell=True)
    else:
        # For Unix-like systems
        activate_cmd = f"source activate {conda_env_name} && {command}"
        subprocess.run(["/bin/bash", "-c", activate_cmd], shell=True)

def run_django():
    run_in_conda_env('python manage.py runserver')

def run_celery_worker():
    run_in_conda_env('celery -A dcrm worker --pool=solo -l info')

def run_celery_beat():
    run_in_conda_env('celery -A dcrm beat -l info')

def run_redis():
    subprocess.run(['wsl', 'redis-server'])

if __name__ == "__main__":
    threads = []
    
    # Start Django server
    t1 = threading.Thread(target=run_django)
    threads.append(t1)
    
    # Start Celery worker
    t2 = threading.Thread(target=run_celery_worker)
    threads.append(t2)
    
    # Start Celery beat
    t3 = threading.Thread(target=run_celery_beat)
    threads.append(t3)
    
    # Start Redis server
    t4 = threading.Thread(target=run_redis)
    threads.append(t4)
    
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()
