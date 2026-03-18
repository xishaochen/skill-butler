#!/usr/bin/env python3
"""
scan_skills.py - 扫描所有已安装技能

功能：
1. 扫描用户级技能目录 (~/.claude/skills/)
2. 扫描项目级技能目录 (./.claude/skills/)
3. 读取技能元数据（SKILL.md）
4. 更新 skill-usage.json 数据文件
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, List


# 配置
SKILL_USAGE_FILE = Path.home() / ".claude" / "skill-usage.json"
USER_SKILLS_DIR = Path.home() / ".claude" / "skills"
# 项目级技能目录 - 使用项目根目录而非当前工作目录
PROJECT_SKILLS_DIR = Path.home() / "PycharmProjects" / "CCAgent" / ".claude" / "skills"
# ccagent-skills 仓库目录
CCAGENT_SKILLS_DIR = Path.home() / "ClaudeProjects" / "ccagent-skills"

# 目录结构 → 层级映射（隐式分类）
DIR_TO_LEVEL = {
    "L3-smart": "L3-高阶决策技能",
    "L2-core": "L2-领域核心技能",
    "L1-utils": "L1-公共技能",
    "Backup-archived": "已归档",
}

# 金字塔分类关键词
L3_KEYWORDS = ["规划", "架构", "治理", "策略", "决策", "顾问", "review", "架构设计", "advisor", "cto", "brainstorm"]

L2_SUBCATEGORIES = {
    "技能管理": ["skill", "vetter", "creator", "find-skills"],  # 技能搜索、创建、审查
    "排查定位": ["排查", "调试", "debug", "诊断", "异常", "error", "detective"],
    "需求转化开发": ["sql", "开发", "实现", "转化", "需求", "mammoth", "ddl", "easydata"],
    "看板改造": ["看板", "bi", "dashboard", "报表", "youshu", "explorer"],
    "数据分析": ["analysis", "统计", "指标", "数据"],  # 移除 excel，避免误分类
    "内容创作": ["内容", "写作", "content", "writer", "research"],
}

# L1 公共技能 - 工具使用类（直接匹配技能名）
L1_TOOL_SKILLS = [
    "xlsx", "docx", "pptx", "pdf-anthropic", "pdf-processing-pro", "excel-analysis",
    "obsidian-markdown", "obsidian-bases", "json-canvas",  # Obsidian 工具
    "guanbao-parser",  # 解析工具
    "glm-quota-check",  # 查询工具
    "pycharm-optimizer",  # IDE 优化工具
]


def load_skill_usage() -> Dict[str, Any]:
    """加载技能使用数据"""
    try:
        if SKILL_USAGE_FILE.exists():
            with open(SKILL_USAGE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"⚠️ 加载数据失败: {e}，将使用空数据")
    return {
        "version": "1.0",
        "last_scan": None,
        "skills": {},
        "pending_skills": []
    }


def save_skill_usage(data: Dict[str, Any]) -> None:
    """保存技能使用数据"""
    SKILL_USAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SKILL_USAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def extract_skill_metadata(skill_dir: Path) -> Dict[str, Any]:
    """从 SKILL.md 提取技能元数据"""
    skill_md = skill_dir / "SKILL.md"
    metadata = {
        "name": skill_dir.name,
        "description": "",
        "entry_file": None,
        "usage": None,
    }

    if skill_md.exists():
        content = skill_md.read_text(encoding="utf-8")

        # 提取描述（第一个标题后的第一段）
        lines = content.split("\n")
        in_description = False
        description_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith("# "):
                # 第一个标题是技能名，跳过
                if not in_description:
                    in_description = True
                continue
            if line.startswith("## "):
                # 遇到二级标题，描述结束
                break
            if in_description:
                description_lines.append(line)
                if len(description_lines) >= 3:  # 只取前3行
                    break

        metadata["description"] = " ".join(description_lines)[:200]

    return metadata


def infer_level_from_path(skill_path: str) -> Optional[str]:
    """从 ccagent-skills 目录结构推断层级"""
    skill_path = Path(skill_path)

    # 检查是否在 ccagent-skills 仓库中
    try:
        relative = skill_path.relative_to(CCAGENT_SKILLS_DIR)
        # 第一级目录名
        first_dir = str(relative).split("/")[0] if "/" in str(relative) else str(relative)
        if first_dir in DIR_TO_LEVEL:
            return DIR_TO_LEVEL[first_dir]
    except ValueError:
        pass  # 不在 ccagent-skills 中

    return None


def classify_skill(skill_name: str, description: str, skill_path: str = "") -> str:
    """智能分类技能层级

    优先级：
    1. ccagent-skills 目录位置（隐式分类）
    2. L1 工具技能精确匹配
    3. L3 高阶决策关键词
    4. L2 领域核心子分类
    5. 默认 L1
    """
    combined = f"{skill_name} {description}".lower()

    # 0. 优先从目录位置推断
    if skill_path:
        dir_level = infer_level_from_path(skill_path)
        if dir_level:
            return dir_level

    # 1. 匹配 L1 工具技能（精确匹配技能名）
    if skill_name in L1_TOOL_SKILLS:
        return "L1-公共技能"

    # 2. 匹配 L3 高阶决策关键词
    if any(kw.lower() in combined for kw in L3_KEYWORDS):
        return "L3-高阶决策技能"

    # 3. 匹配 L2 领域核心（按子分类）
    for subcategory, keywords in L2_SUBCATEGORIES.items():
        if any(kw.lower() in combined for kw in keywords):
            return f"L2-领域核心技能/{subcategory}"

    # 4. 默认 L1 公共技能
    return "L1-公共技能"


def detect_source_type(skill_dir: Path) -> str:
    """检测技能来源类型"""
    git_dir = skill_dir / ".git"
    if git_dir.exists():
        return "github"

    # 检查是否有 package.json 或其他特征
    # 这里的逻辑可以扩展
    return "local"


def get_github_info(skill_dir: Path) -> Tuple[Optional[str], Optional[str]]:
    """获取 GitHub 信息"""
    git_dir = skill_dir / ".git"
    if not git_dir.exists():
        return None, None

    try:
        # 获取远程 URL
        import subprocess
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=skill_dir,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            url = result.stdout.strip()
            # 解析 owner/repo
            match = re.search(r"[:/]([^/]+/[^/.]+)", url)
            if match:
                github_url = match.group(1)

                # 获取 commit hash
                result = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=skill_dir,
                    capture_output=True,
                    text=True
                )
                github_hash = result.stdout.strip() if result.returncode == 0 else None

                return github_url, github_hash
    except Exception:
        pass

    return None, None


def scan_skills_directory(skills_dir: Path, location: str) -> Dict[str, Any]:
    """扫描技能目录"""
    skills = {}

    if not skills_dir.exists():
        return skills

    for skill_dir in skills_dir.iterdir():
        if not skill_dir.is_dir():
            continue
        if skill_dir.name.startswith("."):
            continue

        skill_name = skill_dir.name
        metadata = extract_skill_metadata(skill_dir)
        source_type = detect_source_type(skill_dir)
        github_url, github_hash = get_github_info(skill_dir) if source_type == "github" else (None, None)

        # 分类（传入路径以支持目录结构推断）
        level = classify_skill(skill_name, metadata["description"], str(skill_dir))

        skills[skill_name] = {
            "name": skill_name,
            "location": location,
            "path": str(skill_dir),
            "source_type": source_type,
            "github_url": github_url,
            "github_hash": github_hash,
            "level": level,
            "lifecycle": "需求萌芽期",  # 默认状态
            "lifecycle_changed_at": datetime.now().isoformat(),
            "invocation_count": 0,
            "last_invoked": None,
            "created_at": datetime.now().isoformat(),
            "pushed": source_type == "github",
            "user_marked_deprecated": False,
            "notes": "",
            "description": metadata["description"],
        }

    return skills


def merge_skills(existing: Dict, new: Dict) -> Dict:
    """合并技能数据，保留已有数据"""
    result = existing.copy()

    for skill_name, skill_data in new.items():
        if skill_name in result:
            # 保留使用数据，更新元数据
            existing_skill = result[skill_name]
            skill_data["invocation_count"] = existing_skill.get("invocation_count", 0)
            skill_data["last_invoked"] = existing_skill.get("last_invoked")
            skill_data["lifecycle"] = existing_skill.get("lifecycle", "需求萌芽期")
            skill_data["lifecycle_changed_at"] = existing_skill.get("lifecycle_changed_at")
            skill_data["created_at"] = existing_skill.get("created_at", skill_data["created_at"])
            skill_data["pushed"] = existing_skill.get("pushed", skill_data["pushed"])
            skill_data["user_marked_deprecated"] = existing_skill.get("user_marked_deprecated", False)
            skill_data["notes"] = existing_skill.get("notes", "")

        result[skill_name] = skill_data

    return result


def scan_all_skills() -> Dict[str, Any]:
    """扫描所有技能"""
    data = load_skill_usage()

    # 扫描用户级技能
    user_skills = scan_skills_directory(USER_SKILLS_DIR, "user")

    # 扫描项目级技能
    project_skills = scan_skills_directory(PROJECT_SKILLS_DIR, "project")

    # 合并
    all_skills = merge_skills(data.get("skills", {}), {**user_skills, **project_skills})

    # 更新数据
    data["skills"] = all_skills
    data["last_scan"] = datetime.now().isoformat()

    save_skill_usage(data)

    return data


def print_summary(data: Dict[str, Any]) -> None:
    """打印扫描结果摘要"""
    skills = data.get("skills", {})

    print(f"\n📊 技能扫描完成 - 共发现 {len(skills)} 个技能")
    print(f"📅 扫描时间: {data.get('last_scan', 'N/A')}")

    # 按层级统计
    levels = {}
    for skill in skills.values():
        level = skill.get("level", "L1-公共技能")
        levels[level] = levels.get(level, 0) + 1

    print("\n📈 层级分布:")
    for level, count in sorted(levels.items()):
        print(f"  {level}: {count}")

    # 按位置统计
    locations = {"user": 0, "project": 0}
    for skill in skills.values():
        loc = skill.get("location", "user")
        locations[loc] = locations.get(loc, 0) + 1

    print("\n📍 位置分布:")
    print(f"  用户级: {locations['user']}")
    print(f"  项目级: {locations['project']}")


if __name__ == "__main__":
    data = scan_all_skills()
    print_summary(data)
