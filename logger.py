import os.path
import pickle
from enum import Enum


FILE_DIFF_NAME = 'file_diff'
LOG_NAME = 'log'
REFACTOR_STATUS_NAME = 'refactor_status'


class LoggerError(Exception):
    pass


# Enum for refactor status
class RefactorStatus(Enum):
    INCOMPLETE = 1
    NO_CHANGE = 2
    IJ_SUCCESS = 3
    LLM_FAILED = 4
    IJ_FAILED = 5

class Logger:
    def __init__(self, path: str, initial_file_snapshot: dict):
        self.initial_file_snapshot = initial_file_snapshot
        self.path = path
        self.log_file_path = os.path.join(self.path, f'{LOG_NAME}.txt')
        # Ensure the log file is empty initially
        with open(self.log_file_path, 'w') as f:
            pass
        # Initialize refactor status
        self.refactor_status = dict()
        for key in initial_file_snapshot.keys():
            self.refactor_status[key] = dict()

    def set_refactor_status(self, file_key: int, segment_index: int, status: RefactorStatus):
        if file_key not in self.refactor_status:
            raise LoggerError(f'File key {file_key} is missing.')
        self.refactor_status[file_key][segment_index] = status

    def _write_to_log(self, message: str):
        """Helper function to write messages to the log file."""
        with open(self.log_file_path, 'a') as file:
            file.write(message + '\n')

    def log_change(self, change: str):
        self._write_to_log(change)

    def log_error(self, error: str):
        self._write_to_log(f'Error: {error}')

    def log_file(self, file_key: str):
        self._write_to_log(f'File: {file_key}')

    def log_segment(self, segment: int):
        self._write_to_log(f'Segment: {segment}')

    def write_out(self, end_file_snapshot: dict):
        # Find the mapping of file names
        file_system_diff = []
        for key, value in self.initial_file_snapshot.items():
            if key not in end_file_snapshot:
                raise LoggerError(f'File {key} is missing.')
            file_system_diff.append((key, value, end_file_snapshot[key]))
        # Write out to file
        with open(os.path.join(self.path, f'{FILE_DIFF_NAME}.txt'), 'w') as file:
            for key, beginning_value, end_value in file_system_diff:
                file.write(f'({key}) {beginning_value} -> {end_value}\n')
        # Pickle the log
        with open(os.path.join(self.path, f'{FILE_DIFF_NAME}.pkl'), 'wb') as file:
            pickle.dump(file_system_diff, file)
        # Write out refactor status
        with open(os.path.join(self.path, f'{REFACTOR_STATUS_NAME}.txt'), 'w') as file:
            for key, status in self.refactor_status.items():
                file.write(f'{key}: {status}\n')
