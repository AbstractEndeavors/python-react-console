"""
abstract_browser
=================

The `abstract_browser` module is part of the `abstract_gui` module of the `abstract_essentials` package. 
It provides an abstracted mechanism for creating and managing a file/folder browser using PySimpleGUI.

Classes and Functions:
----------------------
- get_scan_browser_layout: Returns the layout for the file/folder scanner window.
- browse_update: Updates values in the browse window.
- return_directory: Returns the current directory or parent directory if a file is selected.
- scan_window: Handles events for the file/folder scanner window.
- forward_dir: Navigate to the given directory.
- scan_directory: Returns the files or folders present in the given directory based on the selected mode.
- get_browse_scan: Initializes the scanner with default settings and runs it.

"""
import os
import os
import fnmatch
from abstract_gui import sg,get_event_key_js,make_component,text_to_key,expandable,AbstractWindowManager
from abstract_utilities import eatAll,make_list
from create_react import ReactManager
from ExcludedDirectories import ExcludedDirectories
from ApprovedDirectories import ApprovedDirectories


def is_excluded(path, exclusions):
    """
    Check if a given path matches any of the exclusion criteria.

    Args:
    ----
    path (str): The path to check.
    exclusions (list): List of exclusion patterns.

    Returns:
    -------
    bool: True if the path matches any exclusion criteria, False otherwise.
    """
    for exclusion in exclusions:
        if fnmatch.fnmatch(path, exclusion):
            return True
    return False




        

from abstract_gui import sg,get_event_key_js,make_component,text_to_key,expandable
from abstract_utilities import eatAll,make_list
def convert_to_relative_paths(base_directory, paths):
    """
    Convert a list of absolute paths to relative paths with respect to a base directory.

    Args:
    ----
    base_directory (str): The base directory to which paths will be made relative.
    paths (list): List of absolute paths.

    Returns:
    -------
    list: List of relative paths.
    """
    relative_paths = []
    for path in paths:
        relative_path = os.path.relpath(path, base_directory)
        relative_paths.append(relative_path)

    return relative_paths
def find_closest_approved_directory(current_directory, approved_directories):
    """
    Find the closest approved directory by checking parent directories of the current directory.

    Args:
    ----
    current_directory (str): The current directory path.
    approved_directories (list): List of approved directory paths.

    Returns:
    -------
    str: Closest approved directory or None if none found.
    """
    directory = current_directory

    while directory:
        if directory in approved_directories:
            return directory  # Closest approved directory found

        parent_directory = os.path.dirname(directory)
        if parent_directory == directory:  # Reached the root directory without finding an approved directory
            break

        directory = parent_directory

    return None  # No approved directory found

def get_excluded_directories(folder,excluded_folder_paths=[]):
    directories = []
    for root, dirs, files in os.walk(folder):
        for directory in dirs:
            
            if not is_string_in_list(excluded_folder_paths,directory):
                if directory not in directories:
                        directories.append(directory)
    return directories
def is_string_in_list(list_object,string):
    for obj in list_object:
        
        if obj and isinstance(obj,list):
            obj = obj[0]
        if obj and obj in string:
            return True
    return False
def get_specific_folder_paths(directory,folders=[]):
    directories=[]
    for root, dirs, files in os.walk(directory):
        if not is_string_in_list(folders,root):
            for directory in dirs:
                if directory in folders:
                    directory_path = os.path.join(root,directory)
                    if directory_path not in directories:
                        directories.append(directory_path)
    return directories
def get_all_directory_list(folder,excluded_folders=[]):
    directories = []
    for root, dirs, files in os.walk(folder):
        for directory in dirs:
            if not is_string_in_list(excluded_folders,os.path.join(root,directory)):
                directories.append(directory)
    return directories
def get_directory_list(folder,excluded_folders=[]):
    folders=[]
    for item in os.listdir(folder):
        item_path=os.path.join(folder,item)
        if os.path.isdir(item_path):
            if not is_string_in_list(excluded_folders,item_path):
                folders.append(item)
    return folders
class AbstractBrowser:
    """
    This class aims to provide a unified way of browsing through different sources.
    It could be used as the base class for browsing through different APIs, files, databases, etc.
    The actual implementation of how to retrieve or navigate through the data should be done in the derived classes.
    """
    def __init__(self, window_mgr=None,window_name=None,window=None):
        self.window_mgr = window_mgr
        if window_mgr:
            if hasattr(window_mgr, 'window'):
                self.window = window_mgr.window
        elif window_name:
            if hasattr(window_mgr, 'get_window'):
                self.window=window_mgr.get_window(window_name=window_name)

        self.event = None
        self.values = None
        self.last_folder_click = None
        self.last_event = None
        self.scan_modes=[]
        self.first_loop=True
        
        self.history = [os.getcwd()]
        self.project_keys = ["-PARENT_FOLDER_LIST-","-PARENT_FOLDER_LIST-"]
        self.folders_modes = ['-FOLDERS_SCAN_MODE_LOCAL-','-FOLDERS_SCAN_MODE_RECURSIVE-']
        self.files_mode=['-FILES_SCAN_MODE_LOCAL-','-FILES_SCAN_MODE_RECURSIVE-']
        self.initial_keys = [text_to_key(text='initial dir path'),text_to_key(text='initial dir bool'),text_to_key(text='initial directory browser')]
        self.exlusion_keys = ["-EXCLUDE_DIRECTORIES_LIST-","-ADD_EXCLUSION-","-EXCLUDED_DIRECTORIES_LIST-","-REMOVE_EXCLUSION-","-EXCLUDE_SEARCH_DIRECTORIES-"]
        self.inclusion_keys = ["-INCLUDE_DIRECTORIES_LIST-","-ADD_INCLUSION-","-INCLUDED_DIRECTORIES_LIST-","-REMOVE_INCLUSION-","-INCLUDE_SEARCH_DIRECTORIES-"]
        self.key_list = ['-BROWSER_FOLDERS_LIST-','-BROWSER_FILES_LIST-','-CLEAR_LIST-','-ADD_TO_LIST-',"-FILES_BROWSER-","-DIR-","-DIRECTORY_BROWSER-","-FILES_LIST-","-SELECT_HIGHLIGHTED-","-SCAN-", "-SELECT_HIGHLIGHTED-", "-MODE-", "-BROWSE_BACKWARDS-", "-BROWSE_FORWARDS-"]+self.files_mode+self.folders_modes+self.initial_keys+self.exlusion_keys+self.project_keys+self.inclusion_keys+self.exlusion_keys
        self.window_mgr =AbstractWindowManager()
        self.react_mgr = ReactManager(window_mgr = self.window_mgr)
        self.window_name=self.window_mgr.add_window(title="React Project Manager",layout=self.get_scan_browser_layout(react=self.react_mgr.get_layout()))
        
        self.window_mgr.while_window(window_name="React Project Manager",event_handlers=[self.handle_event,self.react_mgr.while_it])

    def reverse_bool(self,key=None,section=None):
        key = key or self.event_key_js['found']
        pieces = key[1:-1].split('_')
        section = section or self.event_key_js['section']
            
            
        list_type = 'FILES' if 'FILES' in pieces else 'FOLDERS'
        scan_type = 'RECURSIVE' if 'RECURSIVE' in pieces else 'LOCAL'
        opposite_scan_type = 'LOCAL' if scan_type == 'RECURSIVE' else 'RECURSIVE'

        # Update scan mode
        self.set_scan_mode(section, list_type, scan_type)

        # Update opposite checkbox
        selected_key = text_to_key(text=f'{list_type} scan mode {scan_type}', section=section)
        opposite_key = text_to_key(text=f'{list_type} scan mode {opposite_scan_type}', section=section)
        bool_type = self.values[selected_key]
        self.window[opposite_key].update({"True":False,"False":True}[str(bool_type)])
        self.scan_it(self.return_directory())
    def get_approved_paths(self,directory, exclusions=[]):
        exclusions = ['*.tmp', 'node_modules', '*.log'] + exclusions
        return self.map_files_and_directories(directory or os.getcwd(), exclusions)
    def list_dir(self,directory):
        directory = directory or self.values[self.event_key_js["-DIR-"]] or self.project_folder_path or self.values[self.event_key_js["-PARENT_FOLDER_LIST-"]]
        self.exluded_directories = get_specific_folder_paths(directory,folders=make_list(self.window[self.event_key_js["-EXCLUDED_DIRECTORIES_LIST-"]].Values))
        approved_directories_mgr = ApprovedDirectories(self.event_key_js, directory)  # Get the list of approved directories
        self.approved_directories = approved_directories_mgr.find_closest_approved_directory(directory,self.exluded_directories)
        directory = directory or self.values[self.event_key_js["-DIR-"]] or self.project_folder_path or self.values[self.event_key_js["-PARENT_FOLDER_LIST-"]]  # Get the current directory
        
        if not os.path.isdir(directory):
            while not os.path.isdir(directory) and directory not in self.approved_directories:
                directory =os.path.dirname(directory)
                print(directory) 
                if directory == os.getcwd():
                    return directory
                
        if directory:
            if os.path.exists(directory):
                if os.path.isdir(directory):
                    return directory
        return directory
    def map_files_and_directories(self,directory, exclusions):
        """
        Map files and directories in a given directory, excluding those that match the exclusion criteria.

        Args:
        ----
        directory (str): The directory to scan.
        exclusions (list): List of exclusion patterns.

        Returns:
        -------
        list: List of non-excluded file and directory paths.
        """
        mapped_items = []
        
        for item in self.list_dir(directory):
            full_path = os.path.join(directory, item)
            if not is_excluded(full_path, exclusions):
                mapped_items.append(full_path)
        return mapped_items
    def list_react_components(self,folder):
        """ Lists .js and .tsx files in the folder """
        components=[]
        excluded_folders = get_specific_folder_paths(folder,folders=['node_modules'])
        if os.path.exists(folder) and os.path.isdir(folder):
            components = get_files_list(folder,excluded_folder_paths=excluded_folders)
        else:
            print(f"Invalid folder path: {folder}")
        return components
    def handle_event(self,event,values,window):
          
        self.event,self.values,self.window=event,values,window
   
        self.event_key_js={"found":event,"section":'',"event":event}
        
        try:
            self.event_key_js = get_event_key_js(self.event,key_list=self.key_list)
        except:
            self.event_key_js={"found":event,"section":'',"event":event}
        if self.event_key_js['found']:
            return self.while_static(event_key_js=self.event_key_js, values=self.values,window=self.window)
        else:
            return self.event, self.values
    def scan_it(self,directory):
        directory = directory or self.values[self.event_key_js['-DIR-']] or os.getcwd()
        if os.path.isdir(directory):
            self.scan_results = self.scan_directory(directory, 'FOLDERS')
            self.browse_update(key=self.event_key_js['-BROWSER_FOLDERS_LIST-'],args={"values":self.scan_results})
            self.scan_results = self.scan_directory(directory, 'FILES')
            self.browse_update(key=self.event_key_js['-BROWSER_FILES_LIST-'],args={"values":self.scan_results})
   
    def get_scan_browser_layout(self,react,section=None, extra_buttons=[]):
        """
        Generate the layout for the file/folder scanning window.

        Returns:
            --------
            list:
                A list of list of PySimpleGUI elements defining the window layout.
            """
        def get_clusions(clusion_type='ex'):
            return sg.Frame(f"{clusion_type}cluisions",[[sg.Input(key=text_to_key(text=f"EXCLUDE_search directories",section=section),enable_events=True,size=(20,5))],
            [sg.Combo(values=excluded_dir_list,key=text_to_key(text=f"EXCLUDE_DIRECTORIES_LIST-",section=section),enable_events=True,size=(20,5)),
             sg.Button(button_text=f"ADD EXCLUSION",key=text_to_key(text=f"ADD EXCLUSION",section=section),enable_events=True)],
            [sg.Listbox([],key=text_to_key(text=f"-EXCLUDED_DIRECTORIES_LIST-",section=section),size=(20,5)),
             sg.Button(button_text=f"REMOVE EXCLUSION",key=text_to_key(text=f"-REMOVE_EXCLUSION-",section=section),enable_events=True)]])
        def get_check_boxes(list_type):
            return [
                sg.Checkbox(
                    'recursive',
                    default = True,
                    key=text_to_key(text=f'{list_type} scan mode recursive', section=section)
                    ,enable_events=True
                ),
                sg.Checkbox(
                    'local',
                    default = False, 
                    key=text_to_key(text=f'{list_type} scan mode local', section=section)
                    ,enable_events=True
                )
            ]
        def get_main_folder_displays(folder_type):
            return [[sg.Frame(f"Select {folder_type[0].upper()}{folder_type[1:].lower()} Folder:",
                              layout=[[sg.Input(os.getcwd(),key=text_to_key(f"-{folder_type.upper()}_FOLDER-",section=section)), sg.FolderBrowse(key=text_to_key(f'-{folder_type}.upper()_BROWSER-',section=section),enable_events=True)],
                                      [make_component("Listbox",values=[], enable_events=True, **expandable(size=(40, 10)), key=text_to_key(f"-{folder_type.upper()}_FOLDER_LIST-",section=section))]])]]
        def get_file_displays(self,folder_type):
            return [[sg.Frame(f"-{text_type[0].upper()}{text_type[1:].lower()}_file:",layout=[[sg.Input(key=text_to_key(f"-{text_type.upper()}_FILE_PATH-",section=section)), sg.FileBrowse(key=text_to_key(f"-REVISION_FILE_BROWSER-",section=section),enable_events=True)][sg.Multiline(key=text_to_key(f"-{text_type.upper()}_FILE_TEXT-",section=section))]])]],
                                                                                                          

        def get_layout():
            layout = []
            layout.append(sg.Column(get_main_folder_displays('parent')))
            layout.append(sg.Column(react))
            return layout
        browser_buttons_layout = [
            sg.FolderBrowse('Folders', key=text_to_key(text='directory browser',section=section)),
            sg.FileBrowse('Files', key=text_to_key(text='files browser',section=section))
        ]
        listboxes_layout=[]
        listboxes_layout.append(sg.Column([[sg.Frame("Directories",[get_check_boxes("folders"),[sg.Listbox(values=[], size=(50, 20), key=text_to_key(text='browser folders list',section=section), enable_events=True)]])]]))
        listboxes_layout.append(sg.Column([[sg.Frame("Files",[get_check_boxes("files"),[sg.Listbox(values=[], size=(50,20), key=text_to_key(text='browser files list',section=section), enable_events=True)]])]]))
        
        control_buttons_layout = [
            sg.Button('Scan', key=text_to_key(text='scan',section=section)),
            sg.Button('<-', key=text_to_key(text='browse backwards',section=section)),
            sg.Button('All Scan Mode', key=text_to_key(text='mode',section=section)),
            sg.Button('->', key=text_to_key(text='browse forwards',section=section)),
            sg.Button('Add', key=text_to_key(text='add_to_list',section=section)),
            sg.Button('Clear', key=text_to_key(text='clear list',section=section))
        ] + extra_buttons
        excluded_dir_list = get_excluded_directories(folder=os.getcwd())
        return [get_layout(),[sg.Column([[get_clusions(clusion_type='ex')]]),sg.Column([[get_clusions(clusion_type='in')]])],
                [sg.Text('Initial Directory:'), sg.InputText(os.getcwd(),key=text_to_key(text='initial dir path',section=section),disabled=False),sg.FolderBrowse('Initial Folder', key=text_to_key(text='initial directory browser',section=section)),sg.Checkbox(
                    'initial',
                    default = False,
                    key=text_to_key(text=f'initial dir bool', section=section)
                    ,enable_events=True
                )],
            [sg.Text('Directory to scan:'), sg.InputText(os.getcwd(),key=text_to_key(text='dir',section=section),size=(70,1)), sg.Column([browser_buttons_layout])],
            [listboxes_layout],
            control_buttons_layout
        ]
         
    def set_scan_mode(self, section, list_type, scan_mode):
        for mode in self.scan_modes:
            if mode['section'] == section:
                mode[list_type] = scan_mode
                return
        # If the section is not found, add a new entry
        self.scan_modes.append({"section": section, list_type: scan_mode})

    def get_scan_mode(self, section, list_type):
        for mode in self.scan_modes:
            if mode['section'] == section:
                return mode.get(list_type, None)
        return None
    def forward_navigate(self,forward_value = None):
        directory=None
        try:
            # Navigate down into the selected directory or move to the next history path
            if forward_value or self.values[self.event_key_js['-BROWSER_FOLDERS_LIST-']]:  # If there's a selected folder in the listbox
                directory = os.path.join(self.return_directory(), forward_value or self.values[self.event_key_js['-BROWSER_FOLDERS_LIST-']][0])
                directory = self.clusion_verify(directory)
                if os.path.isdir(directory) and directory in cluded_list:
                    self.forward_dir(directory)
                    self.scan_it(directory)
            elif self.history:  # If there's a directory in the history stack
                directory = self.history.pop()
                self.update_dir_and_lists(directory)
        except:
            print(f'could not scan directory {directory}')
    def update_parent(self):
        self.parent_folder_path = os.getcwd()
        self.parent_folder_directories = get_directory_list(self.parent_folder_path)
        self.window[self.event_key_js["-PARENT_FOLDER_LIST-"]].update(values=self.parent_folder_directories)
        
    def update_project(self):
        self.project_folder = self.values[self.event_key_js["-PARENT_FOLDER_LIST-"]][0] if self.values[self.event_key_js["-PARENT_FOLDER_LIST-"]] else ''
        self.project_folder_path = os.path.join(self.parent_folder_path, self.project_folder) if self.project_folder else ''
        if self.project_folder_path:
            excluded_folders = get_specific_folder_paths(self.project_folder_path,folders=['node_modules'])
            self.window["ProjectList"].update(values=get_directory_list(self.project_folder_path,excluded_folders=excluded_folders))
            self.window["RunLocation"].update(self.project_folder_path)
    def update_dir(self):
        self.dir_folder = self.values["ProjectList"][0] if self.values["ProjectList"] else ''
        self.dir_folder_path = os.path.join(self.project_folder_path, self.dir_folder) if self.dir_folder else ''
        if self.dir_folder_path:
            self.window[self.event_key_js['-DIR-']].update(self.dir_folder_path)
            self.scan_it(self.dir_folder_path)
    def while_static(self,event_key_js,values,window):
        self.event_key_js,self.values,self.window=event_key_js,values,window
        

  
        if self.first_loop:
            self.update_parent()
            self.update_project()
            self.update_dir()
        self.react_mgr.while_it(self.event,self.values,self.window)
        if self.event_key_js['found'] == "-PARENT_FOLDER_LIST-":
            self.update_project()
        elif self.event == "ProjectList":
            self.update_dir()
        if self.event_key_js['found'] == "-FILES_BROWSER-":
            self.browse_update(key=self.event_key_js['-DIR-'],args={"value":self.values[self.event_key_js["-FILES_BROWSER-"]]})
        elif self.event_key_js['found'] == "-DIRECTORY_BROWSER-":
            self.browse_update(key=self.event_key_js['-DIR-'],args={"value":self.values[self.event_key_js["-DIRECTORY_BROWSER-"]]})
        elif self.event_key_js['found'] == '-SCAN-':
            self.scan_it(self.return_directory())
        elif self.event_key_js['found'] == "-SELECT_HIGHLIGHTED-":
            if len(self.values[self.event_key_js['-BROWSER_FOLDERS_LIST-']])>0:
                self.browse_update(key=self.event_key_js['-DIR-'],args={"value":os.path.join(self.return_directory(), self.values[self.event_key_js['-BROWSER_FOLDER_LIST-']][0])})
        elif event_key_js["found"] in ["-ADD_EXCLUSION-","-REMOVE_EXCLUSION-","-EXCLUDE_SEARCH_DIRECTORIES-","-ADD_INCLUSION-","-REMOVE_INCLUSION-","-INCLUDE_SEARCH_DIRECTORIES-"]:
            for piece in event_key_js['found'][1:-1].split('_'):
                if piece[2:len("EXCLU")] == "CLU":
                    clusion_type=piece[:2]
                    break
            excluded_dirs_mgr = ExcludedDirectories(event_key_js, values, window)
            excluded_dirs_mgr.check()
            # Proceed with scanning
            self.approved_paths_mgr =ApprovedDirectories(self.event_key_js,self.window[self.event_key_js['-DIR-']] or os.getcwd())
            self.scan_it(self.approved_paths_mgr.verify(self.return_directory()))
        elif event_key_js['found'] in self.files_mode+self.folders_modes:
            # Extracting list type and scan type from the event key
            self.reverse_bool()
        elif self.event_key_js['found'] == text_to_key(text='initial dir bool'):
            initial_bool_key = self.event_key_js[text_to_key(text='initial dir bool')]
            
            initial_path_key = self.event_key_js[text_to_key(text='initial dir path')]
            if self.values[initial_bool_key]:
                self.window[initial_path_key].update(disabled=False)
            else:
                self.window[initial_path_key].update(disabled=True)
            
        elif self.event_key_js['found'] == '-BROWSER_FOLDERS_LIST-':
            not_last=False
            folder_list = self.values[self.event_key_js['-BROWSER_FOLDERS_LIST-']]
            print(f"length of folder list={len(folder_list)}")
            self.this_click=folder_list
            if folder_list:
                self.this_click = folder_list[0]
                new_path = os.path.join(self.values[self.event_key_js['-DIR-']],folder_list[0])
                if os.path.exists(new_path):
                    path = new_path
                else:
                    path = self.values[self.event_key_js['-DIR-']]
                if self.last_folder_click != folder_list[0]:
                    self.window[self.event_key_js['-BROWSER_FILES_LIST-']].update(values=self.scan_directory(path, 'FILES'))
                else:
                    self.update_dir_and_lists(path)
                    self.last_folder_click = folder_list[0]
                    self.last_event=self.event_key_js['event']
                    return 
            
            self.last_folder_click = self.this_click
            self.last_event=self.event_key_js['event']
            
        elif self.event_key_js['found'] == '-ADD_TO_LIST-':
            folder_list = self.values[self.event_key_js['-BROWSER_FOLDERS_LIST-']]
            files_list = self.values[self.event_key_js['-BROWSER_FILES_LIST-']] or []
            if folder_list:
                files_list.append(folder_list[0])
            path_dir = self.values[self.event_key_js['-DIR-']].split(';')
            for path in path_dir:
                if path not in files_list:
                    files_list.append(path)
            self.window[self.event_key_js['-BROWSER_FILES_LIST-']].update(files_list)
        elif self.event_key_js['found'] == '-CLEAR_LIST-':
            self.window[self.event_key_js['-BROWSER_FILES_LIST-']].update([])
        elif self.event_key_js['found'] == "-BROWSE_BACKWARDS-":
            # Navigate up to the parent directory
            initial_bool_key = self.event_key_js[text_to_key(text='initial dir bool')]
            initial_path= self.values[self.event_key_js[text_to_key(text='initial dir path')]]
            if self.values[initial_bool_key]:
                if initial_path not in self.return_directory() or initial_path == self.return_directory():
                    return 
            if self.return_directory() not in self.history:
                self.history.append(self.return_directory())
            directory = os.path.dirname(self.return_directory())  # This will give the parent directory
            self.update_dir_and_lists(directory)
            self.scan_it(directory)
        elif self.event_key_js['found'] in ["-BROWSE_FORWARDS-"]:
            self.forward_navigate()
        self.last_event = self.event_key_js['event']
        self.first_loop=False
        return self.event,self.values
    def return_directory(self):
        """
        Return the current directory or parent directory if a file path is provided.

        Returns:
        --------
        str:
            Directory path.
        """
        directory = self.values[self.event_key_js['-DIR-']]
        if os.path.isfile(self.values[self.event_key_js['-DIR-']]):
            directory = os.path.dirname(self.values[self.event_key_js['-DIR-']])
        if directory == '':
            directory = os.getcwd()
        return directory
    def update_dir_and_lists(self,directory):
        
        folders = self.scan_directory(directory, "FOLDERS")
        self.browse_update(key=self.event_key_js['-DIR-'],args={"value":directory})
        self.browse_update(key=self.event_key_js['-BROWSER_FOLDERS_LIST-'],args={"values":folders})
        fold_list = self.values[self.event_key_js['-BROWSER_FOLDERS_LIST-']]
        
        if fold_list:
            fold_path = os.path.join(directory,fold_list[0])
            if os.path.exists(fold_path):
                self.browse_update(key=self.event_key_js['-BROWSER_FILES_LIST-'],args={"values":self.scan_directory(fold_path, "FILES")})
                return
        self.browse_update(key=self.event_key_js['-BROWSER_FILES_LIST-'],args={"values":self.scan_directory(directory, "FILES")})
    def browse_update(self,key: str = None, args: dict = {}):
        """
        Update specific elements in the browse window.

        Parameters:
        -----------
        window : PySimpleGUI.Window
            The window to be updated. Default is the global `browse_window`.
        key : str, optional
            The key of the window element to update.
        args : dict, optional
            Arguments to be passed for the update operation.
        """
        self.window[key](**args)
    def read_window(self):
        self.event,self.values=self.window.read()
        return self.event,self.values
    def get_values(self):
        if self.values==None:
            self.read_window()
        return self.vaues
    def get_event(self):
        if self.values==None:
            self.read_window()
        return self.event
    def scan_window(self):
        """
        Event handler function for the file/folder scanning window.

        Parameters:
        -----------
        event : str
            Name of the event triggered in the window.
        """
        while True:
            self.read_window()
            if self.event == None:
                break
            while_static(event)
        self.window.close()

    def forward_dir(self,directory):
        """
        Navigate and update the scanner to display contents of the given directory.

        Parameters:
        -----------
        directory : str
            Path to the directory to navigate to.
        """
        if os.path.isdir(directory):
            self.update_dir_and_lists(directory)
    def scan_directory(self, directory_path, list_type):
        """
        List files or folders in the given directory based on the provided type and mode.

        Parameters:
        -----------
        directory_path : str
            Path to the directory to scan.
        list_type : str
            Either 'file' or 'folder' to specify what to list.
        scan_mode : str
            Either 'RECURSIVE' or 'LOCAL' to specify the scan depth.

        Returns:
        --------
        list:
            List of file/folder paths present in the directory.
        """
        items = []
        scan_mode = self.get_scan_mode(self.event_key_js['section'],list_type)
        directory_path = self.list_dir(directory_path)
        if scan_mode == 'RECURSIVE':
            for root, dirs, files in os.walk(directory_path):
                
                if list_type.lower() == 'files':
                    items.extend([os.path.join(root, f) for f in files if not is_string_in_list(self.exluded_directories,os.path.join(root, f))])
                elif list_type.lower() == 'folders':
                    items.extend([os.path.join(root, d) for d in dirs if not is_string_in_list(self.exluded_directories,os.path.join(root, d))])
            
        elif scan_mode == 'LOCAL':
            if list_type.lower() == 'files':
                items = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f)) and not is_string_in_list(self.exluded_directories,os.path.join(directory_path, f))]
            elif list_type.lower() == 'folders':
                items = [d for d in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, d)) and not is_string_in_list(self.exluded_directories,os.path.join(directory_path, d))]
        return [eatAll(os.path.relpath(item, directory_path),['.','/']) for item in items]
          

AbstractBrowser()
