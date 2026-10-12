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
import subprocess
import time
import sys
import unicodedata

RESET, BOLD, STRIKE = "\033[0m", "\033[1m", "\033[9m"
rgb = lambda r, g, b: f"\033[38;2;{r};{g};{b}m"  # noqa: E731
ACCENT, OK, GREY, TEXT = rgb(215, 119, 87), rgb(78, 200, 126), rgb(136, 136, 136), rgb(224, 224, 224)
LEAD = re.compile(r"^[\s✅🔨⏳❓]+")
MAX_ROWS = 5


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

    # status-line commands get no tty: ask Herdr for this pane's real width (cached 30 s), so the three
    # columns can fill the whole bottom area without a row ever wrapping (captain 2026-10-12)
    total = 120
    pane = os.environ.get("HERDR_PANE_ID", "")
    cache = f"/tmp/statusline-width-{pane.replace(':', '_')}"
    try:
        if pane and os.path.exists(cache) and time.time() - os.path.getmtime(cache) < 5:
            total = int(open(cache).read())
        elif pane:
            lay = json.loads(subprocess.run(["herdr", "pane", "layout"], capture_output=True, text=True,
                                            timeout=1.5).stdout)["result"]["layout"]
            w = next(x["rect"]["width"] for x in lay["panes"] if x["pane_id"] == pane)
            total = max(60, w - 4)
            open(cache, "w").write(str(total))
    except Exception:  # noqa: BLE001
        pass
    cap = total // 3 - 2

    def stamp(t):
        """In Arbeit: 'seit N min' (< 2 h) else 'seit HH:MM'; Fertig: 'HH:MM'; Warteschlange: 'seit HH:MM'."""
        ts = t.get("_mtime") or 0
        if not ts:
            return ""
        hm = time.strftime("%H:%M", time.localtime(ts))
        if t["status"] == "in_progress":
            mins = int((time.time() - ts) // 60)
            return f"seit {mins} min" if mins < 120 else f"seit {hm}"
        return hm if t["status"] == "completed" else f"seit {hm}"

    def column(title, color, items, glyph, style, more_word, limit=MAX_ROWS, badge=("", 0)):
        # title row carries the column's own counter in the column colour (captain 2026-10-12)
        rows = [(f"{BOLD}{color}{title}{RESET} {badge[0]}", width(title) + 1 + badge[1])]
        if len(items) > limit:
            limit = max(0, limit - 1)  # last visible row becomes the "+N" line, so height never exceeds the cap
        for t in items[:limit]:
            st = stamp(t)
            subj = LEAD.sub("", t.get("subject", ""))
            act = (t.get("activeForm") or "").strip()
            if t["status"] == "in_progress" and act and act.lower() not in subj.lower():
                subj = f"{subj} – {act}"  # what Claude is doing right now (colleague idea 3)
            txt = clip(subj, cap - 3 - (len(st) + 1 if st else 0))
            tail = f" {GREY}{st}{RESET}" if st else ""
            rows.append((f"{glyph} {style}{txt}{RESET}{tail}", 2 + width(txt) + (len(st) + 1 if st else 0)))
        if len(items) > limit:
            m = f"… +{len(items) - limit} {more_word}"
            rows.append((f"{GREY}{m}{RESET}", width(m)))
        return rows

    # captain 2026-10-12: the panel is exactly as tall as "In Arbeit" needs; the other columns cut to that
    height = max(1, len(doing))
    n_done, n_all = len(done), len(tasks)
    filled = round(10 * n_done / n_all) if n_all else 0
    # progress as a pill like the other two counters: " 8/26 " in orange, the done share in full orange and
    # the rest in a darker orange, so it reads as a counter and a bar at once (captain 2026-10-12)
    cells = f" {n_done}/{n_all} "
    bw = len(cells)
    fill = max(1, round(bw * n_done / n_all)) if n_all and n_done else 0
    bar = (f"\033[1;38;2;255;255;255;48;2;215;119;87m{cells[:fill]}"
           f"\033[1;38;2;255;255;255;48;2;170;100;78m{cells[fill:]}{RESET}")
    bar_w = bw
    cols = [
        column("In Arbeit", ACCENT, doing, f"{BOLD}{ACCENT}●{RESET}", f"{BOLD}{TEXT}", "weitere", limit=len(doing),
               badge=(bar, bar_w)),
        column("Fertig", OK, done, f"{OK}✓{RESET}", f"{STRIKE}{GREY}", "ältere", limit=height,
               badge=(f"\033[1;38;2;255;255;255;48;2;78;200;126m {len(done)} {RESET}", len(str(len(done))) + 2)),
        column("Warteschlange", GREY, queued, f"{GREY}○{RESET}", TEXT, "weitere", limit=height,
               badge=(f"\033[1;38;2;255;255;255;48;2;160;160;168m {len(queued)} {RESET}", len(str(len(queued))) + 2)),
    ]
    widths = [cap + 3 for _ in cols]  # equal thirds: use the whole bottom width
    lines = []
    # captain 2026-10-12: counter for open questions that block work (items marked with ❓)
    asks = [t for t in tasks if t["status"] != "completed" and t.get("subject", "").lstrip().startswith("❓")]
    open_ids = {str(t.get("id")) for t in tasks if t["status"] != "completed"}
    blocked = [t for t in tasks if t["status"] != "completed"
               and any(str(b) in open_ids for b in (t.get("blockedBy") or []))]
    # blocked / questions sit at the right edge of the title row, like a window's close button
    flags, flags_w = "", 0
    if asks:
        t = f"❓ {len(asks)} Rückfrage{'n' if len(asks) != 1 else ''}"
        flags += f"{BOLD}\033[38;2;245;165;36m{t}{RESET}  "
        flags_w += width(t) + 2
    if blocked:
        t = f"⛔ {len(blocked)} blockiert"
        flags += f"{BOLD}\033[38;2;239;68;68m{t}{RESET}"
        flags_w += width(t)
    for i in range(max(len(c) for c in cols)):
        line = "\u2800\u2800"
        for j, c in enumerate(cols):
            txt, w = c[i] if i < len(c) else ("", 0)
            # no-break spaces: Claude's status line collapses leading/plain whitespace, which shifted a
            # later column under an empty earlier one (captain bug report 2026-10-12)
            line += txt + ("\u2800" * (widths[j] - w) if j < len(cols) - 1 else "")
            used = 2 + sum(widths[:j]) + w
        if i == 0 and flags:
            line += "\u2800" * max(1, total - used - flags_w) + flags
        lines.append(line.rstrip(" \u2800"))
    # two padding rows so the panel does not sit on the window's bottom edge (captain 2026-10-12);
    # a no-break space survives the status line's blank-line trimming
    lines += ["\u2800", "\u2800"]
    print("\n".join(lines))


if __name__ == "__main__":
    main()
