"""Management flowcharts (Surgery Bank 3rd edition) - Gastrointestinal Tract part.
Chapters: saliv, oeso, stom, intest, anus, gibleed, gitum.
Built from ../surg/summ_git.txt and updated to the current guidelines named on each chart.

Writes data/import/flows/flow_b.json  {chapter_id: [block, ...]}

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

# =================================================================== SALIVARY GLANDS
E_['saliv'] = [
    F("Salivary gland lump (parotid / submandibular)", "BAHNO/ENT UK 2020 · NICE NG36 · Bailey & Love 28e", [
        S("Discrete, persistent lump in the parotid or submandibular region"),
        P("Examine **facial nerve function**, skin fixation, deep-lobe (parapharyngeal) extension, neck nodes; 80% rule: parotid, benign, pleomorphic"),
        P("**Ultrasound + US-guided FNAC or core biopsy**; never open/incisional biopsy (seeding, nerve injury)"),
        P("MRI if deep lobe, malignant cytology or fixed; CT neck/chest for staging malignancy; discuss at head & neck MDT"),
        Q("Diagnosis?", [
            ("Pleomorphic adenoma", [
                P("**Superficial parotidectomy** or extracapsular dissection with nerve monitoring; submandibular → gland excision"),
                E("Never enucleate: pseudopod capsule → recurrence; untreated ~5–10% become carcinoma ex-pleomorphic")]),
            ("Warthin tumour", [
                E("Older smoker, often bilateral, hot on scintigraphy → **observe** if cytology certain, or excise if symptomatic")]),
            ("Malignant (pain, CN VII palsy, fixity)", [
                P("**(Total) parotidectomy, preserving the nerve unless involved**; neck dissection if N+ or high grade"),
                E("Post-op radiotherapy if high grade, close margins, T3–4, perineural invasion · mucoepidermoid commonest, adenoid cystic spreads along nerves")]),
        ]),
        E("Parotidectomy risks: facial palsy (temporary 20–40%, permanent < 2%), **Frey syndrome** (gustatory sweating), sialocele, earlobe numbness"),
    ]),
    F("Painful swelling with meals: stones and sialadenitis", "ENT UK · Bailey & Love 28e", [
        S("Recurrent gland swelling and pain with eating (salivary colic) ± fever, pus at duct"),
        P("Exclude dental abscess and reactive lymphadenitis; check hydration, glucose and drugs that dry the mouth"),
        P("Bimanual palpation of floor of mouth, inspect duct orifice; **ultrasound first line** (sialography/sialendoscopy, CT if needed)"),
        Q("What is it?", [
            ("Acute suppurative sialadenitis", [
                P("Dehydrated, elderly, post-op, poor oral hygiene; *Staph. aureus*"),
                P("**Rehydrate, oral hygiene, sialogogues, massage + IV/oral flucloxacillin or co-amoxiclav**; pus for culture"),
                E("Abscess on US → aspirate / incise (protect facial nerve)")]),
            ("Stone (80% submandibular)", [
                P("Distal, palpable stone → **transoral duct incision and removal**"),
                P("Proximal/hilar → sialendoscopy ± laser or extracorporeal lithotripsy"),
                E("Intraglandular or recurrent with fibrosis → **submandibular gland excision** (protect marginal mandibular, lingual, hypoglossal nerves)")]),
            ("Viral / bilateral parotitis", [
                E("Mumps: supportive, isolate, check for orchitis/pancreatitis; consider HIV (cysts), sarcoid, Sjögren")]),
        ]),
        E("Chronic sialadenitis: sialogogues, hydration, massage; sialendoscopy dilatation of strictures; gland excision only if refractory"),
    ]),
    F("Other swellings and dry mouth", "BSR 2017 Sjögren · ACR/EULAR 2016 criteria · Bailey & Love 28e", [
        S("Floor-of-mouth/lip cyst, diffuse bilateral enlargement or xerostomia"),
        P("Bimanual exam, drug history (anticholinergics), alcohol, diabetes, eating disorder; **ultrasound** first-line imaging"),
        Q("Pattern", [
            ("Lip cyst (mucocele)", [
                E("Lower lip after trauma; may resolve → **excise with underlying minor glands** if persistent")]),
            ("Floor-of-mouth cyst / neck swelling", [
                P("**Ranula** (sublingual gland); plunging if through mylohyoid → MRI/US"),
                E("**Excise the sublingual gland** (± cyst) via mouth; marsupialisation alone recurs")]),
            ("Diffuse painless bilateral", [
                E("**Sialadenosis**: alcohol, diabetes, malnutrition/bulimia, drugs → treat cause; exclude HIV, sarcoid, lymphoma")]),
            ("Dry eyes + dry mouth", [
                P("**Sjögren**: anti-Ro/La, Schirmer test, labial gland biopsy, US; sialometry"),
                E("Saliva substitutes, pilocarpine, dental care; watch for **MALT lymphoma** (persistent gland enlargement)")]),
        ]),
        E("Minor salivary gland lump on palate: majority malignant → biopsy and wide excision"),
    ]),
]

# =================================================================== OESOPHAGUS
E_['oeso'] = [
    F("Dysphagia", "NICE NG12 · Chicago Classification 4.0 · ESNM/UEG 2020 achalasia", [
        S("Difficulty swallowing (oesophageal) or choking/coughing on swallow (oropharyngeal)"),
        P("**Dysphagia at any age = urgent direct-access OGD (2-week wait)** to exclude cancer; biopsy any lesion"),
        P("OGD normal → biopsies for eosinophils; then barium swallow and **high-resolution manometry**; videofluoroscopy if oropharyngeal"),
        Q("Diagnosis?", [
            ("Achalasia", [
                P("Absent peristalsis + incomplete LOS relaxation (HRM types I–III); bird’s beak on barium"),
                P("**Pneumatic dilatation, laparoscopic Heller myotomy + Dor fundoplication or POEM** (POEM best for type III)"),
                E("Botox if unfit · lifelong ↑ SCC risk")]),
            ("Eosinophilic oesophagitis", [
                P("≥ 15 eosinophils/hpf; young atopic man, food bolus, rings/furrows"),
                E("**PPI, orodispersible budesonide** or elimination diet; dilate strictures; dupilumab if refractory")]),
            ("Pharyngeal pouch", [
                E("Elderly, regurgitation, halitosis, gurgling → **endoscopic stapling** or open cricopharyngeal myotomy ± excision")]),
            ("Peptic stricture", [
                E("Endoscopic balloon dilatation + long-term PPI")]),
        ]),
        E("Food bolus obstruction: urgent OGD (within 24 h, < 6 h if total obstruction/drooling); biopsy afterwards to exclude EoE"),
    ]),
    F("GORD, hiatus hernia and Barrett’s oesophagus", "NICE CG184 · BSG 2014 Barrett’s · ESGE 2023 Barrett’s", [
        S("Heartburn and regurgitation"),
        P("Lifestyle: weight loss, stop smoking, raise bed head, avoid late meals; **full-dose PPI for 4–8 weeks**"),
        P("Alarm features (dysphagia, weight loss, ≥ 55 with symptoms) or refractory → **OGD**"),
        Q("Refractory / considering surgery", [
            ("Work-up", [
                P("**24-h pH-impedance off PPI + HRM** (exclude achalasia/ineffective motility)"),
                E("Laparoscopic **Nissen (or partial) fundoplication** if proven reflux, PPI-responsive or volume regurgitation")]),
            ("Para-oesophageal hernia", [
                E("Symptomatic → elective repair (risk of gastric volvulus) · acute volvulus: NG decompression, urgent surgery")]),
        ]),
        Q("Barrett’s (salmon mucosa ≥ 1 cm + intestinal metaplasia)", [
            ("No dysplasia", [P("Surveillance with Seattle biopsies: **< 3 cm 5-yearly, 3–10 cm 3-yearly**; ≥ 10 cm → expert centre")]),
            ("Low-grade dysplasia", [P("Confirm by 2nd GI pathologist → **endoscopic ablation (RFA)** or 6-monthly surveillance")]),
            ("HGD / intramucosal cancer", [P("**Endoscopic resection (EMR/ESD) of visible lesion, then RFA** of residual Barrett’s")]),
        ]),
        E("Barrett’s: long-term PPI; surveillance only if fit for treatment"),
    ]),
    F("Oesophageal perforation", "WSES 2019 oesophageal perforation · Bailey & Love 28e", [
        S("Chest pain after vomiting (Boerhaave) or after endoscopy/dilatation; surgical emphysema, fever, shock"),
        P("Mackler triad: vomiting, chest pain, subcutaneous emphysema; **CT chest/abdomen with oral water-soluble contrast**"),
        P("**Nil by mouth, IV fluids, broad-spectrum antibiotics + antifungal, IV PPI**, chest drain for effusion, early nutrition (NJ / jejunostomy)"),
        Q("Pattern?", [
            ("Contained, stable, minimal contamination", [
                E("**Non-operative** (often iatrogenic): close monitoring, repeat contrast study")]),
            ("Small defect, early, no extensive sepsis", [
                E("**Endoscopic**: covered stent, clips or endoluminal vacuum therapy + drainage of collections")]),
            ("Uncontained / septic", [
                P("**Surgery**: debridement, primary repair (buttressed) + wide drainage"),
                E("Extensive necrosis or underlying cancer → oesophagectomy or diversion")]),
        ]),
        E("Mortality doubles if delay > 24 h · caustic ingestion: no induced vomiting, OGD/CT grading within 24 h"),
    ]),
]

# =================================================================== STOMACH & DUODENUM
E_['stom'] = [
    F("Dyspepsia, H. pylori and peptic ulcer", "NICE CG184 · NICE NG12 · Maastricht VI 2022", [
        S("Upper abdominal pain/discomfort, heartburn, early satiety"),
        P("Review NSAIDs, aspirin, SSRIs, steroids; check FBC"),
        Q("Red flags?", [
            ("≥ 55 with weight loss, or dysphagia", [
                E("**Urgent OGD (2-week wait)**; also upper mass, iron-deficiency anaemia, GI bleeding")]),
            ("No red flags", [
                P("**Test-and-treat H. pylori** (stool antigen or 13C-urea breath test; 2 weeks off PPI) **or** full-dose PPI for 1 month"),
                P("Eradication: PPI + amoxicillin + clarithromycin/metronidazole (NICE 7 days; Maastricht VI 14 days, bismuth quadruple if resistance high)")]),
        ]),
        P("Peptic ulcer: stop NSAIDs, PPI 8 weeks; confirm eradication with breath test if ulcer"),
        E("**Gastric ulcer: biopsy and repeat OGD at 6–8 weeks** to confirm healing (exclude cancer) · refractory ulcers → think Zollinger–Ellison (gastrin)"),
    ]),
    F("Perforated peptic ulcer", "WSES 2020 perforated & bleeding peptic ulcer", [
        S("Sudden severe epigastric pain → generalised peritonitis, board-like rigidity"),
        P("Erect CXR free gas (absent in ~25%) → **CT abdomen** if doubt; lactate, amylase (exclude pancreatitis)"),
        P("**Resuscitate: IV fluids, NBM, NG tube, IV PPI, broad-spectrum antibiotics** (± antifungal), analgesia, catheter"),
        Q("Fit and peritonitic?", [
            ("Yes (most)", [
                P("**Laparoscopic or open omental patch repair** (Graham) + thorough peritoneal lavage"),
                E("Biopsy gastric ulcers · large/malignant ulcer → resection")]),
            ("Contained leak, stable, no peritonitis", [
                E("Selected **non-operative (Taylor) regimen**: NG, PPI, antibiotics; operate if no improvement in 12–24 h")]),
        ]),
        E("Post-op: **eradicate H. pylori**, stop NSAIDs, long-term PPI if NSAID unavoidable · Boey score predicts mortality"),
    ]),
    F("Gastric outlet obstruction", "Bailey & Love 28e · ASGE 2021 GOO", [
        S("Projectile non-bilious vomiting of old food, visible peristalsis, succussion splash, weight loss"),
        P("Bloods: **hypochloraemic, hypokalaemic metabolic alkalosis** with paradoxical aciduria"),
        P("**NG decompression + IV 0.9% saline with KCl** (correct before surgery); IV PPI"),
        P("**OGD + biopsy** (after stomach emptied) and CT to stage"),
        Q("Cause?", [
            ("Benign (peptic stricture)", [
                P("PPI + H. pylori eradication + **endoscopic balloon dilatation**"),
                E("Failure → antrectomy or gastrojejunostomy")]),
            ("Malignant (gastric/pancreatic cancer)", [
                P("Resectable → staging & curative resection"),
                E("Palliative: **duodenal stent** (short survival) or gastrojejunostomy / EUS-GE (fitter, longer survival)")]),
        ]),
        E("After gastric surgery watch for dumping (small frequent dry meals), B12/iron deficiency, bile reflux"),
    ]),
]

# =================================================================== SMALL & LARGE INTESTINE
E_['intest'] = [
    F("Intestinal obstruction", "WSES 2017 ASBO (Bologna) · ESCP/WSES 2021 LBO · Bailey & Love 28e", [
        S("Colicky pain, vomiting, distension, absolute constipation"),
        P("**Drip and suck**: IV fluids, NBM, NG tube, catheter; correct K⁺; check hernial orifices, PR, previous surgery"),
        P("**CT abdomen/pelvis with IV contrast**: level, cause, closed loop, ischaemia"),
        Q("Cause on CT", [
            ("Strangulation / ischaemia / peritonitis", [
                E("Fever, tachycardia, constant pain, ↑ lactate, closed loop, irreducible hernia → **emergency surgery**")]),
            ("Adhesional SBO, no ischaemia", [
                P("**Water-soluble contrast (Gastrografin) challenge**: AXR at 8–24 h"),
                E("Contrast in colon → resolves · no resolution by **72 h → surgery** (laparoscopic adhesiolysis if feasible)")]),
            ("Large bowel: cancer", [
                E("Right → resection + anastomosis · left → resection, Hartmann’s or **stent as bridge**; caecum > 12 cm = perforation risk")]),
            ("Sigmoid volvulus (coffee bean)", [
                P("**Flexible sigmoidoscopic decompression** + flatus tube"),
                E("Elective sigmoid colectomy (high recurrence) · gangrene → Hartmann’s · caecal volvulus → right hemicolectomy")]),
        ]),
        E("Pseudo-obstruction (Ogilvie): no mechanical cause → correct electrolytes, stop opioids; **neostigmine** or colonoscopic decompression"),
    ]),
    F("Acute diverticulitis", "NICE NG147 · WSES 2020 diverticulitis · ESCP 2020", [
        S("Left iliac fossa pain, fever, raised CRP"),
        P("**CT with IV contrast** to confirm and grade (modified Hinchey)"),
        Q("Severity", [
            ("Uncomplicated", [
                E("Immunocompetent, well → analgesia, oral fluids, **antibiotics not routinely needed**; outpatient")]),
            ("Abscess (Hinchey I–II)", [
                E("IV antibiotics; **abscess ≥ 4–5 cm → CT-guided percutaneous drainage**")]),
            ("Purulent peritonitis (III)", [
                E("Laparoscopic resection with **primary anastomosis ± defunctioning ileostomy**; Hartmann’s if unstable · lavage in selected")]),
            ("Faecal peritonitis (IV)", [
                E("Resuscitate → **Hartmann’s procedure** (damage control if septic shock)")]),
        ]),
        P("**Colonoscopy / CT colonography ~6 weeks** after a complicated episode to exclude cancer"),
        E("Elective resection case by case (not by number of attacks): fistula (colovesical → pneumaturia), stricture, persistent symptoms, immunosuppressed"),
    ]),
    F("Acute severe ulcerative colitis (and surgery in IBD)", "BSG 2019 IBD · ECCO 2022 UC", [
        S("Bloody diarrhoea ≥ 6/day + one of: HR > 90, T > 37.8 °C, Hb < 105 g/L, ESR > 30 (Truelove & Witts)"),
        P("Admit (joint medical–surgical care): stool culture + **C. difficile**, CRP, albumin, AXR (colon > 5.5 cm = toxic megacolon), flexible sigmoidoscopy"),
        P("**IV hydrocortisone 100 mg qds** (or methylprednisolone 60 mg/day), IV fluids, K⁺, **LMWH**; avoid opioids, antidiarrhoeals, NSAIDs"),
        Q("Day 3: stool > 8/day, or 3–8 + CRP > 45?", [
            ("Responding", [E("Switch to oral prednisolone taper + maintenance (thiopurine/biologic)")]),
            ("Not responding", [P("**Rescue: infliximab or ciclosporin**"), E("No response by day 5–7 → surgery")]),
            ("Megacolon / perforation / massive bleed", [E("**Emergency subtotal colectomy + end ileostomy**")]),
        ]),
        E("Later: **ileal pouch–anal anastomosis** or proctectomy · Crohn’s: bowel-sparing — ileocaecal resection, strictureplasty; drain abscess before anti-TNF"),
    ]),
]

# =================================================================== ANORECTAL DISORDERS
E_['anus'] = [
    F("Anal fissure", "ACPGBI 2017 · ASCRS 2023 anal fissure", [
        S("Severe pain on defecation lasting hours + bright red blood on paper"),
        P("Gentle parting of buttocks: **posterior midline tear** (± sentinel tag); avoid PR/proctoscopy if too painful"),
        P("Atypical (lateral, multiple, painless, large) → **EUA + biopsy**: Crohn’s, HIV, TB, syphilis, SCC"),
        P("**Fibre, fluids, laxatives, warm baths, topical lidocaine** — most acute fissures heal"),
        P("Chronic (> 6 weeks) → **topical diltiazem 2% or GTN 0.4%** for 6–8 weeks (GTN headache)"),
        Q("Not healed?", [
            ("Men / normal sphincter", [E("**Lateral internal sphincterotomy** (> 90% heal; small risk of incontinence)")]),
            ("Women, post-partum, low pressures", [E("**Botulinum toxin** ± fissurectomy · advancement flap; avoid sphincterotomy")]),
        ]),
        E("Children: constipation management is the key"),
    ]),
    F("Haemorrhoids and prolapse", "ESCP 2020 haemorrhoids · ACPGBI 2019 · NICE NG12", [
        S("Painless bright red bleeding on the pan ± prolapsing lump, pruritus"),
        P("PR + proctoscopy; **exclude colorectal cancer**: FIT / colonoscopy if ≥ 50, change in bowel habit, iron deficiency"),
        P("All: **fibre, fluids, avoid straining**; topical agents for symptoms"),
        Q("Grade (Goligher)", [
            ("I–II (II prolapse, reduce spontaneously)", [E("**Rubber band ligation** (outpatient) ± repeat; sclerotherapy alternative")]),
            ("III (manual reduction) / failed banding", [E("Haemorrhoidal artery ligation (HAL-RAR), **excisional haemorrhoidectomy** or stapled haemorrhoidopexy")]),
            ("IV / external component", [E("**Excisional (Milligan–Morgan) haemorrhoidectomy** — most effective, most painful")]),
            ("Full-thickness rectal prolapse", [E("Concentric folds → **laparoscopic ventral mesh rectopexy** (fit) · perineal Delorme’s / Altemeier (frail)")]),
        ]),
        E("Thrombosed external pile: < 72 h → excision under LA, later → analgesia, ice, laxatives · strangulated piles → analgesia ± urgent excision"),
    ]),
    F("Perianal and pilonidal sepsis", "ACPGBI 2016 anal fistula · ASCRS 2022 · ESCP 2024 pilonidal", [
        S("Painful, hot, tender swelling near anus or natal cleft"),
        Q("Site?", [
            ("Perianal / ischiorectal abscess", [
                P("**Prompt incision and drainage** (don’t wait for fluctuance); no packing needed for small cavities"),
                P("Antibiotics only if cellulitis, diabetes, immunosuppression, sepsis"),
                E("Don’t probe for a fistula unless obvious; check glucose")]),
            ("Natal cleft (pilonidal)", [
                P("Acute abscess → **off-midline incision & drainage**"),
                E("Chronic sinus → pit-picking / cleft lift (Bascom), Karydakis or Limberg flap; avoid midline wounds · hair removal")]),
        ]),
        P("Persistent discharge after abscess → **fistula-in-ano**; Goodsall’s rule; **MRI pelvis** if complex or recurrent"),
        Q("Fistula type (Parks)", [
            ("Simple low fistula", [E("**Fistulotomy** (laying open), > 90% cure")]),
            ("High / complex / anterior in women", [E("**Loose draining seton** → sphincter-preserving: LIFT, advancement flap, fistula plug")]),
            ("Crohn’s", [E("Seton + **anti-TNF** (infliximab); stoma for severe disease")]),
        ]),
        E("Protect continence: never divide a large amount of external sphincter"),
    ]),
]

# =================================================================== GI BLEEDING
E_['gibleed'] = [
    F("Acute upper GI bleeding (non-variceal)", "NICE CG141 · ESGE 2021 NVUGIH · BSG 2022 care bundle", [
        S("Haematemesis, coffee-ground vomit or melaena"),
        P("**ABC: 2 large-bore cannulae, crystalloid, bloods incl. crossmatch, clotting, urea**; stop/plan anticoagulants and antiplatelets"),
        P("**Restrictive transfusion: Hb < 70 g/L (< 80 if cardiovascular disease)**, target 70–90; platelets if < 50 and bleeding"),
        P("**Glasgow–Blatchford score**: ≤ 1 → outpatient management; Rockall after endoscopy"),
        P("**OGD within 24 h** (immediately after resuscitation if unstable); IV PPI may be started pre-endoscopy"),
        Q("Forrest finding", [
            ("Ia/Ib active bleed, IIa visible vessel", [
                P("**Dual endoscopic therapy**: adrenaline + clips or thermal coagulation (haemostatic powder as rescue)"),
                E("High-dose PPI for 72 h after therapy")]),
            ("IIb adherent clot", [E("Consider clot removal and treat underlying lesion; PPI")]),
            ("IIc / III flat spot, clean base", [E("No endoscopic therapy, oral PPI, early feeding & discharge")]),
        ]),
        E("Rebleed → **repeat OGD → interventional radiology (embolisation) → surgery** (under-run ulcer) · test & eradicate H. pylori"),
    ]),
    F("Variceal bleeding", "Baveno VII 2022 · BSG 2015 variceal haemorrhage", [
        S("Haematemesis in a patient with cirrhosis / portal hypertension"),
        P("Resuscitate; **restrictive transfusion (Hb 70–80 g/L)**, avoid over-filling"),
        P("**IV terlipressin + IV antibiotics (ceftriaxone)** before endoscopy"),
        P("**OGD within 12 h**"),
        Q("Varices", [
            ("Oesophageal", [E("**Endoscopic band ligation**")]),
            ("Gastric (fundal)", [E("**Cyanoacrylate injection**; TIPS or BRTO if fails")]),
        ]),
        P("Uncontrolled → **balloon tamponade (Sengstaken) or oesophageal stent** as bridge to **rescue TIPS**"),
        P("Pre-emptive TIPS within 72 h if **Child C 10–13** (or B > 7 with active bleeding)"),
        E("Secondary prevention: **non-selective beta-blocker (carvedilol/propranolol) + band ligation**; lactulose to prevent encephalopathy"),
    ]),
    F("Acute lower GI bleeding", "BSG 2019 LGIB · ACG 2023 LGIB", [
        S("Fresh red blood or maroon stool per rectum"),
        P("Resuscitate; PR exam; **shock index = HR ÷ SBP**; restrictive transfusion (Hb < 70 g/L, < 80 if CVD)"),
        P("FBC, U&E (high urea suggests upper source), clotting, crossmatch; **review anticoagulants/antiplatelets**"),
        Q("Stable or unstable?", [
            ("Unstable (shock index > 1)", [
                P("**CT angiography** (exclude upper source: OGD if CTA negative — UGIB in ~15%)"),
                P("Blush → **catheter angiography + embolisation within 60 min**"),
                E("**Laparotomy** only when bleeding persists despite all localisation attempts")]),
            ("Stable, Oakland score ≤ 8", [
                E("Discharge for **outpatient colonoscopy**")]),
            ("Stable, Oakland > 8", [
                E("Admit → **colonoscopy on next available list**; endoscopic therapy (clips) for diverticular/angiodysplasia bleeds")]),
        ]),
        E("Causes: diverticular (commonest), angiodysplasia, haemorrhoids, ischaemic colitis, IBD, cancer, post-polypectomy · follow up to exclude neoplasia"),
    ]),
]

# =================================================================== GI TUMOURS
E_['gitum'] = [
    F("Oesophageal and gastric cancer", "NICE NG83 · ESMO 2022 gastric / 2023 oesophageal · ESOPEC 2024", [
        S("Dysphagia, dyspepsia ≥ 55 with weight loss, iron-deficiency anaemia, upper abdominal mass"),
        P("**Urgent OGD + multiple biopsies** (HER2, MMR/MSI, PD-L1 if advanced)"),
        P("Stage: **CT chest/abdomen/pelvis → PET-CT** if curable; EUS for T/N; **staging laparoscopy** if gastric/junctional; nutrition, fitness, MDT"),
        Q("Site & stage", [
            ("Early (T1a)", [E("**Endoscopic resection (EMR/ESD)**")]),
            ("Oesophageal adenocarcinoma / GOJ", [
                P("**Perioperative FLOT chemotherapy** (or CROSS chemoradiotherapy) + oesophagectomy (Ivor Lewis)"),
                E("Adjuvant nivolumab if residual disease after neoadjuvant CRT")]),
            ("Oesophageal SCC", [E("**Neoadjuvant CROSS + oesophagectomy**, or definitive chemoradiotherapy (esp. cervical / unfit)")]),
            ("Gastric (≥ T2 or N+)", [
                P("**Perioperative FLOT + total or subtotal gastrectomy with D2 lymphadenectomy**"),
                E("Margins ≥ 5 cm (intestinal), more for diffuse; B12 for life after total gastrectomy")]),
        ]),
        E("Advanced: chemo + **nivolumab/pembrolizumab** (PD-L1) or **trastuzumab** (HER2+) · dysphagia → stent or RT · obstruction → stent/GJ"),
    ]),
    F("Colorectal and anal cancer", "NICE NG151 · ESMO 2023 colon / 2017 rectal · ESMO 2021 anal", [
        S("Change in bowel habit, rectal bleeding, iron-deficiency anaemia, mass; **FIT ≥ 10 µg Hb/g → urgent referral**"),
        P("**Colonoscopy + biopsy** (CT colonography if unfit); CT chest/abdomen/pelvis; CEA; **MMR/MSI testing for all**"),
        P("**Colorectal MDT**; prehabilitation and ERAS · obstruction or perforation → emergency pathway"),
        Q("Site", [
            ("Colon", [
                P("**Resection with complete mesocolic excision** (right/left hemicolectomy, sigmoid colectomy), laparoscopic/robotic, ERAS"),
                E("Stage III: adjuvant **CAPOX 3 months** (low risk) or 6 months · high-risk stage II: consider")]),
            ("Rectum", [
                P("**MRI pelvis**: T, N, CRM, EMVI"),
                P("Early → **TME** (anterior resection / APR) or local excision for T1 · threatened CRM/advanced → **total neoadjuvant therapy**"),
                E("Clinical complete response → **watch and wait** · dMMR → immunotherapy (dostarlimab)")]),
            ("Anal canal SCC", [
                P("HPV/HIV-associated; MRI pelvis, CT/PET-CT"),
                E("**Chemoradiotherapy (mitomycin + 5-FU/capecitabine)**; assess at 26 weeks; residual/recurrent → **salvage APR**")]),
        ]),
        E("Obstructing left colon cancer → stent as bridge or Hartmann’s · isolated liver/lung mets → resection after MDT · follow-up CEA + CT for 3–5 years"),
    ]),
    F("Polyps, screening and hereditary syndromes", "BSG/ACPGBI/PHE 2020 post-polypectomy · BSG/ACPGBI 2020 hereditary CRC", [
        S("Polyp found at colonoscopy or positive screening test"),
        P("**NHS bowel screening: FIT every 2 years from 50–74** (threshold 120 µg Hb/g → colonoscopy)"),
        P("Remove polyps completely (cold snare < 10 mm; **EMR/ESD for large non-pedunculated lesions ≥ 20 mm**, tattoo site)"),
        Q("Histology", [
            ("Malignant polyp", [
                E("**Surgery** if poorly differentiated, LVI, tumour budding, margin < 1 mm, deep submucosal invasion (Haggitt 4 / Kikuchi sm3)")]),
            ("High-risk findings", [
                E("≥ 2 premalignant polyps with ≥ 1 advanced, or ≥ 5 premalignant, or LNPCP ≥ 20 mm → **one surveillance colonoscopy at 3 years**")]),
            ("Low-risk", [E("No surveillance → back to national screening")]),
        ]),
        Q("Hereditary syndrome?", [
            ("Lynch (MMR genes)", [E("**Colonoscopy every 2 years** from 25 (MLH1/MSH2) or 35 (MSH6/PMS2) + daily **aspirin**; hysterectomy + BSO once family complete")]),
            ("FAP (APC, > 100 adenomas)", [E("Annual colonoscopy from 12–14 → **prophylactic colectomy** (IRA or pouch) late teens; duodenal surveillance")]),
        ]),
        E("Piecemeal EMR of LNPCP → **site check at 6 months** then 18 months later"),
    ]),
]

json.dump(E_, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flow_b.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
