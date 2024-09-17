import javalang
from query import get_single_query
from ast_comparator import compare_ast, IdentifierDifference, ASTComparatorError
from intelij_helpers import print_red
from formatting_helpers import get_tab_replaced_source, SubstringBalancingError, remove_ending_braces, \
    add_ending_braces, BalanceType, set_indentation
from segmentation_helpers import temp_replace_segment
import common
import time


class LLMRefactorError(Exception):
    pass


def llm_refactor(source_segment: str, balance_result: tuple, original_indentation_level: int, standards: [str], source_index: int, segment_index: int, num_attempts=3, verbose=True) -> (str, [IdentifierDifference]):
    """
    Refactors a source segment according to the standards.
    Returns refactored segment and a list of identifier differences.
    """

    # Load current source
    source_path = common.file_manager.get_file_path(source_index)
    # Replace tab
    curr_source = get_tab_replaced_source(open(source_path, "r").read())

    try:
        original_tree = javalang.parse.parse(curr_source)
    except javalang.parser.JavaSyntaxError as e:
        raise LLMRefactorError('Failed to parse original segment')

    prior_error_message = None

    for try_index in range(num_attempts):
        if verbose:
            print(f'Previous error message: {prior_error_message}')

        try:
            response = get_single_query(source_segment, standards, prior_error_message)
        except Exception as e:
            print_red(f'Failed to get response in attempt {try_index} due to {e}', pause=False)
            common.logger.log_error('Error in API query.')
            raise LLMRefactorError('Failed to get response from API.')

        # Handle response timeout
        if not response:
            common.logger.log_error('Timeout.')
            raise LLMRefactorError('Timeout.')

        if verbose:
            print(f'Attempt {try_index + 1}:\n{response}\n')

        # Check if the response indicates that the code already meets the standards
        response_lines = response.split('\n')
        first_line = response_lines[0]
        if first_line == 'The provided code already follows convention.':
            return None
        first_line_words = first_line.split(' ')
        if 'already' in first_line_words and 'follows' in first_line_words:
            return None

        # Restore indentation
        response = set_indentation(response, original_indentation_level)

        # Balance braces
        if balance_result is not None:
            # Unpack balance result
            balance_type, brace_change, substring = balance_result
            try:
                # Unbalance braces
                if balance_type is not None:
                    if balance_type == BalanceType.UNCLOSED:
                        # Remove added braces
                        response = remove_ending_braces(response, brace_change)
                    elif balance_type == BalanceType.UNINITIATED:
                        # Add removed braces
                        response = add_ending_braces(response, brace_change,
                                                               original_indentation_level)
                    else:
                        raise ValueError('Invalid balance type')
            except SubstringBalancingError as e:
                print(f'Failed to balance response in attempt {try_index}')
                prior_error_message = 'Previous response could not be parsed.'
                # Wait for connection to settle?
                time.sleep(0.5)
                continue

        # Parse the response
        # Create temp source with the new segment
        temp_source = temp_replace_segment(curr_source, segment_index, response)
        try:
            response_tree = javalang.parse.parse(temp_source)
        except :
            print(f'Failed to parse response in attempt {try_index}')
            prior_error_message = 'Previous response could not be parsed.'
            # Wait for connection to settle?
            time.sleep(0.5)
            continue

        # Compare the trees
        try:
            identifier_diff = compare_ast(original_tree, response_tree, curr_source)
            return response, identifier_diff
        except ASTComparatorError as e:
            print(f'Failed AST verification in attempt {try_index} due to {e}')
            prior_error_message = f'Previous response\'s AST did not match with original segment: {e}.'
            # Wait for connection to settle?
            time.sleep(0.5)
        except ValueError:
            LLMRefactorError('Failed to refactor segment due to incorrect original position.')

    raise LLMRefactorError('Failed to refactor segment in all attempts')
