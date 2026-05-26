#!/usr/bin/env python3
"""
gen_diag_rows.py - 把 book_meta.json 的 diagnostic_dimensions 转成 record-batch-create JSON

用法:
  python3 gen_diag_rows.py <book_meta.json> > diag_rows.json
"""

import sys
import json


def main():
    if len(sys.argv) != 2:
        print("usage: gen_diag_rows.py <book_meta.json>", file=sys.stderr)
        sys.exit(2)
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        meta = json.load(f)

    dims = meta.get("diagnostic_dimensions", [])
    fields = ["维度", "类别", "含义说明", "对应章节", "改善对策"]
    rows = [
        [d.get("name", ""), d.get("category", ""), d.get("definition", ""),
         d.get("chapter_ref", ""), d.get("counter_actions", "")]
        for d in dims
    ]
    print(json.dumps({"fields": fields, "rows": rows}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
