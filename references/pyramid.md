# 金字塔层级定义

> 技能分类的三层金字塔模型

---

## 层级概览

```
        ▲
       /│\        L3-高阶决策技能 (顶层)
      / │ \       规划、架构、治理、策略
     /  │  \
    /───┼───\     L2-领域核心技能 (中层)
   /    │    \    岗位独有的专业技能
  /     │     \
 /──────┼──────\  L1-公共技能 (底层)
/       │       \ 工具使用、流程执行、沟通协作
```

---

## L3-高阶决策技能

**特征**：规划、架构、治理、策略类技能

**预定义关键词**：
- 规划
- 架构
- 治理
- 策略
- 决策
- 顾问
- review
- 架构设计
- advisor
- cto
- brainstorm

**示例**：
- `cto-advisor` - CTO技术顾问
- `work-reviewer` - 工作复盘教练
- `brainstorming` - 头脑风暴
- `competitive-ads-extractor` - 竞品分析（含策略）

---

## L2-领域核心技能

**特征**：岗位独有的专业技能，按子分类组织

### 预定义子分类

#### 技能管理
- 关键词：skill, vetter, creator, find-skills
- 示例：`find-skills`、`skill-creator`、`skill-vetter`

#### 排查定位
- 关键词：排查、调试、debug、诊断、异常、error、detective
- 示例：`systematic-debugging`、`error-detective`

#### 需求转化开发
- 关键词：SQL、开发、实现、转化、需求、mammoth、ddl、easydata
- 示例：`mammoth-sql`、`mammoth-ddl`、`easydata`

#### 看板改造
- 关键词：看板、BI、dashboard、报表、youshu
- 示例：`youshu-dashboard-explorer`、`youshu_model_create`

#### 数据分析
- 关键词：analysis、统计、指标、数据
- 示例：专业数据分析工具

#### 内容创作
- 关键词：内容、写作、content、writer、research
- 示例：`content-explorer`、`content-research-writer`

---

## L1-公共技能

**特征**：工具使用、流程执行、沟通协作类技能

### 预定义工具技能列表

以下技能直接归类为 L1（精确匹配技能名）：

**文档处理工具**：
- `xlsx` - Excel 处理
- `docx` - Word 处理
- `pptx` - PowerPoint 处理
- `pdf-anthropic` - PDF 处理
- `pdf-processing-pro` - PDF 高级处理
- `excel-analysis` - Excel 分析

**Obsidian 工具**：
- `obsidian-markdown` - Obsidian Markdown
- `obsidian-bases` - Obsidian Bases
- `json-canvas` - JSON Canvas

**其他工具**：
- `guanbao-parser` - 管报解析
- `glm-quota-check` - 智谱配额查询
- `pycharm-optimizer` - PyCharm 优化

---

## 分类逻辑

```python
def classify_skill(skill_name: str, description: str) -> str:
    """
    智能分类技能层级
    优先级：L1工具列表 > L3 > L2 > L1默认
    """
    # 0. 优先匹配 L1 工具技能（精确匹配技能名）
    L1_TOOL_SKILLS = [
        "xlsx", "docx", "pptx", "pdf-anthropic", "pdf-processing-pro", "excel-analysis",
        "obsidian-markdown", "obsidian-bases", "json-canvas",
        "guanbao-parser", "glm-quota-check", "pycharm-optimizer",
    ]
    if skill_name in L1_TOOL_SKILLS:
        return "L1-公共技能"

    # 1. 先匹配 L3 高阶决策关键词
    L3_KEYWORDS = ["规划", "架构", "治理", "策略", "决策", "顾问", "review", "架构设计", "advisor", "cto", "brainstorm"]
    combined = f"{skill_name} {description}".lower()
    if any(kw in combined for kw in L3_KEYWORDS):
        return "L3-高阶决策技能"

    # 2. 再匹配 L2 领域核心（按子分类）
    L2_SUBCATEGORIES = {
        "技能管理": ["skill", "vetter", "creator", "find-skills"],
        "排查定位": ["排查", "调试", "debug", "诊断", "异常", "error", "detective"],
        "需求转化开发": ["sql", "开发", "实现", "转化", "需求", "mammoth", "ddl", "easydata"],
        "看板改造": ["看板", "bi", "dashboard", "报表", "youshu", "explorer"],
        "数据分析": ["analysis", "统计", "指标", "数据"],
        "内容创作": ["内容", "写作", "content", "writer", "research"],
    }

    for subcategory, keywords in L2_SUBCATEGORIES.items():
        if any(kw in combined for kw in keywords):
            return f"L2-领域核心技能/{subcategory}"

    # 3. 默认归为 L1 公共技能
    return "L1-公共技能"
```

---

## 动态归类

除了预定义分类，还支持动态归类：

1. **用户自定义**：用户可以手动指定技能层级
2. **学习调整**：根据技能使用模式自动调整
3. **标签扩展**：通过技能描述中的新关键词扩展分类

---

## 分类变更记录

| 日期 | 变更内容 |
|------|---------|
| 2026-03-18 | 新增"技能管理"子分类；移除"文档处理"和"旅游规划"子分类；文档处理工具统一归为L1 |
