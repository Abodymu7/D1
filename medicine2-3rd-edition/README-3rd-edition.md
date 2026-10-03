# Internal Medicine Bank — Medicine 2 — 3rd Edition (2026)

Data-first project: everything lives in `data/questions.json`, `data/book.json` and `data/essentials.json`.
The PDF and the InDesign (IDML) parts are regenerated from the data and are never edited by hand.

## Outputs (`output/`)
| File | What |
|---|---|
| `Internal-Medicine-Bank-Medicine-2-3rd-Edition.pdf` | the whole book: front matter, 19 chapters, linked index |
| `idml/NN-<chapter>.idml` + `idml/Links/` | one InDesign document per chapter (open in InDesign 2020+, keep `Links/` next to it) |
| `questions.csv` | every question, for review in Excel |
| `../data/corrections.csv` | log of every change (old value → new value, reason) |

## What changed from the V4 (2nd-edition) project
1. **Edition** — 3rd Edition / 2026 on cover, title page, colophon and file names. Every chapter divider has new
   artwork drawn for its subject (coronary plaque, dilated heart, septal defects, conduction system + AF strip,
   stenosed valve, pericardial effusion, BP gauge, drugs, stethoscope, asthmatic bronchus, consolidation,
   ARDS + ventilator curves, effusion/pneumothorax, honeycombing, pulmonary embolus, spiculated mass, …) — `build/illus.py`.
2. **Repeated questions** — one question kept per idea, chosen from the earliest source in the chapter
   (local exams first, then the books in chapter order). A highlighted note under it reads
   *REPEATED n× · ALSO ASKED IN …* with the exams/books where it was asked. Patches `300`, `301`.
3. **Explanations** — every explanation (MCQs and each EMQ scenario) cut to 2–3 lines that say why the answer is
   right (patch `302`; drafts in `data/shortex/`). Key fix: `peri-0084` → D (oral amoxicillin, ESC 2023 IE prophylaxis).
4. **Numbering** — restarts for every source inside a chapter. The local exams (39th-batch end-block papers,
   end-block exams 2025, formative & previous-years exams, log book) share one sequence with a sub-heading for each
   source; each international book (Harrison, Davidson, Crash Course, …) has its own sequence from 1.
   EMQs: *Theme 1, Theme 2 …*, scenarios 1, 2 … inside each theme, options A–Z; answers are grouped by theme.
5. **Summaries** — the old summary tables were removed (kept in `data/backups/` only). Each chapter now opens with
   step-by-step management flowcharts (49 charts) built from the source books' summaries and current guidance
   (ESC 2023/2024, NICE, BTS/SIGN, GINA 2025, GOLD 2025, BTS pleural 2023, WHO TB …). Source: `data/import/flow_src.py`.

## Not done — needs the files
The "Questions of 39 batch" **Paper 1** and **Paper 2** files were not attached (only the project zip arrived).
Send them and they will be imported with `tools/import_source.py … --bank "39 Blocks Questions"`, filtered to the
chapters of this book, de-duplicated and numbered in the local-exams sequence.

## Rebuild
```
python build/art.py            # divider + cover artwork
python build/book.py           # PDF (two passes, ~10 min) + output/pagemap.json
python build/idml_book.py cad  # one chapter's IDML (needs the PDF + pagemap)
python tools/csvio.py export   # questions.csv
```
Fonts expected by the PDF build: Source Serif 4, Source Sans 3, Barlow Condensed / Semi Condensed (path `F` in `build/book.py`).
