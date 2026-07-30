# commitdev/pipeline/editor.py

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from rich.console import Console

console = Console()


class Editor:
    """
    Handles editing text inside the user's preferred terminal editor.
    """

    def __init__(self):
        self.editor = os.environ.get("EDITOR", "nano")

    def edit(
        self,
        content: str,
        title: str = "CommitDev Edit Session",
    ) -> Optional[str]:
        """
        Opens the user's preferred editor and returns the edited text.
        """

        template = f"""\
# ---------------------------------------------------
# {title}
# ---------------------------------------------------
#
# Lines beginning with '#' are ignored.
# Save and close the editor to continue.
#
# ---------------------------------------------------

{content}
"""

        temp_path = None

        try:
            with tempfile.NamedTemporaryFile(
                suffix=".txt",
                mode="w",
                delete=False,
                encoding="utf-8",
            ) as tmp:
                tmp.write(template)
                temp_path = Path(tmp.name)

            console.print(
                f"[meta]Opening editor:[/meta] [white]{self.editor}[/white]"
            )

            self._launch_editor(temp_path)

            edited = temp_path.read_text(encoding="utf-8")

            return self._strip_comments(edited).strip()

        except Exception as exc:
            console.print(
                f"[yellow]Editor error:[/yellow] {exc}"
            )
            return None

        finally:
            if temp_path and temp_path.exists():
                temp_path.unlink(missing_ok=True)

    def _launch_editor(self, file_path: Path):
        """
        Launch the configured editor.
        """

        commands = {
            "code": ["code", "--wait", str(file_path)],
            "nano": ["nano", "-$", str(file_path)],
            "vim": ["vim", "+set", "wrap", str(file_path)],
        }

        command = commands.get(
            self.editor,
            [self.editor, str(file_path)],
        )

        subprocess.run(command, check=True)

    @staticmethod
    def _strip_comments(text: str) -> str:
        """
        Removes helper comments before returning content.
        """

        return "\n".join(
            line
            for line in text.splitlines()
            if not line.lstrip().startswith("#")
        )


# ---------------------------------------------------
# Shared editor instance
# ---------------------------------------------------

editor = Editor()


# ---------------------------------------------------
# Backward compatibility
# ---------------------------------------------------

def open_in_editor(
    initial_content: str,
    title: str = "CommitDev Edit Session",
) -> Optional[str]:
    """
    Compatibility wrapper for older code.

    Old:
        open_in_editor(text)

    New:
        editor.edit(text)
    """

    return editor.edit(initial_content, title)