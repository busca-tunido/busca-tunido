import os
import shutil
import subprocess
from typing import Any, Dict, List, Optional, Union
from crewai import BaseLLM

class AgyLLM(BaseLLM):
    def __init__(
        self,
        model: str = "gemini-3.8-flash-high",
        temperature: Optional[float] = None,
        effort: str = "high",
    ) -> None:
        model_name = os.getenv("AGY_MODEL", model)
        super().__init__(model=model_name, temperature=temperature)
        self.effort = os.getenv("AGY_EFFORT", effort)
        self._bin = shutil.which("agy.exe") or shutil.which("agy") or "agy.exe"

    def call(
        self,
        messages: Union[str, List[Dict[str, str]], List[Any]],
        tools: Optional[List[dict]] = None,
        callbacks: Optional[List[Any]] = None,
        available_functions: Optional[Dict[str, Any]] = None,
        from_task: Any = None,
        from_agent: Any = None,
        response_model: Any = None,
    ) -> Union[str, Any]:
        if isinstance(messages, str):
            prompt = messages
        elif isinstance(messages, list):
            formatted_parts: list[str] = []
            for m in messages:
                if isinstance(m, dict):
                    role = m.get("role", "user")
                    content = m.get("content", "")
                else:
                    role = getattr(m, "role", "user")
                    content = getattr(m, "content", str(m))
                formatted_parts.append(f"[{role.upper()}]:\n{content}")
            prompt = "\n\n".join(formatted_parts)
        else:
            prompt = str(messages)

        cmd = [
            self._bin,
            "--model",
            self.model,
            "-p",
            prompt,
            "--output-format",
            "text",
            "--dangerously-skip-permissions",
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        if result.returncode != 0:
            error_output = result.stderr.strip() or result.stdout.strip()
            raise RuntimeError(
                f"AgyLLM execution failed with exit code {result.returncode}: {error_output}"
            )

        return result.stdout.strip()

    def supports_function_calling(self) -> bool:
        return False

    def get_context_window_size(self) -> int:
        return 1048576
