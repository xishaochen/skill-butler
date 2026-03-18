#!/usr/bin/env python3
"""
skill_overview.py - 技能总览展示

功能：
1. 读取 skill-usage.json
2. 按金字塔层级展示技能
3. 显示生命周期状态
"""

import json
from pathlib import Path
from typing import Dict, List, Any

SKILL_USAGE_FILE = Path.home() / ".claude" / "skill-usage.json"

# 生命周期图标
LIFECYCLE_ICONS = {
    "需求萌芽期": "🟡",
    "成熟稳定期": "🟢",
    "上线迭代期": "🔵",
    "下线归档期": "🔴"
}


def load_skill_usage() -> Dict[str, Any]:
    """加载技能使用数据"""
    if SKILL_USAGE_FILE.exists():
        with open(SKILL_USAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"version": "1.0", "skills": {}, "pending_skills": []}


def group_skills_by_level(skills: Dict[str, Any]) -> Dict[str, List[Dict]]:
    """按层级分组技能"""
    grouped = {}

    for name, skill in skills.items():
        level = skill.get("level", "L1-公共技能")

        # 解析层级
        if level.startswith("L3"):
            group = "L3-高阶决策技能"
        elif level.startswith("L2"):
            # L2-领域核心技能/子分类
            parts = level.split("/")
            if len(parts) >= 2:
                group = level
            else:
                group = "L2-领域核心技能/其他"
        else:
            group = "L1-公共技能"

        if group not in grouped:
            grouped[group] = []
        grouped[group].append(skill)

    return grouped


def print_overview() -> None:
    """打印技能总览"""
    data = load_skill_usage()
    skills = data.get("skills", {})

    grouped = group_skills_by_level(skills)

    print(f"\n📊 技能总览 (共 {len(skills)} 个技能)")
    print("=" * 60)

    for level, skills_list in grouped.items():
        # 获取层级图标
        if "L3" in level:
            icon = "🔴"
        elif "L2" in level:
            icon = "🟢"
        else:
            icon = "🟡"

        print(f"\n{icon} {level} ({len(skills_list)})")

        for skill in skills_list:
            lifecycle = skill.get("lifecycle", "需求萌芽期")
            icon = LIFECYCLE_ICONS.get(lifecycle, "⚪")

            invocation = skill.get("invocation_count", 0)

            pushed = "✓" if skill.get("pushed") else ""
            print(f"├── {skill['name']:<20} [{lifecycle}] {icon} 调用: {invocation}次 {pushed}")

    print()


if __name__ == "__main__":
    print_overview()
