# commitdev/pipeline/context.py

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import websockets
from rich.console import Console

from .console import console as shared_console


@dataclass
class PipelineContext:
    """
    Shared runtime state for one publishing session.

    Every pipeline module receives this object.
    """

    # =====================================================
    # Shared Services
    # =====================================================

    console: Console = field(default_factory=lambda: shared_console)

    # =====================================================
    # WebSocket
    # =====================================================

    ws: websockets.WebSocketClientProtocol | None = None

    # =====================================================
    # Draft Information
    # =====================================================

    post_id: int | None = None
    repository: str = ""
    commit_message: str = ""

    # platform -> draft content
    posts_by_platform: Dict[str, str] = field(default_factory=dict)

    # Enabled publishing platforms
    staged_platforms: List[str] = field(default_factory=list)

    # Currently selected platform
    current_platform: Optional[str] = None

    # =====================================================
    # Media
    # =====================================================

    attached_images: List[Path | str] = field(default_factory=list)

    # =====================================================
    # Runtime
    # =====================================================

    running: bool = True

    last_server_payload: Dict = field(default_factory=dict)

    metadata: Dict = field(default_factory=dict)

    # =====================================================
    # Helpers
    # =====================================================

    def get_content(self, platform: str) -> str:
        return self.posts_by_platform.get(platform.lower(), "")

    def set_content(self, platform: str, content: str) -> None:
        self.posts_by_platform[platform.lower()] = content

    def enable_platform(self, platform: str) -> None:
        platform = platform.capitalize()
        if platform not in self.staged_platforms:
            self.staged_platforms.append(platform)

    def disable_platform(self, platform: str) -> None:
        platform = platform.capitalize()
        if platform in self.staged_platforms:
            self.staged_platforms.remove(platform)

    def add_image(self, image: Path | str) -> None:
        self.attached_images.append(image)

    def clear_images(self) -> None:
        self.attached_images.clear()

    @property
    def image_count(self) -> int:
        return len(self.attached_images)
