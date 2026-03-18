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

**示例**：
- `cto-advisor` - CTO技术顾问
- `work-reviewer` - 工作复盘教练
- `brainstorming` - 头脑风暴

---

## L2-领域核心技能

**特征**：岗位独有的专业技能，按子分类组织

### 预定义子分类

#### 排查定位
- 关键词：排查、调试、debug、诊断、异常、error
- 示例：`systematic-debugging`、`error-detective`

#### 需求转化开发
- 关键词：SQL、开发、实现、转化、需求、mammoth
- 示例：`mammoth-sql`、`mammoth-ddl`、`youshu-dashboard-explorer`

#### 看板改造
- 关键词：看板、BI、dashboard、报表、youshu
- 示例：`youshu-dashboard-explorer`

#### 数据分析
- 关键词：分析、统计、指标、数据
- 示例：`excel-analysis`、`pdf-anthropic`

---

## L1-公共技能

**特征**：工具使用、流程执行、沟通协作类技能

**预定义关键词**：
- 工具
- 流程
- 查询
- 探索
- 解析
- 通用

**示例**：
- `find-skills` - 技能搜索
- `pdf-anthropic` - PDF处理
- `xlsx` - Excel处理
- `travel-plan` - 旅游规划

---

## 分类逻辑

```python
def classify_skill(skill_name: str, description: str) -> str:
    """
    智能分类技能层级
    优先级：L3 > L2 > L1
    """
    # 1. 先匹配 L3 高阶决策关键词
    L3_KEYWORDS = ["规划", "架构", "治理", "策略", "决策", "顾问", "review", "架构设计"]

    if any(kw in description.lower() for kw in L3_KEYWORDS):
        return "L3-高阶决策技能"

    # 2. 再匹配 L2 领域核心（按子分类）
    L2_SUBCATEGORIES = {
        "排查定位": ["排查", "调试", "debug", "诊断", "异常", "error"],
        "需求转化开发": ["SQL", "开发", "实现", "转化", "需求", "mammoth"],
        "看板改造": ["看板", "BI", "dashboard", "报表", "youshu"],
        "数据分析": ["分析", "统计", "指标", "数据"]
    }

    for subcategory, keywords in L2_SUBCATEGORIES.items():
        if any(kw in description.lower() for kw in keywords):
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
