import os

def create_directory_map(folder_path):
    """
    Creates a directory map of the specified folder, including relative paths for files.

    :param folder_path: Path of the folder to map.
    :return: A nested dictionary representing the folder structure.
    """
    
    directory_map = {}
    for root, dirs, files in os.walk(folder_path):
        # Extract the relative path from the folder path
        relative_path = os.path.relpath(root, folder_path)
        current_level = directory_map
        
        # If we're not at the top level, find the correct place in the map
        if relative_path != ".":
            for part in relative_path.split(os.sep):
                current_level = current_level.setdefault(part, {})
        
        # Add files and directories to the current level
        current_level.update({d: {} for d in dirs})
        # Include relative path starting from parent directory
        current_level.update({f: os.path.join(relative_path, f) if relative_path != "." else f for f in files})

    return directory_map

# Example usage
folder_path = '/home/joben_joe/Desktop/make_react/create_app/new_test'  # Replace with the path to the directory you want to map
directory_map = create_directory_map(folder_path)
print(directory_map)
