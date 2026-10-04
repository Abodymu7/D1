"""Management flowcharts (Surgery Bank 3rd edition) - flow_a: neck, endo, bbreast, bca, paed.
Built from the old summary tables (summ_neck, summ_bbreast, summ_paed) and updated to the guidelines named on each chart.

Writes data/import/flows/flow_a.json  {chapter_id: [block, ...]}
"""
import json, os

S = lambda t: {"k": "start", "t": t}
P = lambda t: {"k": "step", "t": t}
E = lambda t: {"k": "end", "t": t}
Q = lambda q, br: {"k": "split", "q": q, "br": [{"l": l, "n": n} for l, n in br]}
F = lambda title, source, nodes: {"type": "flowchart", "title": title, "source": source, "nodes": nodes}
E_ = {}

# =================================================================== NECK LUMPS & ENDOCRINE
E_['neck'] = [
    F("Neck lump: from site to diagnosis", "NICE NG12 & NG36 · UK Head & Neck MDT 2016 · Bailey & Love 28e", [
        S("Patient with a lump in the neck"),
        P("History: age, duration, smoking, alcohol, B symptoms · site, movement, transillumination, pulsatility + **full ENT exam with nasendoscopy**"),
        Q("Site and character", [
            ("Midline", [
                P("Moves up on **tongue protrusion** → **thyroglossal cyst**: USS (confirm normal thyroid) → **Sistrunk’s operation** (cyst + tract + central hyoid)"),
                P("Moves on swallowing only → thyroid (nodule pathway) · submental, not moving → dermoid cyst → excision")]),
            ("Lateral cystic, child/young adult", [
                P("Anterior to upper third of SCM → **branchial cyst**: USS ± FNA (cholesterol crystals) → complete excision once infection settles"),
                P("Soft, transilluminant, posterior triangle in infant → **lymphatic malformation**: MRI → **sclerotherapy** (OK-432, bleomycin) or excision")]),
            ("Pulsatile at carotid bifurcation", [
                P("**Carotid body paraganglioma**: moves side to side, not vertically · **never FNA or biopsy**"),
                P("CT/MR angiography (splayed ICA/ECA – lyre sign), plasma metanephrines, SDHx gene testing"),
                E("Excision by vascular/H&N team (Shamblin grade predicts risk) or surveillance/radiotherapy if elderly or unfit")]),
            ("Firm lateral lymph node", [P("Recent URTI, tender → reactive: treat and **review at 3–6 weeks**; persisting node → sample (below)")]),
        ]),
        P("Persistent unexplained neck lump (esp. age ≥ 45, smoker) or cystic lateral mass > 40 y → **2-week-wait head & neck referral**"),
        P("**USS-guided FNA/core biopsy** first · CT/MRI neck + chest · never open excision of a possible SCC node"),
        Q("Tissue result", [
            ("Metastatic SCC", [P("p16/HPV, **PET-CT**, panendoscopy ± tonsillectomy/tongue-base mucosectomy for unknown primary → H&N MDT")]),
            ("Lymphoma", [P("Core or **excision biopsy** for architecture → haematology (staging PET-CT)")]),
            ("Tuberculous adenitis", [P("AFB smear, culture, GeneXpert → **6-month anti-TB therapy**; aspirate cold abscess, avoid incision (sinus)")]),
        ]),
        E("Adult cystic lateral neck mass = metastatic (HPV+ oropharyngeal) SCC until proven otherwise"),
    ]),
    F("Thyroid nodule and goitre", "BTA 2014 thyroid cancer · NICE NG145 (2019) & NG230 (2022)", [
        S("Thyroid nodule or goitre (palpable or incidental)"),
        P("**TSH first** · low TSH → isotope scan: hot nodule = toxic adenoma (rarely malignant) → treat hyperthyroidism, no FNA"),
        P("Red flags: rapid growth, stridor, hoarseness, fixed hard mass, nodes, childhood neck irradiation, MEN2 family history → urgent referral"),
        P("**Ultrasound U-score**: U1 normal · U2 benign · U3 indeterminate · U4 suspicious · U5 malignant → **USS-guided FNA if U3–U5**"),
        Q("FNA cytology (Thy)", [
            ("Thy1 non-diagnostic", [P("**Repeat USS-guided FNA** (± core); Thy1c cyst with benign USS → observe")]),
            ("Thy2 benign", [P("Reassure/discharge if U2 · repeat FNA if U3–U5 or clinical concern")]),
            ("Thy3a / Thy3f / Thy4", [P("Thy3a → repeat FNA/core, MDT · Thy3f & Thy4 → **diagnostic hemithyroidectomy**")]),
            ("Thy5 malignant", [P("Stage (USS nodes ± CT) → MDT → definitive surgery by tumour type (below)")]),
        ]),
        Q("Cancer type", [
            ("Papillary / follicular", [
                P("≤ 4 cm, N0, low risk → **hemithyroidectomy** · > 4 cm, extrathyroidal, nodes or metastases → **total thyroidectomy** ± neck dissection"),
                E("Risk-adapted **radioiodine** + TSH suppression for high risk; follow-up with thyroglobulin")]),
            ("Medullary (C cells)", [
                P("Calcitonin, CEA, **RET testing** · **exclude phaeochromocytoma first**"),
                E("**Total thyroidectomy + central neck dissection**; no role for radioiodine")]),
            ("Anaplastic / lymphoma", [
                P("Anaplastic: secure airway, BRAF testing, MDT (usually palliative) · lymphoma (Hashimoto’s): core biopsy → **R-CHOP ± RT**, not surgery")]),
        ]),
        E("Benign nodular goitre: **no thyroxine suppression** · surgery only for compression, retrosternal extension, growth or cosmesis"),
    ]),
    F("Thyrotoxicosis and safe thyroidectomy", "NICE NG145 (2019) · ETA 2018 Graves · DAS/BAETS 2022 haematoma", [
        S("Low TSH with raised FT4/FT3: tremor, palpitations, weight loss, heat intolerance"),
        P("**Propranolol** for symptoms (diltiazem if asthmatic) · TSH-receptor antibodies (TRAb) · isotope scan if TRAb negative or nodular"),
        Q("Cause", [
            ("Graves (TRAb +, diffuse uptake)", [
                P("**Carbimazole** 12–18 months (titration or block-and-replace); PTU in 1st trimester"),
                P("Warn: sore throat/fever → urgent FBC (**agranulocytosis**) · relapse ~50% → definitive treatment")]),
            ("Toxic nodule / toxic MNG", [P("Antithyroid drug to euthyroid → **radioiodine** or surgery (hemithyroidectomy / total) – rarely remits")]),
            ("Thyroiditis (low uptake)", [P("Painful, post-partum or amiodarone: beta-blocker ± NSAID/steroid; **no antithyroid drugs**")]),
        ]),
        P("Definitive: **radioiodine** (not in pregnancy, avoid conception 6 months, steroid cover/avoid if active orbitopathy) or **total thyroidectomy**"),
        P("Surgery if compressive goitre, active eye disease, suspicious nodule, pregnancy plans or choice · pre-op euthyroid + **potassium iodide 10 days**"),
        P("Pre-op laryngoscopy (cords), calcium · post-op levothyroxine, **adjusted Ca/PTH next morning**"),
        Q("Post-thyroidectomy emergency", [
            ("Neck haematoma, stridor", [P("**SCOOP at bedside**: Skin exposure, Cut sutures, Open skin, Open muscles, Pack → then theatre; call anaesthetist")]),
            ("Hypocalcaemia (tingling, Chvostek)", [P("Mild: oral calcium + **alfacalcidol** · tetany/QT long: **10 mL 10% calcium gluconate IV** over 10 min, then infusion")]),
            ("Hoarse voice / stridor", [P("Unilateral RLN palsy → laryngoscopy, voice therapy · bilateral → **reintubation / tracheostomy**")]),
            ("Fever, tachycardia, delirium", [P("**Thyroid storm**: ICU, propranolol, PTU then iodide 1 h later, hydrocortisone, cooling, fluids")]),
        ]),
        E("Make the patient euthyroid before any surgery or radioiodine – prevents thyroid storm"),
    ]),
]

E_['endo'] = [
    F("Hypercalcaemia and hyperparathyroidism", "NICE NG132 (2019) · 5th International Workshop PHPT 2022 · KDIGO 2017 CKD-MBD", [
        S("Raised albumin-adjusted calcium (often incidental): stones, bones, groans, psychic moans"),
        P("Ca > 3.0 mmol/L or symptomatic → **IV 0.9% saline 3–4 L/24 h**, then IV bisphosphonate (zoledronate); stop thiazides"),
        P("Repeat adjusted Ca + **PTH**, phosphate, 25-OH vitamin D, eGFR"),
        Q("Calcium/PTH pattern", [
            ("High Ca, PTH suppressed", [E("Non-parathyroid: **malignancy** (PTHrP, myeloma screen), vitamin D excess, sarcoid, drugs → treat cause")]),
            ("High Ca, PTH high/inappropriately normal", [P("**Primary HPT** (solitary adenoma ~85%) · exclude **FHH**: urine Ca:Cr clearance ratio < 0.01 → no surgery")]),
            ("Low/normal Ca, high PTH, CKD", [P("**Secondary HPT**: phosphate restriction + binders, vitamin D, alfacalcidol, **cinacalcet** → parathyroidectomy if refractory")]),
            ("High Ca after long CKD / transplant", [P("**Tertiary HPT** (autonomous): cinacalcet → **subtotal (3½-gland) or total parathyroidectomy + forearm autograft**")]),
        ]),
        P("Primary HPT: replete vitamin D · renal USS (stones), DEXA incl. distal radius, 24-h urine calcium"),
        P("Surgery if symptoms, renal stones, osteoporosis/fragility fracture, eGFR < 60 or **adjusted Ca ≥ 2.85 mmol/L** (consider in all)"),
        Q("Surgery indicated?", [
            ("Yes", [
                P("Localise: **neck USS + sestamibi SPECT-CT** (or 4D-CT / choline PET)"),
                P("Concordant → **focused parathyroidectomy** + intra-op PTH (> 50% fall) · non-localised, multigland, MEN → bilateral neck exploration")]),
            ("No / unfit / declines", [P("Monitor Ca & eGFR, DEXA · **cinacalcet** for hypercalcaemia, bisphosphonate for bone; offer surgery again if criteria met")]),
        ]),
        E("Post-op: watch for **hungry bone syndrome** (calcium + alfacalcidol) · cure = normocalcaemia at 6 months"),
    ]),
    F("Multiple endocrine neoplasia (MEN)", "ATA 2015 medullary thyroid cancer · Thakker 2012 MEN1 · Bailey & Love 28e", [
        S("Two or more endocrine tumours, multigland/young HPT, medullary thyroid cancer or family history"),
        P("Screen: adjusted Ca + PTH, calcitonin, **plasma metanephrines**, prolactin, fasting gut hormones"),
        P("**Genetic testing**: MEN1 (menin) or **RET proto-oncogene** → cascade-test first-degree relatives"),
        Q("Syndrome", [
            ("MEN1: 3 Ps", [
                P("**Parathyroid hyperplasia** (~95%) → subtotal (3½-gland) or total parathyroidectomy + autotransplant + **transcervical thymectomy**"),
                P("**Pancreatic NETs** (gastrinoma, insulinoma, non-functioning) → resect if functioning or > 2 cm"),
                P("**Pituitary** adenoma: prolactinoma → cabergoline; others → trans-sphenoidal surgery"),
                E("Lifelong annual biochemistry + periodic imaging from childhood")]),
            ("MEN2A: MTC + phaeo + HPT", [
                P("**Exclude phaeochromocytoma first** (plasma metanephrines) → α-blockade → adrenalectomy before other surgery"),
                P("**Prophylactic total thyroidectomy** by RET risk: high risk (codon 634) **by age 5**; moderate risk when calcitonin rises"),
                E("Established MTC → total thyroidectomy + central neck dissection; follow calcitonin & CEA")]),
            ("MEN2B: M918T", [
                P("MTC + phaeo + **marfanoid habitus, mucosal neuromas**, no HPT"),
                E("**Total thyroidectomy in the first year of life** (most aggressive MTC)")]),
        ]),
        E("Always treat a phaeochromocytoma before thyroid or parathyroid surgery; MTC does not take up radioiodine"),
    ]),
    F("Functioning pancreatic neuroendocrine tumour", "ENETS 2023 functioning pNET · ESMO 2020 GEP-NEN", [
        S("Suspected hormone-secreting pancreatic NET"),
        Q("Clinical syndrome", [
            ("Insulinoma: Whipple’s triad", [
                P("**Supervised 72-h fast**: glucose < 3.0 mmol/L with raised insulin, C-peptide, proinsulin; negative sulfonylurea screen"),
                P("Usually single, benign, < 2 cm → **EUS** + CT/MRI (GLP-1R PET if occult) → **enucleation** or distal pancreatectomy")]),
            ("Gastrinoma: Zollinger–Ellison", [
                P("Refractory/multiple/jejunal ulcers + diarrhoea → **fasting gastrin > 10× ULN with gastric pH < 2** (± secretin test)"),
                P("**High-dose PPI** · gastrinoma triangle (duodenum) · 20–25% MEN1 → resect if sporadic and localised")]),
            ("Glucagonoma / VIPoma", [P("Glucagonoma: necrolytic migratory erythema, diabetes, DVT · VIPoma: watery diarrhoea, ↓K⁺ → **somatostatin analogue** + resection")]),
        ]),
        P("Stage: CT/MRI + EUS · **⁶⁸Ga-DOTATATE PET-CT** · grade by Ki-67 (G1 < 3%, G2 3–20%, G3 > 20%)"),
        P("Screen for MEN1: calcium, PTH, prolactin"),
        E("Metastatic: somatostatin analogue, **PRRT (¹⁷⁷Lu-DOTATATE)**, everolimus/sunitinib, liver-directed therapy · resect where feasible"),
    ]),
]

# =================================================================== BREAST
E_['bbreast'] = [
    F("Breast lump: triple assessment", "NICE NG12 · ABS 2019 best-practice diagnostic guidelines · Bailey & Love 28e", [
        S("Woman with a breast lump"),
        P("**2-week-wait** if ≥ 30 y with unexplained lump (or skin change, ≥ 50 with nipple change) · < 30 y → non-urgent breast clinic"),
        P("**Triple assessment** in one-stop clinic: clinical exam + imaging + **core biopsy**"),
        P("Imaging: **USS if < 40 y**; mammography + USS if ≥ 40 y · score P/U/M 1–5; any score ≥ 3 → core biopsy"),
        Q("Diagnosis", [
            ("Fibroadenoma (young, mobile)", [P("U2 and < 25 y → no biopsy needed · otherwise core-confirm → reassure · > 3 cm, growing or symptomatic → **vacuum-assisted or surgical excision**")]),
            ("Cyst (fluctuant, perimenopausal)", [P("**Aspirate** if symptomatic · discard clear fluid · **bloody aspirate or residual mass → core biopsy**")]),
            ("Rapidly growing large lump", [P("**Phyllodes tumour** on core → **wide local excision with clear margins** (≥ 1 cm if borderline/malignant), no axillary surgery")]),
            ("Trauma, firm irregular mass", [P("**Fat necrosis** (oil cyst, coarse calcification) – mimics cancer → core biopsy to confirm")]),
        ]),
        E("Concordant benign triple assessment → reassure and discharge · any discordance → repeat biopsy or excision"),
    ]),
    F("Nipple discharge", "NICE NG12 · ABS 2019 · Bailey & Love 28e", [
        S("Nipple discharge"),
        P("Character: one or many ducts, uni/bilateral, spontaneous vs expressed, colour, blood (dipstick), associated lump"),
        Q("Type of discharge", [
            ("Bilateral milky (galactorrhoea)", [P("Pregnancy test, **prolactin**, TFT, drug history (antipsychotics, metoclopramide) → pituitary MRI if prolactin high")]),
            ("Multiduct, green/brown, cheesy", [P("Physiological / **duct ectasia** (smokers, perimenopause) → imaging if ≥ 40 y → reassure")]),
            ("Single duct, bloody or serous", [
                P("**Mammography + USS** (≥ 40 y) or USS (< 40) ± core biopsy of any lesion"),
                P("Commonest cause **intraductal papilloma** → **microdochectomy** (diagnostic + therapeutic)")]),
        ]),
        P("≥ 50 y with discharge, retraction or other nipple change → **2-week-wait**"),
        E("Older woman, multiduct troublesome discharge or ectasia → **total duct excision (Hadfield’s)** · eczematous nipple → exclude Paget’s"),
    ]),
    F("Breast pain and breast infection", "NICE CKS 2023 mastitis & mastalgia · ABS 2019 · Bailey & Love 28e", [
        S("Painful or inflamed breast"),
        P("Ask: cycle relation, lactation, smoking, drugs (HRT, OCP), trauma · examine for lump, abscess, skin change"),
        Q("Which picture?", [
            ("Cyclical / non-cyclical mastalgia", [
                P("Examine; imaging only if focal lump or signs · pain alone is **not** a cancer red flag"),
                P("**Reassurance**, well-fitting bra, **topical NSAID**; pain diary · evening primrose oil not recommended"),
                E("Severe refractory: specialist tamoxifen 10 mg (off-label) · danazol rarely (side-effects)")]),
            ("Lactational mastitis", [
                P("**Continue breastfeeding/expressing**, analgesia · **flucloxacillin** 10–14 days (clarithromycin if penicillin allergy)"),
                E("Fluctuant/not settling → USS → **needle aspiration** (repeat) or mini-incision drainage")]),
            ("Non-lactational (periductal)", [
                P("Young smoker, periareolar → **co-amoxiclav** (or clarithromycin + metronidazole), **stop smoking**"),
                E("Abscess → USS-guided aspiration · recurrent or **mammary duct fistula** → total duct excision + fistula excision")]),
        ]),
        P("Inflammation not settling after one or two antibiotic courses → imaging + **core/punch biopsy**"),
        E("Persistent erythema, oedema, peau d’orange despite antibiotics = **inflammatory breast cancer** until proven otherwise"),
    ]),
]

E_['bca'] = [
    F("Suspected breast cancer: diagnosis and staging", "NICE NG101 (2018, updated) · NICE NG12 · ESMO 2024 early breast cancer", [
        S("Breast lump, skin/nipple change, axillary node or screen-detected abnormality"),
        P("**Triple assessment**: exam + mammography/USS + **core biopsy** → ER, PR, **HER2**, grade, Ki-67"),
        P("**Axillary USS** ± core/FNA of abnormal node · MRI if lobular, dense breasts, size discordance, Paget’s or occult primary"),
        P("Staging CT chest/abdomen/pelvis ± bone scan **only** if T3–4, N2–3, inflammatory, symptoms or high-risk neoadjuvant"),
        Q("MDT plan", [
            ("Operable early (T1–2, N0–1)", [P("**Primary surgery**, or neoadjuvant systemic therapy if HER2+ or triple-negative ≥ T2/N+, or to permit breast conservation")]),
            ("Locally advanced / inflammatory", [P("**Neoadjuvant chemotherapy** (+ HER2 therapy) → mastectomy + ALND + chest-wall RT; no immediate reconstruction if inflammatory")]),
            ("Metastatic (bone, lung, liver, brain)", [P("Biopsy a metastasis (receptors) → **systemic therapy by subtype**; surgery only for palliation")]),
        ]),
        P("**Germline BRCA testing** if triple-negative < 60 y, diagnosis < 40 y, male breast cancer, or ≥ 10% carrier probability"),
        E("Paget’s nipple, male breast lump and inflammatory change are cancer until biopsy proves otherwise"),
    ]),
    F("Breast and axillary surgery", "NICE NG101 · ABS 2023 · Z0011 / AMAROS / FAST-Forward trials", [
        S("Operable invasive breast cancer"),
        Q("Breast operation", [
            ("Breast-conserving surgery", [
                P("**Wide local excision** (± oncoplastic) with clear margins: no tumour on ink (invasive), ≥ 2 mm (DCIS)"),
                E("Always + **whole-breast RT 26 Gy in 5 fractions** (may omit if ≥ 65 y, T1N0, ER+, low grade on endocrine)")]),
            ("Mastectomy", [
                P("Large tumour:breast ratio, multicentric, RT contraindicated, inflammatory, BRCA or choice"),
                E("Offer **immediate reconstruction** (implant or flap) · post-mastectomy RT if N+ or T3–4")]),
        ]),
        Q("Axilla", [
            ("Clinically and USS node-negative", [P("**Sentinel lymph node biopsy** (isotope + blue dye, or magnetic tracer)")]),
            ("SLNB: 1–2 macrometastases", [P("BCS + RT + systemic therapy → **no further axillary surgery** (Z0011) · mastectomy → axillary RT or ALND")]),
            ("Biopsy-proven node-positive", [P("**Axillary node clearance** (levels I–II) or axillary RT; after neoadjuvant response → targeted axillary surgery")]),
        ]),
        P("DCIS: BCS + RT (or mastectomy if extensive) · SLNB only if mastectomy or suspected invasion"),
        E("Watch for seroma, lymphoedema, intercostobrachial numbness, **long thoracic (winged scapula)** and thoracodorsal nerve injury"),
    ]),
    F("Adjuvant systemic therapy by receptor status", "NICE NG101 · ESMO 2024 early breast cancer · NICE TA810/TA851/TA886", [
        S("Breast cancer after surgery, or before it (neoadjuvant)"),
        P("Estimate benefit with **PREDICT** ± gene expression test (Oncotype DX) for ER+/HER2−, node 0–3"),
        Q("Receptor status", [
            ("ER+ / HER2− (~70%)", [
                P("**Endocrine therapy 5–10 years**: premenopausal → tamoxifen (± ovarian suppression + AI if high risk); postmenopausal → **aromatase inhibitor**"),
                P("Chemotherapy if high genomic/PREDICT risk · **abemaciclib 2 y** if node+ high risk · olaparib if gBRCA")]),
            ("HER2+ (~15%)", [
                P("Chemotherapy + **trastuzumab 1 year** (+ pertuzumab if node+) · **baseline + 3-monthly echo** (cardiotoxicity)"),
                P("Residual disease after neoadjuvant → **T-DM1** (trastuzumab emtansine)")]),
            ("Triple-negative (~15%)", [
                P("Neoadjuvant anthracycline–taxane + carboplatin + **pembrolizumab** (if ≥ T2 or N+)"),
                P("Residual disease → **capecitabine** (or olaparib if gBRCA)")]),
        ]),
        P("Postmenopausal node-positive → **adjuvant bisphosphonate** (zoledronic acid) · AI → DEXA; tamoxifen → VTE & endometrial risk"),
        E("Metastatic ER+: AI/fulvestrant + **CDK4/6 inhibitor** · HER2+: trastuzumab + pertuzumab + docetaxel · bone mets: denosumab/bisphosphonate"),
    ]),
]

# =================================================================== PAEDIATRIC SURGERY
E_['paed'] = [
    F("Vomiting infant: pyloric stenosis vs malrotation", "NICE NG29 IV fluids in children · Bailey & Love 28e", [
        S("Infant with persistent vomiting"),
        Q("Is the vomit bile-stained (green)?", [
            ("Yes – bilious", [
                P("**Malrotation with midgut volvulus until proven otherwise**: NG tube, IV fluids, urgent surgical review"),
                P("**Urgent upper GI contrast**: DJ flexure right of midline, corkscrew duodenum (USS whirlpool sign)"),
                E("**Emergency Ladd’s procedure**: derotate anticlockwise, divide Ladd’s bands, widen mesentery, appendicectomy")]),
            ("No – projectile, 2–8 weeks old", [
                P("**Pyloric stenosis**: first-born male, hungry after vomiting · **test feed** for olive in RUQ/epigastrium")]),
        ]),
        P("**USS**: pyloric muscle ≥ 3 mm thick, channel ≥ 15 mm long"),
        P("Gas: **hypochloraemic, hypokalaemic metabolic alkalosis** (paradoxical aciduria)"),
        P("**Resuscitate first – it is not a surgical emergency**: 0.9% saline + 5% glucose, add KCl once passing urine; NG tube"),
        P("Operate only when **Cl⁻ ≥ 100 mmol/L, HCO₃⁻ < 28 mmol/L**, K⁺ normal"),
        E("**Ramstedt pyloromyotomy** (open or laparoscopic) → feeds within hours · complications: mucosal perforation, wound infection"),
    ]),
    F("Intussusception", "APSA 2021 intussusception review · Bailey & Love 28e", [
        S("Child 3 months – 3 years: paroxysmal colic, drawing up legs, pallor, vomiting"),
        P("Late signs: **redcurrant-jelly stool**, sausage-shaped mass, empty RIF · often after viral illness (Peyer’s patches)"),
        P("**USS: target/doughnut sign** (diagnostic) · AXR only if perforation suspected"),
        P("Resuscitate: IV access, fluid bolus, NG if vomiting, antibiotics; surgeon informed before reduction"),
        Q("Peritonitis, perforation or uncorrected shock?", [
            ("No", [
                P("**Air (pneumatic) enema reduction** under fluoroscopy (~80–90% success)"),
                P("Partial reduction, child stable → **repeat enema** after 30 min–few hours")]),
            ("Yes, or enema fails", [
                P("**Laparoscopy/laparotomy**: manual reduction by squeezing (not pulling) · resect if non-viable or lead point")]),
        ]),
        P("Lead point (Meckel’s, polyp, duplication, lymphoma, HSP) more likely if < 3 months or > 3 years or recurrent"),
        E("Recurrence ~10% after enema reduction – warn parents to return early"),
    ]),
    F("Neonatal anomalies: OA/TOF, Hirschsprung, anorectal malformation", "ERNICA 2019 OA & 2020 Hirschsprung consensus · Bailey & Love 28e", [
        S("Newborn with feeding problem, distension or abnormal perineum"),
        P("Keep warm, IV maintenance fluid with 10% glucose, **NG decompression** if vomiting · examine perineum in every baby"),
        Q("Presentation", [
            ("Frothing, choking, cough on feeds", [
                P("**Oesophageal atresia**: NG tube coils at T2–T4 on CXR; gastric gas = distal TOF (type C, ~85%)"),
                P("**Replogle tube on continuous suction**, nil by mouth, head up · echo (aortic arch side) + VACTERL screen"),
                E("**Ligation of TOF + primary oesophageal anastomosis** · watch for leak, stricture, GORD, tracheomalacia")]),
            ("No meconium by 48 h, distension", [
                P("**Hirschsprung**: contrast enema (transition zone) → **suction rectal biopsy**: absent ganglion cells, ↑ acetylcholinesterase, absent calretinin"),
                P("**Rectal washouts** · enterocolitis (fever, explosive stool) → nil by mouth, IV antibiotics, washouts"),
                E("**Pull-through** (transanal Soave/Duhamel/Swenson) · stoma if washouts fail")]),
            ("Abnormal or absent anus", [
                P("**Anorectal malformation**: wait 24 h for meconium at perineum/urine · VACTERL: echo, renal & spinal USS, sacral X-ray"),
                E("Perineal fistula → **anoplasty/PSARP** · no visible fistula (high) → **colostomy** then PSARP at 1–3 months")]),
        ]),
        E("Screen every neonatal anomaly for VACTERL associations; Down syndrome ↔ Hirschsprung & duodenal atresia"),
    ]),
]

json.dump(E_, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flow_a.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('chapters', len(E_), 'charts', sum(len(v) for v in E_.values()))
