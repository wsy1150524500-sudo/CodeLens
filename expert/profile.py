"""专家配置加载：从 expert_profile.yaml 读取专家人设和知识库配置。"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List, Optional

import yaml

_PROFILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "expert_profile.yaml")
_profile_cache: Optional["ExpertProfile"] = None


@dataclass
class ExpertProfile:
    name: str
    version: str
    persona: str
    knowledge_base_dir: str
    knowledge_files: List[str] = field(default_factory=list)

    def get_knowledge_paths(self) -> List[str]:
        """返回所有知识库文件的绝对路径。"""
        base = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            self.knowledge_base_dir,
        )
        return [os.path.join(base, f) for f in self.knowledge_files]


def load_profile() -> ExpertProfile:
    """加载专家配置（带缓存）。"""
    global _profile_cache
    if _profile_cache is not None:
        return _profile_cache

    with open(_PROFILE_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    _profile_cache = ExpertProfile(
        name=data["name"],
        version=data.get("version", "1.0.0"),
        persona=data["persona"],
        knowledge_base_dir=data.get("knowledge_base_dir", "knowledge_base"),
        knowledge_files=data.get("knowledge_files", []),
    )
    return _profile_cache
