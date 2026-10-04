# Surgery Bank 3rd edition — management flowcharts brief

Project: <project>
The old summary tables of each part are in data/source/summ_<part>.txt (neck, bbreast, git, paed, abd, uro, extra).
They are being REPLACED by step-by-step management flowcharts that combine those summaries with CURRENT guidelines.
A finished example from the sister book (Medicine) is medicine2-3rd-edition/data/import/flow_src.py — read its header and first chapters to copy the style exactly.

## What to write
One Python file data/import/flows/<your-name>.py (create the folder if needed) that, when run, writes data/import/flows/<your-name>.json = {chapter_id: [block, ...]}.
Use exactly these helpers at the top of your file:

    import json, os
    S = lambda t: {"k": "start", "t": t}
    P = lambda t: {"k": "step", "t": t}
    E = lambda t: {"k": "end", "t": t}
    Q = lambda q, br: {"k": "split", "q": q, "br": [{"l": l, "n": n} for l, n in br]}
    F = lambda title, source, nodes: {"type": "flowchart", "title": title, "source": source, "nodes": nodes}
    E_ = {}
    ...
    json.dump(E_, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '<your-name>.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

## Rules
- 2–3 flowcharts per chapter (1 for very small chapters), on the highest-yield management pathways of that chapter, in teaching order.
- Each flowchart: S(start: the presentation) → P steps → optional ONE or TWO Q splits (2–4 branches, branches contain only S/P/E boxes, 1–4 boxes each) → E (end/key message).
  Keep it to ~5–9 boxes in the main line; text per box ≤ ~150 characters; branch labels ≤ ~40 characters; use **bold** for the key action.
- "source" = the guidelines it follows, short, e.g. "NICE NG12 · Bailey & Love 28e", "ATLS 10th ed", "EAU 2024 Urolithiasis", "WSES 2020 appendicitis", "BTA/ATA 2015 thyroid nodules", "ESMO 2023", "Tokyo Guidelines 2018".
- Medically accurate and current (UK/European guidance preferred, British spelling, SI units). Use the facts in the summary files where still correct; correct or update them where outdated.
- Characters: use → ≤ ≥ × ° µ – ’ freely; NO emoji.
- Run your file with python3 to produce the JSON and check it loads. Do not touch any other file.

## Chapter ids and titles (part → chapters)
Neck Lumps & Endocrine: neck (Neck Lumps, Thyroid & Parathyroid), endo (Endocrine Surgery — MEN, pituitary/pancreatic endocrine, hyperparathyroidism work-up overlap ok)
Breast: bbreast (Benign Breast Disorders), bca (Breast Cancer)
Gastrointestinal Tract: saliv (Salivary Glands), oeso (Oesophagus), stom (Stomach & Duodenum), intest (Small & Large Intestine: obstruction, IBD, diverticular disease, volvulus), anus (Anorectal Disorders), gibleed (Gastrointestinal Bleeding), gitum (Gastrointestinal Tumours: oesophageal, gastric, colorectal, anal cancer, polyps)
Paediatric Surgery: paed
Abdomen: acute (Acute Abdomen & Abdominal Trauma incl. appendicitis, peritonitis, AAA), liver, gb (Gallbladder & Biliary Tree), panc (Pancreas), spleen, adrenal, hernia (Hernias & Abdominal Wall)
Urology: uti, stone (Urinary Stones), renal (Renal Tumours), urogen (Urological Investigation & Haematuria, urethra/penis), uroemerg (Urological Emergencies & Trauma, retention), prostate, congur (Congenital Urology), scrotum (Scrotum & Testis), bladder (Bladder Tumours)
Trauma & Critical Care: trauma (ATLS, chest/head trauma, burns, wounds), metab (Metabolic Response, fluids, electrolytes, nutrition), shock (Shock & haemorrhage, transfusion), obesity (Bariatric surgery)
(EMQ chapters get no flowcharts.)

When done reply with the file path, number of charts per chapter, and anything you were unsure of.
