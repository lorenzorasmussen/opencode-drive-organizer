"""
Tool Integration for fd, fzf, ripgrep, nnn
"""

import os
import subprocess
import time
from typing import Dict, List, Optional
from datetime import datetime


class ToolIntegration:
    """
    Integration with terminal tools: fd, fzf, ripgrep, nnn

    Features:
    - Execute fd commands for fast file search
    - Execute fzf for interactive selection
    - Execute ripgrep for fast content search
    - Execute nnn for file navigation
    - Tool availability checking
    - Execution statistics tracking
    - Timeout handling
    """

    def __init__(self, timeout: int = 30):
        """
        Initialize tool integration

        Args:
            timeout: Default timeout for tool execution in seconds
        """
        self.timeout = timeout
        self.execution_stats = {
            "total_executions": 0,
            "tool_counts": {},
            "successful_executions": 0,
            "failed_executions": 0,
        }

    def check_tool_available(self, tool_name: str) -> bool:
        """
        Check if a tool is available

        Args:
            tool_name: Name of the tool (fd, fzf, ripgrep, nnn)

        Returns:
            True if tool is available, False otherwise
        """
        try:
            result = subprocess.run(
                ["which", tool_name], capture_output=True, timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def execute_tool(
        self, tool_name: str, args: List[str], timeout: Optional[int] = None
    ) -> Optional[List[str]]:
        """
        Execute a tool command

        Args:
            tool_name: Name of the tool to execute
            args: Command arguments
            timeout: Timeout in seconds (uses default if not specified)

        Returns:
            List of output lines, or None if execution failed
        """
        timeout = timeout or self.timeout

        try:
            self.execution_stats["total_executions"] += 1

            if tool_name not in self.execution_stats["tool_counts"]:
                self.execution_stats["tool_counts"][tool_name] = 0
            self.execution_stats["tool_counts"][tool_name] += 1

            result = subprocess.run(
                [tool_name] + args, capture_output=True, text=True, timeout=timeout
            )

            if result.returncode == 0:
                self.execution_stats["successful_executions"] += 1
                output = result.stdout.strip().split("\n")
                return output if output != [""] else []
            else:
                self.execution_stats["failed_executions"] += 1
                return None

        except subprocess.TimeoutExpired:
            self.execution_stats["failed_executions"] += 1
            print(f"⚠️  Tool {tool_name} timed out after {timeout}s")
            return None
        except Exception as e:
            self.execution_stats["failed_executions"] += 1
            print(f"⚠️  Error executing {tool_name}: {e}")
            return None

    def fd_search(
        self,
        directory: str,
        pattern: Optional[str] = None,
        extension: Optional[str] = None,
        hidden: bool = False,
    ) -> List[str]:
        """
        Search files using fd

        Args:
            directory: Directory to search in
            pattern: Search pattern (optional)
            extension: Filter by file extension (e.g., 'txt', 'py')
            hidden: Include hidden files

        Returns:
            List of matching file paths
        """
        args = []

        # Use '.' as default pattern (match all)
        if pattern:
            args.append(pattern)
        else:
            args.append(".")

        if extension:
            args.extend(["-e", extension])

        if hidden:
            args.append("--hidden")

        # Always use absolute paths
        args.append("-a")

        # Directory is always the last argument
        args.append(directory)

        return self.execute_tool("fd", args) or []

    def fzf_select(
        self, items: List[str], prompt: str = "> ", multi: bool = False
    ) -> Optional[List[str]]:
        """
        Interactive selection using fzf

        Args:
            items: List of items to select from
            prompt: Prompt string
            multi: Allow multiple selections

        Returns:
            Selected item(s), or None if cancelled
        """
        args = ["--prompt", prompt]

        if multi:
            args.append("--multi")

        try:
            input_text = "\n".join(items)
            result = subprocess.run(
                ["fzf"] + args,
                input=input_text,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            if result.returncode == 0:
                output = result.stdout.strip()
                if multi:
                    return output.split("\n") if output else []
                else:
                    return [output] if output else None
            else:
                return None

        except Exception as e:
            print(f"⚠️  Error with fzf: {e}")
            return None

    def ripgrep_search(
        self,
        directory: str,
        pattern: str,
        extensions: Optional[List[str]] = None,
        case_sensitive: bool = True,
    ) -> List[str]:
        """
        Search file contents using ripgrep

        Args:
            directory: Directory to search in
            pattern: Search pattern (supports regex)
            extensions: Filter by file extensions
            case_sensitive: Whether search is case sensitive

        Returns:
            List of matching lines with file paths
        """
        args = [pattern, directory]

        # ripgrep uses 'rg' as binary name
        tool_name = "rg"

        if not case_sensitive:
            args.append("-i")

        if extensions:
            args.extend(["-g", f"*.{','.join(extensions)}"])

        return self.execute_tool(tool_name, args) or []

    def nnn_navigate(self, directory: str) -> bool:
        """
        Navigate files using nnn (interactive)

        Args:
            directory: Starting directory

        Returns:
            True if navigation completed, False if cancelled
        """
        args = [directory]

        try:
            result = subprocess.run(
                ["nnn"] + args,
                timeout=None,  # No timeout for interactive navigation
            )
            return result.returncode == 0
        except Exception as e:
            print(f"⚠️  Error with nnn: {e}")
            return False

    def get_execution_stats(self) -> Dict:
        """
        Get tool execution statistics

        Returns:
            Dictionary with execution statistics
        """
        return self.execution_stats

    def reset_stats(self):
        """Reset execution statistics"""
        self.execution_stats = {
            "total_executions": 0,
            "tool_counts": {},
            "successful_executions": 0,
            "failed_executions": 0,
        }

    def batch_fd_search(
        self, directories: List[str], pattern: Optional[str] = None
    ) -> Dict[str, List[str]]:
        """
        Search multiple directories using fd

        Args:
            directories: List of directories to search
            pattern: Search pattern (optional)

        Returns:
            Dictionary mapping directories to search results
        """
        results = {}

        for directory in directories:
            if os.path.isdir(directory):
                results[directory] = self.fd_search(directory, pattern)
            else:
                results[directory] = []

        return results

    def get_tool_info(self, tool_name: str) -> Optional[Dict]:
        """
        Get information about a tool

        Args:
            tool_name: Name of the tool

        Returns:
            Dictionary with tool information, or None if not available
        """
        if not self.check_tool_available(tool_name):
            return None

        try:
            result = subprocess.run(
                [tool_name, "--version"], capture_output=True, text=True, timeout=5
            )

            return {
                "name": tool_name,
                "available": True,
                "version": result.stdout.strip()
                if result.returncode == 0
                else "unknown",
                "checked_at": datetime.now().isoformat(),
            }
        except Exception:
            return {
                "name": tool_name,
                "available": True,
                "version": "unknown",
                "error": "Could not determine version",
            }
