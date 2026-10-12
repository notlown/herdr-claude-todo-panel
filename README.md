# 📋 Herdr + Claude Code: 3-Spalten-Todo-Panel

Zeigt unter dem Claude-Code-Eingabefeld (ideal in [Herdr](https://herdr.dev)) die Aufgabenliste von Claude im Kimi-Stil – in drei Spalten über die volle Fensterbreite:

```
  In Arbeit                         Fertig                             Warteschlange
  ● läuft gerade (fett, orange)     ✓ zuletzt fertig (neueste oben)    ○ noch nicht gestartet
```

## ✨ Features

- **Live:** liest bei jeder Aktualisierung der Statuszeile die Aufgabenliste der Sitzung (`~/.claude/tasks/<session>/`).
- **3 Spalten:** In Arbeit · Fertig (neueste zuerst) · Warteschlange. Die Höhe bestimmt „In Arbeit“ (alle laufenden Aufgaben); Fertig und Warteschlange werden auf diese Höhe gekürzt, die letzte Zeile zeigt dann „… +N“.
- **Volle Breite:** fragt in Herdr die echte Fensterbreite ab (`herdr pane layout`, 30 s gecacht) und teilt sie in drei gleich breite Spalten; ohne Herdr 120 Zeichen. Zeilen brechen nie um.
- **Zähler in den Spaltenköpfen:** In Arbeit mit orangem Fortschrittsbalken, Zahl „8/26“ im Balken, Fertig und Warteschlange mit ihrer Anzahl als farbige Plakette – alle drei im gleichen Plaketten-Stil in der Spaltenfarbe; „⛔ N blockiert“ (offenes `blockedBy`) und „❓ N Rückfragen“ rechts am Rand wie ein Schließen-Knopf.
- **Was gerade passiert:** bei „In Arbeit“ hängt hinter dem Titel Claudes `activeForm`-Text.
- **Zeitstempel:** In Arbeit „seit N min“ (ab 2 h „seit HH:MM“), Fertig mit Uhrzeit, Warteschlange „seit HH:MM“.
- **Kimi-Look:** Kimis Glyphen und Grautöne, Akzentfarbe Claude-Orange; Fertiges durchgestrichen.
- Keine Abhängigkeiten außer `python3`.

Befüllt wird das Panel, wenn Claude seine Aufgaben-Tools nutzt – einfach sagen: „führ eine Todo-Liste“.

## 🚀 Installation

```
git clone https://github.com/notlown/herdr-claude-todo-panel.git
cd herdr-claude-todo-panel && ./install.sh
```

Dann Claude Code neu starten und `Ctrl+T` drücken, damit Claudes eigene Liste eingeklappt ist (sonst steht sie doppelt).

`install.sh` legt Sicherungen an und:
- kopiert `statusline-todo.py` nach `~/.claude/`,
- setzt in `~/.claude/settings.json` die Statuszeile sowie `CLAUDE_CODE_ENABLE_TASKS=1` und `CLAUDE_CODE_ENABLE_TODO_TOOLS=1`,
- stellt in Herdr (falls installiert) die Nutzungsbalken auf „detailed“ (5-Stunden- **und** Wochenfenster).

## 🧰 Tech

Python 3 (Standardbibliothek), Claude Code `statusLine`, optional Herdr-CLI.

## 📁 Struktur

| Datei | Zweck |
|---|---|
| `statusline-todo.py` | rendert das Panel |
| `install.sh` | Installation für Claude Code + Herdr |
