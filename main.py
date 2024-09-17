import shutil

import common
from file_system_helpers import *
from segmentation_helpers import *
from formatting_helpers import *
from intelij_refactor import *
from llm_refactor import *
from logger import Logger, RefactorStatus

PROJECT_DIRECTORY = common.refactoring_directory
SAMPLE_RATIO = common.sampling_ratio

REFACTOR_SEGMENTS_DIRECTORY = 'refactor_generated_segments'
LOG_DIR = 'logs'

ESTIMATED_LINE_COUNT = 1800


def prepare_directories():
    # Clean up refactor segments directory
    if os.path.exists(REFACTOR_SEGMENTS_DIRECTORY):
        shutil.rmtree(REFACTOR_SEGMENTS_DIRECTORY)
    os.mkdir(REFACTOR_SEGMENTS_DIRECTORY)

    # Clean up log directory
    if os.path.exists(LOG_DIR):
        shutil.rmtree(LOG_DIR)
    os.mkdir(LOG_DIR)


if __name__ == "__main__":
    # Load standards
    standards = load_standards('oracle_standards.txt')

    prepare_directories()

    # Get absolute path of refactor segments directory
    refactor_segments_directory = os.path.abspath(REFACTOR_SEGMENTS_DIRECTORY)
    # Get absolute path of log directory
    log_directory = os.path.abspath(LOG_DIR)

    # Change directory to project directory
    os.chdir(PROJECT_DIRECTORY)

    # Discover all files
    common.file_manager = ProjectFileManager(PROJECT_DIRECTORY)
    # Initiate Logger
    common.logger = Logger(log_directory, common.file_manager.file_system_snapshot())

    file_count = len(common.file_manager)
    # Alter file count by sample ratio
    file_count = int(file_count / SAMPLE_RATIO)

    running_file_count = 0
    processed_line_count = 0

    print(f'File count: {file_count}')

    # Variable for resuming from a specific file
    start_from = None

    # Write out log if interrupted
    common.logger.write_out(common.file_manager.file_system_snapshot())

    try:
        # Iterate through each Java file
        for file_path_index in range(len(common.file_manager)):
            if file_path_index % SAMPLE_RATIO != 0:
                continue
            file_path = common.file_manager.get_file_path(file_path_index)

            # Log file
            common.logger.log_file(file_path_index)

            if start_from is not None:
                curr_file = file_path.split('/')[-1]
                if curr_file == start_from:
                    start_from = None
                else:
                    continue

            # Open Intelij
            click_on_intelij()
            open_file(common.file_manager.get_file_path(file_path_index))

            print(f'-> {file_path}')

            # Replace tab
            try:
                replace_tab(file_path)
            except:
                print("Failed to open file.")
                continue

            # Process Java file
            try:
                segment_count = insert_labels(file_path)
            except LabelExistedError:
                remove_labels(file_path)
                segment_count = insert_labels(file_path)
                pass
            except LabelError:
                print_red("Failed to parse file.", pause=False)
                common.logger.log_error(f'File {file_path} failed to parse, skipping...')
                close_file()
                continue

            # Create a directory for the file
            file_name = file_path.split('/')[-1][:-5]
            file_directory = os.path.join(refactor_segments_directory, file_name)
            # Check if directory exists
            if os.path.exists(file_directory):
                shutil.rmtree(file_directory)
            os.mkdir(file_directory)

            try:
                # Iterate through each segment except the first one, as it contains only imports and package declarations
                for segment_index in range(1, segment_count):
                    if contains_fault():
                        print_red('Fault detected.', pause=True)
                        raise ContainsFaultError('Fault detected.')
                    # Reload file path
                    file_path = common.file_manager.get_file_path(file_path_index)
                    common.logger.log_segment(segment_index)

                    print(f'Segment {segment_index}:\n')
                    print(f'Running file count: {running_file_count + 1}/{file_count} Estimated progress: [{(processed_line_count/ESTIMATED_LINE_COUNT)*100}%]')
                    # Fetch segment
                    # Replace tab
                    segment = fetch_segment(file_path, segment_index)

                    # Add to line count
                    processed_line_count += segment.count('\n') + 1

                    # Balance braces
                    try:
                        balance_result = balance_source(segment)
                    except SubstringBalancingError:
                        continue
                    balance_type = None
                    if balance_result is not None:
                        balance_type, brace_change, substring = balance_result
                        segment = substring

                    # Check indentation
                    segment, original_indentation_level = reset_indentation(segment)

                    print(f'Original segment:\n{segment}')

                    # Write the original segment to a file
                    with open(os.path.join(file_directory, f'{segment_index}_original.java'), 'w') as file:
                        file.write(segment)

                    try:
                        refactor_result = llm_refactor(segment, balance_result, original_indentation_level, standards, file_path_index, segment_index)
                    except LLMRefactorError as e:
                        # Store status
                        common.logger.log_error(f'Segment {segment_index} failed LLM refactoring due to: {e}')
                        common.logger.set_refactor_status(file_path_index, segment_index, RefactorStatus.LLM_FAILED)
                        continue

                    # Check if no change is needed
                    if refactor_result is None:
                        # Set refactored segment to original segment
                        print('Segment does not require refactoring.')
                        common.logger.set_refactor_status(file_path_index, segment_index, RefactorStatus.NO_CHANGE)
                        continue
                    else:
                        # Else, unpack
                        refactored_segment, identifier_change = refactor_result
                        if len(identifier_change) == 0:
                            print('Segment does not require refactoring.')
                            common.logger.set_refactor_status(file_path_index, segment_index, RefactorStatus.NO_CHANGE)
                            continue
                        # Write the refactored segment to a file
                        with open(os.path.join(file_directory, f'{segment_index}_refactored.java'), 'w') as file:
                            file.write(refactored_segment)

                    # Refactor changed identifiers
                    try:
                        contains_failed_refactor = refactor_changed_identifiers(file_path_index, segment_index, refactored_segment)
                        common.logger.set_refactor_status(file_path_index, segment_index, RefactorStatus.IJ_SUCCESS)
                    except GlobalRefactorError as e:
                        common.logger.log_error(f'Segment {segment_index} failed inteliJ refactoring due to: {e}')
                        print_red(f'Segment {segment_index} failed due to: {e}', pause=True)
                        common.logger.set_refactor_status(file_path_index, segment_index, RefactorStatus.IJ_FAILED)
                        continue
                    except ValueError as e:
                        common.logger.log_error(f'Segment {segment_index} failed inteliJ refactoring due to: {e}')
                        print_red(f'Segment {segment_index} failed due to: {e}', pause=True)
                        common.logger.set_refactor_status(file_path_index, segment_index, RefactorStatus.IJ_FAILED)
                        continue

                    # Replace segment
                    if not contains_failed_refactor:
                        file_path = common.file_manager.get_file_path(file_path_index)
                        replace_segment(file_path, segment_index, refactored_segment)
                        time.sleep(0.2)
                        reload_from_file()

                # Reload file path
                file_path = common.file_manager.get_file_path(file_path_index)
                close_file()
                # Remove labels
                remove_labels(file_path)

            except ContainsFaultError:
                close_file()
                # Remove labels
                remove_labels(file_path)
                common.logger.log_error(f'File {file_path} contains fault, skipping...')

            running_file_count += 1

    except KeyboardInterrupt:
        # Write out log if interrupted
        common.logger.write_out(common.file_manager.file_system_snapshot())
        print('Exiting...')
        exit(0)

    # Write out log
    common.logger.write_out(common.file_manager.file_system_snapshot())

    # Delete 'screenshot_pic.png' file
    if os.path.exists('screenshot_pic.png'):
        os.remove('screenshot_pic.png')
