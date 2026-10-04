# Surgery Bank 3rd edition — review brief for chapter reviewers

Project: <project>
DO NOT modify data/questions.json or anything except your own TSV output file.

## Inspect
    cd <project> && python3 work/rdump.py <chapter> [start] [count]
Prints every question: id, bank + source number, stem, options A..., KEY, EX (explanation, truncated at 400/300 chars),
EMQ themes with their items (#n). Read EVERY question of your chapters (page through in chunks of ~40).
Full untruncated data is in data/questions.json if needed (fields: id, chapter, type MCQ/EMQ, stem, options, answer,
explanation, images; EMQ: theme, option_letters, options, items[{n, stem, answer, explanation}]).

## Output: one TSV file data/review/<your-name>.tsv (write it with the Write tool, UTF-8)
One op per line: `id[#n]<TAB>FIELD<TAB>value`   (`#n` = EMQ item number; omit for MCQ / theme-level ops)
FIELD:
- EX    new explanation (MCQ, or EMQ item with #n)
- KEY   corrected answer letter(s). Multi-answer true/false items (Bailey & Love "which statements are true") use all true letters, e.g. `ACE`.
- STEM  corrected stem (MCQ, or EMQ item with #n)
- OPTA, OPTB, ... corrected single option text (MCQ)
- OPTS  full replacement option list, `|`-separated, no letters (MCQ or EMQ theme). Use when options are garbled/missing/merged.
- THEME corrected EMQ theme title
- CH    move to another chapter id (only if clearly misfiled; see chapter list)
- DUP   value = id of the EARLIER copy when the question is a duplicate of another question (same question, possibly reworded). The earlier = the one that appears first in the dump order of the book (chapter order below, then id order). Put DUP on the LATER one.
- DEL   value = reason; only for unusable junk (empty, hopelessly garbled, not a question)
- NOTES free text for the editor (rare)

## Review standard (do all of it)
1. Verify every KEY medically against current standard surgical texts / guidelines (Bailey & Love 28th, NICE, ATLS 10th, EAU, ESMO...). Correct wrong keys. Fill every empty KEY.
2. EXPLANATIONS must be 1–2 sentences, at most ~200 characters (2–3 printed lines): why the answer is right (+ the key distractor if it helps). British spelling. Write an EX op when the current EX is empty, longer than ~200 chars, wrong, garbled, starts with junk like "D." "1." ")" or repeats the option text, or is a combined list of distractors ("- X (A) ... - Y (B) ..." — that pattern means every item of that theme needs its own short EX). If the current EX is already correct, clear and short, leave it (no op).
   For multi-answer true/false items the EX should say which statements are false and why, briefly.
3. Fix stems: truncated stems, missing question sentence, options embedded in the stem, OCR artefacts ("”uid"→fluid, "!ssure"→fissure, "speci#c"→specific), units. Keep the clinical content; do not rewrite good stems.
4. Fix options: garbled, duplicated, merged, missing (EMQ lists where a key letter has no option!), prefixes like "(A) ".
5. Two-correct-answer items: fix by editing the distractor or the stem so exactly one is best (or KEY multi-letter only for true/false-format items).
6. Duplicates within your chapters (and with obvious earlier copies elsewhere you notice): DUP on the later one.
7. Misfiled questions: CH to the right chapter.
Be thorough but efficient; do not emit ops that change nothing.

## Chapter ids (book order)
Neck: neck (thyroid/parathyroid/neck), endo (endocrine misc), neckemq
Breast: bbreast (benign), bca (breast cancer), breastemq
GIT: saliv, oeso, stom, intest, anus, gibleed, gitum (GI tumours), gitemq
Paediatric: paed, paedemq
Abdomen: acute (acute abdomen/peritonitis/appendix), liver, gb (gallbladder & bile ducts), panc, spleen, adrenal, hernia, abdemq
Urology: uti, stone, renal (renal tumours/cysts), urogen (urogenital misc), uroemerg, prostate, congur (congenital urology), scrotum, bladder, uroemq
Extra: trauma, metab (surgical metabolism/nutrition/fluids), shock, obesity, extraemq

## Example lines
    paed-0002	KEY	A
    paed-0002	EX	A stable child with intussusception and no peritonitis is reduced by image-guided air (pneumatic) enema; surgery if it fails or perforation.
    uroemq-0003	OPTS	Renal cell carcinoma|Transitional cell carcinoma|Wilms tumour|Angiomyolipoma
    uroemq-0003#2	KEY	C
    uroemq-0003#2	EX	An abdominal mass in a well 3-year-old with haematuria is a Wilms tumour (nephroblastoma).
    hernia-0031	DUP	hernia-0007

When done, reply with: file path, number of ops, and a short list of notable problems (wrong keys fixed, deleted, moved, duplicates).
