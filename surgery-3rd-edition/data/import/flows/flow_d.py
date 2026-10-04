"""Management flowcharts (Surgery Bank 3rd edition) - flow_d: Urology + Trauma & Critical Care.
Replaces the old summary tables (summ_uro.txt, summ_extra.txt) with step-by-step management pathways
updated to the current guidelines named on each chart.

Writes flow_d.json  {chapter_id: [block, ...]}

Block: {"type": "flowchart", "title", "source", "nodes": [node, ...]}
  node  S(text)  start box          P(text)  step box          E(text)  end / key-message box
        Q(question, [(label, [S/P/E nodes]), ...])  decision with 2-4 branches (branches hold boxes only)
Text may use **bold**.
"""
import json, os

S = lambda t: {"k": "start", "t": t}
P = lambda t: {"k": "step", "t": t}
E = lambda t: {"k": "end", "t": t}
Q = lambda q, br: {"k": "split", "q": q, "br": [{"l": l, "n": n} for l, n in br]}
F = lambda title, source, nodes: {"type": "flowchart", "title": title, "source": source, "nodes": nodes}

E_ = {}

# =================================================================== UROLOGY
E_['uti'] = [
    F("Lower UTI (cystitis): who gets what", "NICE NG109 · EAU 2024 Urological Infections", [
        S("Dysuria, frequency, urgency, suprapubic pain ± haematuria"),
        P("Women < 65: **dipstick** (nitrite + leucocytes/RBC = likely UTI); ≥ 65 or catheter: do not dipstick — diagnose clinically"),
        P("Send **urine culture** in men, pregnancy, children, ≥ 65, catheter, recurrent or treatment failure"),
        Q("Who is the patient?", [
            ("Non-pregnant woman", [
                P("**Nitrofurantoin 100 mg MR bd × 3 days** (eGFR ≥ 45) or trimethoprim 200 mg bd × 3 days if low resistance risk"),
                E("2nd line: pivmecillinam or fosfomycin 3 g single dose; back-up prescription acceptable")]),
            ("Man", [
                P("Nitrofurantoin or trimethoprim **× 7 days**; culture before treatment"),
                E("Fever, perineal pain, tender prostate → treat as **acute prostatitis** (fluoroquinolone 14 days)")]),
            ("Pregnant", [
                P("Nitrofurantoin × 7 days (avoid at term); amoxicillin or cefalexin by culture"),
                E("**Treat asymptomatic bacteriuria** in pregnancy; repeat culture as test of cure")]),
            ("Catheterised", [
                E("Treat only if symptomatic · **change the catheter** before starting antibiotics · culture from the new catheter")]),
        ]),
        E("Recurrent UTI (≥ 2 in 6 months / ≥ 3 in 12 months): exclude stones/obstruction · vaginal oestrogen if postmenopausal · methenamine or prophylaxis"),
    ]),
    F("Acute pyelonephritis and the obstructed infected kidney", "NICE NG111 · EAU 2024 Urological Infections", [
        S("Fever, rigors, loin pain and tenderness ± vomiting"),
        P("Sepsis screen (NEWS2), **blood + urine cultures**, FBC, U&E, CRP, lactate"),
        P("Oral cefalexin or ciprofloxacin 7 days if well; **IV antibiotics within 1 h** if septic (e.g. ceftriaxone or gentamicin per local policy)"),
        P("**Ultrasound or CT** if septic, diabetic, stone history, AKI or no response within 48–72 h"),
        Q("Imaging finding", [
            ("Hydronephrosis + stone (obstruction)", [
                P("**Urological emergency**: urgent decompression — percutaneous nephrostomy or retrograde JJ stent"),
                E("Defer definitive stone treatment until infection cleared")]),
            ("Gas in parenchyma (diabetic)", [
                E("**Emphysematous pyelonephritis**: resuscitate, antibiotics, percutaneous drainage; nephrectomy if deteriorating")]),
            ("Renal / perinephric abscess", [
                E("< 3 cm: antibiotics alone · larger or perinephric: **percutaneous drainage** + antibiotics")]),
        ]),
        E("Pus under pressure kills: **antibiotics alone never treat an obstructed infected kidney**"),
    ]),
    F("Sterile pyuria and specific urinary infections", "WHO 2022 TB · EAU 2024 Urological Infections · Bailey & Love 28e", [
        S("Persistent pyuria with negative routine culture"),
        P("Exclude partially treated UTI, stones, carcinoma in situ, chlamydia, interstitial cystitis"),
        Q("Pointer to specific infection?", [
            ("Weight loss, TB contact, frequency", [
                P("**Genitourinary TB**: 3 early-morning urines for AFB culture + NAAT (Xpert); CXR; CT urography (calcification, strictures)"),
                P("**6 months RHZE** (2 HRZE + 4 HR); stent/nephrostomy for ureteric stricture"),
                E("Late: nephrectomy for non-functioning kidney · augmentation cystoplasty for small contracted (thimble) bladder")]),
            ("Endemic area, terminal haematuria", [
                P("**Schistosomiasis (S. haematobium)**: terminal-spined ova in midday urine; serology; calcified bladder on imaging"),
                P("**Praziquantel 40 mg/kg** single dose"),
                E("Long-term: ureteric stricture, bladder neck contracture, **squamous cell carcinoma** → cystoscopy if persistent symptoms")]),
        ]),
        E("Sterile pyuria in a man > 40 or a smoker: **cystoscopy + cytology** to exclude CIS"),
    ]),
]

E_['stone'] = [
    F("Acute renal colic", "EAU 2024 Urolithiasis · NICE NG118", [
        S("Severe colicky loin-to-groin pain, restless, haematuria on dipstick"),
        P("**NSAID first line** (diclofenac or ibuprofen, any route); IV paracetamol if NSAID contraindicated; opioid only if both fail"),
        P("Pregnancy-test women; FBC, U&E, CRP, calcium, urate; urine culture"),
        P("**Low-dose non-contrast CT KUB within 24 h** (immediately if fever, solitary kidney or diagnostic doubt); ultrasound first in pregnancy and children"),
        Q("Infection, AKI, anuria or uncontrollable pain?", [
            ("Yes", [
                P("**Urgent decompression**: nephrostomy or JJ stent + IV antibiotics"),
                E("Definitive treatment only after infection resolved")]),
            ("No: ureteric stone ≤ 10 mm", [
                P("Watchful waiting with analgesia; **tamsulosin** (MET) for distal stones > 5 mm"),
                E("Review/re-image at 4 weeks; treat if not passed, persistent pain or obstruction")]),
            ("No: ureteric stone > 10 mm", [
                E("Unlikely to pass → **ureteroscopy (URS)**; SWL an alternative for proximal stones")]),
        ]),
        E("Consider **AAA in any patient > 60** with first ‘renal colic’"),
    ]),
    F("Choosing active stone removal", "EAU 2024 Urolithiasis · NICE NG118", [
        S("Stone needing removal (size, symptoms, obstruction, growth, infection or occupation)"),
        P("Asymptomatic small renal stone (< 5 mm): surveillance is reasonable"),
        Q("Stone size and site", [
            ("Renal < 10 mm", [P("**SWL** or flexible ureteroscopy (RIRS)")]),
            ("Renal 10–20 mm", [P("SWL or RIRS; lower pole with unfavourable anatomy → **RIRS or PCNL**")]),
            ("Renal > 20 mm / staghorn", [P("**PCNL** first line (RIRS if PCNL unsuitable)")]),
            ("Ureteric", [P("< 10 mm: SWL or **URS** · > 10 mm: URS first line")]),
        ]),
        P("Pregnancy: no CT/SWL — stent or nephrostomy, or URS by experienced surgeon"),
        P("Contraindications to SWL: pregnancy, uncorrected coagulopathy, untreated UTI, aneurysm near stone, distal obstruction"),
        E("**Send stone for analysis** — composition guides prevention"),
    ]),
    F("Metabolic work-up and prevention", "EAU 2024 Urolithiasis · NICE NG118", [
        S("Stone former after the acute episode"),
        P("All: stone analysis, serum Ca, urate, creatinine, bicarbonate, urinalysis"),
        P("High risk (recurrent, child, solitary kidney, bilateral, cystine/uric acid/infection stones) → **2 × 24-h urine collections**"),
        P("**Fluid 2.5–3 L/day** (urine > 2–2.5 L) · normal calcium intake 1000–1200 mg/day · salt ≤ 5 g · moderate animal protein"),
        Q("Specific abnormality", [
            ("Hypercalciuria / hypocitraturia", [P("**Thiazide** for hypercalciuria · **potassium citrate** for hypocitraturia; raised serum Ca → parathyroidectomy")]),
            ("Uric acid (radiolucent)", [P("Alkalinise urine to **pH 6.2–6.8** (potassium citrate) → dissolution; allopurinol if hyperuricosuria")]),
            ("Cystine", [P("Fluid ≥ 3.5 L, alkalinise **pH > 7.5**; tiopronin if > 3 mmol/day")]),
            ("Struvite (infection)", [P("**Complete stone clearance** + culture-directed antibiotics")]),
        ]),
        E("Do **not** restrict dietary calcium — it increases oxalate absorption and stone risk"),
    ]),
]

E_['renal'] = [
    F("Work-up of a renal mass", "EAU 2024 Renal Cell Carcinoma · Bosniak 2019", [
        S("Renal mass, usually incidental on ultrasound or CT"),
        P("**Multiphase contrast CT** (or MRI) abdomen + CT chest; renal function, FBC, calcium"),
        Q("Imaging character", [
            ("Cystic", [
                P("**Bosniak** I–II: benign, discharge · IIF: surveillance imaging up to 5 years"),
                E("III–IV: treat as malignant → partial nephrectomy (surveillance option for III in frail)")]),
            ("Contains fat (negative HU)", [
                P("**Angiomyolipoma**: surveillance if small & asymptomatic"),
                E("Symptomatic, growing or high bleed risk → **selective embolisation** or partial nephrectomy; everolimus in tuberous sclerosis")]),
            ("Solid enhancing", [
                E("**RCC until proven otherwise** → see staging and treatment chart")]),
        ]),
        P("**Biopsy** only if it changes management: before ablation or surveillance, before systemic therapy, or suspected lymphoma/metastasis"),
        E("Classic triad (haematuria, loin pain, mass) is late (< 10%) · watch for left varicocele, paraneoplastic hypercalcaemia, polycythaemia"),
    ]),
    F("Renal cell carcinoma: stage-based treatment", "EAU 2024 Renal Cell Carcinoma", [
        S("Solid renal mass, staged with CT chest/abdomen"),
        Q("Stage", [
            ("T1a (≤ 4 cm)", [
                P("**Partial nephrectomy** (open, laparoscopic or robotic)"),
                E("Frail/comorbid: thermal ablation (≤ 3 cm) or active surveillance")]),
            ("T1b–T2 / locally advanced", [
                P("T1b: partial if feasible; otherwise **radical nephrectomy** (laparoscopic)"),
                P("IVC tumour thrombus → nephrectomy + thrombectomy"),
                E("Adjuvant **pembrolizumab** 1 year for intermediate-high/high-risk clear-cell RCC")]),
            ("Metastatic", [
                P("IMDC risk score; **ICI-based combination**: pembrolizumab + axitinib/lenvatinib, nivolumab + cabozantinib, or nivolumab + ipilimumab"),
                E("Selective cytoreductive nephrectomy · metastasectomy for oligometastases · RT for painful bone mets")]),
        ]),
        E("No routine lymph-node dissection or adrenalectomy if not involved · follow-up CT by risk group"),
    ]),
    F("Upper tract urothelial carcinoma", "EAU 2024 UTUC", [
        S("Visible haematuria with filling defect in renal pelvis or ureter"),
        P("**CT urography** + urine cytology + **cystoscopy** (exclude bladder tumour)"),
        P("**Ureteroscopy + biopsy** for grade; ask about Lynch syndrome (young, family history)"),
        Q("Risk group", [
            ("Low risk", [
                P("Unifocal, < 2 cm, low grade, no invasion on CT"),
                E("**Kidney-sparing**: ureteroscopic laser ablation or segmental ureterectomy, close ureteroscopic follow-up")]),
            ("High risk", [
                P("**Radical nephroureterectomy with bladder cuff excision** ± template lymphadenectomy"),
                E("Adjuvant platinum chemotherapy for pT2–T4 or N+")]),
        ]),
        E("**Single post-operative intravesical chemotherapy** instillation and lifelong cystoscopy — bladder recurrence 22–47%"),
    ]),
]

E_['urogen'] = [
    F("Haematuria: assessment and referral", "NICE NG12 · BAUS · EAU 2024", [
        S("Visible (VH) or dipstick non-visible haematuria (NVH ≥ 1+, persistent = 2 of 3 tests)"),
        P("Exclude **UTI** (culture; re-test after treatment), menstruation, exercise, trauma"),
        P("Check **eGFR, urine ACR/PCR, blood pressure**; dysmorphic RBCs/casts suggest glomerular disease"),
        Q("Referral criteria", [
            ("Urgent suspected cancer", [
                P("Age ≥ 45 with unexplained VH, or VH persisting after UTI treated · age ≥ 60 with NVH + dysuria or raised WCC"),
                E("**Flexible cystoscopy + CT urography** (US for NVH) in one-stop haematuria clinic")]),
            ("Proteinuria, ↓ eGFR, hypertension, young", [
                E("**Nephrology** referral — IgA nephropathy, other glomerulonephritis")]),
            ("Neither", [
                E("Monitor annually: BP, eGFR, ACR; refer if symptoms or VH develop")]),
        ]),
        E("Clot retention: **3-way catheter, washout + continuous irrigation** · haematuria on anticoagulants still needs full investigation"),
    ]),
    F("Male urethral stricture", "EAU 2024 Urethral Strictures · Bailey & Love 28e", [
        S("Poor or spraying stream, straining, recurrent UTI or retention"),
        P("Causes: idiopathic, iatrogenic (catheter, TURP), straddle injury, pelvic fracture, lichen sclerosus, gonorrhoea"),
        P("**Uroflowmetry** (flat plateau curve) + post-void residual; **retrograde urethrogram** ± MCUG; urethroscopy"),
        Q("Stricture type", [
            ("Short (< 2 cm) bulbar, first time", [
                P("**Optical urethrotomy or dilatation** — one attempt only"),
                E("Recurrence → urethroplasty (repeat endoscopic treatment rarely cures)")]),
            ("Recurrent, long or penile", [
                E("**Urethroplasty**: excision + primary anastomosis for short bulbar; **buccal mucosa graft** for longer; staged repair for lichen sclerosus")]),
            ("Pelvic fracture injury", [
                E("Suprapubic catheter → delayed **posterior anastomotic urethroplasty** at ≥ 3 months")]),
        ]),
        E("Acute retention with known stricture: **suprapubic catheter**, do not force a urethral catheter · unfit patients: intermittent self-dilatation"),
    ]),
    F("Penile lesion and penile cancer", "EAU-ASCO 2023 Penile Cancer", [
        S("Non-healing lesion or mass on glans/prepuce (risk: phimosis, HPV, smoking, lichen sclerosus)"),
        P("**Biopsy** (circumcision if phimosis); MRI penis for local extent; examine both groins"),
        Q("Primary tumour", [
            ("PeIN (in situ)", [P("Topical **5-FU or imiquimod**, laser, or glans resurfacing")]),
            ("Ta–T2 (glans, corpus spongiosum)", [P("**Penile-sparing**: wide excision, glansectomy, or partial penectomy")]),
            ("T3–T4 (corpora cavernosa, urethra)", [P("Partial or **total penectomy with perineal urethrostomy**")]),
        ]),
        Q("Groins", [
            ("cN0, ≥ pT1b / grade 2–3", [P("**Dynamic sentinel node biopsy** or modified inguinal lymphadenectomy")]),
            ("Palpable nodes", [P("US-guided FNA → **radical inguinal lymphadenectomy** ± pelvic; bulky/fixed → neoadjuvant TIP chemotherapy")]),
        ]),
        E("Nodal status is the strongest prognostic factor — **never ‘wait and see’ in intermediate/high-risk cN0 groins**"),
    ]),
]

E_['uroemerg'] = [
    F("Acute urinary retention", "EAU 2024 Male LUTS · NICE CG97 · BAUS", [
        S("Painful inability to void, palpable tender bladder"),
        P("Look for precipitants: **constipation**, anticholinergics/opioids, UTI, post-op, alcohol, clot; neuro exam (cauda equina)"),
        P("**Urethral catheter** (suprapubic if fails or known stricture); record **residual volume**; U&E, urinalysis; DRE"),
        Q("Residual and renal function", [
            ("Acute (usually < 1 L), normal creatinine", [
                P("Start **tamsulosin** ≥ 2–3 days, treat precipitant"),
                P("**Trial without catheter (TWOC)**"),
                E("Fails → recatheterise / intermittent self-catheterisation → TURP or HoLEP")]),
            ("Painless, large, ↑ creatinine", [
                P("**Chronic high-pressure retention**: catheterise, do not TWOC"),
                P("Watch for **post-obstructive diuresis** (> 200 mL/h): hourly UO, U&E, IV replacement"),
                E("Definitive: **TURP** once renal function stabilised")]),
        ]),
        E("Retention in a woman or with saddle anaesthesia/back pain → **emergency MRI spine** (cauda equina)"),
    ]),
    F("Genitourinary trauma", "EAU 2024 Urological Trauma · ATLS 10th ed", [
        S("Injured patient — ATLS primary survey first"),
        Q("Suspected injury", [
            ("Kidney", [
                P("CT (arterial + delayed phases) if visible haematuria, NVH with SBP < 90, rapid deceleration or penetrating"),
                P("Stable: **non-operative for all grades** (bed rest, serial Hb)"),
                E("Active bleed → **angioembolisation** · unstable → laparotomy ± nephrectomy")]),
            ("Bladder (pelvic fracture + VH)", [
                P("**CT cystography** (≥ 350 mL retrograde contrast)"),
                E("Extraperitoneal → catheter 10–14 days · **intraperitoneal → surgical repair**")]),
            ("Urethra", [
                P("Blood at meatus, can’t void, perineal butterfly bruise → **retrograde urethrogram**"),
                P("No blind repeated catheterisation; **suprapubic catheter**"),
                E("Posterior (pelvic fracture): delayed urethroplasty ≥ 3 months · penetrating anterior: early repair")]),
            ("Ureter / penis", [
                P("Ureter (mostly iatrogenic): repair over stent if seen at surgery; late → nephrostomy, delayed reconstruction"),
                E("**Penile fracture** (snap, ‘aubergine’ swelling): immediate surgical repair of tunica albuginea")]),
        ]),
        E("Visible haematuria in trauma always needs **imaging** of the urinary tract"),
    ]),
    F("Priapism, paraphimosis and Fournier’s gangrene", "EAU 2024 Sexual & Reproductive Health · Bailey & Love 28e", [
        S("Acute genital emergency"),
        Q("Which picture?", [
            ("Painful rigid erection > 4 h", [
                P("**Ischaemic priapism**: cavernosal blood gas (dark, pO₂ < 30 mmHg, pH < 7.25)"),
                P("**Aspiration ± irrigation**, then intracavernosal **phenylephrine** in boluses with BP/ECG monitoring"),
                E("Fails → surgical shunt; > 36–48 h → consider immediate penile prosthesis · screen for sickle cell, drugs, leukaemia")]),
            ("Painless partial erection after trauma", [
                E("**Non-ischaemic (high-flow)**: Doppler; not an emergency — observe, **selective embolisation** if persistent")]),
            ("Swollen glans, retracted foreskin", [
                P("**Paraphimosis**: analgesia/penile block, compression (ice, sugar), manual reduction"),
                E("Fails → dorsal slit; elective **circumcision** later")]),
            ("Perineal pain, crepitus, sepsis", [
                P("**Fournier’s gangrene** (polymicrobial necrotising fasciitis; diabetes)"),
                P("Resuscitate + broad-spectrum IV antibiotics incl. **clindamycin**"),
                E("**Urgent radical debridement**, re-look at 24–48 h; mortality ~20%")]),
        ]),
        E("Ischaemic priapism is a compartment syndrome — **time = erectile function**"),
    ]),
]

E_['prostate'] = [
    F("Benign prostatic enlargement and male LUTS", "NICE CG97 · EAU 2024 Male LUTS", [
        S("Male LUTS: hesitancy, weak stream, frequency, urgency, nocturia"),
        P("**IPSS**, frequency–volume chart, DRE, urinalysis, U&E if retention suspected; **PSA after counselling**"),
        P("Conservative: fluid timing, cut caffeine/alcohol, bladder training, urethral milking"),
        Q("Main problem", [
            ("Voiding symptoms", [P("**Alpha-blocker** (tamsulosin, alfuzosin, doxazosin) — works in days")]),
            ("Prostate > 30 g or PSA > 1.4", [P("**5-alpha-reductase inhibitor** (finasteride, dutasteride) — takes ~6 months, halves PSA; combination if moderate–severe")]),
            ("Storage symptoms", [P("Add **antimuscarinic or mirabegron**; nocturnal polyuria → late-afternoon loop diuretic or desmopressin (check Na)")]),
        ]),
        P("Surgery if failed drugs, **refractory retention**, recurrent UTI/haematuria, bladder stones or obstructive uropathy"),
        P("**TURP** (bipolar) 30–80 mL · **HoLEP** any size · simple prostatectomy > 80 mL · Urolift/Rezum for selected men"),
        E("TURP risks: retrograde ejaculation (~65%), bleeding, TUR syndrome (less with saline/bipolar), stricture, incontinence"),
    ]),
    F("Raised PSA to localised prostate cancer", "NICE NG131 · NICE NG12 · EAU 2024 Prostate Cancer", [
        S("PSA above age-specific range or abnormal DRE → urgent suspected-cancer referral"),
        P("Repeat PSA if borderline; exclude UTI/retention/recent ejaculation"),
        P("**Multiparametric MRI before biopsy**"),
        Q("MRI score", [
            ("Likert/PI-RADS 1–2", [P("Discuss; may avoid biopsy if PSA density < 0.15 — PSA follow-up")]),
            ("Likert/PI-RADS ≥ 3", [P("**Transperineal biopsy** (LA); ISUP grade group")]),
        ]),
        P("Stage high-risk disease with **PSMA PET-CT** (or CT + bone scan); assign **Cambridge Prognostic Group (CPG)**"),
        Q("CPG", [
            ("CPG 1 (± 2)", [P("**Active surveillance**: PSA 3–4-monthly, MRI, repeat biopsy if progression")]),
            ("CPG 2–3", [P("Radical prostatectomy or **radical RT + 6 months ADT**")]),
            ("CPG 4–5 / locally advanced", [P("**Radical RT + long-term ADT** (up to 3 years) or prostatectomy in selected men")]),
        ]),
        E("Watchful waiting (symptom-led ADT) for men with short life expectancy"),
    ]),
    F("Metastatic prostate cancer", "EAU 2024 Prostate Cancer · NICE NG131", [
        S("High PSA, bone pain or metastases on imaging"),
        P("**ADT**: LHRH agonist with **antiandrogen cover** for flare (bicalutamide), or degarelix / orchidectomy if cord compression threatened"),
        P("Add **ARPI** (abiraterone + prednisolone, enzalutamide, apalutamide) ± **docetaxel** (fit, high volume); prostate RT if low volume"),
        P("Bone health: DEXA, calcium/vit D; denosumab or zoledronic acid for bone metastases in CRPC"),
        Q("Castration-resistant (rising PSA, testosterone < 1.7 nmol/L)?", [
            ("Yes", [
                P("Switch class: docetaxel → cabazitaxel, ARPI if not used"),
                E("**Olaparib** if BRCA/HRR mutation · **¹⁷⁷Lu-PSMA** · radium-223 for symptomatic bone-only disease")]),
            ("No", [E("Continue ADT combination; PSA + testosterone monitoring")]),
        ]),
        E("Back pain + neuro signs = **MSCC**: dexamethasone 16 mg, **MRI whole spine within 24 h**, RT or decompression"),
    ]),
]

E_['congur'] = [
    F("Antenatal hydronephrosis, PUJ obstruction and posterior urethral valves", "EAU/ESPU 2024 Paediatric Urology", [
        S("Antenatal renal pelvic dilatation (third-trimester APD ≥ 10 mm)"),
        P("Postnatal ultrasound **after 48 h** (falsely reassuring earlier); within 24 h if bilateral, solitary kidney or boy with thick bladder"),
        Q("Picture", [
            ("Boy, bilateral hydro + thick bladder", [
                P("**Posterior urethral valves**: urethral catheter at once, U&E"),
                P("**MCUG** (dilated posterior urethra) → endoscopic **valve ablation**"),
                E("Lifelong follow-up: CKD, valve bladder, hypertension")]),
            ("Unilateral hydro, no ureter dilatation", [
                P("**PUJ obstruction**: MAG3 renogram for split function and drainage"),
                E("**Anderson–Hynes pyeloplasty** if split function < 40%, fall > 10%, increasing APD, pain or UTI; otherwise serial US")]),
            ("Hydroureteronephrosis", [
                E("MCUG for **VUR** vs primary obstructive megaureter; antibiotic prophylaxis; most megaureters resolve")]),
        ]),
        E("Adult PUJ obstruction: intermittent loin pain after large fluid/alcohol load (**Dietl’s crisis**)"),
    ]),
    F("Childhood UTI and vesicoureteric reflux", "NICE NG224 · EAU/ESPU 2024 Paediatric Urology", [
        S("Febrile UTI in an infant or child"),
        P("**< 3 months: IV antibiotics** · older: oral cefalexin or co-amoxiclav 7–10 days (upper UTI)"),
        P("Imaging by age and type: US (acute if atypical, else within 6 weeks); **DMSA 4–6 months** for scars; **MCUG** for atypical/recurrent in infants"),
        P("**VUR** graded I–V on MCUG; low grades usually resolve spontaneously"),
        Q("Course", [
            ("Low grade, no breakthrough UTI", [
                E("Observe or **continuous antibiotic prophylaxis**; treat **bladder–bowel dysfunction** (constipation)")]),
            ("Breakthrough UTI, new scars, high grade", [
                E("**Endoscopic subureteric injection** (Deflux) or **ureteric reimplantation** (Cohen)")]),
        ]),
        E("Goal: prevent **renal scarring** → hypertension and CKD · consider circumcision in boys with high-grade VUR"),
    ]),
    F("Undescended testis and hypospadias", "EAU/ESPU 2024 Paediatric Urology · BAPS", [
        S("Newborn boy with abnormal genital examination"),
        Q("Finding", [
            ("Empty scrotum", [
                P("Retractile testis → observe yearly · bilateral impalpable → **urgent DSD work-up** (karyotype, 17-OHP, electrolytes — CAH)"),
                P("No imaging needed; refer by 6 months"),
                P("Palpable → **inguinal orchidopexy at 6–12 months** (by 18 months)"),
                E("Impalpable → EUA + **laparoscopy**: Fowler–Stephens orchidopexy or remove atrophic testis")]),
            ("Ventral meatus, hooded prepuce", [
                P("**Hypospadias**: **do not circumcise** (foreskin used for repair)"),
                P("Proximal hypospadias + undescended testis → DSD work-up"),
                E("Repair at **6–18 months**: TIP (Snodgrass) for distal; staged graft for proximal with severe chordee")]),
        ]),
        E("Orchidopexy lowers torsion/infertility risk and aids self-examination; cancer risk persists but falls if done before puberty"),
    ]),
]

E_['scrotum'] = [
    F("Acute scrotal pain", "EAU/ESPU 2024 Paediatric Urology · BASHH 2020 Epididymo-orchitis", [
        S("Acute painful scrotum — **torsion until proven otherwise**"),
        P("Torsion: sudden severe pain, vomiting, high-riding horizontal testis, **absent cremasteric reflex**; peak neonatal & adolescent"),
        Q("Clinical suspicion of torsion", [
            ("High / uncertain", [
                P("**Immediate scrotal exploration** — do not delay for Doppler US (salvage ~90% < 6 h, < 10% > 24 h)"),
                P("Untwist; viable → **3-point fixation**; non-viable → orchidectomy"),
                E("**Always fix the contralateral testis** (bilateral bell-clapper)")]),
            ("Blue-dot sign, focal upper-pole pain", [
                E("**Torsion of appendix testis**: analgesia, rest; resolves in 1 week")]),
            ("Gradual onset, dysuria, fever", [
                P("**Epididymo-orchitis**: urinalysis, culture, NAAT for chlamydia/gonorrhoea"),
                P("STI likely: **ceftriaxone 1 g IM + doxycycline 100 mg bd 10–14 days**"),
                E("Enteric likely (older, instrumentation): ofloxacin 14 days or levofloxacin 10 days")]),
        ]),
        E("Prehn’s sign and Doppler cannot reliably exclude torsion — **if in doubt, explore**"),
    ]),
    F("Testicular lump and testicular cancer", "EAU 2024 Testicular Cancer · ESMO 2022", [
        S("Painless hard lump in the testis (age 15–40)"),
        P("**Scrotal ultrasound** (both testes) urgently"),
        P("**AFP, β-hCG, LDH** before and after orchidectomy; offer **sperm banking**"),
        P("**Radical inguinal orchidectomy** (never scrotal approach) ± prosthesis"),
        P("Staging CT chest/abdomen/pelvis; markers fall by half-life (AFP 5–7 days, hCG 2–3 days)"),
        Q("Histology and stage", [
            ("Stage I seminoma", [P("**Surveillance** (preferred) or single-dose carboplatin")]),
            ("Stage I non-seminoma", [P("Surveillance; **1 cycle BEP** if lymphovascular invasion")]),
            ("Metastatic", [
                P("IGCCCG risk → **BEP × 3 (good) or × 4**"),
                E("Residual mass: NSGCT > 1 cm → RPLND · seminoma > 3 cm → FDG-PET")]),
        ]),
        E("> 90% overall cure · AFP is **never raised in pure seminoma** — if raised, treat as non-seminoma"),
    ]),
    F("Non-tender scrotal swelling", "EAU 2024 · Bailey & Love 28e", [
        S("Painless scrotal swelling"),
        P("Can you get above it? **No → inguinoscrotal hernia**"),
        Q("Can feel the testis separately?", [
            ("No — transilluminates", [
                P("**Hydrocele**: adults → **US to exclude tumour** behind it"),
                E("Child: wait to age 1–2 (patent processus) then inguinal ligation · adult: Lord’s plication or Jaboulay")]),
            ("Yes — cystic, above/behind testis", [
                E("**Epididymal cyst / spermatocele**: reassure; excise only if troublesome")]),
            ("Yes — ‘bag of worms’, left side", [
                P("**Varicocele**: Doppler US"),
                P("Sudden, right-sided or not emptying supine → **image kidneys** (renal tumour)"),
                E("Treat if pain, subfertility with abnormal semen, or adolescent testicular hypotrophy: embolisation or microsurgical ligation")]),
            ("No — solid, testis enlarged", [
                E("**Testicular tumour until proven otherwise** → urgent US + markers")]),
        ]),
        E("Any adult scrotal swelling of doubtful nature → **ultrasound**"),
    ]),
]

E_['bladder'] = [
    F("Non-muscle-invasive bladder cancer", "EAU 2024 NMIBC · NICE NG2", [
        S("Painless visible haematuria → flexible cystoscopy shows bladder tumour"),
        P("CT urography (upper tracts); **TURBT** — complete resection with **detrusor muscle in specimen**"),
        P("**Single post-op intravesical chemotherapy** (mitomycin C) within 24 h for presumed low/intermediate risk (not if perforation)"),
        P("**Re-TURBT at 2–6 weeks** if T1, incomplete resection or no muscle in specimen"),
        Q("EAU risk group", [
            ("Low", [P("Surveillance cystoscopy at 3 and 12 months, then yearly")]),
            ("Intermediate", [P("Intravesical **chemotherapy** course (≤ 1 year) or BCG 1 year")]),
            ("High (incl. CIS)", [P("**BCG** induction + maintenance 1–3 years")]),
            ("Very high / BCG-unresponsive", [P("**Radical cystectomy** (BCG if unfit/declines)")]),
        ]),
        E("Risk factors: **smoking**, aromatic amines (dyes, rubber), schistosomiasis, pelvic RT, cyclophosphamide · stop smoking"),
    ]),
    F("Muscle-invasive bladder cancer", "EAU 2024 MIBC · NICE NG2", [
        S("TURBT shows ≥ T2 (muscle-invasive) disease"),
        P("Stage: **CT chest/abdomen/pelvis**; MDT; assess fitness and renal function (cisplatin eligibility)"),
        Q("Fit for radical treatment?", [
            ("Yes, cisplatin-eligible", [
                P("**Neoadjuvant cisplatin-based chemotherapy** (gemcitabine–cisplatin or dd-MVAC)"),
                P("**Radical cystectomy + pelvic lymphadenectomy**; ileal conduit or orthotopic neobladder"),
                E("Adjuvant **nivolumab** for high-risk pathology (pT3–4 or N+)")]),
            ("Wants bladder preservation", [
                E("**Trimodal therapy**: maximal TURBT + chemoradiotherapy (best: T2, no CIS, no hydronephrosis)")]),
            ("Metastatic", [
                E("**Enfortumab vedotin + pembrolizumab** first line; platinum-based alternatives; erdafitinib if FGFR3")]),
        ]),
        E("**Squamous cell carcinoma** (schistosomiasis, chronic catheter): chemo/RT-resistant → radical cystectomy"),
    ]),
]

# =================================================================== TRAUMA & CRITICAL CARE
E_['trauma'] = [
    F("Primary survey of the injured patient", "ATLS 10th ed · NICE NG39 Major Trauma", [
        S("Major trauma arrives — team ready, **<C>ABCDE** with simultaneous resuscitation"),
        P("**Catastrophic haemorrhage**: direct pressure, tourniquet, pelvic binder at level of greater trochanters"),
        P("**Airway** with cervical spine motion restriction; definitive airway if GCS ≤ 8 or airway threatened"),
        Q("Breathing: immediately life-threatening?", [
            ("Tension pneumothorax", [P("Clinical diagnosis → **needle/finger decompression** (4th–5th ICS mid-axillary), then chest drain")]),
            ("Open pneumothorax", [P("**3-sided occlusive dressing** (vented seal) → chest drain away from wound")]),
            ("Massive haemothorax", [P("Chest drain; **> 1500 mL at once or > 200 mL/h for 2–4 h → thoracotomy**")]),
            ("Cardiac tamponade / flail", [P("Tamponade (Beck’s triad, FAST) → thoracotomy; pericardiocentesis to bridge · flail → analgesia, O₂, ventilate if hypoxic")]),
        ]),
        P("**Circulation**: 2 large-bore IV, bloods + crossmatch, **TXA 1 g within 3 h**, early blood products, warmed fluids"),
        Q("Response to initial resuscitation", [
            ("Rapid responder", [P("Proceed to CT and secondary survey")]),
            ("Transient / non-responder", [P("Activate **major haemorrhage protocol**; eFAST → theatre or IR for haemorrhage control")]),
        ]),
        P("**Disability** (GCS, pupils, glucose) · **Exposure** (log-roll, prevent hypothermia); adjuncts: CXR, pelvic XR, eFAST, ABG"),
        E("Then **secondary survey** (AMPLE, head-to-toe), whole-body CT if stable, tertiary survey at 24 h"),
    ]),
    F("Head injury", "NICE NG232 (2023) · Brain Trauma Foundation 4th ed", [
        S("Head injury: GCS, pupils, focal signs, mechanism, anticoagulants"),
        P("ABCDE with C-spine protection; **intubate if GCS ≤ 8**, airway at risk, hypoxia or hypercapnia, seizures"),
        P("**CT head within 1 h**: GCS < 13 initially or < 15 at 2 h, open/depressed or basal skull fracture, seizure, focal deficit, > 1 vomit"),
        P("**CT within 8 h**: LOC/amnesia + age ≥ 65, dangerous mechanism or coagulopathy; on **anticoagulants**"),
        Q("CT finding", [
            ("Extradural (biconvex, lucid interval)", [P("**Urgent craniotomy** if > 30 mL, regardless of GCS")]),
            ("Acute subdural (crescent)", [P("**Evacuate** if > 10 mm thick or > 5 mm midline shift")]),
            ("Diffuse injury / contusions", [P("ICU: head-up 30°, PaCO₂ 4.5–5.0 kPa, **CPP 60–70 mmHg**, ICP < 22; hypertonic saline or mannitol")]),
        ]),
        P("**Reverse anticoagulation**: PCC + vitamin K for warfarin; idarucizumab or andexanet/PCC for DOACs"),
        E("Prevent secondary brain injury: **avoid hypoxia (PaO₂ > 13 kPa) and hypotension**"),
    ]),
    F("Major burn", "ATLS 10th ed · BBA / National Burn Care Referral Guidance", [
        S("Burn injury — stop the burning process"),
        P("**Cool with running water for 20 min** (useful up to 3 h); keep the patient warm; cling film"),
        P("**Airway**: inhalation injury (facial burns, singed nasal hair, soot, hoarseness, stridor) → **early intubation** with uncut tube"),
        P("CO/cyanide: **100% O₂**, COHb; hydroxocobalamin if cyanide suspected (enclosed space, high lactate)"),
        P("**TBSA** by Lund–Browder or rule of 9s (palm + fingers ≈ 1%); **ignore simple erythema**"),
        Q("TBSA (partial + full thickness)", [
            ("Adult > 15% / child > 10%", [
                P("IV Hartmann’s: **ATLS 2 mL × kg × %TBSA** (3 mL children, 4 mL electrical; Parkland 4 mL) — half in first 8 h from burn"),
                E("Titrate to **urine output 0.5 mL/kg/h** adult (1 mL/kg/h child); catheterise")]),
            ("Smaller", [E("Oral fluids, analgesia, dressings; **refer** if special area or criteria met")]),
        ]),
        P("Circumferential full-thickness burn of limb/chest → **escharotomy** · tetanus prophylaxis · no prophylactic antibiotics"),
        E("Refer to burns service: ≥ 3% adult / ≥ 2% child, face, hands, feet, perineum, joints, circumferential, electrical, chemical, inhalation, **NAI**"),
    ]),
]

E_['metab'] = [
    F("IV fluid prescribing: the 5 Rs", "NICE CG174 IV Fluids (2017)", [
        S("Surgical patient who may need IV fluids"),
        P("Assess: history, fluid balance, weight, U&E, NEWS2; **can they drink?** — oral/enteral first"),
        Q("Which need?", [
            ("Resuscitation", [
                P("SBP < 100, HR > 90, CRT > 2 s, RR > 20, NEWS ≥ 5 → **500 mL crystalloid (Na 130–154) over < 15 min**"),
                E("Reassess after each bolus; after 2000 mL seek expert help")]),
            ("Routine maintenance", [
                P("**25–30 mL/kg/day water, ~1 mmol/kg/day Na, K, Cl, 50–100 g/day glucose**"),
                E("e.g. 0.18% NaCl/4% glucose + KCl; 20–25 mL/kg/day if elderly, frail, renal/cardiac failure")]),
            ("Replacement / redistribution", [
                E("Add measured ongoing losses (vomiting, NG, fistula, drains, third space) with matched electrolyte content")]),
        ]),
        P("**Reassess**: daily U&E, fluid balance, weight; stop IV fluids as soon as possible"),
        E("Excess 0.9% saline → **hyperchloraemic acidosis**; hypotonic fluids → **hyponatraemia** (dangerous in children)"),
    ]),
    F("Peri-operative electrolyte emergencies", "UKKA 2023 Hyperkalaemia · ESE/ERA-EDTA 2014 Hyponatraemia", [
        S("Abnormal U&E in a surgical patient — repeat if unexpected (haemolysis), ECG, review fluids and drugs"),
        Q("Problem", [
            ("K⁺ ≥ 6.5 mmol/L or ECG changes", [
                P("**IV calcium** (30 mL 10% gluconate or 10 mL 10% chloride) to protect the heart"),
                P("**Insulin 10 units + 25 g glucose** IV; salbutamol 10–20 mg nebulised"),
                E("Remove K⁺: stop culprit drugs, sodium zirconium cyclosilicate, **dialysis if refractory**; monitor glucose")]),
            ("Na⁺ low", [
                P("Assess volume status, serum/urine osmolality, urine Na (SIADH common post-op)"),
                P("Severe symptoms (seizure, coma) → **150 mL 3% saline over 20 min**, repeat until Na ↑ 5 mmol/L"),
                E("**Limit rise to ≤ 10 mmol/L in 24 h** (osmotic demyelination) · hypovolaemic → 0.9% saline · SIADH → fluid restriction")]),
            ("K⁺ < 3.0 mmol/L", [
                E("IV KCl **≤ 10 mmol/h peripherally** (higher only centrally with ECG monitoring); correct **magnesium**; oral if 3.0–3.4")]),
        ]),
        E("Hypokalaemia → **paralytic ileus** and arrhythmias · never give potassium as a bolus"),
    ]),
    F("Metabolic response to surgery and nutritional support", "NICE CG32 · ESPEN 2021 Clinical Nutrition in Surgery · ERAS Society", [
        S("Injury/surgery → **ebb phase** (hours: ↓ metabolic rate) → **flow phase** (days: catabolism, then anabolism)"),
        P("Cortisol, catecholamines, glucagon, ADH, aldosterone, IL-6 → hyperglycaemia, protein breakdown, Na/water retention"),
        P("Blunt it with **ERAS**: clear fluids to 2 h pre-op, carbohydrate loading, regional analgesia, early oral feeding"),
        P("**MUST** screen: BMI < 18.5, unintentional weight loss > 10% in 3–6 months, or little intake > 5 days → nutrition support"),
        Q("Is the gut working and accessible?", [
            ("Yes", [P("**Enteral**: oral supplements → NG/NJ tube → gastrostomy/jejunostomy if > 4 weeks")]),
            ("No (obstruction, fistula, short bowel)", [P("**Parenteral nutrition** via PICC/central line; watch line sepsis, LFTs, glucose")]),
        ]),
        P("**Refeeding risk** → start ≤ 10 kcal/kg/day (5 if extreme), thiamine before feeding, daily PO₄, K, Mg"),
        E("Severely malnourished elective patients: **7–14 days pre-op nutrition** before major surgery"),
    ]),
]

E_['shock'] = [
    F("Undifferentiated shock", "Surviving Sepsis Campaign 2021 · NICE NG51 · RCUK Anaphylaxis 2021", [
        S("Hypotension, tachycardia, ↓ urine output, confusion, **lactate > 2 mmol/L**"),
        P("ABCDE, high-flow O₂, 2 large-bore cannulae, bloods incl. lactate, crossmatch, cultures; catheter for hourly UO"),
        P("Bedside **echo/POCUS** + JVP + skin: classify the shock"),
        Q("Type", [
            ("Hypovolaemic (flat IVC, cold)", [P("**Stop the bleeding**, blood products, see haemorrhage chart")]),
            ("Distributive (warm, vasodilated)", [P("Sepsis: **antibiotics within 1 h**, 30 mL/kg balanced crystalloid, source control · anaphylaxis: **IM adrenaline 500 µg**, repeat at 5 min")]),
            ("Cardiogenic (big heart, wet lungs)", [P("ECG/troponin → PCI for ACS; **dobutamine** ± noradrenaline; avoid fluid overload")]),
            ("Obstructive", [P("**Decompress** tension pneumothorax, drain tamponade, thrombolyse massive PE")]),
        ]),
        P("Persistent hypotension → **noradrenaline** to **MAP ≥ 65 mmHg**; add vasopressin ± hydrocortisone in septic shock"),
        E("Neurogenic (spinal injury above T6: hypotension + bradycardia) → fluids, noradrenaline, atropine · adrenal crisis → **hydrocortisone 100 mg IV**"),
    ]),
    F("Haemorrhagic shock and major haemorrhage", "ATLS 10th ed · BSH/JPAC Major Haemorrhage · ESA/European Trauma 2023", [
        S("Bleeding patient with signs of shock"),
        P("Estimate loss — **ATLS class**: I < 15% · II 15–30% (tachycardia) · III 31–40% (hypotension) · IV > 40%"),
        P("**Control the source** (pressure, tourniquet, binder) and **activate major haemorrhage protocol**"),
        P("**TXA 1 g over 10 min within 3 h**, then 1 g over 8 h"),
        P("**Balanced blood products** (RBC:FFP 1:1, add platelets and cryoprecipitate); minimise crystalloid; warmed fluids, check ionised Ca²⁺"),
        P("**Permissive hypotension** (SBP 80–90 mmHg) until bleeding controlled — not in TBI (keep MAP ≥ 80)"),
        Q("Response to resuscitation", [
            ("Rapid", [P("Observe; CT to define injuries")]),
            ("Transient / none", [P("**Damage-control surgery** or interventional radiology now")]),
        ]),
        P("Targets: Hb 70–90 g/L, platelets > 75 × 10⁹/L (> 100 in TBI), **fibrinogen > 1.5 g/L**, PT ratio < 1.5; viscoelastic testing"),
        E("Avoid the **lethal triad**: hypothermia, acidosis, coagulopathy (+ hypocalcaemia)"),
    ]),
    F("Blood transfusion and transfusion reactions", "NICE NG24 · BSH 2023 · SHOT", [
        S("Surgical patient who may need blood"),
        P("Pre-op: correct anaemia (IV iron); **TXA if expected blood loss > 500 mL**; cell salvage"),
        P("**Restrictive threshold Hb 70 g/L** (target 70–90); 80 g/L if ACS; give **single units** and reassess if not bleeding"),
        P("Bedside **positive patient ID**, observations before, 15 min after start and at end"),
        Q("Acute reaction — stop transfusion, check ID", [
            ("Fever, loin pain, hypotension, red urine", [P("**ABO incompatibility**: stop, resuscitate, return unit, DAT, haemolysis screen, watch for DIC/AKI")]),
            ("Wheeze, angio-oedema, hypotension", [P("**Anaphylaxis**: IM adrenaline 500 µg, fluids")]),
            ("Hypoxia within 6 h", [P("**TRALI** (bilateral infiltrates, normal JVP) → O₂/ventilation · **TACO** (overload, ↑ BP) → diuretic")]),
            ("Isolated fever < 2 °C rise", [P("Febrile non-haemolytic: paracetamol, restart slowly")]),
        ]),
        E("Report serious reactions to **SHOT / MHRA SABRE**"),
    ]),
]

E_['obesity'] = [
    F("Selection and work-up for bariatric surgery", "NICE NG246 (2025) · IFSO/ASMBS 2022 · BOMSS", [
        S("Adult with obesity (BMI ≥ 30 kg/m²)"),
        P("Exclude secondary causes when suggested clinically: **TSH**, cortisol (Cushing’s), drugs; screen for eating disorders"),
        P("Specialist weight management: diet, activity, behavioural; **GLP-1/GIP agonists** (semaglutide, tirzepatide)"),
        Q("Surgical candidate?", [
            ("BMI ≥ 40, or ≥ 35 + comorbidity", [P("Refer for **bariatric surgery** if fit and committed to lifelong follow-up")]),
            ("BMI ≥ 35 (or 30–34.9) + recent T2DM", [P("**Expedited assessment** (metabolic surgery); thresholds 2.5 lower for Asian/Black ethnicity")]),
        ]),
        P("Pre-op: OSA screening (STOP-BANG/CPAP), smoking cessation, nutritional bloods, selective OGD, **2-week liver-shrinking diet**"),
        P("Procedure: **sleeve gastrectomy** (commonest) · **Roux-en-Y gastric bypass** (preferred with GORD/T2DM) · OAGB · SADI-S/duodenal switch for super-obesity"),
        E("Lifelong: multivitamin, calcium + vit D, iron, **IM B₁₂ 3-monthly**, annual bloods · avoid pregnancy for 12–18 months"),
    ]),
    F("Complications after bariatric surgery", "BOMSS · IFSO 2022 · Bailey & Love 28e", [
        S("Bariatric patient unwell after surgery"),
        Q("Timing", [
            ("Early (days)", [
                P("**Leak**: persistent **tachycardia > 120** may be the only sign → CT with oral + IV contrast"),
                P("Unstable → **re-laparoscopy**, washout, drains · contained → drainage + endoscopic stent/vacuum"),
                E("Also: bleeding, PE (extended prophylaxis), gastric outlet narrowing after sleeve")]),
            ("Late: pain/obstruction after bypass", [
                P("**Internal hernia** (Petersen’s): CT mesenteric swirl"),
                E("**Diagnostic laparoscopy even if CT normal** — risk of bowel infarction")]),
            ("Late: other", [
                P("Marginal ulcer (smoking, NSAIDs) → PPI · anastomotic stricture → endoscopic dilatation"),
                P("**Dumping**: early (osmotic, 30 min) / late (hypoglycaemia, 1–3 h) → small meals, avoid simple sugars"),
                E("Gallstones (UDCA × 6 months) · band slip/erosion → deflate/remove · deficiencies (iron, B₁₂, folate)")]),
        ]),
        E("Persistent vomiting → give **thiamine before glucose** (Wernicke’s encephalopathy)"),
    ]),
]

json.dump(E_, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flow_d.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
