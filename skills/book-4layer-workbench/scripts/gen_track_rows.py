#!/usr/bin/env python3
"""
gen_track_rows.py - 生成 30 天打卡表的 record-batch-create JSON

用法:
  python3 gen_track_rows.py <start_date YYYY-MM-DD> <habit1> <habit2> <habit3> > track_rows.json
"""

import sys
import json
import datetime


def main():
    if len(sys.argv) != 5:
        print("usage: gen_track_rows.py <YYYY-MM-DD> <h1> <h2> <h3>", file=sys.stderr)
        sys.exit(2)
    start = datetime.datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
    h1, h2, h3 = sys.argv[2], sys.argv[3], sys.argv[4]

    fields = ["日期", "周次", f"微习惯1:{h1}", f"微习惯2:{h2}", f"微习惯3:{h3}", "当日感受", "是否周复盘"]
    rows = []
    for i in range(30):
        d = start + datetime.timedelta(days=i)
        ts = int(datetime.datetime(d.year, d.month, d.day).timestamp() * 1000)
        week = f"第{i // 7 + 1}周"
        is_review = "是" if (i + 1) % 7 == 0 else ""
        rows.append([ts, week, False, False, False, "", is_review])

    print(json.dumps({"fields": fields, "rows": rows}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
