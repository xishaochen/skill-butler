#!/usr/bin/env python3
"""
show_pyramid.py - 按金字塔层级展示技能列表
"""

import json
from pathlib import Path
from collections import defaultdict

SKILL_USAGE_FILE = Path.home() / ".claude" / "skill-usage.json"

# 生命周期图标
LIFECYCLE_ICONS = {
    "需求萌芽期": "🟡",
    "成熟稳定期": "🟢",
    "上线迭代期": "🔵",
    "下线归档期": "🔴",
}


def load_data():
    with open(SKILL_USAGE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def show_pyramid():
    data = load_data()
    skills = data.get("skills", {})

    # 按层级分组
    by_level = defaultdict(list)
    for name, info in skills.items():
        level = info.get("level", "L1-公共技能")
        by_level[level].append((name, info))

    # 展示金字塔
    print("\n# 技能金字塔\n")
    print("```")
    print("        ▲")
    print("       /|\\        L3-高阶决策技能")
    print("      / | \\")
    print("     /  |  \\")
    print("    /───┼───\\     L2-领域核心技能")
    print("   /    │    \\")
    print("  /     │     \\")
    print(" /──────┼──────\\  L1-公共技能")
    print("/       │       \\")
    print("```\n")

    # L3
    print("## L3-高阶决策技能\n")
    for name, info in sorted(by_level.get("L3-高阶决策技能", [])):
        icon = LIFECYCLE_ICONS.get(info.get("lifecycle"), "⚪")
        print(f"- {icon} **{name}**")

    # L2 按子分类
    l2_skills = {k: v for k, v in by_level.items() if k.startswith("L2-")}
    for level in sorted(l2_skills.keys()):
        subcategory = level.split("/")[-1] if "/" in level else level
        print(f"\n### {subcategory}\n")
        for name, info in sorted(l2_skills[level]):
            icon = LIFECYCLE_ICONS.get(info.get("lifecycle"), "⚪")
            print(f"- {icon} **{name}**")

    # L1
    print("\n## L1-公共技能\n")
    for name, info in sorted(by_level.get("L1-公共技能", [])):
        icon = LIFECYCLE_ICONS.get(info.get("lifecycle"), "⚪")
        print(f"- {icon} **{name}**")

    # 统计
    print(f"\n---\n")
    print(f"**总计**: {len(skills)} 个技能")
    print(f"- L3: {len(by_level.get('L3-高阶决策技能', []))}")
    print(f"- L2: {sum(len(v) for k, v in by_level.items() if k.startswith('L2-'))}")
    print(f"- L1: {len(by_level.get('L1-公共技能', []))}")
    print(f"- 🔴 已归档: {sum(1 for s in skills.values() if s.get('lifecycle') == '下线归档期')}")


if __name__ == "__main__":
    show_pyramid()
