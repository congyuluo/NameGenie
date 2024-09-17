import common
import statistics

from file_system_helpers import *
from segmentation_helpers import *
from formatting_helpers import *


PROJECT_DIRECTORY = common.refactoring_directory
SAMPLE_RATIO = common.sampling_ratio


if __name__ == "__main__":
    # Change directory to project directory
    os.chdir(PROJECT_DIRECTORY)

    # Discover all files
    common.file_manager = ProjectFileManager(PROJECT_DIRECTORY)

    file_count = len(common.file_manager)
    attempted_file_count = 0
    line_count = 0
    fault_count = 0
    print(f'File count: {file_count}')

    segment_lengths = []

    # Iterate through each Java file
    for file_path_index in range(len(common.file_manager)):
        if file_path_index % SAMPLE_RATIO != 0:
            continue
        attempted_file_count += 1
        file_path = common.file_manager.get_file_path(file_path_index)

        # Read file
        with open(file_path, 'r') as f:
            source = f.read()
            line_count += source.count('\n') + 1
            del source

        # Process Java file
        try:
            segment_count = insert_labels(file_path)
        except LabelExistedError:
            remove_labels(file_path)
            segment_count = insert_labels(file_path)
            pass
        except LabelError as e:
            # print(f'Label error: {e}')
            fault_count += 1
            continue

        # Iterate through each segment except the first one, as it contains only imports and package declarations
        for segment_index in range(1, segment_count):
            # Replace tab
            segment = fetch_segment(file_path, segment_index)

            segment_lengths.append(segment.count('\n') + 1)

            # Balance braces
            try:
                balanced_result = balance_source(segment)
            except SubstringBalancingError as e:
                fault_count += 1
                continue

            balance_type = None
            if balanced_result is not None:
                balance_type, brace_change, substring = balanced_result
                segment = substring

            # Check indentation
            segment, original_indentation_level = reset_indentation(segment)

            # Parse segment

            # Restore indentation
            refactored_segment = set_indentation(segment, original_indentation_level)

        # Remove labels
        remove_labels(file_path)

    print(f'Under sampling ratio: {SAMPLE_RATIO}')
    print(f'Attempted file count: {attempted_file_count}')

    print(f'\nFault count: {fault_count}')
    print(f'Java line count: {line_count}')

    print(f'\nSegment count: {len(segment_lengths)}')
    # Print average, median, and SD of segment lengths
    print(f'Average segment length: {sum(segment_lengths) / len(segment_lengths)}')
    print(f'Median segment length: {sorted(segment_lengths)[len(segment_lengths) // 2]}')
    print(f'SD segment length: {statistics.stdev(segment_lengths)}')
    # Print max and min segment lengths
    print(f'Max segment length: {max(segment_lengths)}')
    print(f'Min segment length: {min(segment_lengths)}')


