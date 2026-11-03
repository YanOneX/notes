#!/usr/bin/env python3
"""把 video2book 的产物导入 Quartz 笔记库。

用法：
    python tools/import_video2book.py --src "D:/video2book/output/计算机网络"
    python tools/import_video2book.py --src ... --course 计算机网络 --with-subtitles
    python tools/import_video2book.py --src ... --dry-run

它会做四件事：
  1. 把 video2book 的 articles / textbooks / notes / subtitles 映射到
     content/课程/<课程名>/ 下对应的子目录，图片等附件按原相对路径一起搬，
     保证笔记里的相对链接不断。
  2. 给每篇笔记补 frontmatter（title / tags / date），已有 frontmatter 的只做合并。
  3. 重建 content/课程/<课程名>/index.md 里的目录块（<!-- AUTO:START --> 之间）。
  4. 重建 content/index.md 里的课程列表（<!-- COURSES:START --> 之间）。

只依赖标准库，不需要 pip install 任何东西。
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

# video2book 子目录 -> 站内子目录
TYPE_MAP = {
    "articles": ("精读长文", "精读长文"),
    "textbooks": ("整编教材", "整编教材"),
    "notes": ("复习笔记", "复习笔记"),
    "subtitles": ("逐字稿", "逐字稿"),
}

FM_DELIM = re.compile(r"^---\s*$", re.MULTILINE)
H1 = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)


def split_frontmatter(text: str) -> tuple[dict, str]:
    """极简 YAML frontmatter 解析：只认 key: value 和 - item 列表。"""
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    head, body = parts[1], parts[2].lstrip("\n")
    meta: dict = {}
    key = None
    for raw in head.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.strip().startswith("#"):
            continue
        if re.match(r"^\s*-\s+", line) and key:
            meta.setdefault(key, [])
            if isinstance(meta[key], list):
                meta[key].append(line.strip()[1:].strip().strip("\"'"))
            continue
        m = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            meta[key] = [] if val == "" else val.strip("\"'")
    return meta, body


def emit_frontmatter(meta: dict) -> str:
    lines = ["---"]
    for k, v in meta.items():
        if isinstance(v, list):
            lines.append(f"{k}:")
            for item in v:
                lines.append(f"  - {json.dumps(str(item), ensure_ascii=False)}")
        else:
            lines.append(f"{k}: {json.dumps(str(v), ensure_ascii=False)}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def yaml_str(value: str) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def strip_md_ext(name: str) -> str:
    return name[:-3] if name.lower().endswith(".md") else name


def import_course(src: Path, vault: Path, course: str, with_subtitles: bool, dry: bool) -> list[Path]:
    course_dir = vault / "课程" / course
    written: list[Path] = []

    for src_sub, (dst_sub, tag) in TYPE_MAP.items():
        sdir = src / src_sub
        if not sdir.is_dir():
            continue
        if src_sub == "subtitles" and not with_subtitles:
            continue
        for item in sorted(sdir.rglob("*")):
            if item.is_dir():
                continue
            if item.name.endswith("_TASK.md") or item.suffix.lower() == ".json":
                continue  # 派发任务书与中间 JSON 不进笔记库
            rel = item.relative_to(sdir)
            dst = course_dir / dst_sub / rel
            if item.suffix.lower() == ".md":
                text = item.read_text(encoding="utf-8", errors="replace")
                meta, body = split_frontmatter(text)
                h1 = H1.search(body)
                title = (meta.get("title") if isinstance(meta.get("title"), str) else None) \
                    or (h1.group(1).strip() if h1 else strip_md_ext(item.name))
                tags = meta.get("tags")
                tags = tags if isinstance(tags, list) else ([tags] if tags else [])
                for t in (course, tag):
                    if t not in tags:
                        tags.append(t)
                meta["title"] = title
                meta["tags"] = tags
                if "date" not in meta:
                    meta["date"] = datetime.fromtimestamp(item.stat().st_mtime).strftime("%Y-%m-%d")
                out_text = emit_frontmatter(meta) + body.lstrip("\n")
                if not dry:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    dst.write_text(out_text, encoding="utf-8")
            else:
                # 图片、代码等附件：按原相对路径搬，笔记里的相对链接才不会断
                if not dry:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dst)
            written.append(dst)

    return written


def _short_title(title: str, limit: int = 20) -> str:
    """章节/知识点短名：冒号前、去空格与非法文件名字符，并清掉截断留下的残句。"""
    s = re.split(r"[：:]", title, maxsplit=1)[0].strip()
    # 少数字段会被上游截断成「if进阶(if」「语法」这类残句，先去掉没闭合的括号段
    s = re.sub(r"[（(][^）)]*[）)]", "", s)
    s = re.sub(r"[（(][^）)]*$", "", s)
    s = re.sub(r'[\\/:*?"<>|\s]+', "", s)
    s = s.strip("-—·、,，.。;；+")
    return (s or "未命名")[:limit]


def _split_sections(body: str) -> list[tuple[str, str]]:
    """把一篇笔记按 `## ` 切成知识点小节。"""
    out: list[tuple[str, str]] = []
    name: str | None = None
    buf: list[str] = []
    for ln in body.splitlines():
        if ln.startswith("## "):
            if name is not None:
                out.append((name, "\n".join(buf).strip("\n")))
            name, buf = ln[3:].strip(), []
        elif ln.startswith("# "):
            continue
        else:
            buf.append(ln)
    if name is not None:
        out.append((name, "\n".join(buf).strip("\n")))
    return out


def _dedent_bullets(body: str) -> str:
    """笔记里的条目用 4 空格缩进模拟层级，Quartz 会把整段渲染成 <pre>；导入时压平缩进。"""
    out = []
    for ln in body.splitlines():
        while ln.startswith("    "):
            ln = ln[4:]
        out.append(ln)
    return "\n".join(out)


def import_course_chapter(src: Path, vault: Path, course: str, with_subtitles: bool, dry: bool) -> list[Path]:
    """章节布局：一章一个文件夹，内含按知识点编号的笔记与 精读长文/ 子目录。"""
    course_dir = vault / "课程" / course
    plan = json.loads((src / "note_plan.json").read_text(encoding="utf-8"))
    block_topic: dict[int, str] = {}
    bp_file = src / "block_plan.json"
    if bp_file.is_file():
        bp = json.loads(bp_file.read_text(encoding="utf-8"))
        for b in bp["blocks"] if isinstance(bp, dict) else bp:
            title = re.sub(r"^\d+\.\s*", "", str(b.get("title", "")))
            block_topic[int(b["block_id"])] = title.split("-")[-1]
    folder = {n["note_id"]: f"{n['note_id']:02d}-{_short_title(n['note_title'])}" for n in plan}
    # note_plan.json 里可选的 topics: {"块号": "短名"}，优先于从块标题裁出来的名字
    topic_override: dict[int, str] = {}
    for n in plan:
        for k, v in (n.get("topics") or {}).items():
            topic_override[int(k)] = str(v)
    block2note = {b: n["note_id"] for n in plan for b in n["blocks"]}
    written: list[Path] = []

    # 精读长文 → <章>/精读长文/NN-<短名>.md
    art_dir = src / "articles"
    if art_dir.is_dir():
        counter: dict[int, int] = {}
        for f in sorted(art_dir.glob("*.md")):
            if f.name.endswith("_TASK.md"):
                continue
            m = re.match(r"模块(\d+)_", f.name)
            if not m or int(m.group(1)) not in block2note:
                continue
            nid = block2note[int(m.group(1))]
            counter[nid] = counter.get(nid, 0) + 1
            text = f.read_text(encoding="utf-8", errors="replace")
            meta, body = split_frontmatter(text)
            h1 = H1.search(body)
            title = meta.get("title") if isinstance(meta.get("title"), str) else None
            title = title or (h1.group(1).strip() if h1 else strip_md_ext(f.name))
            tags = meta.get("tags") if isinstance(meta.get("tags"), list) else []
            for t in (course, "精读长文", _short_title(next(n["note_title"] for n in plan if n["note_id"] == nid))):
                if t not in tags:
                    tags.append(t)
            meta["title"] = title
            meta["tags"] = tags
            meta.setdefault("date", datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d"))
            dst = course_dir / folder[nid] / "精读长文" / f"{counter[nid]:02d}-{_short_title(topic_override.get(int(m.group(1)), block_topic.get(int(m.group(1)), title)))}.md"
            if not dry:
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_text(emit_frontmatter(meta) + body.lstrip("\n"), encoding="utf-8")
            written.append(dst)

    # 复习笔记 → <章>/NN-<知识点>.md（按 ## 拆篇）
    note_dir = src / "notes"
    if note_dir.is_dir():
        for f in sorted(note_dir.glob("*.md")):
            if f.name.endswith("_TASK.md"):
                continue
            m = re.match(r"笔记(\d+)_", f.name)
            if not m:
                continue
            note = next((n for n in plan if n["note_id"] == int(m.group(1))), None)
            if not note:
                continue
            _, body = split_frontmatter(f.read_text(encoding="utf-8", errors="replace"))
            for i, (name, content) in enumerate(_split_sections(body), 1):
                title = name.strip()
                meta = {
                    "title": title,
                    "tags": [course, "复习笔记", _short_title(note["note_title"])],
                    "date": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d"),
                }
                dst = course_dir / folder[note["note_id"]] / f"{i:02d}-{title.replace(' ', '')}.md"
                if not dry:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    dst.write_text(
                        emit_frontmatter(meta) + f"# {title}\n\n" + _dedent_bullets(content) + "\n",
                        encoding="utf-8",
                    )
                written.append(dst)

    # 其它子目录（教材/逐字稿）保持课程级扁平结构
    for src_sub, (dst_sub, tag) in TYPE_MAP.items():
        if src_sub in ("articles", "notes"):
            continue
        sdir = src / src_sub
        if not sdir.is_dir() or (src_sub == "subtitles" and not with_subtitles):
            continue
        for item in sorted(sdir.rglob("*")):
            if item.is_dir() or item.name.endswith("_TASK.md") or item.suffix.lower() == ".json":
                continue
            dst = course_dir / dst_sub / item.relative_to(sdir)
            if not dry:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dst)
            written.append(dst)

    return written


def rebuild_course_index(vault: Path, course: str, dry: bool) -> None:
    course_dir = vault / "课程" / course
    index = course_dir / "index.md"
    sections = []
    for sub in ("精读长文", "整编教材", "复习笔记", "逐字稿"):
        d = course_dir / sub
        if not d.is_dir():
            continue
        files = sorted(p for p in d.glob("*.md"))
        if not files:
            continue
        lines = [f"### {sub}", ""]
        for f in files:
            text = f.read_text(encoding="utf-8", errors="replace")
            meta, body = split_frontmatter(text)
            h1 = H1.search(body)
            title = meta.get("title") or (h1.group(1) if h1 else strip_md_ext(f.name))
            lines.append(f"- [{title}]({sub}/{f.name})")
        lines.append("")
        sections.append("\n".join(lines))

    block = "<!-- AUTO:START -->\n" + "\n".join(sections).rstrip() + "\n<!-- AUTO:END -->"

    if index.exists():
        text = index.read_text(encoding="utf-8")
        if "<!-- AUTO:START -->" in text and "<!-- AUTO:END -->" in text:
            new = re.sub(
                r"<!-- AUTO:START -->.*?<!-- AUTO:END -->", block, text, flags=re.DOTALL
            )
        else:
            new = text.rstrip() + "\n\n## 目录\n\n" + block + "\n"
    else:
        new = (
            f"---\ntitle: {yaml_str(course)}\ntags:\n  - 课程概览\n---\n\n"
            f"# {course}\n\n## 目录\n\n{block}\n"
        )
    if not dry:
        index.parent.mkdir(parents=True, exist_ok=True)
        index.write_text(new, encoding="utf-8")


def rebuild_root_index(vault: Path, dry: bool) -> None:
    root = vault / "index.md"
    if not root.exists():
        return
    course_root = vault / "课程"
    lines = []
    for d in sorted(p for p in course_root.iterdir() if p.is_dir()) if course_root.is_dir() else []:
        if d.name.startswith("."):
            continue
        desc = ""
        idx = d / "index.md"
        if idx.exists():
            meta, _ = split_frontmatter(idx.read_text(encoding="utf-8", errors="replace"))
            desc = meta.get("description") or ""
        suffix = f" —— {desc}" if desc else ""
        lines.append(f"- [{d.name}](课程/{d.name}/){suffix}")
    if not lines:
        lines = ["- （还没有课程，导入一门试试）"]

    block = "<!-- COURSES:START -->\n" + "\n".join(lines) + "\n<!-- COURSES:END -->"
    text = root.read_text(encoding="utf-8")
    if "<!-- COURSES:START -->" in text and "<!-- COURSES:END -->" in text:
        new = re.sub(r"<!-- COURSES:START -->.*?<!-- COURSES:END -->", block, text, flags=re.DOTALL)
    else:
        new = text.rstrip() + "\n\n## 课程目录\n\n" + block + "\n"
    if not dry:
        root.write_text(new, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="导入 video2book 产物到 Quartz 笔记库")
    ap.add_argument("--src", required=True, help="video2book 的课程工作区目录（含 articles/textbooks/notes）")
    ap.add_argument("--course", help="课程名，默认取 --src 的目录名")
    ap.add_argument("--vault", default="content", help="Quartz content 目录，默认 content")
    ap.add_argument("--with-subtitles", action="store_true", help="连逐字稿一起导入（体积很大，默认不导）")
    ap.add_argument("--dry-run", action="store_true", help="只打印计划，不写文件")
    ap.add_argument("--flat", action="store_true", help="用旧的扁平布局（不按章节文件夹拆分）")
    args = ap.parse_args()

    src = Path(args.src).expanduser().resolve()
    if not src.is_dir():
        print(f"[x] 找不到目录：{src}", file=sys.stderr)
        return 1
    vault = Path(args.vault).expanduser().resolve()
    if not vault.is_dir():
        print(f"[x] 找不到 content 目录：{vault}（在仓库根目录运行本脚本）", file=sys.stderr)
        return 1

    course = args.course or src.name
    subs = [s for s in TYPE_MAP if (src / s).is_dir()]
    if not subs:
        print(f"[x] {src} 下没有 articles/textbooks/notes 子目录，不像是 video2book 产物", file=sys.stderr)
        return 1

    print(f"源目录 : {src}")
    print(f"课程名 : {course}")
    print(f"输出到 : {vault / '课程' / course}")
    print(f"子目录 : {', '.join(subs)}" + ("" if args.with_subtitles else "（逐字稿跳过）"))

    chapter_layout = (src / "note_plan.json").is_file() and not args.flat
    if chapter_layout:
        print("布局   : 章节文件夹（一章一夹 + 按知识点拆篇）")
        written = import_course_chapter(src, vault, course, args.with_subtitles, args.dry_run)
    else:
        print("布局   : 扁平（articles/notes/textbooks 三大目录）")
        written = import_course(src, vault, course, args.with_subtitles, args.dry_run)
        rebuild_course_index(vault, course, args.dry_run)
    rebuild_root_index(vault, args.dry_run)

    md = sum(1 for p in written if p.suffix.lower() == ".md")
    asset = len(written) - md
    print(f"\n[ok] {md} 篇笔记、{asset} 个附件" + ("（dry-run，未写盘）" if args.dry_run else ""))
    print("下一步：npm run quartz build --serve  本地预览；git add -A && git commit && git push 发布")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
