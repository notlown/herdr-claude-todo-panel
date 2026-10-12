# Herdr + Claude Code: 3-Spalten-Todo-Panel

Zeigt unter dem Claude-Code-Eingabefeld (z. B. in Herdr) die Aufgabenliste im Kimi-Stil:

```
  In Arbeit                  Fertig                       Warteschlange
  ● läuft gerade (fett)      ✓ zuletzt fertig (neueste oben) ○ noch nicht gestartet
```

- Live: liest die Claude-Aufgabenliste der Sitzung (`~/.claude/tasks/<session>/`) bei jeder Aktualisierung der Statuszeile.
- Befüllt wird sie, wenn Claude seine Aufgaben-Tools nutzt (TaskCreate/TaskUpdate) – einfach sagen: "führ eine Todo-Liste".

## Installation
```
./install.sh
```
Dann Claude Code neu starten. `Ctrl+T` klappt Claudes eigene Liste ein, damit sie nicht doppelt steht.
Voraussetzung: python3 (ohne Zusatzpakete), Terminal mit Truecolor.
