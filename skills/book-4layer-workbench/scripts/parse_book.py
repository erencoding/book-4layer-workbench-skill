#!/usr/bin/env python3
"""
parse_book.py - 解析书籍 PDF,输出 book_meta.json

用法:
  python3 parse_book.py <pdf_path> <output_json>

依赖:
  - PyMuPDF (fitz) 用于 PDF 解析
  - 调用方需在 Mira Agent 上下文中,把抽取结果再喂给 LLM
    生成 diagnostic_dimensions / action_strategies(本脚本只产出原文)
"""

import sys
import json
import os
import re

try:
    import fitz  # PyMuPDF
except ImportError:
    print("ERROR: need pip install --user --break-system-packages PyMuPDF", file=sys.stderr)
    sys.exit(1)


def extract_pdf(pdf_path: str) -> dict:
    doc = fitz.open(pdf_path)
    meta = doc.metadata or {}

    # 章节启发式: 找形如 "第X章" / "Chapter X" / "X. " 的页面起点
    chapter_pat = re.compile(r"^\s*(第[\d一二三四五六七八九十百]+章|Chapter\s+\d+|\d+[\.\s]\s*\S)", re.M)

    pages = []
    for i, page in enumerate(doc):
        text = page.get_text("text")
        pages.append({"page": i + 1, "text": text})

    # 找章节起始
    chapters = []
    for p in pages:
        m = chapter_pat.search(p["text"][:200])
        if m:
            title_line = p["text"].split("\n", 3)
            title = next((ln.strip() for ln in title_line[:3] if ln.strip()), m.group(1))
            chapters.append({"page": p["page"], "title": title})

    # 抽取章节正文(到下一章前)
    out_chapters = []
    for idx, ch in enumerate(chapters):
        start = ch["page"] - 1
        end = chapters[idx + 1]["page"] - 1 if idx + 1 < len(chapters) else len(pages)
        body = "\n".join(p["text"] for p in pages[start:end])
        # 取前 1500 + 末 800
        head = body[:1500]
        tail = body[-800:] if len(body) > 2300 else ""
        out_chapters.append({
            "no": idx + 1,
            "title": ch["title"],
            "head_excerpt": head,
            "tail_excerpt": tail,
            "word_count": len(body),
        })

    return {
        "title": meta.get("title") or os.path.basename(pdf_path),
        "author": meta.get("author") or "",
        "page_count": len(pages),
        "chapters": out_chapters,
        "_note": "diagnostic_dimensions / action_strategies / one_sentence 需由 Agent LLM 基于本结构补全",
    }


def main():
    if len(sys.argv) != 3:
        print("usage: parse_book.py <pdf> <output.json>", file=sys.stderr)
        sys.exit(2)
    pdf_path, out_path = sys.argv[1], sys.argv[2]
    data = extract_pdf(pdf_path)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"OK: wrote {out_path} ({len(data['chapters'])} chapters)")


if __name__ == "__main__":
    main()
