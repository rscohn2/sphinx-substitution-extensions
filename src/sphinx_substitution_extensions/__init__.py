"""
Custom Sphinx extensions.
"""

import importlib
from typing import Dict, List, Tuple

from docutils.nodes import Node, system_message
from docutils.parsers.rst import directives
from docutils.parsers.rst.roles import code_role
from docutils.parsers.rst.states import Inliner
from sphinx.application import Sphinx
from sphinx.directives.code import CodeBlock

# Due to the dash in the name, we cannot import sphinx-prompt using a normal
# import.
_SPHINX_PROMPT = importlib.import_module('sphinx-prompt')
_PROMPT_DIRECTIVE = _SPHINX_PROMPT.PromptDirective  # type: ignore


class SubstitutionCodeBlock(CodeBlock):
    """
    Similar to CodeBlock but replaces placeholders with variables.
    """

    def run(self) -> List:
        """
        Replace placeholders with given variables.
        """
        new_content = []
        self.content = self.content  # type: List[str]
        existing_content = self.content
        for item in existing_content:
            for name in self.state.document.substitution_names:
                replacement = self.state.document.substitution_defs[name
                                                                    ].astext()
                item = item.replace(
                    '|{original}|'.format(original=name),
                    replacement,
                )
            new_content.append(item)

        self.content = new_content
        return list(CodeBlock.run(self))


class SubstitutionPrompt(_PROMPT_DIRECTIVE):  # type: ignore
    """
    Similar to PromptDirective but replaces placeholders with variables.
    """

    def run(self) -> List:
        """
        Replace placeholders with given variables.
        """
        new_content = []
        self.content = (  # pylint: disable=attribute-defined-outside-init
            self.content
        )  # type: List[str]
        existing_content = self.content
        for item in existing_content:
            for name in self.state.document.substitution_names:
                replacement = self.state.document.substitution_defs[name
                                                                    ].astext()
                item = item.replace(
                    '|{original}|'.format(original=name),
                    replacement,
                )
            new_content.append(item)

        self.content = (  # pylint: disable=attribute-defined-outside-init
            new_content
        )
        return list(_PROMPT_DIRECTIVE.run(self))


def substitution_code_role(  # pylint: disable=dangerous-default-value
    typ: str,
    rawtext: str,
    text: str,
    lineno: int,
    inliner: Inliner,
    options: Dict = {},
    content: List[str] = [],
) -> Tuple[List[Node], List[system_message]]:
    """
    Replace placeholders with given variables.
    """
    document = inliner.document  # type: ignore
    for name in document.substitution_names:
        replacement = document.substitution_defs[name].astext()
        text = text.replace(
            '|{original}|'.format(original=name),
            replacement,
        )
        rawtext = text.replace(
            '|{original}|'.format(original=name),
            replacement,
        )
        rawtext = rawtext.replace(name, replacement)

    result_nodes, system_messages = code_role(
        role=typ,
        rawtext=rawtext,
        text=text,
        lineno=lineno,
        inliner=inliner,
        options=options,
        content=content,
    )

    return result_nodes, system_messages


substitution_code_role.options = {  # type: ignore
    'class': directives.class_option,
    'language': directives.unchanged,
}


def setup(app: Sphinx) -> None:
    """
    Add the custom directives to Sphinx.
    """
    app.add_config_value('substitutions', [], 'html')
    app.add_directive('substitution-prompt', SubstitutionPrompt)
    app.add_directive('substitution-code-block', SubstitutionCodeBlock)
    app.add_role('substitution-code', substitution_code_role)
