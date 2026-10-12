#!/bin/bash
# Installs the 3-column Claude Code task panel (In Arbeit | Fertig | Warteschlange) as the Claude status
# line, plus optional Herdr tweaks. Safe to re-run; backs up every file it touches.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
mkdir -p ~/.claude
cp "$here/statusline-todo.py" ~/.claude/statusline-todo.py
s=~/.claude/settings.json; [ -f "$s" ] || echo '{}' > "$s"; cp "$s" "$s.bak-todo-kit"
python3 - "$s" <<'PY'
import json, sys
p = sys.argv[1]; d = json.load(open(p))
d.setdefault("env", {}).update({"CLAUDE_CODE_ENABLE_TASKS": "1", "CLAUDE_CODE_ENABLE_TODO_TOOLS": "1"})
d["statusLine"] = {"type": "command", "command": "python3 ~/.claude/statusline-todo.py", "padding": 0}
json.dump(d, open(p, "w"), indent=2, ensure_ascii=False)
PY
echo "Claude: task tools + 3-column status line installed (restart Claude Code; Ctrl+T collapses Claude's own list)."
if [ -d ~/.config/herdr ]; then
  g=~/.config/herdr/config-gpui.local.toml; touch "$g"; cp "$g" "$g.bak-todo-kit"
  grep -q "todo-kit" "$g" || cat >> "$g" <<'TOML'

# >>> todo-kit: usage bars show 5-hour AND weekly window; fonts with the task-list glyphs
[status_bar]
usage = "detailed"
TOML
  echo "Herdr: detailed usage bars set in $g (merge by hand if you already have a [status_bar] table)."
fi
