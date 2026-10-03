# Review brief — Internal Medicine Bank, Medicine 2 (Cardiorespiratory), 4th edition 2026

You are reviewing one slice of a medical question bank for M.B.Ch.B students (final-year internal medicine level).
Project root: /home/claude/med2book  (always `cd` there). Data: data/questions.json (READ-ONLY for you).
You write review PATCH files only. NEVER run tools/apply.py, never edit data/questions.json, never touch other agents' patch files.

## Tools
- `python3 work/rv.py <chapter> <start-index-or-id> <n> > $SCR/rv.txt` then Read $SCR/rv.txt
  (dumps items: id, [bank pPAGE#NUM], key, IMG=attached images, DUP?=candidate duplicates by text similarity (any chapter),
  stem, options, `~` = the source's own explanation, truncated). 39 Blocks items are listed first. Use n≈30 per dump.
  EMQ themes print their options and items `n) [key] stem`; `notes` may contain the source's raw key as a HINT only.
- Look at any question from any chapter: `python3 -c "import json;Q={q['id']:q for q in json.load(open('data/questions.json'))};import pprint;pprint.pprint(Q['valv-0012'])"`
- Images: `python3 work/qimg.py id1,id2,o120 $SCR/img.png` then Read the PNG (a token like `o120` lists every asset
  image cut from original PDF page 120: files assets/q/oPPP_N.*; 39 Blocks images are q/b39_*). Check EVERY question that has an image
  or whose stem says "shown/below/this ECG/X-ray" — images were attached by position and some are wrong or missing.
- Validate: `python3 work/checkpatch.py 'data/patches/<your prefix>*.json' <chapter> [chapter…]` → must print OK and
  `uncovered: 0` for each of your chapters before you finish.
- $SCR = a scratch dir of your own: `mkdir -p /tmp/claude-0/<your-agent-name>`.

## What to do with EVERY live item (status "original") in your slice
1. **Verify the key** against current guidance (ESC, NICE, AHA/ACC, BTS, GINA, GOLD, ERS/ATS, BHIVA, WHO TB…) and physiology.
   Source keys are often wrong (re-lettering errors, outdated practice, key contradicting its own explanation).
   If you change the key → `"status":"corrected"` + a `why` (one line, factual).
2. **Single best answer**: if two options are defensible, change a distractor or add the discriminating detail to the stem (say so in `why`).
3. **Stem self-contained & clean**: fix OCR/parse garbage, truncated text, units (SI first), "Question V-54 / the patient
   in question 12" references (rewrite to stand alone), letter prefixes, missing data needed to answer. Keep the question's
   substance and level; you may tidy English. If an image is referenced, say "(shown)" / "shown in the image".
4. **Options**: 4–5 plausible options, no duplicates, no merged options, no letter prefixes; if you change `options`
   give the full list and make sure `answer` still points to the right option.
5. **Explanation — ALWAYS write a fresh one** (never copy the source's explanation): 2–4 sentences — why the key is right
   (mechanism, criteria, numbers/thresholds, drug names), why the tempting distractors are wrong, and the practical next
   step/guideline point. British spelling (haemoglobin, oedema, oesophagus, anaemia, paediatric, adrenaline, furosemide,
   ciclosporin), SI units, en dash for ranges (2–4). **No option letters** in explanations ("the answer is B" is forbidden).
   EMQ item explanations: 1–3 sentences each.
6. **topics**: 1–3 specific terms (disease/test/drug/sign, Title case first word, e.g. ["Atrial fibrillation","Anticoagulation"]).
   A generic facet ("ECG", "Chest X-ray", "Management") may be added as an extra.
7. **Chapter**: if an item is clearly misfiled, you may add `"chapter":"<id>"` in `set` (ids below). Do not move 39 Blocks items.
8. **Images**: remove a wrong image (`"images": []`), attach the right one from assets (`"images": ["q/o120_2.png"]`),
   or, if a needed image is missing and cannot be found, rewrite the stem to describe the finding in words.

## Duplicates — THE USER'S RULE (follow exactly)
Delete questions whose IDEA is repeated. BUT: a question may share the same scientific answer and still be kept if its
framing makes the student think — a harder type or a different level (e.g. a clinical vignette requiring diagnosis vs a
one-line recall question; a data-interpretation version; a question asking the mechanism vs the drug name). Those are
KEPT, not deleted. Only delete when the idea AND the level/framing are essentially the same.
When you delete a duplicate you MUST give `dup_of` = the id of the survivor — a highlighted caption on the survivor will
later say how many times and in which sources that idea was repeated, so accuracy matters.
- Keep the better one: 39 Blocks Questions first; otherwise the better-written/harder one, and prefer the earlier bank
  in this order: 39 Blocks Questions, End-Block Exams, Formative & Previous Years, Log Book, Davidson, Harrison,
  Crash Course, PreTest, Passmedicine, PasTest, Irfan, Get Ahead, Other Sources. (If the better-written one is from a
  later bank, keep it anyway — the caption lists all sources.)
- Ordering rules (checkpatch enforces them, to avoid cycles between agents): a 39 Blocks item is never deleted in favour
  of a non-39B item; otherwise `dup_of` must point to your own chapter or an EARLIER chapter in book order
  (cad hf chd arr valv peri htn cpharm cvsx cvsemq airway resinf crit pleura ild pvasc lca resx resemq), except that
  any non-39B item may point to a 39B item in any chapter. Never point to an item that is already deleted.
- `"silent": true` only when the deleted item is the SAME question printed twice in the SAME bank (a reprint), or a
  parse fragment — it will not count in the repeat caption. Parse fragments / non-questions: delete with a `why` and no dup_of.
- MCQs and EMQs are not duplicates of each other. EMQ themes may duplicate other EMQ themes (delete whole theme, or a single
  item via `"items": {"3": {"delete": true}}` is NOT supported — instead keep the theme and rewrite that item into a new
  scenario, or leave it).
- DUP? hints are only candidates: judge each one yourself; also catch duplicates the hint missed.

## EMQ themes (cvsemq, resemq)
Re-key EVERY item from scratch (the source keys are unreliable and often scrambled between themes). Letters must exist
in option_letters. If the right answer is missing from the list, add an option (append to `options` and `option_letters`).
Fix the theme title and lead-in if garbled. Give `topics` for the theme. Every item gets an explanation.

## Patch format (JSON list, one op per item; write in UTF-8; ~30–40 ops per file)
```json
[
{"id":"arr-0031","status":"expanded","set":{"topics":["Atrial fibrillation","Alcohol"],"explanation":"Alcohol is a well-established trigger ... hypertension rather than hypotension."}},
{"id":"hf-0097","status":"corrected","set":{"answer":"A","topics":["Pulmonary oedema","Left ventricular failure"],"explanation":"..."},"why":"Source key (tricuspid regurgitation) contradicts its own explanation; bat-wing oedema reflects LV failure"},
{"id":"arr-0032","status":"expanded","set":{"stem":"A 55-year-old woman ... (shown) ...?","topics":["Cardiac sarcoidosis"],"explanation":"..."}},
{"id":"cad-0024","delete":true,"dup_of":"cad-0015","why":"Same idea as cad-0015 (persistent ST elevation after MI = LV aneurysm)"},
{"id":"arr-0052","delete":true,"dup_of":"arr-0044","silent":true,"why":"The same Harrison question is printed twice in the source"},
{"id":"cvsemq-0001","status":"corrected","set":{"topics":["Peripheral oedema"],"options":[...],"option_letters":[...]},
 "items":{"1":{"answer":"D","explanation":"..."},"2":{"answer":"B","stem":"(fixed stem)","explanation":"..."}},
 "why":"Item 3 re-keyed: ... "}
]
```
`status`: "expanded" = only stem tidy/explanation/topics; "corrected" = key, options, clinical content, or image changed.
A tidy of English with no clinical change stays "expanded".

## Chapters
Cardiovascular: cad Coronary & Vascular Disease · hf Heart Failure & Cardiomyopathy · chd Congenital Heart Disease ·
arr Arrhythmias & Conduction Disease · valv Valvular Heart Disease & Endocarditis · peri Pericardial & Inflammatory Heart Disease ·
htn Hypertension · cpharm Cardiovascular Pharmacology · cvsx Mixed Cardiology · cvsemq Cardiology EMQs.
Respiratory: airway Obstructive Airway Disease (asthma, COPD, bronchiectasis, CF together — the student must diagnose) ·
resinf Respiratory Infection & Inflammation (pneumonia, TB, sarcoid…) · crit Respiratory Failure & ARDS · pleura Pleural Disease ·
ild Interstitial Lung Disease · pvasc Pulmonary Vascular Disease (PE, pulmonary hypertension) · lca Lung Cancer ·
resx Mixed Respiratory Medicine · resemq Respiratory EMQs.

## Finish
Run checkpatch until OK with 0 uncovered. Then reply with a SHORT report (under 250 words): files written, counts
(expanded / corrected / deleted), the notable corrections (id: one line each, max 15), and anything you could not resolve.
