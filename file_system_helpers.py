import os
from copy import deepcopy


def discover_all_packages(project_directory: str) -> list:
    """Discovers all package directories based on file system structure."""
    package_list = []
    for root, dirs, files in os.walk(project_directory):
        # Check if any Java files are present in the directory
        if any(file.endswith('.java') for file in files):
            # Append the directory path directly without conversion
            package_list.append(root)

    return package_list


def discover_all_java_files(project_path: str) -> [str]:
    """
    Returns a list of all Java files in the project
    Temporary implementation for development purposes
    """
    java_files = []
    for root, dirs, files in os.walk(project_path):
        for file in files:
            if file.endswith(".java"):
                java_files.append(os.path.join(root, file))
    return java_files


def load_standards(standards_file: str) -> [str]:
    with open(standards_file, 'r') as file:
        standards = file.read().splitlines()
    return [i for i in standards if not i.startswith('#')]


class ProjectFileManagerError(Exception):
    pass


class ProjectFileManager:
    """
    Class for handling projects and their files.
    Specifically, for dynamic file system changes.
    """

    def __init__(self, root_directory: str):
        self.root_directory = root_directory

        self.files = dict()
        # Iterate through each file in the project
        for file_index, file_path in enumerate(discover_all_java_files(root_directory)):
            self.files[file_index] = file_path

    def get_file_path(self, file_index: int) -> str:
        return self.files[file_index]

    def update_file_system(self):
        java_files_set = set(discover_all_java_files(self.root_directory))
        # Find missing files
        missing_index = None
        missing_name = None
        for file_index, file_path in self.files.items():
            if file_path not in java_files_set:
                if missing_index is not None:
                    raise ProjectFileManagerError('Multiple missing files detected.')
                missing_index = file_index
        # If no missing files are detected, continue
        if missing_index is None:
            return
        # Find new name
        existing_names = set(self.files.values())
        new_name = None
        for name in java_files_set:
            if name not in existing_names:
                new_name = name
                break
        # If no new name is found, raise an error
        if new_name is None:
            raise ProjectFileManagerError('No new name found.')
        # Update the file system
        self.files[missing_index] = new_name
        # Print the update
        print(f'File system updated: {new_name} replaced {missing_name}')

    def file_system_snapshot(self) -> dict:
        """Returns a snapshot of the file system."""
        return deepcopy(self.files)

    def __len__(self):
        return len(self.files)




