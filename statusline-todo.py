#!/usr/bin/env python3
"""Claude Code statusLine: Kimi-style todo panel under the prompt (captain 2026-10-12).

Three columns (captain 2026-10-12), Kimi's glyphs and greys with Claude's orange accent:
  In Arbeit            Fertig                      Warteschlange
  ● in progress (bold)  ✓ newest done first (struck) ○ not started
Done is ordered by task-file modification time, the others by creation order. Reads ~/.claude/tasks/<session or CLAUDE_CODE_TASK_LIST_ID>/*.json.
"""
import glob
import json
import os
import re
import shutil
import sys
import unicodedata

RESET, BOLD, STRIKE = "\033[0m", "\033[1m", "\033[9m"
rgb = lambda r, g, b: f"\033[38;2;{r};{g};{b}m"  # noqa: E731
ACCENT, OK, GREY, TEXT = rgb(215, 119, 87), rgb(78, 200, 126), rgb(136, 136, 136), rgb(224, 224, 224)
LEAD = re.compile(r"^[\s✅🔨⏳❓]+")
MAX_ROWS = 6


def width(s):
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 0 if unicodedata.combining(c) else 1 for c in s)


def clip(s, n):
    out, w = "", 0
    for c in s:
        cw = width(c)
        if w + cw > n - 1:
            return out + "…"
        out, w = out + c, w + cw
    return out


def main():
    try:
        ev = json.load(sys.stdin)
    except Exception:  # noqa: BLE001
        ev = {}
    list_id = os.environ.get("CLAUDE_CODE_TASK_LIST_ID") or ev.get("session_id") or ""
    tasks = []
    for f in glob.glob(os.path.expanduser(f"~/.claude/tasks/{list_id}/*.json")):
        try:
            t = json.load(open(f))
            t["_mtime"] = os.path.getmtime(f)
        except Exception:  # noqa: BLE001
            continue
        if t.get("status") in ("pending", "in_progress", "completed"):
            tasks.append(t)
    if not tasks:
        return
    num = lambda t: int(t["id"]) if str(t.get("id", "")).isdigit() else 0  # noqa: E731
    doing = sorted((t for t in tasks if t["status"] == "in_progress"), key=num)
    queued = sorted((t for t in tasks if t["status"] == "pending"), key=num)
    done = sorted((t for t in tasks if t["status"] == "completed"), key=lambda t: -t["_mtime"])

    total = max(90, shutil.get_terminal_size((180, 20)).columns - 4)
    cap = total // 3 - 2

    def column(title, color, items, glyph, style, more_word):
        rows = [(f"{BOLD}{color}{title}{RESET}", width(title))]
        for t in items[:MAX_ROWS]:
            txt = clip(LEAD.sub("", t.get("subject", "")), cap - 2)
            rows.append((f"{glyph} {style}{txt}{RESET}", 2 + width(txt)))
        if len(items) > MAX_ROWS:
            m = f"… +{len(items) - MAX_ROWS} {more_word}"
            rows.append((f"{GREY}{m}{RESET}", width(m)))
        return rows

    cols = [
        column("In Arbeit", ACCENT, doing, f"{BOLD}{ACCENT}●{RESET}", f"{BOLD}{TEXT}", "weitere"),
        column("Fertig", OK, done, f"{OK}✓{RESET}", f"{STRIKE}{GREY}", "ältere"),
        column("Warteschlange", GREY, queued, f"{GREY}○{RESET}", TEXT, "weitere"),
    ]
    widths = [min(cap, max(w for _, w in c)) + 3 for c in cols]
    lines = []
    for i in range(max(len(c) for c in cols)):
        line = "  "
        for j, c in enumerate(cols):
            txt, w = c[i] if i < len(c) else ("", 0)
            line += txt + (" " * (widths[j] - w) if j < len(cols) - 1 else "")
        lines.append(line.rstrip())
    # two padding rows so the panel does not sit on the window's bottom edge (captain 2026-10-12);
    # a no-break space survives the status line's blank-line trimming
    lines += ["\u00a0", "\u00a0"]
    print("\n".join(lines))


if __name__ == "__main__":
    main()
