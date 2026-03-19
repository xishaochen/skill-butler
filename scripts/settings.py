#!/usr/bin/env python3
"""
settings.py - skill-butler 设置管理

功能：
1. 查看当前配置
2. 修改设置
"""

import json
from pathlib import Path
from typing import Dict, Any

SKILL_USAGE_FILE = Path.home() / ".claude" / "skill-usage.json"
USER_SKILLS_DIR = Path.home() / ".claude" / "skills"
ARCHIVE_DIR = Path.home() / ".claude" / "skills-archive"

# 默认配置
DEFAULT_CONFIG = {
    "version": "1.0",
    "settings": {
        "archive_days_threshold": 90,  # 归档阈值（天）
        "lifecycle_thresholds": {
            "mature_invocation_count": 2,  # 成熟期调用次数阈值
            "online_invocation_count": 5,  # 上线期调用次数阈值
        },
        "scan_directories": {
            "user_skills": str(USER_SKILLS_DIR),
            "project_skills": "./.claude/skills"
        },
        "auto_scan": True,  # 自动扫描
        "auto_lifecycle_check": True,  # 自动生命周期检查
    },
    "skills": {},
    "pending_skills": [],
    "archived_skills": []
}


def load_config() -> Dict[str, Any]:
    """加载配置"""
    try:
        if SKILL_USAGE_FILE.exists():
            with open(SKILL_USAGE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # 合并默认配置
                if "settings" not in data:
                    data["settings"] = DEFAULT_CONFIG["settings"]
                return data
    except (json.JSONDecodeError, IOError) as e:
        print(f"⚠️ 加载配置失败: {e}")
    return DEFAULT_CONFIG.copy()


def save_config(data: Dict[str, Any]) -> None:
    """保存配置"""
    SKILL_USAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SKILL_USAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def view_settings() -> None:
    """查看当前配置"""
    data = load_config()
    settings = data.get("settings", DEFAULT_CONFIG["settings"])

    print("\n⚙️ skill-butler 设置")
    print("=" * 50)

    print("\n📁 目录配置:")
    print(f"  数据文件: {SKILL_USAGE_FILE}")
    print(f"  用户技能目录: {USER_SKILLS_DIR}")
    print(f"  归档目录: {ARCHIVE_DIR}")

    print("\n📊 生命周期阈值:")
    thresholds = settings.get("lifecycle_thresholds", {})
    print(f"  成熟期调用次数: {thresholds.get('mature_invocation_count', 2)}")
    print(f"  上线期调用次数: {thresholds.get('online_invocation_count', 5)}")
    print(f"  归档天数阈值: {settings.get('archive_days_threshold', 90)}")

    print("\n🔄 自动化设置:")
    print(f"  自动扫描: {'✓' if settings.get('auto_scan', True) else '✗'}")
    print(f"  自动生命周期检查: {'✓' if settings.get('auto_lifecycle_check', True) else '✗'}")

    print("\n📈 统计信息:")
    skills = data.get("skills", {})
    print(f"  技能总数: {len(skills)}")
    print(f"  待创建: {len(data.get('pending_skills', []))}")
    print(f"  已归档: {len(data.get('archived_skills', []))}")


def modify_settings() -> None:
    """修改设置"""
    data = load_config()
    settings = data.get("settings", DEFAULT_CONFIG["settings"])

    print("\n⚙️ 修改设置")
    print("=" * 50)
    print("可修改的选项:")
    print("  1. 归档天数阈值")
    print("  2. 成熟期调用次数阈值")
    print("  3. 上线期调用次数阈值")
    print("  4. 自动扫描开关")
    print("  5. 自动生命周期检查开关")
    print("  0. 返回")

    choice = input("\n请选择 (0-5): ").strip()

    if choice == "1":
        current = settings.get("archive_days_threshold", 90)
        new_value = input(f"归档天数阈值 [{current}]: ").strip()
        if new_value:
            settings["archive_days_threshold"] = int(new_value)
            print(f"✓ 已更新为 {new_value} 天")

    elif choice == "2":
        current = settings.get("lifecycle_thresholds", {}).get("mature_invocation_count", 2)
        new_value = input(f"成熟期调用次数阈值 [{current}]: ").strip()
        if new_value:
            if "lifecycle_thresholds" not in settings:
                settings["lifecycle_thresholds"] = {}
            settings["lifecycle_thresholds"]["mature_invocation_count"] = int(new_value)
            print(f"✓ 已更新为 {new_value} 次")

    elif choice == "3":
        current = settings.get("lifecycle_thresholds", {}).get("online_invocation_count", 5)
        new_value = input(f"上线期调用次数阈值 [{current}]: ").strip()
        if new_value:
            if "lifecycle_thresholds" not in settings:
                settings["lifecycle_thresholds"] = {}
            settings["lifecycle_thresholds"]["online_invocation_count"] = int(new_value)
            print(f"✓ 已更新为 {new_value} 次")

    elif choice == "4":
        current = settings.get("auto_scan", True)
        new_value = not current
        settings["auto_scan"] = new_value
        print(f"✓ 自动扫描已{'开启' if new_value else '关闭'}")

    elif choice == "5":
        current = settings.get("auto_lifecycle_check", True)
        new_value = not current
        settings["auto_lifecycle_check"] = new_value
        print(f"✓ 自动生命周期检查已{'开启' if new_value else '关闭'}")

    elif choice == "0":
        return
    else:
        print("⚠️ 无效选择")
        return

    data["settings"] = settings
    save_config(data)
    print("\n✓ 设置已保存")


def reset_settings() -> None:
    """重置为默认设置"""
    data = load_config()
    data["settings"] = DEFAULT_CONFIG["settings"].copy()
    save_config(data)
    print("\n✓ 已重置为默认设置")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "view":
            view_settings()
        elif arg == "modify":
            modify_settings()
        elif arg == "reset":
            reset_settings()
        else:
            print(f"未知命令: {arg}")
            print("用法: python settings.py [view|modify|reset]")
    else:
        view_settings()
