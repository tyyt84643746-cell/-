# Graph Report - -  (2026-11-12)

## Corpus Check
- Corpus is ~17,490 words - fits in a single context window. You may not need a graph.

## Summary
- 234 nodes · 618 edges · 8 communities (7 shown, 1 thin omitted)
- Extraction: 74% EXTRACTED · 26% INFERRED · 0% AMBIGUOUS · INFERRED: 162 edges (avg confidence: 0.85)
- Token cost: 74,073 input · 0 output

## Community Hubs (Navigation)
- Фоны и слои сцен
- Сцены и эффекты «Блэкаута»
- Рендер и звук
- Сцены и персонажи «Тридцати дней»
- Артём и примитивы рисования
- Описание проекта и персонажи
- Деревня и силуэты

## God Nodes (most connected - your core abstractions)
1. `P` - 41 edges
2. `hero()` - 32 edges
3. `glow()` - 25 edges
4. `ease()` - 22 edges
5. `lerp()` - 20 edges
6. `vgrad()` - 18 edges
7. `scene7()` - 18 edges
8. `layer()` - 17 edges
9. `scene6()` - 17 edges
10. `scene4()` - 17 edges

## Surprising Connections (you probably didn't know these)
- `pop()` --calls--> `clamp()`  [INFERRED]
  series/tridtsat-dney/scenes.py → series/blackout/art.py
- `scene9()` --calls--> `clamp()`  [INFERRED]
  series/tridtsat-dney/scenes.py → series/blackout/art.py
- `box()` --calls--> `mixc()`  [INFERRED]
  series/tridtsat-dney/scenes.py → series/blackout/art.py
- `scene5()` --calls--> `mixc()`  [INFERRED]
  series/tridtsat-dney/scenes.py → series/blackout/art.py
- `scene9()` --calls--> `mixc()`  [INFERRED]
  series/tridtsat-dney/scenes.py → series/blackout/art.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Конвейер производства серии: сценарий → озвучка → сцены → рендер** — readme_script_py, readme_tts_py, readme_voice_timecodes, readme_scenes_py, readme_render_py, readme_ffmpeg [INFERRED 0.85]
- **Постоянные персонажи из blackout/art.py** — readme_art_py, readme_artyom, readme_pyotr_ilyich, readme_sosedka [EXTRACTED 1.00]

## Communities (8 total, 1 thin omitted)

### Community 0 - "Фоны и слои сцен"
Cohesion: 0.07
Nodes (12): layer(), Snow, vgrad(), Balcony, Candles, Door, Home, city() (+4 more)

### Community 1 - "Сцены и эффекты «Блэкаута»"
Cohesion: 0.10
Nodes (24): clamp(), comp(), glow(), lamp_glow(), steam(), card(), flick(), font() (+16 more)

### Community 2 - "Рендер и звук"
Cohesion: 0.08
Nodes (13): audio(), post(), preview(), render_scene(), wrap(), carrier(), _finish(), kolyan() (+5 more)

### Community 3 - "Сцены и персонажи «Тридцати дней»"
Cohesion: 0.15
Nodes (29): ease(), lerp(), cat(), granny(), shovel(), box(), bubble(), ctext() (+21 more)

### Community 4 - "Артём и примитивы рисования"
Cohesion: 0.17
Nodes (7): glow_sprite(), hero(), old_man(), P, woman(), scene7(), scene9()

### Community 5 - "Описание проекта и персонажи"
Cohesion: 0.11
Nodes (23): art.py (blackout) — общая графика и постоянные персонажи, Артём — главный герой, Баба Валя, Как собрать (процедура сборки), chars.py (tridtsat-dney) — персонажи серии, Анимационные серии «Что если…», Шрифт DejaVu Sans Bold, ElevenLabs (озвучка, api.elevenlabs.io) (+15 more)

### Community 6 - "Деревня и силуэты"
Cohesion: 0.12
Nodes (8): mixc(), passenger(), mid(), silhouette(), l(), Village, forest(), Yard

## Knowledge Gaps
- **8 isolated node(s):** `Вертикальный формат 9:16, 1080×1920, 30 fps`, `script.py — текст озвучки по сценам и заголовки`, `render.py preview — лист превью preview.jpg`, `Пётр Ильич — постоянный персонаж`, `Соседка — постоянный персонаж` (+3 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 76 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `P` connect `Артём и примитивы рисования` to `Фоны и слои сцен`, `Сцены и эффекты «Блэкаута»`, `Рендер и звук`, `Сцены и персонажи «Тридцати дней»`, `Деревня и силуэты`?**
  _High betweenness centrality (0.120) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `P` (e.g. with `cat()` and `granny()`) actually correct?**
  _`P` has 14 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Вертикальный формат 9:16, 1080×1920, 30 fps`, `script.py — текст озвучки по сценам и заголовки`, `render.py preview — лист превью preview.jpg` to the rest of the system?**
  _8 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Фоны и слои сцен` be split into smaller, more focused modules?**
  _Cohesion score 0.06755260243632337 - nodes in this community are weakly interconnected._
- **Why does `vgrad()` connect `Фоны и слои сцен` to `Сцены и персонажи «Тридцати дней»`, `Артём и примитивы рисования`, `Деревня и силуэты`?**
  _High betweenness centrality (0.093) - this node is a cross-community bridge._
- **Are the 15 inferred relationships involving `hero()` (e.g. with `.arc()` and `.chord()`) actually correct?**
  _`hero()` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Should `Сцены и эффекты «Блэкаута»` be split into smaller, more focused modules?**
  _Cohesion score 0.10336817653890824 - nodes in this community are weakly interconnected._