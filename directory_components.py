import os
def create_directory_map(folder_path, excluded_dirs=None):
    """
    Creates a directory map of the specified folder, excluding specified directories.

    :param folder_path: Path of the folder to map.
    :param excluded_dirs: List of directories to exclude.
    :return: A nested dictionary representing the folder structure.
    """
    if excluded_dirs is None:
        excluded_dirs = []

    directory_map = {}
    for root, dirs, files in os.walk(folder_path):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in excluded_dirs]

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
def count_all_items(directory):
    """
    Count all items (files and folders) in a directory recursively.

    :param directory: Path of the directory to count items in.
    :return: Total count of files and folders.
    """
    file_count = 0
    folder_count = 0

    for root, dirs, files in os.walk(directory):
        file_count += len(files)
        folder_count += len(dirs)

    total_count = file_count + folder_count
    return total_count, file_count, folder_count
def calculate_completion_percentage(template_path, project_path, excluded_dirs=None):
    """
    Calculates the completion percentage of a project creation, excluding specified directories.

    :param template_path: Path of the template project.
    :param project_path: Path of the current building project.
    :param excluded_dirs: List of directories to exclude from the comparison.
    :return: An integer representing the completion percentage (0-100).
    """
    template_map = create_directory_map(template_path, excluded_dirs=excluded_dirs)
    project_map = create_directory_map(project_path, excluded_dirs=excluded_dirs)
    
    def count_items(directory_map):
        """Counts the number of files and directories in a directory map."""
        count = 0
        for key, value in directory_map.items():
            if isinstance(value, dict):
                count += count_items(value)
            else:
                count += 1
        return count

    total_items = count_items(template_map)
    def count_matches(template_map, project_map):
        """Counts the number of matching files and directories in two directory maps."""
        matches = 0
        for key, value in template_map.items():
            if key in project_map:
                if isinstance(value, dict):
                    matches += count_matches(value, project_map[key])
                else:
                    matches += 1
        return matches

    matched_items = count_matches(template_map, project_map)

    completion_percentage = int((matched_items / total_items) * 100) if total_items > 0 else 0
    return completion_percentage
