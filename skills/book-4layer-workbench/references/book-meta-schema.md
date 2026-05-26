# book-meta JSON Schema

`book_meta.json` 是本 skill 的核心中间产物,所有后续脚本都基于它生成。

```jsonc
{
  "title": "如何成为不完美主义者",
  "author": "[美]斯蒂芬·盖斯",
  "one_sentence": "不完美主义不是放弃高标准,而是把高标准从'结果'转移到'是否在做'上。",
  "page_count": 240,

  "chapters": [
    {
      "no": 1,
      "title": "第1章 我是完美主义者吗",
      "one_sentence": "完美主义是消极心态,不是'高标准'的褒义词。",
      "key_points": ["完美主义 ≠ 追求卓越", "8 维度自评", "找出 Top 3 病灶"],
      "action": "做 8 维度自评,标记 Top 3"
    }
  ],

  "diagnostic_dimensions": [
    {
      "name": "整洁有序",
      "category": "内心自觉型",
      "definition": "需要环境 / 流程 / 文件极度有序才能开始做事",
      "chapter_ref": "第4章",
      "counter_actions": "故意在不整洁的环境下完成 1 件事"
    }
  ],

  "action_strategies": [
    {"group": "A.整体", "no": 1, "name": "重新定义完美主义", "desc": "把'我是完美主义者'改说'我有完美主义倾向,正在改'"},
    {"group": "B.过高期待", "no": 2, "name": "觉察期待", "desc": "做事前 30 秒先问'我对这件事的预期是什么?'"}
  ],

  "micro_habits": [
    "叛逆练习:每天 1 件不在意他人评价的小事",
    "成绩日志:每晚记 3 件做成的事",
    "本可以替换本应该"
  ]
}
```

## 字段责任划分

| 字段 | 由谁生成 |
|---|---|
| `title`, `author`, `chapters[].title` | `parse_book.py` 从 PDF 元数据/章节启发式抽取 |
| `chapters[].one_sentence/key_points/action` | Agent LLM 基于 `head_excerpt + tail_excerpt` 抽取 |
| `one_sentence` | Agent LLM 通读章节总结生成 |
| `diagnostic_dimensions[]` | Agent LLM 找出本书的"症状维度分类法" |
| `action_strategies[]` | Agent LLM 抽取全书所有可操作动作,归类到 A-F 组 |
| `micro_habits[]` | Agent LLM 从 action_strategies 里选 3 个"小到不可能失败"的 |

## 校验规则

- `chapters` 长度 ≥ 5
- `diagnostic_dimensions` 长度在 4~12 之间(< 4 提示"本书不适合"; > 12 合并)
- `action_strategies` 长度在 10~30 之间
- `micro_habits` 长度严格 = 3
