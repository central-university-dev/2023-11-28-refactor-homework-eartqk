from pathlib import Path

from refactor_tool.renamer import rename_fn_or_cls_in_code


def test_func_rename():
    expected = rename_fn_or_cls_in_code(
        Path('tests/fixtures/source_func.py').read_text(),
        'source_func',
        'expected_func',
    )

    assert Path('tests/fixtures/expected_func.py').read_text() == expected


def test_class_rename():
    expected = rename_fn_or_cls_in_code(
        Path('tests/fixtures/source_class.py').read_text(),
        'SourceClass',
        'ExpectedClass',
    )

    assert Path('tests/fixtures/expected_class.py').read_text() == expected


def test_func_rename_import_from():
    expected = rename_fn_or_cls_in_code(
        'from tests.fixtures.source_func import source_func',
        'source_func',
        'expected_func',
    )

    assert 'from tests.fixtures.source_func import expected_func' == expected


def test_class_rename_import_from():
    expected = rename_fn_or_cls_in_code(
        'from tests.fixtures.source_class import SourceClass',
        'SourceClass',
        'ExpectedClass',
    )

    assert 'from tests.fixtures.source_class import ExpectedClass' == expected


def test_func_rename_call():
    expected = rename_fn_or_cls_in_code(
        'source_func(1, 2, 3)',
        'source_func',
        'expected_func',
    )

    assert 'expected_func(1, 2, 3)' == expected


def test_class_rename_call():
    expected = rename_fn_or_cls_in_code(
        'SourceClass(value)',
        'SourceClass',
        'ExpectedClass',
    )

    assert 'ExpectedClass(value)' == expected


def test_func_rename_remove_source():
    expected = rename_fn_or_cls_in_code(
        Path('tests/fixtures/source_func.py').read_text(),
        'source_func',
        'expected_func',
        True,
    )

    assert '\n' == expected


def test_class_rename_remove_source():
    expected = rename_fn_or_cls_in_code(
        Path('tests/fixtures/source_class.py').read_text(),
        'SourceClass',
        'ExpectedClass',
        True,
    )

    assert '\n' == expected
