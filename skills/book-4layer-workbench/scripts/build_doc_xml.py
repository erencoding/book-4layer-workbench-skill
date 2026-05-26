#!/usr/bin/env python3
"""
build_doc_xml.py - 把 book_meta.json 转换为飞书文档 XML

用法:
  python3 build_doc_xml.py <book_meta.json> > doc.xml

book_meta.json 必须包含:
  title, author, one_sentence, chapters[],
  diagnostic_dimensions[], action_strategies[], micro_habits[]
"""

import sys
import json
import html


def esc(s: str) -> str:
    return html.escape(str(s or ""))


def build(meta: dict) -> str:
    out = []
    title = esc(meta["title"])
    author = esc(meta.get("author", ""))
    one = esc(meta.get("one_sentence", ""))

    # 头部 - 今天就做
    out.append(f"<h1>《{title}》四层精读工作台</h1>")
    if author:
        out.append(f"<p><b>作者</b>:{author}</p>")

    out.append(
        '<callout emoji="🚀" background-color="light-green" border-color="green">'
        "<p><b>今天就做(5 分钟启动包)</b>:</p>"
        "<p>① 打开 <b>L3 自我诊断多维表格</b>,每项 1-5 分凭直觉打分(不超过 30 秒/项)</p>"
        "<p>② 找出得分 ≥ 4 的 Top 3,勾上"列入 Top3"</p>"
        "<p>③ 回到本文档 L4 实验设计,从对策清单中选 3 项,小到不可能失败</p>"
        "<p>④ 明天起在 <b>30 天打卡多维表格</b> 每晚 1 分钟勾选</p>"
        "<p><b>就这样。不要为这 5 分钟做更多准备——准备本身就是完美主义。</b></p>"
        "</callout>"
    )

    # L0
    out.append("<h2>L0 全书一句话</h2>")
    out.append(f"<callout emoji=\"💡\"><p>{one}</p></callout>")

    # L1 mindmap
    out.append("<h2>L1 全书思维导图</h2>")
    mm = ["mindmap", f"  root(({title}))"]
    for ch in meta.get("chapters", []):
        ch_title = ch.get("title", f"第{ch.get('no')}章")
        mm.append(f"    {esc(ch_title)}")
        for kp in (ch.get("key_points") or [])[:3]:
            mm.append(f"      {esc(kp)}")
    out.append('<whiteboard type="mermaid">')
    out.append("\n".join(mm))
    out.append("</whiteboard>")

    # L2 章节卡片
    out.append("<h2>L2 章节卡片</h2>")
    out.append("<table>")
    out.append("<thead><tr><th><p>章</p></th><th><p>一句话</p></th><th><p>关键概念</p></th><th><p>可执行动作</p></th></tr></thead><tbody>")
    for ch in meta.get("chapters", []):
        out.append(
            f"<tr><td><p>{esc(ch.get('title'))}</p></td>"
            f"<td><p>{esc(ch.get('one_sentence',''))}</p></td>"
            f"<td><p>{esc(', '.join(ch.get('key_points',[])[:3]))}</p></td>"
            f"<td><p>{esc(ch.get('action',''))}</p></td></tr>"
        )
    out.append("</tbody></table>")

    # L3 引导
    out.append("<h2>L3 自我诊断</h2>")
    out.append('<p>打开配套多维表格,完成自评:<a href="L3_TABLE_URL_PLACEHOLDER">诊断量表</a></p>')

    # L4 对策清单
    out.append("<h2>L4 实验设计——对策清单</h2>")
    by_group: dict[str, list] = {}
    for s in meta.get("action_strategies", []):
        by_group.setdefault(s.get("group", "通用"), []).append(s)
    for grp, items in by_group.items():
        out.append(f"<h3>{esc(grp)}</h3><ol>")
        for it in items:
            out.append(f"<li><b>{esc(it.get('name'))}</b>——{esc(it.get('desc',''))}</li>")
        out.append("</ol>")

    # Top3 选择映射表
    out.append("<h2>L4 → 30 天计划:Top3 映射</h2>")
    out.append(
        '<callout emoji="💡" background-color="light-cyan"><p><b>填写示例</b>(供参考):</p>'
        "<p>1. <b>诊断维度A</b> → 第X章 → 对策n(微习惯描述)</p>"
        "<p>2. <b>诊断维度B</b> → 第Y章 → 对策m(微习惯描述)</p>"
        "<p>3. <b>诊断维度C</b> → 第Z章 → 对策k(微习惯描述)</p></callout>"
    )

    # 配套资源
    out.append("<h2>配套资源</h2>")
    out.append(
        "<ul>"
        '<li><b>L3 自我诊断多维表格</b>:<a href="L3_TABLE_URL_PLACEHOLDER">诊断量表</a></li>'
        '<li><b>30 天打卡多维表格</b>:<a href="L4_TABLE_URL_PLACEHOLDER">打卡表</a></li>'
        "</ul>"
    )

    # 30 天后滚动
    out.append("<h2>🔁 30 天之后:滚动机制</h2>")
    out.append(
        '<callout emoji="🔄" background-color="light-purple">'
        "<p><b>30 天只是验证期</b>。建议:</p></callout>"
        "<ol>"
        "<li>保留 1 个最有效的微习惯,变成永久基础习惯</li>"
        "<li>淘汰 1 个最没效果的</li>"
        "<li>新增 1 个挑战式微习惯</li>"
        "<li>每季度做 1 次诊断重测</li>"
        "<li>把 30 天报告公开发布</li>"
        "</ol>"
    )

    # 求助清单
    out.append("<h2>📞 求助清单</h2>")
    out.append("<table><thead><tr><th><p>症状</p></th><th><p>立刻做的事</p></th></tr></thead><tbody>")
    for sym, fix in [
        ("连续 3 天 0 打卡", "微习惯减半,保证今天能完成"),
        ("看到打卡表就焦虑", "关掉打卡表,只在脑子里默念"今天我做了 X 件小事""),
        ("想推倒重做这个工作台", "立刻停止。今天不动文档,只完成微习惯"),
        ("觉得"自己没变"", "翻诊断表的自评分数列,与第 1 天对比"),
    ]:
        out.append(f"<tr><td><p>{esc(sym)}</p></td><td><p>{esc(fix)}</p></td></tr>")
    out.append("</tbody></table>")

    # 元认知检查
    out.append("<h2>🚨 元认知检查清单(每周复盘前过一遍)</h2>")
    out.append("<ol>")
    for q in [
        "我这周修改了 N 次微习惯定义,因为"觉得现在的不够好"",
        "我没有打卡,是因为"今天做得太敷衍,不算"",
        "我跳过了周复盘,因为"还没到完美状态"",
        "我把"完成"标准悄悄抬高了",
        "我觉得这个计划本身"不够好",想推倒重做",
    ]:
        out.append(f"<li>{esc(q)}</li>")
    out.append("</ol>")
    out.append(
        '<callout emoji="💊" background-color="light-green"><p><b>解药</b>:'
        "出现 ≥ 2 条 → 立刻按"二进制思维"打卡(今天有没有动?有 = 1)。"
        "本周不允许再修改任何微习惯定义。</p></callout>"
    )

    return "\n".join(out)


def main():
    if len(sys.argv) != 2:
        print("usage: build_doc_xml.py <book_meta.json>", file=sys.stderr)
        sys.exit(2)
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        meta = json.load(f)
    print(build(meta))


if __name__ == "__main__":
    main()
