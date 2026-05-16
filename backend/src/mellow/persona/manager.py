"""角色管理器 —— 预设角色 + 自定义角色 CRUD。

角色记忆独立存储，学习档案跨角色共享。
"""

import json
import uuid
from collections import defaultdict
from pathlib import Path
from typing import Any

from mellow.config import Settings, get_settings
from mellow.models import LanguageStyle, Persona, TeachingStyle


class SafeDict(dict):
    """字典子类：缺失的键返回 {key} 占位符，而非抛出 KeyError。
    
    用于 str.format_map() 安全渲染包含未知变量的模板字符串。
    """
    def __missing__(self, key: str) -> str:
        return f"{{{key}}}"


class PersonaManager:
    """角色管理器。

    功能：
    - 加载预设角色 JSON 文件
    - 创建/读取/更新/删除自定义角色
    - 渲染角色的 system prompt
    """

    def __init__(self, settings: Settings | None = None):
        self._settings = settings or get_settings()
        self._preset_dir = Path(__file__).parent / "presets"
        self._custom_personas: dict[str, Persona] = {}

    # ---- 预设角色 ----

    def list_presets(self) -> list[Persona]:
        """列出所有预设角色。"""
        personas = []
        if self._preset_dir.exists():
            for f in sorted(self._preset_dir.glob("*.json")):
                p = self._load_preset(f)
                if p:
                    personas.append(p)
        return personas

    def get_preset(self, name: str) -> Persona | None:
        """根据名称获取预设角色。"""
        path = self._preset_dir / f"{name}.json"
        if path.exists():
            return self._load_preset(path)
        return None

    def _load_preset(self, path: Path) -> Persona | None:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            data["id"] = f"preset_{path.stem}"
            data["is_preset"] = True
            if "language_style" in data and isinstance(data["language_style"], dict):
                data["language_style"] = LanguageStyle(**data["language_style"])
            if "teaching_style" in data and isinstance(data["teaching_style"], dict):
                data["teaching_style"] = TeachingStyle(**data["teaching_style"])
            return Persona(**data)
        except (json.JSONDecodeError, TypeError):
            return None

    # ---- 自定义角色 ----

    def create_custom(self, data: dict[str, Any]) -> Persona:
        """创建自定义角色。"""
        persona_id = str(uuid.uuid4())[:8]
        persona = Persona(
            id=f"custom_{persona_id}",
            name=data.get("name", "Custom"),
            role=data.get("role", "buddy"),
            is_preset=False,
            created_by=data.get("created_by"),
            **{k: v for k, v in data.items()
               if k not in ("id", "name", "role", "is_preset", "created_by")},
        )
        self._custom_personas[persona.id] = persona
        return persona

    def list_custom(self, user_id: str | None = None) -> list[Persona]:
        """列出自定义角色。"""
        personas = list(self._custom_personas.values())
        if user_id:
            personas = [p for p in personas if p.created_by == user_id]
        return personas

    def get_persona(self, persona_id: str) -> Persona | None:
        """获取任意角色（预设或自定义）。"""
        if persona_id.startswith("preset_"):
            name = persona_id.replace("preset_", "")
            return self.get_preset(name)
        return self._custom_personas.get(persona_id)

    def update_custom(self, persona_id: str, data: dict[str, Any]) -> Persona | None:
        """更新自定义角色。"""
        existing = self._custom_personas.get(persona_id)
        if not existing:
            return None
        updated_data = existing.model_dump()
        updated_data.update({k: v for k, v in data.items() if v is not None})
        updated = Persona(**updated_data)
        self._custom_personas[persona_id] = updated
        return updated

    def delete_custom(self, persona_id: str) -> bool:
        """删除自定义角色。"""
        if persona_id in self._custom_personas:
            del self._custom_personas[persona_id]
            return True
        return False

    # ---- Prompt 渲染 ----

    def render_system_prompt(
        self,
        persona: Persona,
        user_name: str = "同学",
        profile_summary: str = "",
        memory_context: str = "",
    ) -> str:
        """渲染角色的完整 system prompt。

        使用 persona.system_prompt_template 中的 {变量} 进行填充。
        """
        template = persona.system_prompt_template
        if not template:
            # 使用默认模板
            template = self._default_template()

        safe_kwargs = SafeDict(
            name=persona.name,
            role=persona.role,
            user_name=user_name,
            personality=persona.language_style.tone,
            language_style=", ".join(persona.language_style.traits),
            teaching_style=persona.teaching_style.approach,
            intimacy=persona.intimacy_level,
            correction_frequency=persona.teaching_style.correction_frequency,
            profile_summary=profile_summary or "新用户",
            memory_context=memory_context or "无历史记录",
        )
        return template.format_map(safe_kwargs)

    def _default_template(self) -> str:
        return """你是一个名为 {name} 的{role}，正在帮助 {user_name} 学习英语。

## 你的性格
{personality}

## 语言风格
{language_style}

## 教学风格
{teaching_style}
纠错频率: {correction_frequency}

## 当前用户情况
{profile_summary}

## 关系记忆
{memory_context}

## 规则
1. 始终用你设定的性格和语言风格回复
2. 适当纠正英语错误，但不要过度
3. 保持自然对话
4. 关注用户情绪，适时关心
5. 回复以中文为主，英语教学部分用英文"""
