"""
Interactive File Selector using fzf

Features:
- Select files with fzf for interactive organization
- Multi-select support
- Preview functionality
- Custom formatting
"""

import os
import subprocess
from typing import Dict, List, Optional, Tuple


class InteractiveSelector:
    """Interactive file selector using fzf"""

    def __init__(self):
        """Initialize selector"""
        self.fzf_available = self._check_fzf()

    def _check_fzf(self) -> bool:
        """Check if fzf is available"""
        try:
            subprocess.run(["which", "fzf"], capture_output=True, timeout=5)
            return True
        except Exception:
            return False

    def select_files(
        self,
        files: List[str],
        prompt: str = "Select files > ",
        multi: bool = True,
        preview: Optional[str] = None,
        format_str: str = "{}",
    ) -> List[str]:
        """
        Select files using fzf

        Args:
            files: List of file paths to select from
            prompt: Prompt string
            multi: Allow multi-select
            preview: Preview command template
            format_str: Display format string

        Returns:
            List of selected file paths
        """
        if not self.fzf_available:
            print("⚠️  fzf not installed. Install with: brew install fzf")
            return files

        try:
            # Prepare file list for fzf
            file_list = "\n".join(files)

            # Build fzf command
            cmd = ["fzf", "--prompt=" + prompt, "--tiebreak=index"]

            if multi:
                cmd.append("--multi")

            if preview:
                cmd.extend(["--preview", preview])
                cmd.extend(["--preview-window=right:60%"])

            cmd.extend(["--header", f"{len(files)} files available"])

            # Run fzf
            result = subprocess.run(
                cmd,
                input=file_list,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0 and result.stdout:
                selected = result.stdout.strip().split("\n")
                return [s for s in selected if s]
            return []

        except subprocess.TimeoutExpired:
            print("⚠️  fzf timed out")
            return []
        except Exception as e:
            print(f"⚠️  fzf error: {e}")
            return files

    def select_destinations(
        self,
        current_path: str,
        suggestions: List[str],
    ) -> Tuple[str, str]:
        """
        Interactive destination selection

        Args:
            current_path: Current file path
            suggestions: Suggested destination paths

        Returns:
            Tuple of (selected_path, custom_input)
        """
        if not self.fzf_available:
            return suggestions[0] if suggestions else current_path, ""

        try:
            options = suggestions + ["[Custom path]"]
            options_str = "\n".join(options)

            cmd = [
                "fzf",
                "--prompt=Select destination > ",
                "--header=Choose where to move the file",
            ]

            result = subprocess.run(
                cmd,
                input=options_str,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                selected = result.stdout.strip()
                if selected == "[Custom path]":
                    return current_path, "custom"
                return selected, ""

            return current_path, ""

        except Exception as e:
            print(f"⚠️  Selection error: {e}")
            return current_path, ""

    def confirm_action(
        self,
        action: str,
        count: int,
        details: Optional[str] = None,
    ) -> bool:
        """
        Interactive action confirmation

        Args:
            action: Action description (move, delete, etc.)
            count: Number of files
            details: Optional details string

        Returns:
            True if confirmed
        """
        if not self.fzf_available:
            response = input(f"\n{action} {count} files? [y/N]: ")
            return response.lower() in ["y", "yes"]

        try:
            msg = f"{action} {count} files"
            if details:
                msg += f"\n{details}"

            cmd = [
                "fzf",
                "--prompt=Confirm action > ",
                "--header=" + msg,
                "--print-query",
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                query = result.stdout.strip().lower()
                return query in ["y", "yes", ""]
            return False

        except Exception:
            return False

    def interactive_organize(
        self,
        files: List[Dict],
        suggestions: Dict[str, str],
    ) -> Dict[str, str]:
        """
        Interactive organization workflow

        Args:
            files: List of file dictionaries with path and info
            suggestions: Dict mapping file path to suggested destination

        Returns:
            Dict of file -> destination
        """
        if not self.fzf_available:
            print("⚠️  fzf not installed. Using automatic organization.")
            return suggestions

        result = {}
        processed = set()

        for file_info in files:
            path = file_info.get("path", "")
            if path in processed:
                continue

            filename = os.path.basename(path)
            current_dest = suggestions.get(path, "Skip")

            options = [
                current_dest,
                "Skip",
                "[Select different]",
                "[Delete]",
            ]

            options_str = "\n".join(options)

            try:
                cmd = [
                    "fzf",
                    "--prompt=" + filename + " > ",
                    "--header=Current: " + current_dest,
                ]

                proc = subprocess.run(
                    cmd,
                    input=options_str,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if proc.returncode == 0:
                    choice = proc.stdout.strip()
                    if choice == "Skip":
                        processed.add(path)
                    elif choice == "[Select different]":
                        result[path] = current_dest
                    elif choice == "[Delete]":
                        result[path] = "__DELETE__"
                        processed.add(path)
                    else:
                        result[path] = choice
                        processed.add(path)

            except Exception as e:
                print(f"⚠️  Error processing {filename}: {e}")
                result[path] = current_dest
                processed.add(path)

        return result


def interactive_select(files: List[str]) -> List[str]:
    """Quick file selection"""
    selector = InteractiveSelector()
    return selector.select_files(files)
