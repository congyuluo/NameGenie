import javalang


class ASTComparatorError(Exception):
    pass


class IdentifierDifference:
    def __init__(self, node_type: type, name_1: str, name_2: str, original_line: int, original_index: int):
        self.node_type = node_type
        self.name_1 = name_1
        self.name_2 = name_2
        self.original_line = original_line
        self.original_index = original_index

    def __str__(self):
        return f'({self.node_type.__name__}) {self.name_1} -> {self.name_2} @ ({self.original_line}, {self.original_index})'


def print_change(identifier_diffs: [IdentifierDifference]) -> None:
    """
    Prints the change.
    """
    if identifier_diffs is None:
        print('ASTs are not structurally equivalent.')
    else:
        print('ASTs are structurally equivalent.')
        if len(identifier_diffs) == 0:
            print('No identifier change detected.')
        for diff in identifier_diffs:
            print(diff)


def check_identifier_diff_positions(identifier_diffs: [IdentifierDifference], source: str) -> None:
    """
    Checks if the original position is correct.
    """
    # Build line to index list
    lines = source.split("\n")
    running_index = 0
    line_to_index_list = []
    for line in lines:
        line_to_index_list.append(running_index)
        running_index += len(line) + 1

    for diff in identifier_diffs:
        line = diff.original_line
        index = diff.original_index
        start_index = line_to_index_list[line - 1] + index - 1
        end_index = start_index + len(diff.name_1)
        if source[start_index:end_index] != diff.name_1:
            print('Identifier differences:')
            for diff in identifier_diffs:
                print(diff)
            print('\nOriginal source:')
            print(source)
            raise ValueError(f'Original position is incorrect for {diff.name_1} at line {line}, index {index}. Received'
                             f' "{source[start_index:end_index]}".)')


def compare_ast(tree_1: javalang.ast.Node, tree_2: javalang.ast.Node, tree_1_source: str, system_testing=False) -> [IdentifierDifference]:
    """
    Compares two ASTs for structural equivalence.
    Returns a list containing changes between two ASTs.
    Raises ASTComparatorError if the trees are not structurally equivalent.
    """
    identifier_diffs = []
    for (path_1, node_1), (path_2, node_2) in zip(tree_1, tree_2):

        # Get position for error reporting purposes
        position = None
        if hasattr(node_1, 'position'):
            position = node_1.position

        # Perform type check
        if type(node_1) != type(node_2):
            raise ASTComparatorError(f'Node types are not equivalent: {type(node_1).__name__} != '
                                     f'{type(node_2).__name__} @ {position}')

        # Skip useless node types
        if isinstance(node_1, javalang.tree.SuperMethodInvocation):
            continue

        # Literal value check
        if type(node_1) is javalang.tree.Literal:
            if node_1.value != node_2.value:
                raise ASTComparatorError(f'Literal values are not equivalent: {node_1.value} != {node_2.value}')

        # Catch type check
        if type(node_1) is javalang.tree.CatchClauseParameter:
            if node_1.types != node_2.types:
                raise ASTComparatorError(f'Catch clause types are not equivalent: {node_1.types} != {node_2.types} @ {position}')

        # These are all the ones wit name attribute
        if isinstance(node_1, (javalang.tree.BasicType,
                               javalang.tree.PackageDeclaration)):
            if node_1.name != node_2.name:
                raise ASTComparatorError(f'{type(node_1).__name__} names are not equivalent: {node_1.name} != '
                                         f'{node_2.name} @ {position}')

        # Check nodes with modifier attributes
        if hasattr(node_1, 'modifiers'):
            if node_1.modifiers != node_2.modifiers:
                raise ASTComparatorError(f'{type(node_1).__name__} modifiers are not equivalent: {node_1.modifiers} != '
                                         f'{node_2.modifiers} @ {position}')

        # # Check dimensions
        if hasattr(node_1, 'dimensions'):
            if node_1.dimensions != node_2.dimensions:
                raise ASTComparatorError(f'{type(node_1).__name__} dimensions are not equivalent: {node_1.dimensions} !'
                                         f'= {node_2.dimensions} @ {position}')

        # Check static import status
        if hasattr(node_1, 'static'):
            if node_1.static != node_2.static:
                raise ASTComparatorError(f'{type(node_1).__name__} static status is not equivalent @ {position}')

        # Check for name attribute
        if hasattr(node_1, 'name'):
            if node_1.name != node_2.name or system_testing:
                if not node_1.position:
                    raise ValueError(f'Node position is not defined. Type: {type(node_1).__name__} Name: {node_1.name} @ {position}')
                identifier_diffs.append(IdentifierDifference(type(node_1), node_1.name, node_2.name, node_1.position.line, node_1.position.column))

        # Check for member attribute
        if hasattr(node_1, 'member'):
            if not node_1.position:
                raise ValueError(f'Node position is not defined. Type: {type(node_1).__name__} Name: {node_1.member} @ {position}')
            if node_1.member != node_2.member or system_testing:
                # Find out actual index
                offset = 0
                if hasattr(node_1, 'qualifier') and node_1.qualifier:
                    offset += len(node_1.qualifier) + 1
                identifier_diffs.append(IdentifierDifference(type(node_1), node_1.member, node_2.member, node_1.position.line, node_1.position.column + offset))

        def compare_reference_sequence(seq_1: str, seq_2: str, node_1_pos, error_message):
            seg_1 = [i for i in seq_1.split('.') if len(i) > 0]
            seg_2 = [i for i in seq_2.split('.') if len(i) > 0]
            if len(seg_1) != len(seg_2):
                raise ASTComparatorError(f'Qualifier segments lengths are not equivalent: "{node_1.qualifier}" != '
                                         f'"{node_2.qualifier}" @ {position}')
            running_offset = 0
            for seg_1, seg_2 in zip(seg_1, seg_2):
                if seg_1 != seg_2 or system_testing:
                    identifier_diffs.append(IdentifierDifference(type(node_1), seg_1, seg_2, node_1_pos.line, node_1_pos.column + running_offset))
                running_offset += len(seg_1) + 1

        # Check for qualifier attribute
        if hasattr(node_1, 'qualifier'):
            if node_1.qualifier != node_2.qualifier:
                compare_reference_sequence(node_1.qualifier, node_2.qualifier, node_1.position, "Qualifier segments lengths are not equivalent @ {position}")

        # Check for static import path
        if isinstance(node_1, javalang.tree.Import):
            if node_1.path != node_2.path:
                compare_reference_sequence(node_1.path, node_2.path, node_1.position,"Import segments lengths are not equivalent @ {position}")

    check_identifier_diff_positions(identifier_diffs, tree_1_source)
    return identifier_diffs

