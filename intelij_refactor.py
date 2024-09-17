import javalang

from intelij_helpers import *
from ast_comparator import compare_ast, ASTComparatorError
from segmentation_helpers import temp_replace_segment
from formatting_helpers import get_tab_replaced_source
import common


class GlobalRefactorError(Exception):
    pass


class IntelijRefactorError(Exception):
    pass


def refactor_changed_identifiers(source_path_index: int, segment_index: int, segment: str, debug=True):
    """
    Refactors changed identifiers in a segment.
    """

    prior_identifier_change = None

    # Reload the source
    reload_from_file()

    # Create variable for omitted identifiers
    omitted_names = set()

    # Create variable for storing all original names
    original_names = set()

    contains_failed_refactor = False

    take_two = False

    while True:
        # Load current source
        source_path = common.file_manager.get_file_path(source_path_index)
        # Replace tab
        curr_source = get_tab_replaced_source(open(source_path, "r").read())

        # Create temp source with the new segment
        temp_source = temp_replace_segment(curr_source, segment_index, segment)

        # Parse both sources
        try:
            curr_tree = javalang.parse.parse(curr_source)
        except javalang.parser.JavaSyntaxError as e:
            print(f'Current source:\n{curr_source}')
            print(f'Temporary source:\n{temp_source}')
            raise GlobalRefactorError('Failed to parse current source.')

        try:
            temp_tree = javalang.parse.parse(temp_source)
        except javalang.parser.JavaSyntaxError as e:
            print(f'Temporary source:\n{temp_source}')
            print(f'Current source:\n{curr_source}')
            raise GlobalRefactorError('Failed to parse temporary source.')

        # Find changed identifiers
        try:
            identifier_changes = compare_ast(curr_tree, temp_tree, curr_source)
        except ASTComparatorError as e:
            print(f'Current source:\n{curr_source}')
            print(f'Temporary source:\n{temp_source}')
            raise GlobalRefactorError('AST comparison failed.')

        for change in identifier_changes:
            original_names.add(change.name_1)
        # Filter out omitted names
        identifier_changes = [change for change in identifier_changes if change.name_1 not in omitted_names]
        # Filter out resulting names that overlap with original names
        identifier_changes = [change for change in identifier_changes if change.name_2 not in original_names]

        if len(identifier_changes) == 0:
            break

        # Refactor the first identifier
        identifier_to_change = identifier_changes[0]

        if prior_identifier_change is not None and len(prior_identifier_change) <= len(identifier_changes):
            if not take_two:
                take_two = True
                print_red("Trying again.", pause=False)
                time.sleep(1)
                continue

            print(f'Prior identifier change:\n')
            for change in prior_identifier_change:
                print(change)
            print(f'Current identifier to change:\n')
            for change in identifier_changes:
                print(change)
            # Testing
            common.logger.log_error(f'Failed to refactor (Identifier Change Count) {identifier_to_change.name_1}.')
            print_red(f'Prior identifier change did not reduce the number of changes.', pause=False)
            choice = input('Continue? (y/n): ')
            if choice == 'y':
                omitted_names.add(identifier_to_change.name_1)
                click_on_intelij()
                continue
            click_on_intelij()
            # Save
            save_file()
            # Refresh file system
            common.file_manager.update_file_system()
            return True
            # End testing
        else:
            take_two = False

        prior_identifier_change = identifier_changes

        if debug:
            for change in identifier_changes:
                print(change)
            print(f'\nCurrent identifier:')
            print(identifier_to_change)
            print()

        # Seek the position
        seek_position(identifier_to_change.original_line, identifier_to_change.original_index)
        # Refactor the identifier
        if not refactor(identifier_to_change.name_2):
            # Add to omitted names
            omitted_names.add(identifier_to_change.name_1)
            # Set prior identifier change to None
            prior_identifier_change = None
            contains_failed_refactor = True
        else:
            time.sleep(0.1)
            common.logger.log_change(str(identifier_to_change))
        # Save
        save_file()
        # Refresh file system
        common.file_manager.update_file_system()

    return contains_failed_refactor
