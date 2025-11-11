# -*- coding: utf-8 -*-
#  Copyright (c) 2022 Jonah Lawrence
#  Copyright (c) 2024 Manuel Schneider

import re
import unicodedata
from pathlib import Path
from pylatexenc.latex2text import LatexNodes2Text

from albert import *

md_iid = "5.0"
md_version = "2.1.1"
md_name = "TeX to Unicode"
md_description = "Convert TeX mathmode commands to unicode characters"
md_license = "MIT"
md_url = "https://github.com/albertlauncher/albert-plugin-python-tex-to-unicode"
md_authors = ["@DenverCoder1", "@ManuelSchneid3r", "@tyilo", "@BarrensZeppelin"]
md_maintainers = ["@DenverCoder1", "@BarrensZeppelin"]
md_lib_dependencies = ["pylatexenc"]


class Plugin(PluginInstance, GeneratorQueryHandler):

    icon_path = Path(__file__).parent / "tex.svg"

    def __init__(self):
        PluginInstance.__init__(self)
        GeneratorQueryHandler.__init__(self)
        self.COMBINING_LONG_SOLIDUS_OVERLAY = "\u0338"

    def _create_item(self, text: str, subtext: str, can_copy: bool):
        actions = []
        if can_copy:
            actions.append(
                Action(
                    "copy",
                    "Copy result to clipboard",
                    lambda t=text: setClipboardText(t),
                )
            )
        return StandardItem(
            id=self.id(),
            text=text,
            subtext=subtext,
            icon_factory=lambda: makeImageIcon(Plugin.icon_path),
            actions=actions,
        )

    def defaultTrigger(self):
        return "tex "

    def items(self, ctx):
        query = ctx.query.strip()

        if not query:
            return

        if not query.startswith("\\"):
            query = "\\" + query

        # Remove double backslashes (newlines)
        query = query.replace("\\\\", " ")

        # pylatexenc doesn't support \not
        query = query.replace("\\not", "@NOT@")

        n = LatexNodes2Text()
        result = n.latex_to_text(query)

        if not result:
            yield [self._create_item(query, "Type some TeX math", False)]
            return

        # success
        result = unicodedata.normalize("NFC", result)
        result = re.sub(r"@NOT@\s*(\S)", "\\1" + self.COMBINING_LONG_SOLIDUS_OVERLAY, result)
        result = result.replace("@NOT@", "")
        result = unicodedata.normalize("NFC", result)
        yield [self._create_item(result, "Result", True)]
