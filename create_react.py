import PySimpleGUI as sg
import os
import socket
import subprocess
import webbrowser
import threading
import time
from abstract_gui import AbstractWindowManager
from directory_components import *
from process_management import SubprocessManager
from progress_bar_manager import ProgressBarManager
import re
def get_target_dir(target_dir):
        return target_dir or  os.getcwd()


class ReactManager:
    def __init__(self,window_mgr,parent_dir=None):
        self.port_regex = re.compile(r'http://localhost:(\d+)')
        self.default_port = 3000
        self.selected_project=None
        self.looped=False
        self.project_list=[]
        self.template_name = 'template_project'
        self.parent_dir=get_target_dir(parent_dir)
        self.template_path = self.get_template_path(self.parent_dir)
        self.template_count=100
        self.subprocess_manager = SubprocessManager()
        self.window_mgr = window_mgr
    
    
    def get_layout(self):
        return [[sg.Text("Create React Project")],
                [sg.Text("Project Name:"), sg.InputText(key="ProjectName")],
                [sg.Text("Location:"), sg.InputText(os.getcwd()), sg.FolderBrowse(key="ProjectLocation")],
                [sg.Button("Create", key="CreateProject"), sg.ProgressBar(100, orientation='h', size=(20, 20), key='ProgressBar'),sg.Text('awaiting project',key='-PROGRESS_TEXT-')],
                [sg.Text("_" * 80)],[sg.Text("Run React Project")],
                [sg.Text("Select Project Directory:"), sg.InputText(os.getcwd(),key="RunLocation"), sg.FolderBrowse()],
                [sg.Listbox(values=[], size=(60, 6), key="ProjectList")],
                [sg.Button("Run", key="RunProject")]]

    
    def get_template_path(self,target_dir):
        self.parent_dir=get_target_dir(target_dir)
        self.template_path = os.path.join(self.parent_dir,self.template_name)
        return self.template_path
    
    def get_template_count(self,target_dir=None):
        if not os.path.isdir(self.template_path):
            self.create_react_project(self.template_name,self.template_path)
        return count_all_items(self.template_path)[0]

    
        
    def create_react_project(self,project_name=None,project_path=None,template_count=None):
        # Start the subprocess using the manager
        project_name = project_name or self.project_name
        project_path = project_path or self.project_path
        template_count=template_count or self.template_count
        progress_thread = threading.Thread(target=self.progress_mgr.update_progress, args=(project_path, template_count), daemon=True)
        self.subprocess_manager.start_process(f"npx create-react-app {project_name}")
        progress_thread.start()

    def create_react_app(self,project_name=None, target_dir=None):
        self.target_dir=get_target_dir(target_dir or self.parent_dir)
        self.project_name = project_name or self.project_name
        self.project_path = os.path.join(target_dir,self.project_name)
        revert = os.getcwd()
        os.chdir(self.target_dir)
        self.create_react_process = self.create_react_project(project_name=project_name)
        os.chdir(revert)
        
    def is_port_in_use(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0

    def run_react_app(self, project_dir):
        if project_dir:
            os.chdir(project_dir)
            self.port_num = self.default_port
            # Check if the default port is in use
            while self.is_port_in_use(self.port_num):
                print(f"Port {self.default_port} is in use. Trying a different port...")
                # Set an environment variable to specify a different port
                self.port_num += 1
                os.environ["PORT"] = str(self.port_num)
            # Start the React app
            process = subprocess.Popen(["npm", "start"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, bufsize=1)
        
            # Use a thread to monitor the output
            threading.Thread(target=self._monitor_output, args=(process,), daemon=True).start()
            #webbrowser.open(f'http://localhost:{self.port_num}')
    def _monitor_output(self, process):
        for line in iter(process.stdout.readline, ''):
            print(line, end='')  # Or handle it as you see fit

    def threaded_create_react_app(self,project_name, target_dir):
        self.target_dir=get_target_dir(target_dir or self.parent_dir)
        self.project_name = project_name or self.project_name
        threading.Thread(target=self.create_react_app, args=(project_name, target_dir), daemon=True).start()

    def update_project_listbox(self):
        self.run_location=self.window_mgr.get_from_value("RunLocation")
        self.project_list=[]
        for item in os.listdir(self.run_location):
            item_path = os.path.join(self.run_location,item)
            if os.path.isdir(item_path):
                self.project_list.append(item)
        return self.project_list
    def while_it(self,event,values,window):
        self.event,self.values,self.window=event,values,window
  
        if not self.looped:
            
            self.progress_mgr =ProgressBarManager(subprocess_manager=self.subprocess_manager,window=self.window)

            self.template_count = self.get_template_count()
            self.window["ProjectList"].update(values=self.update_project_listbox())
        self.window_mgr.update_value('ProgressBar',(0,100))  # Reset progress bar
        
        if self.event == "CreateProject":
            self.project_name = self.window_mgr.get_from_value("ProjectName")
            if self.project_name:
                self.project_location = self.values["ProjectLocation"]
                self.threaded_create_react_app(self.project_name,self.project_location)
        if self.event == '-THREAD DONE-':
            sg.popup('React project creation completed!')

        if self.event == "RunLocation":
            run_location = self.window_mgr.get_from_value("RunLocation")
            if run_location:
                self.window["ProjectList"].update(values=self.update_project_listbox())
        if self.event == "RunProject":
            if self.values["ProjectList"]:
                self.selected_project = self.values["ProjectList"][0]
            if self.selected_project:
                self.run_react_app(os.path.join(self.run_location, self.selected_project))
        self.looped = True

    # Use a separate thread to update the progress bar








