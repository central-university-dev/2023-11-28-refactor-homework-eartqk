from pathlib import Path

from libcst import BaseExpression, CSTTransformer, Call, Import, ImportFrom, Module, Name, RemovalSentinel, ensure_type, \
    parse_module, ClassDef, \
    FunctionDef


class RenameTransformer(CSTTransformer):
    """
    Transformer that can rename/migrate function/class. Can rename and migrate simultaneously.
    """

    def __init__(self, old_name: str, new_name: str, need_to_remove_source: bool = False):
        super().__init__()
        self._old_name = old_name
        self._new_name = new_name
        self._need_to_remove_source = need_to_remove_source

    def _rename(self, original_node, renamed_node):
        if original_node.name.value == self._old_name:
            renamed_node = renamed_node.with_changes(name=Name(self._new_name))
        return renamed_node

    def _remove_from_source(self, original_node):
        if original_node.name.value == self._old_name:
            return RemovalSentinel.REMOVE
        return original_node

    def _update_import(self, original_node, updated_node):
        new_names = []
        for alias in updated_node.names:
            if alias.name.value == self._old_name:
                alias = alias.with_changes(name=Name(self._new_name))
            new_names.append(alias)
        updated_node = updated_node.with_changes(names=new_names)
        return updated_node

    def leave_FunctionDef(self, original_node: FunctionDef, updated_node: FunctionDef) -> FunctionDef:
        if self._need_to_remove_source:
            return self._remove_from_source(original_node)
        return self._rename(original_node, updated_node)

    def leave_ClassDef(self, original_node: ClassDef, updated_node: ClassDef) -> ClassDef:
        if self._need_to_remove_source:
            return self._remove_from_source(original_node)
        return self._rename(original_node, updated_node)

    def leave_Call(self, original_node: Call, updated_node: Call) -> BaseExpression:
        if isinstance(original_node.func, Name) and original_node.func.value == self._old_name:
            updated_node = updated_node.with_changes(func=Name(self._new_name))
        return updated_node

    def leave_Import(self, original_node: Import, updated_node: Import) -> Import:
        return self._update_import(original_node, updated_node)

    def leave_ImportFrom(self, original_node: ImportFrom, updated_node: ImportFrom) -> ImportFrom:
        return self._update_import(original_node, updated_node)


def rename_fn_or_cls_in_code(source_code: str, old_name: str, new_name: str, remove_source: bool = False) -> str:
    """
    Rename and migrate a function or class with 'old_name' to 'new_name' from source_code.
    Removes function/class from source_code if 'remove_souce' specified as True.
    This functions does not have a side effect.
    Returns a modified source code.

    :param source_code: str
    :param old_name: str
    :param new_name: str
    :param remove_source: bool
    :return:
    """
    rename_transformer = RenameTransformer(old_name, new_name, remove_source)
    original_tree = parse_module(source_code)
    modified_tree = original_tree.visit(rename_transformer)

    return modified_tree.code


def rename_over_project(
        source_code_path: str, old_name: str, new_name: str, project_path: str, target_file_path: str = None,
) -> None:
    """
    Rename and migrate a function/class in source_code_path with 'old_name' to 'new_name'.
    If you specify target_file_path it removes function/class from source_code_path and write it in target_file_path.
    Specify base project_path to rename/migrate function/class over all project, it will run through the entire project.
    Writes in 'source_code_path', 'target_file_path' and *.py files over 'project_path'
    BE CAREFUL!!!

    :param source_code_path: str
    :param old_name: str
    :param new_name: str
    :param project_path: str = None
    :param target_file_path: str = None
    :return: None
    """
    rename_transformer = RenameTransformer(old_name, new_name, False)

    source_code = Path(source_code_path).read_text()
    original_tree = parse_module(source_code)
    modified_tree = original_tree.visit(rename_transformer)

    if target_file_path:
        migrate_node = None
        for node in modified_tree.body:
            if isinstance(node, (FunctionDef, ClassDef)) and node.name.value == new_name:
                migrate_node = node
                break

        target_tree = Module(body=[migrate_node])
        Path(target_file_path).write_text(target_tree.code)

    modified_code = rename_fn_or_cls_in_code(modified_tree.code, old_name, new_name, bool(target_file_path))
    Path(source_code_path).write_text(modified_code)

    project_path = Path(project_path)
    python_files = project_path.rglob('*.py')

    for file_path in python_files:
        file_path_source_code = file_path.read_text()
        updated_code = rename_fn_or_cls_in_code(file_path_source_code, old_name, new_name, False)
        file_path.write_text(updated_code)
