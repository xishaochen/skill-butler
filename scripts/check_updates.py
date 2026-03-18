#!/usr/bin/env python3
"""
check_updates.py - 检查 GitHub 远程更新

功能：
1. 扫描所有 source_type=github 的技能
2. 检查远程是否有更新
3. 输出可更新的技能列表
"""

import json
import subprocess
from pathlib import Path

SKILL_USAGE_FILE = Path.home() / ".claude" / "skill-usage.json"


def load_skill_usage() -> dict:
    """加载技能使用数据"""
    if SKILL_USAGE_FILE.exists():
        with open(SKILL_USAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"version": "1.0", "skills": {}, "pending_skills": []}


def check_github_updates(skill_path: str, current_hash: str) -> dict:
    """检查 GitHub 技能是否有更新"""
    try:
        # 获取远程最新 commit
        result = subprocess.run(
            ["git", "fetch", "origin"],
            cwd=skill_path,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return {"has_update": False, "error": result.stderr}

        # 获取远程 HEAD hash
        result = subprocess.run(
            ["git", "rev-parse", "origin/HEAD"],
            cwd=skill_path,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return {"has_update": False, "error": result.stderr}

        remote_hash = result.stdout.strip()

        if remote_hash != current_hash:
            # 获取 commit 信息
            result = subprocess.run(
                ["git", "log", f"{current_hash}..{remote_hash}", "--oneline"],
                cwd=skill_path,
                capture_output=True,
                text=True
            )
            commits = result.stdout.strip() if result.returncode == 0 else ""

            return {
                "has_update": True,
                "current_hash": current_hash,
                "remote_hash": remote_hash,
                "commits": commits.split("\n") if commits else []
            }

        return {"has_update": False}

    except Exception as e:
        return {"has_update": False, "error": str(e)}


def check_all_updates() -> dict:
    """检查所有 GitHub 技能的更新"""
    data = load_skill_usage()
    skills = data.get("skills", {})

    updates_available = []
    errors = []
    up_to_date = []

    for name, skill in skills.items():
        if skill.get("source_type") != "github":
            continue

        skill_path = skill.get("path")
        current_hash = skill.get("github_hash")

        if not skill_path or not current_hash:
            continue

        result = check_github_updates(skill_path, current_hash)

        if result.get("has_update"):
            updates_available.append({
                "name": name,
                "current_hash": current_hash[:8],
                "remote_hash": result.get("remote_hash", "")[:8],
                "commits": result.get("commits", [])
            })
        elif result.get("error"):
            errors.append({
                "name": name,
                "error": result["error"]
            })
        else:
            up_to_date.append(name)

    return {
        "updates_available": updates_available,
        "errors": errors,
        "up_to_date": up_to_date
    }


def print_report(report: dict) -> None:
    """打印检查报告"""
    print("\n🔄 更新检查报告")
    print("=" * 50)

    if report["updates_available"]:
        print("\n📥 可更新的技能:")
        for u in report["updates_available"]:
            print(f"  📌 {u['name']}")
            print(f"     当前: {u['current_hash']} → 最新: {u['remote_hash']}")
            if u['commits']:
                for commit in u['commits'][:3]:
                    print(f"     - {commit}")
                if len(u['commits']) > 3:
                    print(f"     ... 还有 {len(u['commits']) - 3} 个提交")

    if report["errors"]:
        print("\n⚠️ 检查出错:")
        for e in report["errors"]:
            print(f"  📌 {e['name']}: {e['error']}")

    if report["up_to_date"]:
        print(f"\n✅ 已是最新: {len(report['up_to_date'])} 个技能")

    if not report["updates_available"] and not report["errors"]:
        print("\n✅ 所有技能已是最新版本")


if __name__ == "__main__":
    report = check_all_updates()
    print_report(report)
