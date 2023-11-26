import os
class ApprovedDirectories:
    def __init__(self, event_key_js, project_folder_path):
        self.event_key_js = event_key_js
        self.project_folder_path = project_folder_path

    def verify(self, directory=None):
        closest_approved_dir = directory or self.event_key_js['-DIR-']
        excluded_list = self.event_key_js[f"-EXCLUDED_DIRECTORIES_LIST-"]

        if not self.is_directory_excluded(closest_approved_dir, excluded_list):
            closest_approved_dir = self.find_closest_approved_directory(closest_approved_dir, excluded_list)
            if not closest_approved_dir:
                closest_approved_dir = self.project_folder_path
            self.update_dir_and_lists(closest_approved_dir)

        return closest_approved_dir

    def is_directory_excluded(self, directory, excluded_list):
        for excluded_dir in excluded_list:
            if directory.startswith(excluded_dir):
                return True
        return False

    def find_closest_approved_directory(self, current_directory, excluded_list):
        while current_directory:
            current_directory = os.path.dirname(current_directory)
            if not self.is_directory_excluded(current_directory, excluded_list):
                return current_directory
        return None

    def update_dir_and_lists(self, directory):
        # Add logic to update directories and lists as needed
        pass
