"""
Tests for Sphinx extensions.
"""

import subprocess
import sys
from pathlib import Path
from textwrap import dedent


def test_prompt_specified_late(tmp_path: Path) -> None:
    """
    If sphinx-prompt is not specified in extensions before Sphinx substitution
    extensions, an error is given.
    """
    source_directory = tmp_path / 'source'
    source_directory.mkdir()
    source_file = source_directory / 'index.rst'
    conf_py = source_directory / 'conf.py'
    conf_py.touch()
    source_file.touch()
    conf_py_content = dedent(
        """\
        extensions = ['sphinx_substitution_extensions', 'sphinx-prompt']
        """,
    )
    conf_py.write_text(conf_py_content)
    destination_directory = tmp_path / 'destination'
    args = [
        sys.executable,
        '-m',
        'sphinx',
        '-b',
        'html',
        '-W',
        # Directory containing source and configuration files.
        str(source_directory),
        # Directory containing build files.
        str(destination_directory),
        # Source file to process.
        str(source_file),
    ]
    result = subprocess.run(
        args=args,
        check=False,
        stderr=subprocess.PIPE,
    )

    expected_message = (
        'sphinx-prompt must be in the conf.py extensions list before '
        'sphinx_substitution_extensions'
    )

    assert result.returncode != 0
    assert expected_message in result.stderr.decode()


def test_substitution_prompt(tmp_path: Path) -> None:
    """
    The ``prompt`` directive replaces the placeholders defined in ``conf.py``
    when requested.
    """
    source_directory = tmp_path / 'source'
    source_directory.mkdir()
    source_file = source_directory / 'index.rst'
    conf_py = source_directory / 'conf.py'
    conf_py.touch()
    source_file.touch()
    conf_py_content = dedent(
        """\
        extensions = ['sphinx-prompt', 'sphinx_substitution_extensions']
        rst_prolog = '''
        .. |a| replace:: example_substitution
        '''
        """,
    )
    conf_py.write_text(conf_py_content)
    source_file_content = dedent(
        """\
        .. prompt:: bash $
           :substitutions:

           $ PRE-|a|-POST
        """,
    )
    source_file.write_text(source_file_content)
    destination_directory = tmp_path / 'destination'
    args = [
        sys.executable,
        '-m',
        'sphinx',
        '-b',
        'html',
        '-W',
        # Directory containing source and configuration files.
        str(source_directory),
        # Directory containing build files.
        str(destination_directory),
        # Source file to process.
        str(source_file),
    ]
    subprocess.check_output(args=args)
    expected = 'PRE-example_substitution-POST'
    content_html = Path(str(destination_directory)) / 'index.html'
    assert expected in content_html.read_text()


def test_substitution_prompt_is_case_preserving(tmp_path: Path) -> None:
    """
    The ``prompt`` directive respects the original case of replacements.
    """
    source_directory = tmp_path / 'source'
    source_directory.mkdir()
    source_file = source_directory / 'index.rst'
    conf_py = source_directory / 'conf.py'
    conf_py.touch()
    source_file.touch()
    conf_py_content = dedent(
        """\
        extensions = ['sphinx-prompt', 'sphinx_substitution_extensions']
        rst_prolog = '''
        .. |aBcD_eFgH| replace:: example_substitution
        '''
        """,
    )
    conf_py.write_text(conf_py_content)
    source_file_content = dedent(
        """\
        .. prompt:: bash $
           :substitutions:

           $ PRE-|aBcD_eFgH|-POST
        """,
    )
    source_file.write_text(source_file_content)
    destination_directory = tmp_path / 'destination'
    args = [
        sys.executable,
        '-m',
        'sphinx',
        '-b',
        'html',
        '-W',
        # Directory containing source and configuration files.
        str(source_directory),
        # Directory containing build files.
        str(destination_directory),
        # Source file to process.
        str(source_file),
    ]
    subprocess.check_output(args=args)
    expected = 'PRE-example_substitution-POST'
    content_html = Path(str(destination_directory)) / 'index.html'
    assert expected in content_html.read_text()


def test_no_substitution_prompt(tmp_path: Path) -> None:
    """
    The ``prompt`` directive does not replace the placeholders defined in
    ``conf.py`` when that is not requested.
    """
    source_directory = tmp_path / 'source'
    source_directory.mkdir()
    source_file = source_directory / 'index.rst'
    conf_py = source_directory / 'conf.py'
    conf_py.touch()
    source_file.touch()
    conf_py_content = dedent(
        """\
        extensions = ['sphinx-prompt', 'sphinx_substitution_extensions']
        rst_prolog = '''
        .. |a| replace:: example_substitution
        '''
        """,
    )
    conf_py.write_text(conf_py_content)
    source_file_content = dedent(
        """\
        .. prompt:: bash $

           $ PRE-|a|-POST
        """,
    )
    source_file.write_text(source_file_content)
    destination_directory = tmp_path / 'destination'
    args = [
        sys.executable,
        '-m',
        'sphinx',
        '-b',
        'html',
        '-W',
        # Directory containing source and configuration files.
        str(source_directory),
        # Directory containing build files.
        str(destination_directory),
        # Source file to process.
        str(source_file),
    ]
    subprocess.check_output(args=args)
    expected = 'PRE-example_substitution-POST'
    content_html = Path(str(destination_directory)) / 'index.html'
    assert expected not in content_html.read_text()


def test_no_substitution_code_block(tmp_path: Path) -> None:
    """
    The ``code-block`` directive does not replace the placeholders defined in
    ``conf.py`` when not specified.
    """
    source_directory = tmp_path / 'source'
    source_directory.mkdir()
    source_file = source_directory / 'index.rst'
    conf_py = source_directory / 'conf.py'
    conf_py.touch()
    source_file.touch()
    conf_py_content = dedent(
        """\
        extensions = ['sphinx-prompt', 'sphinx_substitution_extensions']
        rst_prolog = '''
        .. |a| replace:: example_substitution
        '''
        """,
    )
    conf_py.write_text(conf_py_content)
    source_file_content = dedent(
        """\
        .. code-block:: bash

           $ PRE-|a|-POST
        """,
    )
    source_file.write_text(source_file_content)
    destination_directory = tmp_path / 'destination'
    args = [
        sys.executable,
        '-m',
        'sphinx',
        '-b',
        'html',
        '-W',
        # Directory containing source and configuration files.
        str(source_directory),
        # Directory containing build files.
        str(destination_directory),
        # Source file to process.
        str(source_file),
    ]
    subprocess.check_output(args=args)
    expected = 'PRE-example_substitution-POST'
    content_html = Path(str(destination_directory)) / 'index.html'
    assert expected not in content_html.read_text()


def test_substitution_code_block(tmp_path: Path) -> None:
    """
    The ``code-block`` directive replaces the placeholders defined in
    ``conf.py`` as specified.
    """
    source_directory = tmp_path / 'source'
    source_directory.mkdir()
    source_file = source_directory / 'index.rst'
    conf_py = source_directory / 'conf.py'
    conf_py.touch()
    source_file.touch()
    conf_py_content = dedent(
        """\
        extensions = ['sphinx-prompt', 'sphinx_substitution_extensions']
        rst_prolog = '''
        .. |a| replace:: example_substitution
        '''
        """,
    )
    conf_py.write_text(conf_py_content)
    source_file_content = dedent(
        """\
        .. code-block:: bash
           :substitutions:

           $ PRE-|a|-POST
        """,
    )
    source_file.write_text(source_file_content)
    destination_directory = tmp_path / 'destination'
    args = [
        sys.executable,
        '-m',
        'sphinx',
        '-b',
        'html',
        '-W',
        # Directory containing source and configuration files.
        str(source_directory),
        # Directory containing build files.
        str(destination_directory),
        # Source file to process.
        str(source_file),
    ]
    subprocess.check_output(args=args)
    expected = 'PRE-example_substitution-POST'
    content_html = Path(str(destination_directory)) / 'index.html'
    assert expected in content_html.read_text()


def test_substitution_code_block_case_preserving(tmp_path: Path) -> None:
    """
    The ``code-block`` directive respects the original case of replacements.
    """
    source_directory = tmp_path / 'source'
    source_directory.mkdir()
    source_file = source_directory / 'index.rst'
    conf_py = source_directory / 'conf.py'
    conf_py.touch()
    source_file.touch()
    conf_py_content = dedent(
        """\
        extensions = ['sphinx-prompt', 'sphinx_substitution_extensions']
        rst_prolog = '''
        .. |aBcD_eFgH| replace:: example_substitution
        '''
        """,
    )
    conf_py.write_text(conf_py_content)
    source_file_content = dedent(
        """\
        .. code-block:: bash
           :substitutions:

           $ PRE-|aBcD_eFgH|-POST
        """,
    )
    source_file.write_text(source_file_content)
    destination_directory = tmp_path / 'destination'
    args = [
        sys.executable,
        '-m',
        'sphinx',
        '-b',
        'html',
        '-W',
        # Directory containing source and configuration files.
        str(source_directory),
        # Directory containing build files.
        str(destination_directory),
        # Source file to process.
        str(source_file),
    ]
    subprocess.check_output(args=args)
    expected = 'PRE-example_substitution-POST'
    content_html = Path(str(destination_directory)) / 'index.html'
    assert expected in content_html.read_text()


def test_substitution_inline(tmp_path: Path) -> None:
    """
    The ``substitution-code`` role replaces the placeholders defined in
    ``conf.py`` as specified.
    """
    source_directory = tmp_path / 'source'
    source_directory.mkdir()
    source_file = source_directory / 'index.rst'
    conf_py = source_directory / 'conf.py'
    conf_py.touch()
    source_file.touch()
    conf_py_content = dedent(
        """\
        extensions = ['sphinx-prompt', 'sphinx_substitution_extensions']
        rst_prolog = '''
        .. |a| replace:: example_substitution
        '''
        """,
    )
    conf_py.write_text(conf_py_content)
    source_file_content = dedent(
        """\
        Example :substitution-code:`PRE-|a|-POST`
        """,
    )
    source_file.write_text(source_file_content)
    destination_directory = tmp_path / 'destination'
    args = [
        sys.executable,
        '-m',
        'sphinx',
        '-b',
        'html',
        '-W',
        # Directory containing source and configuration files.
        str(source_directory),
        # Directory containing build files.
        str(destination_directory),
        # Source file to process.
        str(source_file),
    ]
    subprocess.check_output(args=args)
    expected = 'PRE-example_substitution-POST'
    content_html = Path(str(destination_directory)) / 'index.html'
    assert expected in content_html.read_text()


def test_substitution_inline_case_preserving(tmp_path: Path) -> None:
    """
    The ``substitution-code`` role respects the original case of replacements.
    """
    source_directory = tmp_path / 'source'
    source_directory.mkdir()
    source_file = source_directory / 'index.rst'
    conf_py = source_directory / 'conf.py'
    conf_py.touch()
    source_file.touch()
    conf_py_content = dedent(
        """\
        extensions = ['sphinx-prompt', 'sphinx_substitution_extensions']
        rst_prolog = '''
        .. |aBcD_eFgH| replace:: example_substitution
        '''
        """,
    )
    conf_py.write_text(conf_py_content)
    source_file_content = dedent(
        """\
        Example :substitution-code:`PRE-|aBcD_eFgH|-POST`
        """,
    )
    source_file.write_text(source_file_content)
    destination_directory = tmp_path / 'destination'
    args = [
        sys.executable,
        '-m',
        'sphinx',
        '-b',
        'html',
        '-W',
        # Directory containing source and configuration files.
        str(source_directory),
        # Directory containing build files.
        str(destination_directory),
        # Source file to process.
        str(source_file),
    ]
    subprocess.check_output(args=args)
    expected = 'PRE-example_substitution-POST'
    content_html = Path(str(destination_directory)) / 'index.html'
    assert expected in content_html.read_text()
