import math
import re
import javalang


class SubstringBalancingError(Exception):
    pass


# Define enum for balance type
class BalanceType:
    UNCLOSED = 0
    UNINITIATED = 1

def find_first_unbalanced_closing_brace(s: str) -> int:
    """Helper function to find the first unbalanced closing brace in a string."""
    stack = []
    i = 0
    while i < len(s):
        c = s[i]
        # Check for the start of a Javadoc comment
        if c == '/' and i + 2 < len(s) and s[i + 1] == '*' and s[i + 2] == '*':
            # Skip until the end of the Javadoc comment
            i += 3
            while i + 1 < len(s) and not (s[i] == '*' and s[i + 1] == '/'):
                i += 1
            i += 2  # Skip past the '*/'
            continue

        if c == '{':
            stack.append(i)
        elif c == '}':
            if len(stack) == 0:
                return i
            stack.pop()
        i += 1

    raise SubstringBalancingError('Unable to find unbalanced closing brace')


def balance_source(s: str) -> (BalanceType, (int, int), str):
    """
    Balances a source string by adding braces.
    Returns None if the string is already balanced.
    If unclosed braces: returns the number of added braces.
    If uninitiated braces: returns the number of removed braces.
    """
    stack = []
    i = 0
    while i < len(s):
        c = s[i]

        # Check for the start of a Javadoc comment
        if c == '/' and i + 2 < len(s) and s[i + 1] == '*' and s[i + 2] == '*':
            # Skip until the end of the Javadoc comment
            i += 3
            while i + 1 < len(s) and not (s[i] == '*' and s[i + 1] == '/'):
                i += 1
            i += 2  # Skip past the '*/'
            continue

        if c == '{':
            if len(stack) > 0 and stack[-1] == '}':
                raise SubstringBalancingError('Format Error')
            stack.append(c)
        elif c == '}':
            if len(stack) > 0 and stack[-1] == '{':
                stack.pop()
            else:
                stack.append(c)

        i += 1

    # If the stack is empty, the string is balanced
    if len(stack) == 0:
        return None
    # Determine balance type
    stack_length = len(stack)
    # Unclosed string
    if stack[0] == '{':
        result_string = s + ''.join(['}' for _ in range(stack_length)])
        return BalanceType.UNCLOSED, stack_length, result_string
    # Uninitiated string
    else:
        end_position = find_first_unbalanced_closing_brace(s)
        result_string = s[:end_position]
        return BalanceType.UNINITIATED, stack_length, result_string


def is_suitable_segment_after_cut(s: str) -> bool:
    """
    Checks if a segment is suitable after cutting.
    """
    # First, try to balance the segment
    try:
        balance_result = balance_source(s)
    except SubstringBalancingError:
        # If balancing fails, this is automatically a fail
        return False
    # If the segment is balanced is it suitable
    if balance_result is None:
        return True
    # If the segment is unclosed, it is suitable
    balance_type, brace_count, result_string = balance_result
    if balance_type == BalanceType.UNCLOSED:
        return True
    # Find the removed braces
    removed_length = len(s) - len(result_string)
    removed_string = s[-removed_length:]
    # If the removed string contains anything other than whitespace, braces, or newlines, it is not suitable
    allowed_chars = set([' ', '\n', '{', '}', '(', ')', ';'])
    for c in removed_string:
        if c not in allowed_chars:
            return False
    return True


def remove_ending_braces(s: str, num_braces: int) -> str:
    """
    Removes a specific number of ending braces from a string.
    """
    # Find the last index of the string
    last_index = len(s) - 1
    # Find the index of the last brace
    for i in range(last_index, -1, -1):
        if s[i] == '}':
            num_braces -= 1
            if num_braces == 0:
                return s[:i]
    return s


def add_ending_braces(s: str, num_braces: int, indentation_level: int, indentation_step=4) -> str:
    """
    Adds a specific number of ending braces to a string.
    """
    if (indentation_level - num_braces * indentation_step) < 0:
        raise SubstringBalancingError('Invalid indentation level')
    running_indentation_count = 1
    for i in range(num_braces):
        curr_indent_count = indentation_level - running_indentation_count * indentation_step
        s += '\n' + ' ' * curr_indent_count + '}'
    return s


def reset_indentation(s: str) -> (str, int):
    """
    Resets the indentation of a string to 0.
    Returns resulting string and the original indentation level.
    """
    # Split the string into lines
    lines = s.split('\n')
    # Determine the indentation
    min_indentation = math.inf
    for line in lines:
        if line.strip() == '':
            continue
        indentation = len(line) - len(line.lstrip())
        min_indentation = min(min_indentation, indentation)

    if min_indentation == math.inf:
        min_indentation = 0

    # Reset the indentation
    result_lines = []
    for line in lines:
        result_lines.append(line[min_indentation:])
    return '\n'.join(result_lines), min_indentation


def set_indentation(s: str, indentation_level: int) -> str:
    """
    Sets the indentation of a string to a specific level.
    """
    # Split the string into lines
    lines = s.split('\n')
    # Set the indentation
    result_lines = []
    for line in lines:
        result_lines.append(' ' * indentation_level + line)
    return '\n'.join(result_lines)


def get_tab_replaced_source(s: str) -> str:
    return re.sub(r'\t', '    ', s)


def replace_tab(path: str):
    with open(path, 'r') as file:
        content = file.read()
    # Replace each tab with four spaces
    content = re.sub(r'\t', '    ', content)
    with open(path, 'w') as file:
        file.write(content)
    return content
