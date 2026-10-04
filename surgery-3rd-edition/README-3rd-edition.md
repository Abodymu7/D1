# Surgery Bank — Surgery 1 (General Surgery & Urology) — 3rd Edition (2026)

Data-first project, same engine and principles as the Medicine 2 3rd edition: everything lives in
`data/questions.json`, `data/book.json` and `data/essentials.json`; the PDF and the InDesign (IDML) parts are
regenerated from the data and are never edited by hand.

## Outputs (`output/`)
| File | What |
|---|---|
| `Surgery-Bank-Surgery-1-3rd-Edition.pdf` | the whole book: front matter, 7 parts / 39 chapters, linked index |
| `idml/NN-<chapter>.idml` + `idml/Links/` | one InDesign document per chapter (InDesign 2020+, keep `Links/` next to it) |
| `../data/questions.csv` | every question, for review in Excel |
| `../data/corrections.csv` | log of every change (old value → new value, reason) |

## Where the data came from
* `Surgery_1_Version2.0_IDML.idml` (2nd edition, the user's export of the INDD) was parsed story by story
  (`work`/scratch `surg/parse.py` → `parsed.json`) and converted by `data/import/convert_surg.py`:
  1,381 MCQs and 185 EMQ themes (935 scenarios) in 13 banks, 7 parts. The original text is kept in each record's `orig`.
* `Surgery_Question_Bank.html` — the 39th-batch exams (Surgery 1 Block 2, Block 3, End-induction GS1 Block A,
  final Paper 1 and Paper 2): 178 items, added by `data/import/b39_surg_src.py` (patch `400`).

## What changed from Version 2.0
1. **Edition** — 3rd Edition / 2026. The book is now organised in 7 parts (Neck & Endocrine, Breast, GIT,
   Paediatric Surgery, Abdomen, Urology, Trauma & Critical Care); each part opens with new artwork drawn for its
   subject (thyroid, ductal tree, gut, teddy bear with a sutured tummy, liver–biliary–pancreas–spleen, urinary tract,
   scalpel/suture/monitor) — `build/illus_surg.py`, rendered by `build/art_surg.py`. New chapter
   *Gastrointestinal Tumours* (the tumour questions that were filed under GI bleeding).
2. **Review** — every question was read: wrong keys corrected, empty keys filled (10 MCQs, 20 EMQ scenarios),
   garbled/merged options and stems repaired, misfiled questions moved, EMQ themes whose scenarios had been run
   together split again. Review sheets: `data/review/*.tsv` → `tools/review2patch.py` → patch `300`.
3. **Repeated questions** — one question kept per idea (the earliest source in book order: local exams first);
   the highlighted note *REPEATED n× · ALSO ASKED IN …* under it lists where else it was asked.
4. **Explanations** — every explanation cut to 2–3 lines (≤ ~200 characters) saying why the answer is right; true/false
   (multiple-answer) questions name the false statements; the answer chip lists all true letters (e.g. **A C E**).
5. **Numbering** — restarts for every source inside a chapter. Local exams (39th batch, Ministerial, Formative,
   Previous Years) share one sequence with a sub-heading per source; Essay-to-MCQ and each book (Bailey & Love, Lange,
   SBA, Oxford, PreTest, Get Ahead, Crash Course, Irfan) has its own sequence from 1. EMQs: Theme 1, 2 …, scenarios
   1, 2 … inside each theme, options A–Z.
6. **Summaries → flowcharts** — the old summary tables were removed; each teaching chapter opens with 2–3
   step-by-step management flowcharts built from those summaries and current guidance (NICE, ATLS 10th ed, EAU,
   ESMO, WSES, Tokyo 2018, HerniaSurge, BTA/ATA, ESGE …). Sources: `data/import/flows/flow_*.py` → `merge.py`.
7. **39th batch exams** — added to the chapters they belong to as the first local source. Recalled questions had no
   key: every answer was set and explained; blank options completed with plausible distractors; the OSCE short-answer
   tasks recast as single-best-answer MCQs (Group C/D repeats of Group A/B tasks merged); the 8 unlabelled radiology
   images became image questions (the answer label printed on one CT was removed).
8. **Index** — topics assigned to every question (`tools/autotopics.py`, patch `600`); the index gives page numbers.

## Pictures still needed
61 questions link pictures from the original book (`C:/Users/LCI/Desktop/pic/...`) that were not inside the IDML
export. The PDF shows a labelled frame **FIGURE / file name**; the IDML has a grey placeholder with the same file
name in `Links/`. Copy the real `pic` folder files over those placeholders (same names) and update links in InDesign,
or put them in `assets/pic/` and rebuild. Four images that were embedded in the INDD could not be recovered; those
questions are answerable without them and the image was dropped.

## Rebuild
```
./tools/rebuild_data.sh            # base from the parsed IDML + all patches (review, 39th batch, topics)
python3 data/import/flows/merge.py # flowcharts -> data/essentials.json
python3 build/art_surg.py          # part + cover artwork
python3 build/book.py              # PDF (two passes) + output/pagemap.json
python3 build/idml_book.py neck    # one chapter's IDML (needs the PDF + pagemap)
python3 tools/csvio.py export      # data/questions.csv
```
