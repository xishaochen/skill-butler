#!/usr/bin/env python3
"""
check_lifecycle.py - 检查生命周期状态变更

功能：
1. 扫描所有技能
2. 检查是否需要状态变更
3. 输出变更建议列表
"""

import json
from datetime import datetime
from pathlib import Path

SKILL_USAGE_FILE = Path.home() / ".claude" / "skill-usage.json"


def load_skill_usage() -> dict:
    """加载技能使用数据"""
    if SKILL_USAGE_FILE.exists():
        with open(SKILL_USAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"version": "1.0", "skills": {}, "pending_skills": []}


def check_lifecycle_transition(skill: dict) -> tuple[str, bool, str]:
    """
    检查是否需要生命周期状态流转
    返回: (目标状态, 是否需要变更, 原因)
    """
    current_lifecycle = skill.get("lifecycle", "需求萌芽期")
    invocation_count = skill.get("invocation_count", 0)
    pushed = skill.get("pushed", False)
    name = skill.get("name", "unknown")

    # 需求萌芽期 → 成熟稳定期
    if current_lifecycle == "需求萌芽期":
        if invocation_count >= 1:
            return "成熟稳定期", True, f"已调用 {invocation_count} 次"

    # 成熟稳定期 → 上线迭代期
    if current_lifecycle == "成熟稳定期":
        if pushed:
            return "上线迭代期", True, "已推送到 GitHub"
        if invocation_count >= 5:
            return "上线迭代期", True, f"已调用 {invocation_count} 次"

    # 上线迭代期 → 下线归档期
    if current_lifecycle == "上线迭代期":
        last_invoked = skill.get("last_invoked")
        user_marked = skill.get("user_marked_deprecated", False)

        if user_marked:
            return "下线归档期", True, "用户手动标记"

        if last_invoked:
            last_date = datetime.fromisoformat(last_invoked)
            days_since = (datetime.now() - last_date).days
            if days_since > 90:
                return "下线归档期", True, f"{days_since} 天未调用"

    return current_lifecycle, False, ""


def check_all_lifecycles() -> dict:
    """检查所有技能的生命周期状态"""
    data = load_skill_usage()
    skills = data.get("skills", {})

    transitions = []
    warnings = []
    healthy = []

    for name, skill in skills.items():
        current = skill.get("lifecycle", "需求萌芽期")
        target, needs_transition, reason = check_lifecycle_transition(skill)

        if needs_transition:
            transitions.append({
                "name": name,
                "current": current,
                "target": target,
                "reason": reason
            })
        elif current == "需求萌芽期":
            warnings.append({
                "name": name,
                "lifecycle": current,
                "invocation_count": skill.get("invocation_count", 0),
                "suggestion": "考虑试用或删除"
            })
        elif current == "上线迭代期":
            last_invoked = skill.get("last_invoked")
            if last_invoked:
                last_date = datetime.fromisoformat(last_invoked)
                days_since = (datetime.now() - last_date).days
                if days_since > 60:
                    warnings.append({
                        "name": name,
                        "lifecycle": current,
                        "days_since_invoked": days_since,
                        "suggestion": f"{days_since} 天未调用，关注使用情况"
                    })

    # 统计健康状态
    healthy_count = len(skills) - len(transitions) - len(warnings)
    if healthy_count > 0:
        healthy.append({"count": healthy_count, "status": "状态正常"})

    return {
        "total_skills": len(skills),
        "transitions": transitions,
        "warnings": warnings,
        "healthy": healthy
    }


def print_report(report: dict) -> None:
    """打印检查报告"""
    print("\n📊 生命周期检查报告")
    print("=" * 50)
    print(f"总技能数: {report['total_skills']}")

    if report["transitions"]:
        print("\n🔄 需要状态变更:")
        for t in report["transitions"]:
            print(f"  📌 {t['name']}")
            print(f"     {t['current']} → {t['target']}")
            print(f"     原因: {t['reason']}")

    if report["warnings"]:
        print("\n⚠️ 需要关注:")
        for w in report["warnings"]:
            msg = f"  📌 {w['name']} - {w['suggestion']}"
            print(msg)

    if report["healthy"]:
        print("\n✅ 状态良好:")
        for h in report["healthy"]:
            print(f"  {h['count']} 个技能 {h['status']}")


if __name__ == "__main__":
    report = check_all_lifecycles()
    print_report(report)
