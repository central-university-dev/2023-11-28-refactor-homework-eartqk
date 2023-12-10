from pathlib import Path

import pytest

from refactor_tool.renamer import rename_over_project


@pytest.fixture
def setup_tmp_files(tmp_path) -> tuple[Path, Path, Path]:
    source_code = 'def old_function():\n    return("old")'
    migration_target_code = 'print("some text for test")'
    code_with_imports = 'from .source import old_function\n\nresult_function = old_function()'

    source_code_path = tmp_path / 'source.py'
    migration_target_code_path = tmp_path / 'migration_target.py'
    code_with_imports_path = tmp_path / 'code_with_imports.py'

    source_code_path.write_text(source_code)
    migration_target_code_path.write_text(migration_target_code)
    code_with_imports_path.write_text(code_with_imports)

    return source_code_path, migration_target_code_path, code_with_imports_path


def test_rename_function(tmp_path, setup_tmp_files):
    source_code_path, migration_target_path, code_with_imports_path = setup_tmp_files

    rename_over_project(source_code_path, 'old_function', 'new_function', tmp_path, migration_target_path)

    expected_source_code = ''
    assert source_code_path.read_text() == expected_source_code

    expected_migration_target_code = 'print(\"some text for test\")\ndef old_function():\n    return(\"old\")'
    assert migration_target_path.read_text() == expected_migration_target_code

    expected_code_with_imports = 'from .migration_target import new_function\nresult_function = new_function()\n'
    assert code_with_imports_path.read_text() == expected_code_with_imports
