# book-4layer-workbench-skill

把任意书籍 PDF 转化为「四层精读工作台」的 Mira Agent Skill。

## 输出物

读完一本书,你会得到:

1. **一个飞书文档**——四层精读主文档(L0 一句话 / L1 思维导图 / L2 章节卡片 / L3 自我诊断 / L4 实验设计 + 22 项对策 + 30 天计划 + 滚动机制 + 求助清单 + 元认知检查)
2. **一张飞书多维表格**——自我诊断量表(字段按本书的"症状维度"动态生成)
3. **一张飞书多维表格**——30 天打卡(微习惯 + 周复盘,从书的对策清单里选)

## 适用书籍

最适合:**心理类 / 自助类 / 方法论类 / 工具书**(《非暴力沟通》《原子习惯》《关键对话》《被讨厌的勇气》《如何成为不完美主义者》等)

不太适合:小说 / 散文 / 传记 / 学术专著

## 安装

把 `skills/book-4layer-workbench/` 整个目录扔进你的 Mira Agent skill 目录,或通过 Skill Market 安装。

需要环境:
- Python 3 + `PyMuPDF`
- Mira Agent + `lark-shared` skill(用于飞书写入)
- `pdf` skill(用于 PDF 解析)

## 使用

在 Mira Agent 对话框中:

```
帮我把这本《XXX》做一个四层精读工作台
[上传 PDF]
```

Agent 会自动:
1. 解析 PDF
2. LLM 抽取诊断维度 / 对策清单 / 微习惯
3. 创建飞书文档 + 2 张多维表格
4. 回填表格链接到主文档

## 目录结构

```
skills/book-4layer-workbench/
├── SKILL.md                 # skill 入口
├── references/
│   └── book-meta-schema.md  # 中间 JSON schema
└── scripts/
    ├── parse_book.py        # PDF → raw_meta.json
    ├── build_doc_xml.py     # book_meta.json → 文档 XML
    ├── gen_diag_rows.py     # → 诊断表 record-batch JSON
    ├── gen_track_rows.py    # → 30 天打卡 record-batch JSON
    └── run.sh               # 端到端编排
```

## 参考案例

`examples/perfect-imperfectionist/` 是用本 skill 给《如何成为不完美主义者》生成的完整产物,作为新书生成时的对照模板。

## License

MIT
