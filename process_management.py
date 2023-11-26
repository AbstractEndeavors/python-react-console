import subprocess
import datetime
import threading
import time

class SubprocessWrapper:
    def __init__(self, command):
        self.command = command
        self.process = subprocess.Popen(command, shell=True)
        self.start_time = datetime.datetime.now()
        self.end_time = None

    def poll(self):
        return self.process.poll()

    def is_running(self):
        return self.poll() is None

    def finish_time(self):
        if self.poll() is not None and self.end_time is None:
            self.end_time = datetime.datetime.now()
        return self.end_time

class SubprocessManager:
    def __init__(self):
        self.subprocesses = []
        self.log = []
        self.lock = threading.Lock()
        self.log_updater = threading.Thread(target=self.update_log, daemon=True)
        self.log_updater.start()

    def start_process(self, command):
        wrapper = SubprocessWrapper(command)
        with self.lock:
            self.subprocesses.append(wrapper)
        return wrapper

    def update_log(self):
        while True:
            with self.lock:
                for process in self.subprocesses:
                    if not process.is_running() and process not in self.log:
                        completion_status = {
                            'command': process.command,
                            'start_time': process.start_time,
                            'end_time': process.finish_time(),
                            'exit_code': process.poll()
                        }
                        self.log.append(completion_status)
            time.sleep(1)  # Update every second

    def get_running_processes(self):
        with self.lock:
            return [proc for proc in self.subprocesses if proc.is_running()]

    def get_log(self):
        with self.lock:
            return self.log


