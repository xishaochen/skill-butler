#!/usr/bin/env python3
"""
classify_skill.py - 智能分类技能层级

功能：
1. 根据技能名称和描述自动分类
2. 支持手动指定层级
"""

import json
import sys
from pathlib import Path

# 添加父目录到路径以导入 scan_skills
sys.path.insert(0, str(Path(__file__).parent))
from scan_skills import classify_skill, load_skill_usage, save_skill_usage


def get_skill_classification(skill_name: str) -> dict:
    """获取技能分类信息"""
    data = load_skill_usage()
    skills = data.get("skills", {})

    if skill_name not in skills:
        return {"error": f"技能 '{skill_name}' 不存在"}

    skill = skills[skill_name]
    return {
        "name": skill_name,
        "current_level": skill.get("level", "L1-公共技能"),
        "description": skill.get("description", ""),
        "source_type": skill.get("source_type"),
    }


def update_skill_level(skill_name: str, new_level: str) -> dict:
    """更新技能层级"""
    data = load_skill_usage()
    skills = data.get("skills", {})

    if skill_name not in skills:
        return {"error": f"技能 '{skill_name}' 不存在"}

    old_level = skills[skill_name].get("level", "L1-公共技能")
    skills[skill_name]["level"] = new_level

    save_skill_usage(data)

    return {
        "name": skill_name,
        "old_level": old_level,
        "new_level": new_level,
        "success": True
    }


def suggest_classification(skill_name: str, description: str = "") -> dict:
    """建议技能分类"""
    suggested = classify_skill(skill_name, description)

    return {
        "name": skill_name,
        "description": description,
        "suggested_level": suggested,
        "reasoning": get_classification_reasoning(skill_name, description, suggested)
    }


def get_classification_reasoning(skill_name: str, description: str, level: str) -> str:
    """获取分类理由"""
    combined = f"{skill_name} {description}".lower()

    L3_KEYWORDS = ["规划", "架构", "治理", "策略", "决策", "顾问", "review", "架构设计", "advisor", "cto"]
    L2_SUBCATEGORIES = {
        "排查定位": ["排查", "调试", "debug", "诊断", "异常", "error", "detective"],
        "需求转化开发": ["sql", "开发", "实现", "转化", "需求", "mammoth", "ddl"],
        "看板改造": ["看板", "bi", "dashboard", "报表", "youshu", "explorer"],
        "数据分析": ["分析", "统计", "指标", "数据", "analysis", "excel"],
        "内容创作": ["内容", "写作", "content", "writer", "research"],
        "文档处理": ["pdf", "docx", "xlsx", "pptx", "文档", "document"],
        "旅游规划": ["旅游", "行程", "travel", "plan", "route", "accommodation"],
    }

    # 检查匹配的关键词
    if level.startswith("L3"):
        matched = [kw for kw in L3_KEYWORDS if kw.lower() in combined]
        return f"匹配 L3 关键词: {', '.join(matched)}"

    elif level.startswith("L2"):
        for subcategory, keywords in L2_SUBCATEGORIES.items():
            if subcategory in level:
                matched = [kw for kw in keywords if kw.lower() in combined]
                if matched:
                    return f"匹配 L2/{subcategory} 关键词: {', '.join(matched)}"

    return "未匹配特定关键词，归类为公共技能"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  python classify_skill.py <skill_name>           # 查看分类")
        print("  python classify_skill.py <skill_name> <level>   # 更新分类")
        sys.exit(1)

    skill_name = sys.argv[1]

    if len(sys.argv) >= 3:
        new_level = sys.argv[2]
        result = update_skill_level(skill_name, new_level)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        result = get_skill_classification(skill_name)
        print(json.dumps(result, ensure_ascii=False, indent=2))
