import os
def get_excluded_directories(folder,excluded_folder_paths=[]):
    directories = []
    for root, dirs, files in os.walk(folder):
        for directory in dirs:
            
            if not is_string_in_list(excluded_folder_paths,directory):
                if directory not in directories:
                        directories.append(directory)
    return directories
class ExcludedDirectories:
    def __init__(self, event_key_js, values, window):
        self.event_key_js = event_key_js
        self.values = values
        self.window = window
        self.excluded_dir_list = get_excluded_directories(folder=os.getcwd())
    def check(self):
        directories_list = make_list(self.values[self.event_key_js[f"-EXCLUDE_DIRECTORIES_LIST-"]])

        if self.event_key_js["found"] == f"-EXCLUDE_SEARCH_DIRECTORIES-":
            search_text = self.values[self.event_key_js[f"-EXCLUDE_SEARCH_DIRECTORIES-"]]
            new_directories_list = [key for key, values in directories_list if key.startswith(search_text)]

            if new_directories_list:
                value = new_directories_list[0]
                self.window[self.event_key_js[f"-EXCLUDE_DIRECTORIES_LIST-"]].update(values=new_directories_list, value=value)
                self.scan_it(self.return_directory())
        elif self.event_key_js["found"] == f"-REMOVE_EXCLUSION-":
            selected_clusion = self.values[self.event_key_js[f"-EXCLUDED_DIRECTORIES_LIST-"]]
            if selected_clusion:
                selected_clusion = selected_clusion[0]
                self.window[self.event_key_js[f"-EXCLUDED_DIRECTORIES_LIST-"]].update(values=[excluded_dir for excluded_dir in excluded_list if excluded_dir != selected_clusion])
        else:
            clude_directory = directories_list[0] if directories_list else None
            if clude_directory and clude_directory not in self.excluded_dir_list:
                self.excluded_dir_list.append(clude_directory)
                self.window[self.event_key_js[f"-EXCLUDED_DIRECTORIES_LIST-"]].update(values=self.excluded_dir_list)
