#!/usr/bin/env python3
"""
archive_skill.py - 归档过期技能

功能：
1. 备份技能到归档目录
2. 从技能列表中移除
3. 可选：删除技能文件
"""

import json
import shutil
from datetime import datetime
from pathlib import Path

SKILL_USAGE_FILE = Path.home() / ".claude" / "skill-usage.json"
ARCHIVE_DIR = Path.home() / ".claude" / "skills-archive"


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


def archive_skill(skill_name: str, delete_files: bool = False) -> dict:
    """归档技能"""
    data = load_skill_usage()
    skills = data.get("skills", {})

    if skill_name not in skills:
        return {"success": False, "error": f"技能 '{skill_name}' 不存在"}

    skill = skills[skill_name]
    skill_path = Path(skill.get("path", ""))

    # 创建归档目录
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    # 归档信息
    archive_info = {
        "name": skill_name,
        "archived_at": datetime.now().isoformat(),
        "original_path": str(skill_path),
        "lifecycle": skill.get("lifecycle"),
        "invocation_count": skill.get("invocation_count", 0),
        "source_type": skill.get("source_type"),
        "github_url": skill.get("github_url"),
    }

    # 备份技能目录
    if skill_path.exists():
        archive_path = ARCHIVE_DIR / f"{skill_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            shutil.copytree(skill_path, archive_path)
            archive_info["archive_path"] = str(archive_path)

            # 删除原文件
            if delete_files:
                shutil.rmtree(skill_path)
                archive_info["files_deleted"] = True
            else:
                archive_info["files_deleted"] = False

        except Exception as e:
            return {"success": False, "error": f"备份失败: {str(e)}"}
    else:
        archive_info["archive_path"] = None
        archive_info["files_deleted"] = False

    # 从数据中移除
    del skills[skill_name]

    # 添加到归档记录
    if "archived_skills" not in data:
        data["archived_skills"] = []
    data["archived_skills"].append(archive_info)

    save_skill_usage(data)

    return {
        "success": True,
        "skill": skill_name,
        "archive_path": archive_info.get("archive_path"),
        "files_deleted": archive_info.get("files_deleted", False)
    }


def list_archived_skills() -> list:
    """列出已归档的技能"""
    data = load_skill_usage()
    return data.get("archived_skills", [])


def print_archived_skills() -> None:
    """打印已归档技能列表"""
    archived = list_archived_skills()

    if not archived:
        print("\n📭 暂无已归档的技能")
        return

    print(f"\n📦 已归档技能 ({len(archived)})")
    print("=" * 50)

    for skill in archived:
        print(f"  📌 {skill['name']}")
        print(f"     归档时间: {skill['archived_at']}")
        print(f"     调用次数: {skill.get('invocation_count', 0)}")
        if skill.get('archive_path'):
            print(f"     备份路径: {skill['archive_path']}")
        print()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法:")
        print("  python archive_skill.py list              # 列出已归档技能")
        print("  python archive_skill.py <skill_name>      # 归档技能（保留文件）")
        print("  python archive_skill.py <skill_name> del  # 归档技能（删除文件）")
        sys.exit(1)

    if sys.argv[1] == "list":
        print_archived_skills()
    else:
        skill_name = sys.argv[1]
        delete_files = len(sys.argv) > 2 and sys.argv[2] == "del"

        result = archive_skill(skill_name, delete_files)
        print(json.dumps(result, ensure_ascii=False, indent=2))
