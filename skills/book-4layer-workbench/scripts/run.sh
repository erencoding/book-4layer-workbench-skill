#!/usr/bin/env bash
# run.sh - 端到端编排:PDF → 工作台(主文档 + 2 张 Base)
# 用法: ./run.sh <pdf_path> <YYYY-MM-DD>
#
# 注意: 本脚本假定在 Mira Agent 环境中运行,且已加载 lark-cli 环境
# (source /data/plugins/market/lark-shared/skills/lark-shared/scripts/source_lark_cli_env.sh)
# diagnostic_dimensions / action_strategies / one_sentence / micro_habits
# 必须由 Agent 通过 LLM 抽取后补写进 book_meta.json,否则后续步骤会失败。

set -euo pipefail
PDF="${1:?need pdf path}"
START="${2:?need YYYY-MM-DD start date}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORK="${TMPDIR:-/tmp}/book-workbench-$$"
mkdir -p "$WORK"

echo ">> [1/5] parse pdf"
python3 "$SCRIPT_DIR/parse_book.py" "$PDF" "$WORK/raw_meta.json"

echo ">> [2/5] WAIT FOR AGENT: 请 Agent 基于 $WORK/raw_meta.json 抽取以下字段并写入 $WORK/book_meta.json:"
echo "         - one_sentence"
echo "         - chapters[].one_sentence / key_points / action"
echo "         - diagnostic_dimensions[]"
echo "         - action_strategies[]"
echo "         - micro_habits[3]"
echo "完成后再次运行此脚本第二段..."

if [ ! -f "$WORK/book_meta.json" ]; then
  echo "exit: book_meta.json not ready. Agent 需先补写。"
  exit 0
fi

echo ">> [3/5] build doc xml"
python3 "$SCRIPT_DIR/build_doc_xml.py" "$WORK/book_meta.json" > "$WORK/doc.xml"

echo ">> [4/5] gen diag rows"
python3 "$SCRIPT_DIR/gen_diag_rows.py" "$WORK/book_meta.json" > "$WORK/diag_rows.json"

echo ">> [5/5] gen track rows"
TITLE=$(python3 -c "import json,sys;print(json.load(open('$WORK/book_meta.json'))['title'])")
H1=$(python3 -c "import json;m=json.load(open('$WORK/book_meta.json'));print(m['micro_habits'][0])")
H2=$(python3 -c "import json;m=json.load(open('$WORK/book_meta.json'));print(m['micro_habits'][1])")
H3=$(python3 -c "import json;m=json.load(open('$WORK/book_meta.json'));print(m['micro_habits'][2])")
python3 "$SCRIPT_DIR/gen_track_rows.py" "$START" "$H1" "$H2" "$H3" > "$WORK/track_rows.json"

cat <<EOF
>> done. artifacts in $WORK:
  - book_meta.json
  - doc.xml          (用 lark-cli docs +create --type docx --markdown-format xml --content @doc.xml)
  - diag_rows.json   (用 lark-cli base +record-batch-create --json "\$(cat diag_rows.json)")
  - track_rows.json  (同上)

下一步建议 Agent 执行:
  1. 创建主文档 docx
  2. 创建诊断 base + 字段 + 灌入 diag_rows.json
  3. 创建打卡 base + 字段 + 灌入 track_rows.json
  4. 替换 doc.xml 中的 L3_TABLE_URL_PLACEHOLDER / L4_TABLE_URL_PLACEHOLDER 后 update 主文档
EOF
