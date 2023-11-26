import os
import time
from directory_components import *
class ProgressBarManager:
    def __init__(self,subprocess_manager,window,default_progress_text =None):
        self.subprocess_manager=subprocess_manager
        self.default_progress_text = default_progress_text  or 'awaiting project'
        self.window=window
    def get_dots(self,text):
        i=0
        dots=''
        for char in text:
            i+=1
            if text[-i] !='.':
                break
            dots +=text[-i]
        if len(dots) != 3:
            text+='.'
        else:
            text = text[:-3]
        return text
    @staticmethod
    def make_percentage(current,total):
        return int((current/total)*100)
    def update_progress(self,project_path,total_count=100):
        self.reset_bar(self.default_progress_text)
        self.project_path=project_path
        self.project_name = os.path.basename(self.project_path)
        self.total_count=total_count
        self.progress_text = f'building {self.project_name}'
        self.start_progress()
        while self.subprocess_manager.get_running_processes():
            time.sleep(1)  # Update every second
            self.update_bar()
        self.end_progress()
        self.reset_bar(self.default_progress_text)
    def update_progress_text(self):
        self.progress_text=self.get_dots(self.progress_text)
        self.window['-PROGRESS_TEXT-'].update(self.progress_text)
    def update_bar(self):
        item_count = count_all_items(self.project_path)[0]
        perc = self.make_percentage(item_count,self.total_count)
        self.window['ProgressBar'].update(perc)
        self.update_progress_text()
    def reset_bar(self,text):
        self.window['ProgressBar'].update(0)
        self.window['-PROGRESS_TEXT-'].update(text)
    def start_progress(self):
        self.reset_bar(self.progress_text)
    def end_progress(self):
        self.window['ProgressBar'].update(100)
        self.window.write_event_value('-THREAD DONE-', '')
