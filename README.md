# Skill Butler - 你的技能管家

> 一个强大的 Claude Code 技能管理元技能，帮助你统一管理用户级和项目级技能

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)

---

## ✨ 功能特性

| 能力域 | 说明 |
|--------|------|
| **输入管理** | 外部安装 + 内部原创 (skill-creator) |
| **输出管理** | 推送 GitHub + 归档备份 |
| **层级管理** | 金字塔三层分类 (L1/L2/L3) |
| **生命周期** | 四阶段自动流转 (量化指标驱动) |
| **版本控制** | GitHub 远程同步 + 更新检测 |

---

## 📦 安装

### 前置要求

- Python 3.8+
- Claude Code CLI 或 OpenClaw
- Git (用于 GitHub 同步)

### Claude Code 安装

```bash
# 1. 克隆到 Claude Code 用户技能目录
git clone https://github.com/xishaochen/skill-butler.git ~/.claude/skills/skill-butler

# 2. 验证安装
ls ~/.claude/skills/skill-butler/SKILL.md

# 3. 初始化技能扫描
cd ~/.claude/skills/skill-butler && python scripts/scan_skills.py
```

### OpenClaw 安装

> **兼容性说明**：OpenClaw 使用与 Claude Code 相同的 SKILL.md 格式，理论上完全兼容。

```bash
# 1. 确认 OpenClaw 技能目录位置（通常是以下之一）
# - ~/.openclaw/skills/
# - ~/.config/openclaw/skills/
# 请根据你的 OpenClaw 版本确认实际路径

# 2. 克隆到技能目录
git clone https://github.com/xishaochen/skill-butler.git ~/.openclaw/skills/skill-butler

# 3. 修改配置文件中的路径（如果需要）
# 编辑 scripts/settings.py，将 USER_SKILLS_DIR 改为你的 OpenClaw 技能目录

# 4. 初始化技能扫描
cd ~/.openclaw/skills/skill-butler && python scripts/scan_skills.py
```

<details>
<summary>🔧 OpenClaw 路径适配</summary>

如果你的 OpenClaw 使用不同的目录结构，需要修改 `scripts/settings.py`：

```python
# 原配置（Claude Code）
USER_SKILLS_DIR = Path.home() / ".claude" / "skills"

# 修改为（OpenClaw 示例）
USER_SKILLS_DIR = Path.home() / ".openclaw" / "skills"
```

</details>

---

## 🚀 快速开始

### 在 Claude Code 中使用

安装完成后，在 Claude Code 中输入：

```
/skill-butler
```

你将看到技能管家主菜单：

```
┌─────────────────────────────────────────────────────────────┐
│ 你好！我是你的技能管家。今天想做什么？                        │
│                                                             │
│ [1] 📥 安装新技能    [2] ✨ 创建新技能                       │
│ [3] 📊 查看技能总览  [4] 🔄 检查更新                         │
│ [5] 📤 推送技能      [6] 🗑️ 归档技能                        │
│ [7] 📈 技能健康报告  [8] ⚙️ 设置                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 目录结构

```
skill-butler/
├── SKILL.md              # 技能定义文件（必需）
├── README.md             # 本文档
├── scripts/              # 核心脚本
│   ├── scan_skills.py    # 技能扫描
│   ├── show_pyramid.py   # 金字塔视图
│   ├── check_lifecycle.py# 生命周期检查
│   ├── check_updates.py  # 更新检测
│   ├── health_report.py  # 健康报告
│   ├── archive_skill.py  # 归档技能
│   └── settings.py       # 设置管理
├── references/           # 参考文档
│   ├── pyramid.md        # 金字塔层级定义
│   ├── lifecycle.md      # 生命周期规则
│   └── subskills.md      # 子技能说明
└── templates/            # 模板文件
    └── usage_log.json    # 使用记录模板
```

---

## 📖 详细使用指南

### [1] 📥 安装新技能

从技能仓库搜索并安装新技能：

1. 告诉技能管家你想要什么功能
2. 查看搜索结果
3. 安全审查确认
4. 一键安装

### [2] ✨ 创建新技能

引导式创建自定义技能：

1. 定义技能名称和描述
2. 编写 SKILL.md 文档
3. 自动分类层级

### [3] 📊 查看技能总览

展示金字塔视图：

```
        ▲
       /│\        L3-高阶决策技能
      / │ \       规划、架构、治理、策略
     /  │  \
    /───┼───\     L2-领域核心技能
   /    │    \    岗位独有的专业技能
  /     │     \
 /──────┼──────\  L1-公共技能
/       │       \ 工具使用、流程执行
```

### [4] 🔄 检查更新

自动检测 GitHub 托管的技能是否有更新

### [5] 📤 推送技能

将成熟技能推送到 GitHub：

1. 选择要推送的技能
2. 安全扫描
3. 打包上传

### [6] 🗑️ 归档技能

安全归档不再使用的技能

### [7] 📈 技能健康报告

生成包含以下内容的健康报告：

- 需要关注的技能
- 状态良好的技能统计
- 优化建议

---

## 🔄 生命周期管理

技能遵循四阶段生命周期：

| 阶段 | 判断标准 | 图标 | 建议动作 |
|------|---------|------|---------|
| **需求萌芽期** | 未调用过 | 🌱 | 评估试用 |
| **成熟稳定期** | 调用≥2次 | 🌿 | 推送 GitHub |
| **上线迭代期** | 已推送或调用≥5次 | 🌺 | 检查更新 |
| **下线归档期** | 90天未使用 | 🍂  | 归档备份 |

```
需求萌芽期 ──► 成熟稳定期 ──► 上线迭代期 ──► 下线归档期
   🌱            🌿           🌺           🍂 
```

---

## ⚙️ 配置

配置文件位置: `~/.claude/skill-usage.json`

### 可配置项

```json
{
  "settings": {
    "archive_days_threshold": 90,     // 归档阈值（天）
    "lifecycle_thresholds": {
      "mature_invocation_count": 2,   // 成熟期调用次数
      "online_invocation_count": 5    // 上线期调用次数
    },
    "auto_scan": true,                // 自动扫描
    "auto_lifecycle_check": true      // 自动生命周期检查
  }
}
```

---

## 🧩 金字塔层级分类

### L3-高阶决策技能

规划、架构、治理、策略类技能

**关键词**: 规划、架构、治理、策略、决策、顾问、review

**示例**: `cto-advisor`, `work-reviewer`, `brainstorming`

### L2-领域核心技能

岗位独有的专业技能

| 子分类 | 关键词 |
|--------|--------|
| 技能管理 | skill, vetter, creator |
| 排查定位 | debug, 诊断, 异常 |
| 需求转化开发 | sql, mammoth, ddl |
| 看板改造 | bi, dashboard, youshu |
| 数据分析 | analysis, 统计, 指标 |
| 内容创作 | content, writer, research |

### L1-公共技能

工具使用、流程执行类技能

**示例**: `xlsx`, `docx`, `pptx`, `pdf-anthropic`, `obsidian-markdown`

---

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

### 开发

```bash
# 克隆仓库
git clone https://github.com/xishaochen/skill-butler.git
cd skill-butler

# 运行测试
python scripts/scan_skills.py
```

### 提交 PR

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

- [Claude Code](https://claude.ai/code) - Anthropic 官方 CLI 工具
- 所有贡献者和使用者

---

## 📮 联系方式

- 作者: 阿辰
- GitHub: [@xishaochen](https://github.com/xishaochen)
- Issues: [提交问题](https://github.com/xishaochen/skill-butler/issues)

---

**如果这个项目对你有帮助，请给一个 ⭐ Star！**
