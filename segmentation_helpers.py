import javalang
from formatting_helpers import is_suitable_segment_after_cut


class LabelError(Exception):
    pass


class LabelExistedError(LabelError):
    pass


def get_labels(tree) -> (set, int):
    """Get all label locations"""

    labels = set()
    label_count = 0

    def under_method_declaration(node_path: tuple):
        "Determine if current node is under method or constructor declaration"
        for parent in node_path:
            if isinstance(parent, (javalang.tree.MethodDeclaration,
                                   javalang.tree.ConstructorDeclaration,)):
                return True
        return False

    # Iterate through the tree to find the nodes that we want to label
    for path, node in tree:
        # Find the nodes that we want to label
        if isinstance(node, (javalang.tree.ClassDeclaration,
                             javalang.tree.EnumDeclaration,
                             javalang.tree.InterfaceDeclaration,
                             javalang.tree.MethodDeclaration,
                             javalang.tree.ConstructorDeclaration,)):

            # Skip declarations under method definition
            if under_method_declaration(path):
                continue

            # Get position
            if not hasattr(node, 'position') or node.position is None:
                raise LabelError(f'Node with type {type(node).__name__} does not have position attribute')

            # Try to use modifier position if available
            if hasattr(node, '_modifier_position'):
                labels.add(node._modifier_position.line - 1)
            # Otherwise, use the node position
            else:
                labels.add(node.position.line - 1)

            label_count += 1

    return labels, label_count


def breakdown_segments(labels: set, source_lines, min_segment_length=10, target_segment_length=30) -> set:
    """Given existing major breakpoints, break long segments down"""
    labels = list(labels)
    labels.sort()
    omitted_segments = set()

    # Find all segments
    segments = [(labels[i], labels[i+1]) for i in range(len(labels)-1)]
    segments.append((labels[-1], labels[-1] + len(source_lines)))
    # Rule out small segments
    segments = [i for i in segments if i[1] - i[0] > target_segment_length]
    # Rule out omitted
    segments = [i for i in segments if i not in omitted_segments]

    def binary_breakdown(s: int, e: int) -> int:
        # Create temporary segment
        curr_segment = source_lines[s:e]
        # Find possible breakpoints
        possible_breakpoints = [i for i, line in enumerate(curr_segment) if len(line.replace(' ', '')) == 0]

        # Remove neighboring breakpoints
        temp_breakpoints = set()
        for i in possible_breakpoints:
            if not (i-1 in temp_breakpoints or i+1 in temp_breakpoints):
                temp_breakpoints.add(i)
        possible_breakpoints = list(temp_breakpoints)
        del temp_breakpoints

        # Remove short segment breakpoints
        possible_breakpoints.sort()
        temp_breakpoints = []
        # Iterate each breakpoint to filter out
        for i, bp in enumerate(possible_breakpoints):
            # If the breakpoint causes tail segment to be too small
            if len(curr_segment) - bp < min_segment_length:
                continue

            # Initial point
            if len(temp_breakpoints) == 0:
                # Check if it results in head segment to be too small
                if bp > min_segment_length:
                    temp_breakpoints.append(bp)
            # Rest of the points
            else:
                # Check distance to previous breakpoint
                if bp - temp_breakpoints[-1] > min_segment_length:
                    temp_breakpoints.append(bp)
        possible_breakpoints = temp_breakpoints

        # Test
        # for i, line in enumerate(curr_segment):
        #     if i in possible_breakpoints:
        #         print('<<break>>')
        #     print(f'{i:2d} |' + line, end='')
        #     print(line)
        # Endtest

        # Iterate breakpoints
        for bp in possible_breakpoints:
            # Try splitting the segment
            seg_1 = '\n'.join(source_lines[s:s+bp])
            if not is_suitable_segment_after_cut(seg_1):
                continue
            seg_2 = '\n'.join(source_lines[s+bp:e])
            if not is_suitable_segment_after_cut(seg_2):
                continue
            # At this point, balancing is correct
            return bp + s
        return None

    while len(segments) > 0:
        # Iterate segments to break down using binary breakdown function
        for start, end in segments:
            additional_label = binary_breakdown(start, end)
            # If additional label is available, add to labels and re-calculate
            if additional_label:
                labels.append(additional_label)
                labels.sort()
                break
            # Else, omit this segment
            else:
                omitted_segments.add((start, end))
        # Re-calculate segments list
        segments = [(labels[i], labels[i + 1]) for i in range(len(labels) - 1)]
        segments.append((labels[-1], labels[-1] + len(source_lines)))
        # Rule out small segments
        segments = [i for i in segments if i[1] - i[0] > target_segment_length]
        segments = [i for i in segments if i not in omitted_segments]

    return set(labels)


def find_label(source_lines: [str], label: int) -> int:
    # Iterate through the source lines
    for i, line in enumerate(source_lines):
        # Check if the line contains the label
        if line.startswith(f'// <Label: {label}>'):
            # Find the start of the segment
            return i
    return None


def get_segment_from_source(source: str, label: int) -> str:
    # Split the source into lines
    source_lines = source.split('\n')

    # Find the start of the segment
    start = find_label(source_lines, label)

    # If the label is not found, raise an error
    if start is None:
        raise LabelError(f'Label {label} not found in source')

    segment = ''

    # Find the end of the segment
    for i, line in enumerate(source_lines[start + 1:]):
        if line.startswith('// <Label:'):
            break
        segment += line + '\n'

    return segment


def fetch_segment(source_path: str, label: int) -> str:
    """
    Fetches a segment from the source file
    """
    # Open the source file
    source = open(source_path, 'r').read()
    return get_segment_from_source(source, label)


def insert_labels(source_path: str) -> int:
    """
    Inserts labels to divide source into segments
    Labels are zero-indexed, each label indicates the start of a segment with corresponding index
    Label ends are indicated by either the next label or the end of the file
    :return: The number of labels inserted
    """

    # Open the source file
    source = open(source_path, 'r').read()

    # Split the source into lines
    source_lines = source.split('\n')

    # Check for existing labels
    for line in source_lines:
        if line.startswith('// <Label:'):
            raise LabelExistedError('Labels already exist in the source file')

    # Parse the source file
    try:
        tree = javalang.parse.parse(source)
    except javalang.parser.JavaSyntaxError:
        raise LabelError('Failed to parse source')
    except javalang.tokenizer.LexerError:
        raise LabelError('Failed to parse source')

    labels, label_count = get_labels(tree)

    if len(labels) > 0:
        labels = breakdown_segments(labels, source_lines)

    line_count = len(source_lines)

    result_source = '// <Label: 0>\n'
    label_count = 1
    # Iterate through the source lines
    for i, line in enumerate(source_lines):
        # Add a label if the line number is in the labels list
        if i in labels:
            result_source += f'// <Label: {label_count}>\n'
            label_count += 1
        result_source += line
        if i != line_count - 1:
            result_source += '\n'

    # Write the result to the source file
    with open(source_path, 'w') as f:
        f.write(result_source)

    return label_count


def temp_replace_segment(source: str, label: int, new_segment: str) -> str:
    """
    Replaces a segment in the source, and returns the result.
    """
    # Split the source into lines
    source_lines = source.split('\n')

    # Find the start of the segment
    start = find_label(source_lines, label)

    # If the label is not found, raise an error
    if start is None:
        raise LabelError(f'Label {label} not found in source')

    # Add previous lines to the result source
    result_source = '\n'.join(source_lines[:start + 1]) + '\n'

    # Add the new segment to the result source
    result_source += new_segment

    # Add an extra new line if the new segment does not end with a new line
    if not new_segment.endswith('\n'):
        result_source += '\n'

    # Find the end of the segment
    dist_to_next_label = None
    for i, line in enumerate(source_lines[start + 1:]):
        if line.startswith('// <Label:'):
            dist_to_next_label = i + 1
            break

    # If end is not none, add the rest of the lines to the result source
    if dist_to_next_label is not None:
        result_source += '\n'.join(source_lines[start + dist_to_next_label:])

    return result_source


def replace_segment(source_path: str, label: int, new_segment: str):
    """
    Replaces a segment in the source file
    """
    # Open the source file
    source = open(source_path, 'r').read()

    # Replace the segment
    result_source = temp_replace_segment(source, label, new_segment)

    # Write the result to the source file
    with open(source_path, 'w') as f:
        f.write(result_source)


def remove_labels(source_path: str):
    """
    Removes labels from the source file
    """
    # Open the source file
    source = open(source_path, 'r').read()
    # Split the source into lines
    source_lines = source.split('\n')
    # Filter out the lines that do not contain labels
    source_lines = [line for line in source_lines if not line.startswith('// <Label:')]

    # Write the result to the source file
    with open(source_path, 'w') as f:
        f.write('\n'.join(source_lines))
