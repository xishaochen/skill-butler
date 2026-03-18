#!/usr/bin/env python3
"""
record_invocation.py - 记录技能调用

功能：
1. 记录技能调用次数
2. 更新最后调用时间
3. 检查是否需要状态流转
"""

import json
import sys
from datetime import datetime
from pathlib import Path

SKILL_USAGE_FILE = Path.home() / ".claude" / "skill-usage.json"


def load_skill_usage() -> dict:
    """加载技能使用数据"""
    if SKILL_USAGE_FILE.exists():
        with open(SKILL_USAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"version": "1.0", "skills": {}, "pending_skills": []}


def save_skill_usage(data: dict) -> None:
    """保存技能使用数据"""
    with open(SKILL_USAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def check_lifecycle_transition(skill: dict) -> tuple[str, bool]:
    """
    检查是否需要生命周期状态流转
    返回: (目标状态, 是否需要变更)
    """
    current_lifecycle = skill.get("lifecycle", "需求萌芽期")
    invocation_count = skill.get("invocation_count", 0)
    pushed = skill.get("pushed", False)

    # 需求萌芽期 → 成熟稳定期
    if current_lifecycle == "需求萌芽期" and invocation_count >= 1:
        return "成熟稳定期", True

    # 成熟稳定期 → 上线迭代期
    if current_lifecycle == "成熟稳定期" and (pushed or invocation_count >= 5):
        return "上线迭代期", True

    # 上线迭代期 → 下线归档期
    if current_lifecycle == "上线迭代期":
        last_invoked = skill.get("last_invoked")
        user_marked = skill.get("user_marked_deprecated", False)

        if user_marked:
            return "下线归档期", True

        if last_invoked:
            last_date = datetime.fromisoformat(last_invoked)
            days_since = (datetime.now() - last_date).days
            if days_since > 90:
                return "下线归档期", True

    return current_lifecycle, False


def record_invocation(skill_name: str) -> dict:
    """记录技能调用"""
    data = load_skill_usage()
    skills = data.get("skills", {})

    if skill_name not in skills:
        return {
            "success": False,
            "error": f"技能 '{skill_name}' 不存在",
            "hint": "请先运行 scan_skills.py 扫描技能"
        }

    skill = skills[skill_name]

    # 更新调用数据
    skill["invocation_count"] = skill.get("invocation_count", 0) + 1
    skill["last_invoked"] = datetime.now().isoformat()

    # 检查生命周期状态
    old_lifecycle = skill.get("lifecycle", "需求萌芽期")
    new_lifecycle, needs_transition = check_lifecycle_transition(skill)

    if needs_transition:
        skill["lifecycle"] = new_lifecycle
        skill["lifecycle_changed_at"] = datetime.now().isoformat()

    skills[skill_name] = skill
    data["skills"] = skills
    save_skill_usage(data)

    result = {
        "success": True,
        "skill": skill_name,
        "invocation_count": skill["invocation_count"],
        "lifecycle": skill["lifecycle"],
        "lifecycle_changed": needs_transition
    }

    if needs_transition:
        result["old_lifecycle"] = old_lifecycle
        result["new_lifecycle"] = new_lifecycle

    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python record_invocation.py <skill_name>")
        sys.exit(1)

    skill_name = sys.argv[1]
    result = record_invocation(skill_name)
    print(json.dumps(result, ensure_ascii=False, indent=2))
