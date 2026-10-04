"""Management flowcharts (Surgery Bank 3rd edition) - Abdomen part.
Chapters: acute, liver, gb, panc, spleen, adrenal, hernia.
Built from ../surg/summ_abd.txt and updated to the current guidelines named on each chart.

Writes data/import/flows/flow_c.json  {chapter_id: [block, ...]}

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

# =================================================================== ACUTE ABDOMEN & ABDOMINAL TRAUMA
E_['acute'] = [
    F("Suspected acute appendicitis", "WSES 2020 Jerusalem guidelines · Bailey & Love 28e", [
        S("Periumbilical pain migrating to the RIF, anorexia, nausea, low-grade fever"),
        P("FBC, CRP, urinalysis, **pregnancy test in every woman of reproductive age**; analgesia, IV fluids"),
        P("Stratify with a score: **Alvarado, AIR or Adult Appendicitis Score** → low, intermediate or high probability"),
        Q("Probability?", [
            ("Low", [P("Discharge with safety-net or short observation; re-assess in 12–24 h if pain persists")]),
            ("Intermediate", [P("**Imaging**: ultrasound first (children, young women, pregnancy → MRI if US inconclusive); **low-dose CT** in adults")]),
            ("High", [P("Proceed to surgery; imaging optional < 40 y, advisable in older adults (exclude tumour, diverticulitis)")]),
        ]),
        Q("Confirmed appendicitis: what type?", [
            ("Uncomplicated", [
                P("**Laparoscopic appendicectomy** (within 24 h); single pre-op antibiotic dose, none after"),
                P("Antibiotics-first is an option if no appendicolith, but ~40% need appendicectomy within 5 years")]),
            ("Gangrenous / perforated", [
                P("**Urgent laparoscopic appendicectomy**, suction of pus (lavage adds nothing)"),
                P("Post-op antibiotics **3–5 days** only")]),
            ("Mass (phlegmon) or abscess", [
                P("IV antibiotics; abscess > 3 cm → **percutaneous drainage**"),
                P("Interval appendicectomy not routine; **colonoscopy + CT if ≥ 40 y** (neoplasm risk)")]),
        ]),
        E("Normal-looking appendix with no other cause found: remove it; always check for Meckel’s diverticulum and adnexal pathology"),
    ]),
    F("Acute abdomen with peritonitis, collection or shock", "WSES 2017 intra-abdominal infection · NELA · ESVS 2024 AAA", [
        S("Severe abdominal pain ± peritonism, tachycardia, hypotension"),
        P("ABCDE; **Sepsis Six within 1 h** (O₂, cultures, IV antibiotics, fluids, lactate, urine output)"),
        P("FBC, U&E, LFT, **lipase/amylase**, lactate, VBG, group & save, βhCG; ECG (inferior MI), erect CXR"),
        Q("Which picture?", [
            ("Back pain, pulsatile mass, shock", [
                P("**Ruptured AAA**: permissive hypotension (SBP 70–90 mmHg, conscious), major haemorrhage protocol"),
                P("CT angiography only if stable → **EVAR if anatomy suitable**, otherwise open repair"),
                E("Elective repair: ≥ 5.5 cm (≥ 5.0 cm women, ESVS), growth > 1 cm/yr or symptomatic · screen men at 65")]),
            ("Generalised peritonitis / free gas", [
                P("**CT abdomen-pelvis** if stable; broad-spectrum IV antibiotics (e.g. piperacillin–tazobactam)"),
                P("**Source control**: laparoscopy/laparotomy, e.g. perforated ulcer → omental patch + PPI + H. pylori eradication")]),
            ("Localised collection", [
                P("IV antibiotics + **image-guided percutaneous drainage**; surgery if it fails or is inaccessible")]),
            ("Pain out of proportion, AF", [
                P("Suspect **mesenteric ischaemia** (lactate may be normal early) → **CT angiography**"),
                P("Revascularise (endovascular/open), resect dead bowel, planned second look")]),
        ]),
        P("Emergency laparotomy with predicted mortality ≥ 5%: **consultant surgeon + anaesthetist present**, critical care after (NELA)"),
        E("Antibiotics **~4 days after adequate source control** · physiologically exhausted → **damage-control surgery**, ICU, relook 24–48 h"),
    ]),
    F("Blunt and penetrating abdominal trauma", "ATLS 10th ed · WSES 2020 liver & spleen trauma · NICE NG39", [
        S("Abdominal trauma: seatbelt sign, abdominal pain, shock, penetrating wound"),
        P("**<C>ABCDE**: control external bleeding, 2 large-bore IV/IO, bloods + crossmatch, **tranexamic acid 1 g within 3 h**"),
        P("Major haemorrhage protocol: **balanced transfusion** (RBC:FFP 1:1, platelets), permissive hypotension until bleeding controlled (not in TBI)"),
        P("**eFAST** in the resuscitation room; pelvic binder if pelvic injury possible"),
        Q("Haemodynamics?", [
            ("Unstable, FAST positive", [
                P("**Damage-control laparotomy**: pack, control bleeding and contamination, temporary closure")]),
            ("Unstable, FAST negative", [
                P("Look elsewhere: chest, **pelvis** (binder, angioembolisation, pre-peritoneal packing), long bones, scalp")]),
            ("Stable or responding", [
                P("**CT chest-abdomen-pelvis with IV contrast**"),
                P("Solid-organ injury → **non-operative management** ± angioembolisation for contrast blush; serial exam & Hb")]),
        ]),
        E("Penetrating: shock, peritonitis, evisceration or gunshot to abdomen → **laparotomy**; stable stab wound → CT ± serial examination"),
    ]),
]

# =================================================================== LIVER
E_['liver'] = [
    F("Jaundice: pre-hepatic, hepatic or post-hepatic?", "BSG 2018 abnormal liver blood tests · Bailey & Love 28e", [
        S("Yellow sclera/skin (clinically visible when bilirubin > ~40 µmol/L)"),
        P("History: pain, fever, weight loss, pruritus, pale stools/dark urine, alcohol, drugs, travel; examine for **Courvoisier’s sign**"),
        P("**Split bilirubin + LFT pattern** (ALT, ALP, GGT), FBC, film, INR, albumin; **ultrasound first-line**"),
        Q("Pattern?", [
            ("Unconjugated, normal LFTs", [
                P("**Pre-hepatic**: haemolysis (reticulocytes, LDH↑, haptoglobin↓, film, DAT) or Gilbert’s syndrome"),
                E("Treat the cause; Gilbert’s is benign → reassure")]),
            ("ALT ≫ ALP, ducts not dilated", [
                P("**Hepatocellular**: viral serology (A, B, C, E), autoantibodies, immunoglobulins, ferritin, paracetamol level"),
                E("Stop hepatotoxins; rising INR or encephalopathy → **liver unit** (King’s College criteria)")]),
            ("ALP/GGT ≫ ALT, dilated ducts", [
                P("**Obstructive**: MRCP (stones, strictures) or pancreatic-protocol CT (mass) ± EUS"),
                E("ERCP for stones/stent; resection if malignant and resectable (see gb and panc charts)")]),
        ]),
        E("Before intervention: **vitamin K** if INR prolonged, IV fluids (renal protection); cholangitis → antibiotics + urgent drainage"),
    ]),
    F("Focal liver lesion: abscess, cyst or benign tumour", "EASL 2016 benign liver tumours · WHO-IWGE echinococcosis", [
        S("Liver lesion on ultrasound: symptomatic or incidental"),
        P("Characterise with **contrast-enhanced CT/MRI** (or CEUS); LFTs, CRP, blood cultures, travel and cancer history"),
        Q("What is it?", [
            ("Fever, RUQ pain, rim-enhancing", [
                P("**Pyogenic abscess**: blood cultures, IV antibiotics (e.g. ceftriaxone + metronidazole) for 4–6 weeks"),
                P("**Percutaneous aspiration/drainage** if > 3–5 cm; find the source (biliary, colonic)"),
                P("Amoebic (travel, serology +): **metronidazole** then a luminal agent; drain only if no response")]),
            ("Cyst with daughter cysts", [
                P("**Hydatid**: serology, WHO cyst stage; **albendazole** cover"),
                P("PAIR for CE1/CE3a, otherwise surgery (pericystectomy); avoid spillage → anaphylaxis")]),
            ("Benign solid lesion", [
                P("**Haemangioma or FNH** (central scar): typical imaging → no follow-up"),
                P("**Adenoma**: stop OCP, lose weight; **resect if ≥ 5 cm** at 6 months, any in men, or bleeding")]),
            ("Cirrhosis or cancer history", [
                E("Treat as **HCC or metastasis** until proven otherwise → next chart")]),
        ]),
        E("Simple cysts: no follow-up; treat only if symptomatic (laparoscopic deroofing) · never biopsy a suspected hydatid cyst"),
    ]),
    F("Hepatocellular carcinoma and liver metastases", "EASL 2018 HCC · BCLC 2022 · ESMO 2023 mCRC", [
        S("Cirrhosis or chronic HBV under surveillance (**US ± AFP every 6 months**) or new solid lesion"),
        P("Nodule ≥ 1 cm → **multiphase CT or MRI**: arterial enhancement + washout = HCC in cirrhosis, **no biopsy needed**"),
        P("Stage with **BCLC**: tumour burden, liver function (Child–Pugh, ALBI), performance status; HCC MDT"),
        Q("BCLC stage?", [
            ("0 / A: early", [
                P("**Resection** (Child A, no portal hypertension), **ablation** ≤ 3 cm, or **transplant** within Milan criteria"),
                E("Milan: single ≤ 5 cm or ≤ 3 nodules each ≤ 3 cm, no vascular invasion")]),
            ("B: intermediate", [
                P("**TACE**; transplant if downstaged within criteria")]),
            ("C: advanced", [
                P("Systemic: **atezolizumab + bevacizumab** or durvalumab + tremelimumab; lenvatinib/sorafenib 2nd choice")]),
            ("D: end-stage", [
                E("Best supportive care")]),
        ]),
        E("**Colorectal liver metastases**: resect if R0 possible with future liver remnant ≥ 25–30% ± peri-operative chemo; ablation"),
    ]),
]

# =================================================================== GALLBLADDER & BILIARY TREE
E_['gb'] = [
    F("Gallstones: biliary colic and acute cholecystitis", "Tokyo Guidelines 2018 · NICE CG188", [
        S("Gallstones on ultrasound ± RUQ/epigastric pain after meals"),
        P("FBC, CRP, LFT, amylase/lipase; **ultrasound**: wall > 4 mm, pericholecystic fluid, sonographic Murphy’s, CBD diameter"),
        Q("Clinical picture?", [
            ("Asymptomatic stones", [
                E("**No treatment**: reassure, explain symptoms to report")]),
            ("Biliary colic", [
                P("Analgesia (NSAID); **elective laparoscopic cholecystectomy**")]),
            ("Acute cholecystitis", [
                P("IV fluids, analgesia, antibiotics; grade with **TG18** (I mild, II moderate, III organ dysfunction)"),
                P("Grade I–II and fit → **early laparoscopic cholecystectomy** (≤ 72 h ideal; NICE ≤ 1 week)"),
                P("Grade III or unfit → organ support + **percutaneous cholecystostomy**; delayed cholecystectomy if fit")]),
            ("Jaundice / LFTs ↑ / pancreatitis", [
                E("Look for **CBD stones** or cholangitis → next chart")]),
        ]),
        P("At surgery achieve the **critical view of safety**; if not possible → subtotal cholecystectomy or cholecystostomy"),
        E("Bile leak or duct injury: drain, ERCP ± stent; major injury → **refer HPB unit** (hepaticojejunostomy)"),
    ]),
    F("Common bile duct stones and acute cholangitis", "ESGE 2019 CBD stones · BSG 2017 · Tokyo Guidelines 2018", [
        S("Gallstones with jaundice, abnormal LFTs, dilated CBD or fever"),
        P("Charcot’s triad (fever, RUQ pain, jaundice); **Reynolds’ pentad** adds confusion + shock"),
        Q("Probability of CBD stone (ESGE)?", [
            ("Acute cholangitis", [
                P("Blood cultures, **IV antibiotics**, fluids; grade with TG18"),
                P("**ERCP biliary drainage**: severe urgently once resuscitated, moderate ≤ 24 h, mild if no response"),
                P("Too unwell to clear stones → stent (or PTC); definitive clearance later")]),
            ("High: CBD stone seen on US", [
                P("**ERCP**: sphincterotomy + stone extraction")]),
            ("Intermediate: LFTs ↑ or CBD > 6 mm", [
                P("**MRCP or EUS** → ERCP if stone confirmed; or LC + intra-operative cholangiography/CBD exploration")]),
            ("Low", [
                P("**Laparoscopic cholecystectomy** ± intra-operative cholangiography")]),
        ]),
        P("Large or difficult stones: cholangioscopy-guided lithotripsy or temporary plastic stent"),
        E("Then **cholecystectomy in the same admission** (or within 2 weeks) to prevent recurrence"),
    ]),
    F("Gallbladder polyps and gallbladder cancer", "ESGAR/EAES/EFISDS/ESGE 2022 · ESMO 2023 biliary cancer", [
        S("Gallbladder polyp on ultrasound"),
        P("Exclude sludge/stone (mobile, shadowing); risk factors: **age > 60, PSC, Asian ethnicity, sessile polyp/wall > 4 mm**"),
        Q("Polyp size?", [
            ("≥ 10 mm", [P("**Cholecystectomy** if fit")]),
            ("6–9 mm", [P("Risk factor → **cholecystectomy**; none → US at 6 months, 1 y, 2 y")]),
            ("≤ 5 mm", [P("Risk factor → US at 6 months, 1 y, 2 y; none → **no follow-up**")]),
        ]),
        P("On surveillance: growth ≥ 2 mm → MDT; reaches 10 mm → cholecystectomy"),
        Q("Gallbladder cancer?", [
            ("Incidental T1a", [E("Simple cholecystectomy is enough")]),
            ("T1b or deeper", [
                P("Staging CT → **re-resection**: segments IVb/V + portal lymphadenectomy"),
                P("Adjuvant **capecitabine**")]),
            ("Unresectable", [
                P("Biliary stent; **gemcitabine–cisplatin + durvalumab**")]),
        ]),
        E("Suspected cancer before surgery (mass, invasion): **no laparoscopic cholecystectomy** → HPB MDT for radical resection"),
    ]),
]

# =================================================================== PANCREAS
E_['panc'] = [
    F("Acute pancreatitis", "IAP/APA 2013 · Revised Atlanta 2012 · WSES 2019 · ACG 2024", [
        S("Epigastric pain radiating to the back, vomiting"),
        P("Diagnose with **2 of 3**: typical pain, lipase/amylase ≥ 3× ULN, imaging; CT only if diagnosis unclear or no improvement at 72–96 h"),
        P("Cause: **US for gallstones**, alcohol, triglycerides, calcium, drugs, post-ERCP; monitor organ failure (modified Marshall), CRP"),
        P("**Goal-directed moderate fluids** (Hartmann’s/Ringer’s lactate, avoid overload), analgesia, early oral feeding, **no prophylactic antibiotics**"),
        Q("Severity (Revised Atlanta)?", [
            ("Mild: no organ failure", [
                P("Ward care; gallstone cause → **cholecystectomy in the same admission**")]),
            ("Moderate: OF < 48 h or collection", [
                P("HDU; enteral (NG/NJ) feeding if oral fails; collections managed conservatively")]),
            ("Severe: organ failure > 48 h", [
                P("**ICU**, organ support, enteral nutrition; **ERCP ≤ 24 h only if cholangitis**"),
                P("Cholecystectomy delayed until collections resolve or > 6 weeks")]),
        ]),
        E("Infected necrosis (gas, deterioration) → antibiotics → **step-up**: endoscopic/percutaneous drainage, then necrosectomy, ideally ≥ 4 weeks"),
    ]),
    F("Painless obstructive jaundice: pancreatic head cancer", "NICE NG85 · ESMO 2023 pancreatic cancer", [
        S("Painless jaundice, weight loss, new-onset diabetes, palpable gallbladder"),
        P("**Pancreatic-protocol CT** (chest-abdomen-pelvis); CA19-9 (supportive, not diagnostic; raised by obstruction)"),
        P("**FDG PET-CT** if localised disease; **EUS-guided biopsy** if diagnosis unclear or before neoadjuvant therapy; MDT"),
        Q("Resectability (SMA, coeliac axis, SMV/PV)?", [
            ("Resectable", [
                P("**Pancreaticoduodenectomy (Whipple)**; no routine pre-op stent (drain if cholangitis or surgery delayed)"),
                P("Adjuvant **mFOLFIRINOX** (gemcitabine–capecitabine if less fit) for 6 months")]),
            ("Borderline / locally advanced", [
                P("**Neoadjuvant FOLFIRINOX** ± chemoradiotherapy → restage → resect if response")]),
            ("Metastatic", [
                P("Palliative chemotherapy (FOLFIRINOX or gemcitabine–nab-paclitaxel) by fitness"),
                P("**Endoscopic metal biliary stent**; duodenal stent or gastrojejunostomy for gastric outlet obstruction")]),
        ]),
        E("Everyone: **pancreatic enzyme replacement**, diabetes care, coeliac plexus block for pain, early palliative care"),
    ]),
    F("Pancreatic cystic lesion", "European PCN guidelines 2018 · Kyoto IAP 2024", [
        S("Pancreatic cyst on imaging"),
        P("History of pancreatitis? **MRI/MRCP**: duct communication, septa, mural nodule, MPD size; EUS ± fluid CEA/cytology if unclear"),
        Q("Cyst type?", [
            ("After pancreatitis", [
                P("**Pseudocyst / walled-off necrosis**: observe; drain only if symptomatic, infected or obstructing"),
                P("**EUS-guided cystgastrostomy** first line, ≥ 4 weeks after onset")]),
            ("Serous (microcystic, honeycomb)", [
                E("Benign: no follow-up unless symptomatic")]),
            ("Mucinous cystic neoplasm", [
                P("Women, body/tail: **resect if ≥ 4 cm**, symptomatic or mural nodule; < 4 cm → surveillance")]),
            ("IPMN", [
                P("**Absolute**: jaundice, enhancing nodule ≥ 5 mm, solid mass, positive cytology, **MPD ≥ 10 mm** → resect"),
                P("**Relative**: ≥ 40 mm, growth ≥ 5 mm/yr, MPD 5–9 mm, CA19-9↑, new diabetes → surgery if fit")]),
        ]),
        E("Not resected: **MRI ± EUS surveillance** at 6 months then yearly while fit for surgery"),
    ]),
]

# =================================================================== SPLEEN
E_['spleen'] = [
    F("Splenic trauma", "WSES 2017 spleen trauma · ATLS 10th ed · AAST 2018", [
        S("Blunt LUQ trauma, left lower rib fractures, Kehr’s sign (left shoulder-tip pain)"),
        P("**<C>ABCDE**, eFAST, tranexamic acid, major haemorrhage protocol"),
        Q("Haemodynamics?", [
            ("Unstable / non-responder", [
                P("**Emergency laparotomy → splenectomy** (splenorrhaphy rarely)")]),
            ("Stable or responding", [
                P("**CT with IV contrast** (arterial + portal phases): AAST grade, blush, pseudoaneurysm")]),
        ]),
        Q("Stable patient: CT findings?", [
            ("Grade I–III, no blush", [
                P("**Non-operative management**: HDU, serial examination and Hb, theatre available")]),
            ("Blush, pseudoaneurysm, grade IV–V", [
                P("**Angioembolisation** + non-operative management (centre with interventional radiology)")]),
            ("Fails NOM (instability, Hb falling)", [
                P("**Splenectomy**")]),
        ]),
        E("Children: NOM almost always · after NOM avoid contact sport ~6–12 weeks (delayed rupture) · after splenectomy → vaccines + penicillin"),
    ]),
    F("Splenectomy and post-splenectomy prophylaxis", "BSH 2011 asplenia · UKHSA Green Book · ICR 2019 ITP", [
        S("Splenectomy considered: trauma, refractory ITP, hereditary spherocytosis, hypersplenism, splenic tumour/cyst"),
        Q("Indication?", [
            ("ITP", [
                P("First line **corticosteroids ± IVIG** (bleeding); second line **TPO-receptor agonists**, rituximab, fostamatinib"),
                P("Splenectomy only if refractory, ideally **≥ 12 months** after diagnosis")]),
            ("Hereditary spherocytosis", [
                P("Splenectomy if severe (transfusion-dependent, poor growth), delay to ≥ 6 y; cholecystectomy if gallstones")]),
            ("Hypersplenism / portal HT", [
                P("Treat portal hypertension (beta-blocker, TIPS); splenectomy rarely (bleeding)")]),
        ]),
        P("**Laparoscopic splenectomy** preferred; search for accessory spleens (splenunculi) in ITP and spherocytosis"),
        P("**Vaccinate ≥ 2 weeks before** elective (or ≥ 2 weeks after emergency) surgery: pneumococcal, MenACWY, MenB, Hib, yearly influenza"),
        P("**Prophylactic penicillin V** (macrolide if allergic): ≥ 1–2 years, lifelong if high risk; standby antibiotics at home"),
        P("Post-op: thrombocytosis, portal/splenic vein thrombosis, pancreatic tail injury (fistula), left basal atelectasis"),
        E("Prevent **OPSI** (pneumococcus, meningococcus, Hib): alert card, seek help early with fever, malaria prophylaxis, animal bites"),
    ]),
    F("LUQ pain with fever: splenic infarct or abscess", "Bailey & Love 28e · ESC 2023 endocarditis", [
        S("LUQ pain ± fever, splenomegaly"),
        P("FBC, CRP, **blood cultures**, ECG (AF), echocardiogram (endocarditis); **CT with IV contrast**"),
        Q("CT appearance?", [
            ("Wedge-shaped, non-enhancing", [
                P("**Infarct**: analgesia; anticoagulate if embolic (AF); find source: echo, thrombophilia, haematological disease"),
                E("Splenectomy only for complications (abscess, rupture, haemorrhage)")]),
            ("Rim-enhancing collection", [
                P("**Abscess**: IV antibiotics after cultures (streptococci, staphylococci, Gram negatives, anaerobes)"),
                P("**Percutaneous drainage** if unilocular; splenectomy if multilocular, fails or ruptures")]),
            ("Diffuse splenomegaly", [
                P("Portal hypertension (cirrhosis, splenic vein thrombosis), haematological disease, infection (malaria, EBV)")]),
        ]),
        E("Isolated splenic vein thrombosis (pancreatitis, cancer) → gastric varices: **splenectomy** cures left-sided portal hypertension"),
    ]),
]

# =================================================================== ADRENAL
E_['adrenal'] = [
    F("Adrenal incidentaloma", "ESE/ENSAT 2023 adrenal incidentaloma", [
        S("Adrenal mass ≥ 1 cm found on imaging done for another reason"),
        P("Look for features of Cushing’s, phaeochromocytoma, aldosteronism, cancer; **unenhanced CT attenuation (HU)**"),
        Q("Imaging phenotype?", [
            ("≤ 10 HU, homogeneous", [
                E("Lipid-rich **benign adenoma**: no further imaging")]),
            ("> 10 HU, < 4 cm, homogeneous", [
                P("Further imaging (chemical-shift MRI, CT washout, FDG-PET) **or** repeat CT in 6–12 months; stable → stop")]),
            ("≥ 4 cm, heterogeneous or growing", [
                P("Suspect **adrenocortical carcinoma**: adrenal MDT, staging; **open adrenalectomy** if resectable")]),
        ]),
        P("Hormones in all: **1 mg overnight dexamethasone test**; metanephrines if > 10 HU; aldosterone:renin if hypertension or low K⁺"),
        Q("Hormonal result?", [
            ("Cortisol > 50 nmol/L after dex", [
                P("**Mild autonomous cortisol secretion**: screen HTN, diabetes, osteoporosis; adrenalectomy individualised")]),
            ("Overt Cushing’s", [
                P("**Laparoscopic adrenalectomy** with peri-operative and post-op steroid cover")]),
            ("Metanephrines raised", [
                E("**Phaeochromocytoma** → next chart")]),
            ("Aldosterone:renin ratio raised", [
                E("**Primary aldosteronism** → third chart")]),
        ]),
        E("Benign, non-functioning adenoma: **no further follow-up** (ESE 2023)"),
    ]),
    F("Phaeochromocytoma and paraganglioma", "Endocrine Society 2014 PPGL · ESE 2023 · ESH 2023", [
        S("Episodic headache, sweating, palpitations; labile or resistant hypertension; incidentaloma > 10 HU"),
        P("**Plasma free metanephrines** (supine) or 24-h urine fractionated metanephrines; stop interfering drugs"),
        P("Positive → **CT/MRI abdomen-pelvis**; functional imaging (**⁶⁸Ga-DOTATATE PET** or ¹²³I-MIBG) if extra-adrenal, large or metastatic"),
        P("**Genetic testing for all** (SDHx, VHL, RET, NF1); exclude MEN2 (calcitonin, calcium)"),
        P("**Alpha-blockade first** (phenoxybenzamine or doxazosin) 7–14 days + high-salt diet and fluids; **beta-blocker only after alpha**"),
        P("**Laparoscopic adrenalectomy** (open if large/invasive); anaesthetist ready for BP surges on handling"),
        E("Post-op: watch for **hypotension and hypoglycaemia**; metanephrines at 2–6 weeks, then **lifelong annual** follow-up"),
    ]),
    F("Primary aldosteronism (Conn’s)", "Endocrine Society 2016 · ESH 2023 hypertension", [
        S("Hypertension with hypokalaemia, resistant HTN, adrenal incidentaloma, AF, sleep apnoea or early-onset HTN"),
        P("Screen: **aldosterone:renin ratio** (correct K⁺ first; stop MRA; note ACEi/ARB/beta-blocker effects)"),
        P("Confirm (saline infusion, captopril or fludrocortisone test); skip if low K⁺, renin suppressed and aldosterone > 550 pmol/L"),
        P("**Adrenal CT** (exclude carcinoma)"),
        Q("Surgery wanted and feasible?", [
            ("Yes", [
                P("**Adrenal vein sampling** to lateralise (may skip if < 35 y, low K⁺ and clear unilateral adenoma)")]),
            ("No", [
                P("**MRA**: spironolactone (eplerenone if gynaecomastia)")]),
        ]),
        Q("Lateralisation?", [
            ("Unilateral (Conn’s adenoma)", [
                P("**Laparoscopic adrenalectomy**: K⁺ normalises; BP cured in ~1/3–1/2, improved in most")]),
            ("Bilateral hyperplasia", [
                P("**Lifelong MRA** (spironolactone or eplerenone)")]),
        ]),
        E("After adrenalectomy: stop K⁺ supplements and MRA; check K⁺ and creatinine (hyperkalaemia risk) within 1–2 weeks"),
    ]),
]

# =================================================================== HERNIAS & ABDOMINAL WALL
E_['hernia'] = [
    F("Inguinal and femoral hernia", "HerniaSurge 2018 international groin hernia guidelines (2023 update)", [
        S("Groin lump with a cough impulse ± discomfort"),
        P("Clinical diagnosis; **ultrasound** if uncertain, MRI for occult hernia; femoral lies below and lateral to the pubic tubercle"),
        Q("Type and symptoms?", [
            ("Asymptomatic inguinal, man", [
                P("**Watchful waiting** acceptable; ~70% become symptomatic within 5 years → repair then")]),
            ("Symptomatic inguinal", [
                P("**Mesh repair**: open Lichtenstein or laparo-endoscopic **TEP/TAPP**")]),
            ("Femoral, or any in a woman", [
                P("**Repair promptly** (strangulation risk); laparo-endoscopic preferred to find occult femoral hernia")]),
        ]),
        Q("Which approach?", [
            ("Bilateral, or recurrent after open", [P("**TEP/TAPP** (posterior)")]),
            ("Recurrent after laparoscopic", [P("**Lichtenstein** (anterior)")]),
            ("Unfit for GA / preference", [P("Lichtenstein under **local anaesthetic**")]),
        ]),
        E("Day-case surgery; early return to activity · complications: chronic pain (~10%), haematoma, recurrence, ischaemic orchitis"),
    ]),
    F("Irreducible, obstructed or strangulated hernia", "WSES 2017 incarcerated/strangulated hernia · HerniaSurge 2018", [
        S("Painful irreducible hernia ± vomiting, distension, absolute constipation"),
        P("Tense tender lump, **no cough impulse**, skin changes, peritonism; FBC, U&E, CRP, **lactate**, VBG; CT if unclear"),
        Q("Clinical picture?", [
            ("Irreducible, no obstruction/ischaemia", [
                P("Analgesia ± sedation, gentle **manual reduction** (never if strangulation suspected)"),
                P("Observe for peritonitis; **early elective repair**")]),
            ("Obstructed", [
                P("IV fluids, **NG decompression**, catheter"),
                P("**Urgent surgery**")]),
            ("Strangulated (pain, lactate↑, skin)", [
                P("Resuscitate, IV antibiotics → **emergency surgery** without delay for imaging")]),
        ]),
        P("At operation: assess viability (colour, peristalsis, mesenteric pulsation, warm packs); **resect non-viable bowel**"),
        Q("Wound contamination?", [
            ("Clean / clean-contaminated", [P("**Synthetic mesh repair** is safe")]),
            ("Contaminated / dirty", [P("**Tissue (suture) repair** or biological/biosynthetic mesh; staged repair")]),
        ]),
        E("Femoral hernias carry the highest strangulation risk; **Richter’s hernia** can strangulate without obstruction"),
    ]),
    F("Umbilical, epigastric and incisional hernia", "EHS/AHS 2020 umbilical · EHS 2023 incisional · EHS/AHS 2022 closure", [
        S("Midline or periumbilical bulge"),
        P("Clinical examination; **CT** for incisional hernia (defect width, loss of domain, multiple defects); US for small primary hernias"),
        P("**Optimise** before elective repair: stop smoking ≥ 4 weeks, weight loss (BMI < 35), diabetes control"),
        Q("Type?", [
            ("Umbilical / epigastric", [
                P("Defect ≥ 1 cm → **mesh repair** (open preperitoneal flat mesh); < 1 cm → suture repair")]),
            ("Incisional", [
                P("**Mesh repair**: open retromuscular (sublay) or laparoscopic/robotic; avoid onlay where possible"),
                P("Large defect/loss of domain: component separation; pre-op botulinum toxin ± progressive pneumoperitoneum")]),
            ("Rectus diastasis", [
                E("Not a hernia: physiotherapy; surgery only for selected symptomatic patients")]),
        ]),
        E("Prevention: **small bites (5 mm × 5 mm), slowly absorbable suture, SL:WL ≥ 4:1**; prophylactic mesh if high risk (AAA, BMI ≥ 27)"),
    ]),
]

json.dump(E_, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flow_c.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
