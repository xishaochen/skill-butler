#!/usr/bin/env python3
"""
health_report.py - 生成技能健康报告

功能：
1. 扫描所有技能状态
2. 生成健康报告
3. 提供优化建议
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

SKILL_USAGE_FILE = Path.home() / ".claude" / "skill-usage.json"


def load_skill_usage() -> Dict[str, Any]:
    """加载技能使用数据"""
    if SKILL_USAGE_FILE.exists():
        with open(SKILL_USAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"version": "1.0", "skills": {}, "pending_skills": []}


def generate_health_report() -> Dict[str, Any]:
    """生成健康报告"""
    data = load_skill_usage()
    skills = data.get("skills", {})

    report = {
        "generated_at": datetime.now().isoformat(),
        "total_skills": len(skills),
        "summary": {},
        "attention_needed": [],
        "suggestions": [],
        "healthy_skills": [],
        "statistics": {}
    }

    # 统计各状态技能数量
    lifecycle_counts = {}
    level_counts = {}
    source_counts = {}

    attention_items = []
    healthy_count = 0

    for name, skill in skills.items():
        # 生命周期统计
        lifecycle = skill.get("lifecycle", "需求萌芽期")
        lifecycle_counts[lifecycle] = lifecycle_counts.get(lifecycle, 0) + 1

        # 层级统计
        level = skill.get("level", "L1-公共技能")
        level_counts[level] = level_counts.get(level, 0) + 1

        # 来源统计
        source = skill.get("source_type", "local")
        source_counts[source] = source_counts.get(source, 0) + 1

        # 检查需要关注的技能
        issues = []
        invocation_count = skill.get("invocation_count", 0)
        last_invoked = skill.get("last_invoked")

        # 萌芽期未使用
        if lifecycle == "需求萌芽期" and invocation_count == 0:
            issues.append("从未使用，建议试用或删除")

        # 长期未调用
        if last_invoked:
            try:
                last_date = datetime.fromisoformat(last_invoked)
                days_since = (datetime.now() - last_date).days
                if days_since > 60:
                    issues.append(f"{days_since} 天未调用")
            except:
                pass

        # 检查是否需要推送
        if lifecycle == "成熟稳定期" and not skill.get("pushed"):
            issues.append("建议推送到 GitHub 固化")

        if issues:
            attention_items.append({
                "name": name,
                "lifecycle": lifecycle,
                "level": level,
                "issues": issues
            })
        else:
            healthy_count += 1
            if lifecycle in ["成熟稳定期", "上线迭代期"]:
                report["healthy_skills"].append(name)

    # 汇总统计
    report["statistics"] = {
        "lifecycle": lifecycle_counts,
        "level": level_counts,
        "source": source_counts
    }

    report["attention_needed"] = attention_items

    # 生成建议
    suggestions = []

    # 萌芽期过多
    budding_count = lifecycle_counts.get("需求萌芽期", 0)
    if budding_count > 10:
        suggestions.append(f"有 {budding_count} 个技能处于萌芽期，建议筛选保留有价值的")

    # 未推送的成熟技能
    mature_unpushed = [s for s in attention_items
                       if s["lifecycle"] == "成熟稳定期"
                       and any("推送" in i for i in s["issues"])]
    if mature_unpushed:
        suggestions.append(f"有 {len(mature_unpushed)} 个成熟技能可推送到 GitHub")

    # 长期未使用
    unused = [s for s in attention_items
              if any("未调用" in i for i in s["issues"])]
    if unused:
        suggestions.append(f"有 {len(unused)} 个技能长期未使用，考虑归档")

    # 健康度评估
    health_score = int((healthy_count / len(skills)) * 100) if skills else 0
    report["summary"] = {
        "health_score": health_score,
        "healthy_count": healthy_count,
        "attention_count": len(attention_items),
        "grade": "优秀" if health_score >= 80 else "良好" if health_score >= 60 else "需改进"
    }

    report["suggestions"] = suggestions

    return report


def print_report(report: Dict[str, Any]) -> None:
    """打印健康报告"""
    print("\n" + "=" * 60)
    print("📊 技能健康报告")
    print("=" * 60)
    print(f"📅 生成时间: {report['generated_at']}")
    print(f"📈 技能总数: {report['total_skills']}")

    # 健康度
    summary = report["summary"]
    print(f"\n🎯 健康度: {summary['health_score']}% ({summary['grade']})")
    print(f"   ✅ 健康: {summary['healthy_count']} | ⚠️ 关注: {summary['attention_count']}")

    # 生命周期分布
    print("\n📋 生命周期分布:")
    for lifecycle, count in report["statistics"]["lifecycle"].items():
        icon = {"需求萌芽期": "🟡", "成熟稳定期": "🟢", "上线迭代期": "🔵", "下线归档期": "🔴"}.get(lifecycle, "⚪")
        print(f"   {icon} {lifecycle}: {count}")

    # 层级分布
    print("\n📐 层级分布:")
    for level, count in sorted(report["statistics"]["level"].items()):
        print(f"   {level}: {count}")

    # 需要关注
    if report["attention_needed"]:
        print("\n⚠️ 需要关注:")
        for item in report["attention_needed"][:10]:  # 最多显示10个
            print(f"   📌 {item['name']}")
            for issue in item["issues"]:
                print(f"      - {issue}")

        if len(report["attention_needed"]) > 10:
            print(f"   ... 还有 {len(report['attention_needed']) - 10} 个")

    # 建议
    if report["suggestions"]:
        print("\n💡 优化建议:")
        for i, suggestion in enumerate(report["suggestions"], 1):
            print(f"   {i}. {suggestion}")

    # 健康技能
    if report["healthy_skills"]:
        print(f"\n✅ 状态良好的技能: {len(report['healthy_skills'])} 个")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    report = generate_health_report()
    print_report(report)
