---
name: book-4layer-workbench
description: 把任意书籍 PDF 转化为"四层精读工作台"——一个 Feishu 文档 + 一个诊断多维表格 + 一个 30 天打卡多维表格,适合心理类/方法论类/工具书。当用户说"做这本书的精读工作台 / 4 层精读 / L0-L4 工作台 / 把这本书变成可执行的 30 天计划 / 给我做一个读完能落地的版本"时触发。
---

# book-4layer-workbench

## 何时使用

触发关键词:
- "四层精读 / 4 层精读 / L0-L4"
- "把书做成工作台 / 读完能落地的版本"
- "精读 + 30 天打卡 + 诊断量表"
- 用户上传一本书的 PDF + 说"按你给《XXX》做的那套流程再做一遍"

不触发:
- 用户只要书摘 / 读后感 / 单篇笔记
- 用户只要 mindmap 而不要打卡 / 诊断

## 输出物(3 个)

| 编号 | 形式 | 内容 |
|---|---|---|
| A | 飞书文档 | 四层精读主文档(L0 全书一句话 / L1 mindmap / L2 章节卡片 / L3 自我诊断 / L4 实验设计 + 22 项对策 + 30 天计划 + 滚动机制 + 求助清单 + 元认知检查) |
| B | 飞书多维表格 | 自我诊断量表(每本书的"症状维度"不同,字段按书自动生成) |
| C | 飞书多维表格 | 30 天打卡(微习惯打卡 + 周复盘) |

## 工作流(5 阶段)

### Stage 1 - 解析书籍

1. 调用 `pdf` skill 解析 PDF,提取:
   - 书名 / 作者 / 章节标题
   - 每章核心观点(取前 1500 字 + 末 800 字传给 LLM 抽取)
   - 全书 "症状维度 / 类别"(让 LLM 找出本书的核心问题分类法,例如《不完美主义者》是 Hill 8 维度,《非暴力沟通》是 4 步流程,《原子习惯》是 4 法则)
   - 全书 "对策清单"(让 LLM 抽取可执行动作,通常 15-30 条)

2. 输出结构化 JSON(`book_meta.json`):
```json
{
  "title": "...",
  "author": "...",
  "one_sentence": "...",
  "chapters": [{"no":1, "title":"...", "summary":"...", "key_points":[...]}],
  "diagnostic_dimensions": [{"name":"...", "category":"...", "definition":"...", "chapter_ref":"第X章", "counter_actions":"..."}],
  "action_strategies": [{"group":"A.整体", "no":1, "name":"...", "desc":"..."}],
  "micro_habits": ["...","...","..."]
}
```

### Stage 2 - 生成主文档 XML

调用脚本 `scripts/build_doc_xml.py book_meta.json > doc.xml` 生成飞书文档 XML,包含:

- 文档头部 callout: "今天就做(5 分钟启动包)"
- L0 一句话 + 3 个事实锚点
- L1 全书 mindmap(`<whiteboard type="mermaid">`)
- L2 章节卡片表格(章 / 一句话 / 关键概念 / 可执行动作)
- L3 自我诊断引导 + 配套表格链接
- L4 实验设计(22 项对策按组归类 + Top3 选择映射表 + 填写示例)
- 30 天计划日历表
- 30 天后滚动机制
- 求助清单
- 元认知检查清单 + 解药
- 30 天前后状态画像对照表

### Stage 3 - 创建并填充诊断多维表格

```bash
# 1. 创建 Base
lark-cli docs +create --type bitable --title "《<书名>》自我诊断量表"

# 2. 创建字段(根据 diagnostic_dimensions 的字段集动态生成)
lark-cli base +field-create --base-token <T> --table-id <TID> --field-name 维度 --field-type 1
lark-cli base +field-create ... 类别(单选) 含义说明(多行文本) 对应章节(单选) 改善对策(多行文本)
lark-cli base +field-create ... 自评分数(1-5)(数字) 是否列入Top3(复选框)

# 3. 批量写入诊断维度行
lark-cli base +record-batch-create --base-token <T> --table-id <TID> --json "<JSON>"
```

### Stage 4 - 创建并填充 30 天打卡多维表格

```bash
# 1. 创建 Base
lark-cli docs +create --type bitable --title "《<书名>》30 天打卡"

# 2. 字段: 日期 周次(单选第1-5周) 微习惯1/2/3(复选框) 当日感受 是否周复盘
# 3. 用 scripts/gen_track_rows.py 生成 30 天行 JSON,批量写入
```

### Stage 5 - 把表格 URL 回填到主文档

替换主文档 "配套资源" 章节里的 `<L3_TABLE_URL>` `<L4_TABLE_URL>` 占位符。

## 关键脚本

| 脚本 | 输入 | 输出 |
|---|---|---|
| `scripts/parse_book.py` | PDF 路径 | `book_meta.json` |
| `scripts/build_doc_xml.py` | `book_meta.json` | 飞书文档 XML |
| `scripts/gen_track_rows.py` | 起始日期 + 微习惯名 | 30 天打卡批量 JSON |
| `scripts/gen_diag_rows.py` | `book_meta.json` | 诊断维度批量 JSON |
| `scripts/run.sh` | PDF 路径 + 起始日期 | 一键端到端执行 |

## 前置约束

1. 先按 `lark-shared` skill 的 `source_lark_cli_env.sh` 加载环境
2. PDF 解析依赖 `pdf` skill(轻量引擎 PyMuPDF)
3. 诊断字段不要写死成 Hill 8 维度——必须从书本内容动态推导
4. 微习惯必须满足"小到不可能失败"原则(50 字 / 1 个俯卧撑量级)
5. `+record-batch-create` 用 `--json` 接 `{"fields":[...],"rows":[[...]]}` 格式
6. `--json` 因 wrapper 重置 CWD,必须用 `JSON=$(cat file) && --json "$JSON"`

## 参考实现案例

`examples/perfect-imperfectionist/` 目录下保留了《如何成为不完美主义者》的完整产物(book_meta.json + doc.xml + 两张 base 的字段+行 JSON),作为新书生成时的对照模板。

## 失败处理

- PDF 抽取章节失败 → 退回到目录页文字 OCR
- LLM 抽取维度数 < 4 → 提示"本书可能不适合精读工作台模式"
- lark-cli 任一步失败 → 保存中间产物到 `/tmp/<book>/`,允许从断点续跑
