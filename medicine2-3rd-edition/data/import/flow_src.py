"""Management flowcharts (3rd edition) - replace the old 'Essentials at a glance' tables.
Each chapter gets step-by-step flowcharts, in the order the chapter's topics are taught, built from the
summaries in the source books and updated to the current guidelines named on each chart.

Writes data/essentials.json  {chapter_id: [block, ...]}

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

# =================================================================== CARDIOVASCULAR
E_['cad'] = [
    F("Acute chest pain: suspected acute coronary syndrome", "ESC 2023 ACS · NICE NG185", [
        S("Acute chest pain or anginal equivalent"),
        P("**12-lead ECG within 10 min**, monitor, aspirin 300 mg, GTN; O₂ only if SpO₂ < 90%; opioid for severe pain"),
        Q("ECG?", [
            ("ST elevation / new LBBB / posterior MI", [
                P("**STEMI**: primary PCI if achievable ≤ 120 min of diagnosis (radial, drug-eluting stent)"),
                P("Otherwise fibrinolysis (tenecteplase) ≤ 12 h, then angiography 2–24 h; **rescue PCI** if ST resolution < 50% at 60–90 min"),
                E("Cardiogenic shock: culprit-vessel PCI, noradrenaline ± dobutamine")]),
            ("No ST elevation", [
                P("**hs-troponin 0/1 h (or 0/2 h)**: rise/fall = NSTEMI, normal = unstable angina or non-cardiac"),
                P("Very high risk (shock, refractory pain, VT/VF, acute HF) → angiography **< 2 h**"),
                P("High risk (NSTEMI, dynamic ST/T, GRACE > 140) → angiography **< 24 h**"),
                E("Low risk → non-invasive imaging or selective invasive strategy")]),
        ]),
        P("Antithrombotics: P2Y12 inhibitor (prasugrel if PCI, ticagrelor; clopidogrel if high bleeding risk) + anticoagulant (UFH at PCI, fondaparinux if conservative)"),
        E("Secondary prevention: DAPT 12 months · high-intensity statin to **LDL < 1.4 mmol/L** (+ ezetimibe) · ACEi · beta-blocker if LVEF ≤ 40% · MRA if LVEF ≤ 40% with HF/diabetes · SGLT2i if HF · cardiac rehab · stop smoking"),
    ]),
    F("Stable chest pain: chronic coronary syndrome", "ESC 2024 CCS · NICE CG95", [
        S("Exertional chest pain relieved by rest/GTN, no ACS features"),
        P("ECG, FBC, lipids, HbA1c, renal & thyroid function; echo if murmur or suspected HF"),
        Q("Clinical likelihood of obstructive CAD", [
            ("Low–moderate", [P("**CT coronary angiography** first line")]),
            ("High / known CAD / CT non-diagnostic", [P("**Functional imaging** (stress echo, SPECT, perfusion CMR) or invasive angiography")]),
        ]),
        P("Anti-anginal: **GTN PRN + beta-blocker or rate-limiting CCB** (combine if needed); add long-acting nitrate, ivabradine, nicorandil or ranolazine"),
        P("Prevention: aspirin 75 mg (clopidogrel if intolerant), statin, ACEi if diabetes/HTN/CKD/LV dysfunction; risk-factor control"),
        E("Revascularise (PCI/CABG, heart team) if symptoms persist on drugs or high-risk anatomy: left main, proximal LAD, 3-vessel disease with LV dysfunction"),
    ]),
    F("Aorta and limb ischaemia", "ESC 2024 Aortic & PAD · NICE NG156", [
        S("Vascular presentation"),
        Q("Which picture?", [
            ("Tearing chest/back pain", [
                P("**Aortic dissection**: IV labetalol/esmolol → HR < 60, SBP 100–120; analgesia"),
                P("CT aortography (TOE if unstable); never thrombolyse"),
                E("Type A → emergency surgery · Type B uncomplicated → medical; TEVAR if complicated")]),
            ("Cold, pale, pulseless limb (6 Ps)", [
                P("**Acute limb ischaemia**: IV unfractionated heparin + analgesia, urgent vascular review"),
                E("Viable → imaging + catheter thrombolysis/endovascular · threatened → embolectomy · irreversible → amputation; find source (AF)")]),
            ("Calf pain on walking", [
                P("**Claudication**: ABPI < 0.9 confirms PAD (falsely high if calcified)"),
                P("Stop smoking, statin, clopidogrel, supervised exercise; naftidrofuryl/cilostazol"),
                E("Revascularise if lifestyle-limiting or chronic limb-threatening ischaemia")]),
        ]),
        E("AAA: ultrasound screen men at 65 · repair if ≥ 5.5 cm, growth > 1 cm/yr or symptomatic (EVAR or open) · 3.0–5.4 cm → surveillance + risk-factor control"),
    ]),
]

E_['hf'] = [
    F("Chronic heart failure: diagnosis to treatment", "ESC 2021 + 2023 update · NICE NG106", [
        S("Breathlessness, orthopnoea, oedema, fatigue"),
        P("**NT-proBNP** + ECG (normal ECG makes HF unlikely)"),
        Q("NT-proBNP", [
            ("< 400 ng/L", [E("HF unlikely → look for another cause")]),
            ("400–2000", [P("Echo + specialist **within 6 weeks**")]),
            ("> 2000", [P("Echo + specialist **within 2 weeks**")]),
        ]),
        Q("Echo: LVEF", [
            ("≤ 40%: HFrEF", [
                P("**Four pillars, started rapidly**: ACEi/ARNI (sacubitril–valsartan) + beta-blocker + MRA + SGLT2i"),
                P("Loop diuretic for congestion only")]),
            ("41–49%: HFmrEF", [P("SGLT2i + diuretic; consider ACEi/ARNI, beta-blocker, MRA")]),
            ("≥ 50%: HFpEF", [P("**SGLT2i** (dapagliflozin/empagliflozin) + diuretic; consider MRA; treat HTN, AF, obesity, OSA")]),
        ]),
        P("Still symptomatic: ivabradine (sinus, HR ≥ 70) · hydralazine–nitrate if ACEi/ARB intolerant · **IV iron** if ferritin < 100 or 100–299 with TSAT < 20% · digoxin for symptoms/AF"),
        E("Devices: **ICD** if LVEF ≤ 35% after ≥ 3 months optimal therapy · **CRT** if LVEF ≤ 35% + LBBB, QRS ≥ 150 ms · advanced HF → LVAD/transplant, palliative care"),
    ]),
    F("Acute heart failure", "ESC 2021 · NICE CG187", [
        S("Acute breathlessness, crackles, raised JVP, pink frothy sputum"),
        P("Sit up · O₂ if SpO₂ < 90% · ECG, troponin, NT-proBNP, CXR, bedside echo"),
        P("Find the trigger (**CHAMPIT**): ACS, Hypertension, Arrhythmia, Mechanical cause, PE, Infection, Tamponade"),
        Q("Haemodynamic profile", [
            ("Warm & wet (commonest)", [P("**IV furosemide** ≥ usual oral dose; IV nitrate if SBP > 110")]),
            ("Hypertensive pulmonary oedema", [P("IV nitrates + diuretic; **CPAP/NIV** if respiratory distress")]),
            ("Cold & wet: cardiogenic shock", [P("Inotrope (dobutamine) ± noradrenaline; urgent PCI if ACS; mechanical support")]),
        ]),
        E("Avoid routine opioids · before discharge: euvolaemic, start/continue all four pillars, review within 1–2 weeks"),
    ]),
    F("Cardiomyopathies", "ESC 2023 Cardiomyopathy", [
        S("Abnormal myocardium on echo / cardiac MRI"),
        Q("Phenotype", [
            ("Dilated (DCM)", [
                P("Exclude CAD, alcohol, thyroid, iron overload, myocarditis, anthracyclines, peripartum, genetic (TTN, LMNA)"),
                E("Treat as HFrEF · ICD/CRT by criteria · screen first-degree relatives")]),
            ("Hypertrophic (HCM, wall ≥ 15 mm)", [
                P("Beta-blocker or verapamil; **mavacamten** if obstructive & symptomatic; myectomy / alcohol septal ablation"),
                E("HCM Risk-SCD ≥ 6% → ICD · avoid dehydration & vasodilators · family screening (autosomal dominant)")]),
            ("Restrictive / infiltrative", [
                P("Amyloid: serum & urine immunofixation + free light chains (AL) → bone scintigraphy (ATTR → tafamidis)"),
                E("Sarcoid: CMR/FDG-PET → immunosuppression, pacing/ICD · haemochromatosis → venesection")]),
        ]),
        E("Takotsubo: apical ballooning after stress with normal coronaries → supportive; recovers within weeks"),
    ]),
]

E_['chd'] = [
    F("Congenital heart disease: from clue to action", "ESC 2020 ACHD", [
        S("Murmur, cyanosis or failure to thrive → echocardiography"),
        Q("Cyanosis?", [
            ("Acyanotic (L→R shunt or obstruction)", [
                P("**ASD**: fixed split S2, RBBB → close (device for secundum) if RV dilated"),
                P("**VSD**: harsh pansystolic at LSE → small: observe; LV overload or Qp:Qs ≥ 1.5 → close"),
                P("**PDA**: machinery murmur → preterm: ibuprofen/indometacin/paracetamol; later: device closure"),
                E("**Coarctation**: radiofemoral delay, arm–leg BP gradient, rib notching → stent/surgery; lifelong BP review")]),
            ("Cyanotic (R→L)", [
                P("**Tetralogy**: spells, boot-shaped heart → knee–chest, O₂, morphine, propranolol → complete repair < 1 yr"),
                P("**Transposition**: cyanosis at birth → prostaglandin E1 → balloon septostomy → arterial switch"),
                E("**Eisenmenger**: shunt reversal → never close; PAH drugs; pregnancy contraindicated")]),
        ]),
        E("All: endocarditis prophylaxis only for cyanotic disease or prosthetic material (ESC) · pregnancy counselling (mWHO class) · associations: Turner (coarctation, bicuspid), Down (AVSD)"),
    ]),
]

E_['arr'] = [
    F("Tachycardia with a pulse", "Resuscitation Council UK 2021 · ERC 2025", [
        S("Tachycardia: ABCDE, O₂ if hypoxic, IV access, 12-lead ECG"),
        Q("Adverse features? (shock, syncope, myocardial ischaemia, severe heart failure)", [
            ("Yes: unstable", [P("**Synchronised DC shock** (up to 3) under sedation → amiodarone 300 mg IV over 10–20 min → repeat shock")]),
            ("No: stable", [P("Assess QRS width and regularity")]),
        ]),
        Q("Stable rhythm", [
            ("Narrow regular (SVT, flutter)", [P("Vagal manoeuvres (modified Valsalva) → **adenosine 6–12–18 mg** → verapamil or beta-blocker")]),
            ("Narrow irregular (AF)", [P("Rate control: beta-blocker or diltiazem (digoxin/amiodarone if HF) → see AF chart")]),
            ("Broad regular (VT)", [P("**Amiodarone 300 mg IV** over 20–60 min; expert help")]),
            ("Broad irregular", [P("Pre-excited AF: **no AV-nodal blockers** → DC shock; torsades → **IV magnesium 2 g**")]),
        ]),
        E("Pulseless VT/VF → cardiac arrest algorithm (ALS chart)"),
    ]),
    F("Atrial fibrillation: AF-CARE", "ESC 2024 AF · NICE NG196", [
        S("AF confirmed on ECG"),
        P("**C**omorbidity & risk factors: BP, weight, alcohol, OSA, diabetes, exercise"),
        Q("**A**void stroke: CHA₂DS₂-VA (ESC 2024; NICE uses CHA₂DS₂-VASc)", [
            ("Score ≥ 2", [P("**DOAC recommended**; warfarin if mechanical valve or moderate–severe mitral stenosis")]),
            ("Score 1", [P("Consider DOAC")]),
            ("Score 0", [P("No anticoagulation; reassess yearly")]),
        ]),
        P("Bleeding risk: correct modifiable factors (BP, alcohol, NSAIDs, antiplatelets) — never withhold OAC because of a high bleeding score"),
        Q("**R**educe symptoms", [
            ("Rate control (everyone)", [P("Beta-blocker or diltiazem/verapamil (not if LVEF ≤ 40%); digoxin add-on; resting HR < 110")]),
            ("Rhythm control", [
                P("Onset < 24 h, or ≥ 3 weeks of OAC / TOE-guided → DC or drug cardioversion (flecainide if no structural disease, amiodarone if structural)"),
                P("**Catheter ablation** if drugs fail, or early in selected patients/HFrEF")]),
        ]),
        E("**E**valuate dynamically: echo, TFTs, renal function, reassess risk at every review"),
    ]),
    F("Bradycardia and heart block", "Resuscitation Council UK 2021", [
        S("Bradycardia: ABCDE, 12-lead ECG, check K⁺, drugs, TFTs"),
        Q("Adverse features or risk of asystole? (Mobitz II, CHB with broad QRS, pause > 3 s, recent asystole)", [
            ("Yes", [
                P("**Atropine 500 µg IV**, repeat to 3 mg"),
                P("No response → isoprenaline/adrenaline infusion or **transcutaneous pacing** → transvenous pacing")]),
            ("No", [P("Observe; stop AV-nodal blockers (beta-blocker, CCB, digoxin); treat cause")]),
        ]),
        E("**Permanent pacemaker**: symptomatic sick sinus, Mobitz II, complete heart block (unless reversible, e.g. inferior MI, drugs) · 1st-degree & Mobitz I usually benign"),
    ]),
]

E_['valv'] = [
    F("Aortic stenosis", "ESC/EACTS 2025 Valvular Heart Disease", [
        S("Ejection systolic murmur → echocardiography"),
        Q("Severity", [
            ("Severe (Vmax ≥ 4 m/s, mean ≥ 40 mmHg, AVA ≤ 1 cm²)", [
                P("**Symptoms or LVEF < 50% → intervene**"),
                P("Asymptomatic: exercise test, BNP; early intervention increasingly favoured (very severe, Vmax ≥ 5 m/s, rapid progression)")]),
            ("Low-flow, low-gradient", [P("**Dobutamine stress echo** or CT calcium score to confirm true severe AS")]),
            ("Mild–moderate", [P("Echo every 1–3 years; treat BP; no drug slows progression")]),
        ]),
        E("Heart team: **TAVI** if ≥ 70 years or high surgical risk with suitable access · **SAVR** if younger / low risk / bicuspid · balloon valvuloplasty only as a bridge"),
    ]),
    F("Mitral valve disease", "ESC/EACTS 2025 Valvular Heart Disease", [
        S("Mitral murmur → echocardiography"),
        Q("Lesion", [
            ("Mitral stenosis (rheumatic)", [
                P("AF → **warfarin** (not DOAC) + rate control (beta-blocker)"),
                E("Symptomatic, MVA ≤ 1.5 cm², favourable valve → **balloon commissurotomy**; unfavourable → surgery")]),
            ("Primary MR (prolapse, flail)", [
                P("Symptoms, LVEF ≤ 60%, LVESD ≥ 40 mm, new AF or PASP > 50 mmHg → **repair** (preferred to replacement)"),
                E("High surgical risk → transcatheter edge-to-edge repair (TEER)")]),
            ("Secondary MR (dilated LV)", [
                P("Optimise HF therapy ± CRT first"),
                E("Persistent symptoms → TEER in selected patients (COAPT)")]),
        ]),
        E("Prevent rheumatic recurrence with secondary penicillin prophylaxis · dental hygiene for all"),
    ]),
    F("Aortic regurgitation and prosthetic valves", "ESC/EACTS 2025 Valvular Heart Disease", [
        S("Early diastolic murmur, collapsing pulse, wide pulse pressure"),
        Q("Onset", [
            ("Acute (dissection, endocarditis)", [P("**Emergency surgery**; vasodilator (nitroprusside) as bridge; IABP contraindicated")]),
            ("Chronic severe", [
                P("Surgery if symptoms, LVEF ≤ 50–55%, or LVESD > 50 mm (> 25 mm/m²)"),
                P("Inoperable: ACEi/ARB or dihydropyridine for symptoms · Marfan: beta-blocker/ARB, root surgery ≥ 50 mm")]),
        ]),
        E("Mechanical valve → lifelong **warfarin** (INR 2.5–3.5 mitral; 2–3 bileaflet aortic) — DOACs contraindicated · bioprosthesis degenerates after ~10–15 years"),
    ]),
]

E_['peri'] = [
    F("Acute pericarditis and tamponade", "ESC 2025 Myocarditis & Pericarditis", [
        S("Pleuritic chest pain eased by sitting forward"),
        P("Diagnosis: ≥ 2 of typical pain · rub · widespread concave ST↑ with PR↓ · new effusion (supported by ↑CRP)"),
        P("ECG, CRP, troponin, CXR and **echo for all**"),
        Q("Risk features? (fever > 38 °C, large effusion/tamponade, immunosuppression, anticoagulation, trauma, no response to NSAID)", [
            ("None", [P("Outpatient: **aspirin/NSAID + PPI**, tapered over 1–2 weeks, + **colchicine 3 months**; restrict exercise")]),
            ("Present", [P("Admit; look for cause (TB, malignancy, autoimmune, uraemia, post-MI/Dressler)")]),
            ("Troponin ↑ (myopericarditis)", [P("Lower-dose NSAID; cardiac MRI; avoid sport ≥ 6 months")]),
        ]),
        P("Recurrent: colchicine ≥ 6 months; steroid-dependent → IL-1 blockade (anakinra, rilonacept)"),
        E("**Tamponade** (hypotension, ↑JVP, muffled sounds, pulsus paradoxus) → urgent echo-guided **pericardiocentesis** · constriction → pericardiectomy"),
    ]),
    F("Infective endocarditis", "ESC 2023 Endocarditis", [
        S("Fever + new murmur, embolic event, or risk (prosthetic valve, PWID, CIED)"),
        P("**3 sets of blood cultures** from separate sites before antibiotics"),
        P("**TTE first** → TOE if prosthetic valve, negative TTE with high suspicion, or to look for abscess; PET-CT for prosthetic/device IE"),
        Q("Modified Duke criteria (ESC 2023)", [
            ("Definite (2 major / 1 major + 3 minor / 5 minor)", [
                P("Empirical: native/late prosthetic → ampicillin + (flu)cloxacillin + gentamicin; early prosthetic/MRSA risk → vancomycin + gentamicin (+ rifampicin for staphylococcal PVE)"),
                P("Tailor to organism; 4–6 weeks; stable patients may switch to oral after ≥ 10 days IV")]),
            ("Possible / culture-negative", [P("Repeat cultures, serology (Coxiella, Bartonella), PCR, imaging")]),
        ]),
        E("Surgery (endocarditis team): heart failure · uncontrolled infection (abscess, fungi, resistant organism) · vegetation ≥ 10 mm with embolism"),
    ]),
    F("Acute rheumatic fever", "AHA revised Jones 2015 · WHO", [
        S("2–4 weeks after group A streptococcal pharyngitis"),
        P("Evidence of strep infection (raised ASO / anti-DNase B, culture) **plus** 2 major, or 1 major + 2 minor"),
        P("Major: **carditis, polyarthritis, chorea, erythema marginatum, subcutaneous nodules** · Minor: fever, arthralgia, ↑ESR/CRP, prolonged PR"),
        P("Treat: penicillin (eradication; macrolide if allergic), aspirin/NSAID for arthritis, steroids for severe carditis, echo for all"),
        E("**Secondary prophylaxis**: benzathine penicillin every 3–4 weeks — ≥ 10 years or to age 21–40 if carditis"),
    ]),
]

E_['htn'] = [
    F("Raised blood pressure: diagnosis and urgency", "NICE NG136 · ESC 2024 Hypertension", [
        S("Clinic BP ≥ 140/90 mmHg"),
        Q("How high, and is there acute organ damage?", [
            ("≥ 180/120 + acute damage (papilloedema, retinal haemorrhage, encephalopathy, AKI, ACS, HF, dissection)", [
                P("**Hypertensive emergency** → admit, IV labetalol / nicardipine / nitroprusside"),
                E("Lower MAP by no more than 20–25% in the first hours")]),
            ("≥ 180/120, no acute damage", [P("Urgency: check target organs same day; start oral treatment and review within days — never lower rapidly")]),
            ("140–179/90–119", [P("Confirm with **ABPM or HBPM** (mean ≥ 135/85)")]),
        ]),
        P("Work-up: U&E/eGFR, urine ACR, HbA1c, lipids, ECG (LVH), fundoscopy, QRISK3"),
        E("Look for a secondary cause if < 40, resistant, hypokalaemic or abrupt: aldosterone:renin ratio, metanephrines, renal ultrasound/MRA, sleep study"),
    ]),
    F("Drug treatment steps", "NICE NG136 (2023) · ESC 2024", [
        S("Lifestyle for everyone: salt < 6 g, weight, alcohol, exercise, stop smoking"),
        Q("Step 1", [
            ("Type 2 diabetes, or < 55 and not Black African/Caribbean", [P("**ACE inhibitor** (ARB if Black or ACEi-intolerant)")]),
            ("≥ 55, or Black African/Caribbean (no diabetes)", [P("**Calcium-channel blocker** (amlodipine)")]),
        ]),
        P("Step 2: ACEi/ARB + CCB, or + thiazide-like diuretic (indapamide)"),
        P("Step 3: ACEi/ARB + CCB + thiazide-like diuretic"),
        P("Step 4 (confirm with ABPM, check adherence): K⁺ ≤ 4.5 → **spironolactone**; K⁺ > 4.5 → alpha- or beta-blocker; specialist review"),
        E("Targets: clinic < 140/90 (< 80 yrs), < 150/90 (≥ 80 yrs) · ESC 2024: SBP 120–129 if tolerated · ESC favours single-pill combinations"),
    ]),
    F("Hypertension in pregnancy", "NICE NG133", [
        S("BP ≥ 140/90 in pregnancy"),
        Q("Type", [
            ("Before 20 weeks", [P("**Chronic hypertension**: stop ACEi/ARB/thiazide → labetalol (nifedipine, methyldopa)")]),
            ("After 20 weeks, no proteinuria", [P("**Gestational hypertension**: labetalol; target 135/85")]),
            ("After 20 weeks + proteinuria or organ dysfunction", [P("**Pre-eclampsia**: admit if severe; labetalol; **MgSO₄** for severe disease/eclampsia; plan delivery")]),
        ]),
        E("High risk of pre-eclampsia → **aspirin 75–150 mg** from 12 weeks to birth"),
    ]),
]

E_['cpharm'] = [
    F("Choosing an antithrombotic", "ESC 2023 ACS · ESC 2024 AF · NICE NG158", [
        S("What is the indication?"),
        Q("Indication", [
            ("ACS / PCI", [P("**DAPT**: aspirin + ticagrelor or prasugrel for 12 months (clopidogrel if high bleeding risk), then single antiplatelet")]),
            ("Stable CAD / PAD / ischaemic stroke", [P("Single antiplatelet: aspirin 75 mg or clopidogrel")]),
            ("AF / VTE", [P("**DOAC** (apixaban, rivaroxaban, edoxaban, dabigatran); warfarin for mechanical valve, moderate–severe MS, antiphospholipid syndrome")]),
        ]),
        P("AF + PCI: triple therapy ≤ 1 week → DOAC + clopidogrel to 12 months → DOAC alone"),
        E("Reversal: warfarin → vitamin K + prothrombin complex · dabigatran → idarucizumab · factor Xa inhibitors → andexanet alfa or PCC"),
    ]),
    F("Prescribing cardiovascular drugs safely", "BNF · NICE", [
        S("Starting or reviewing a cardiovascular drug"),
        Q("Drug group", [
            ("ACEi / ARB / MRA", [P("U&E before and 1–2 weeks after; accept creatinine rise < 30%; stop if K⁺ ≥ 6; ACEi cough → ARB; angioedema → stop")]),
            ("Rate & rhythm drugs", [P("Amiodarone: TFTs, LFTs, CXR, eyes, skin · digoxin toxicity ↑ with low K⁺, CKD, amiodarone/verapamil · flecainide only without structural disease")]),
            ("Statins & nitrates", [P("Statin myalgia → CK; avoid simvastatin with clarithromycin · no nitrates within 24–48 h of PDE-5 inhibitors")]),
        ]),
        E("Avoid: NSAIDs in HF/CKD ('triple whammy') · non-dihydropyridine CCB in HFrEF · non-selective beta-blockers in asthma · verapamil + beta-blocker IV"),
    ]),
]

E_['cvsx'] = [
    F("Cardiac arrest: advanced life support", "Resuscitation Council UK 2021 · ERC 2025", [
        S("Unresponsive, not breathing normally"),
        P("Call arrest team · **CPR 30:2** · attach defibrillator; minimise pauses"),
        Q("Rhythm", [
            ("Shockable (VF / pulseless VT)", [
                P("**Shock** → CPR 2 min → reassess"),
                P("After 3rd shock: **adrenaline 1 mg + amiodarone 300 mg**; adrenaline every 3–5 min; amiodarone 150 mg after 5th")]),
            ("Non-shockable (PEA / asystole)", [P("**Adrenaline 1 mg ASAP**, then every 3–5 min; CPR 2-min cycles")]),
        ]),
        P("Treat reversible causes — **4 Hs**: hypoxia, hypovolaemia, hypo/hyperkalaemia, hypothermia · **4 Ts**: thrombosis, tamponade, toxins, tension pneumothorax"),
        E("After ROSC: ABCDE, SpO₂ 94–98%, 12-lead ECG, PCI if STEMI, avoid fever, ICU"),
    ]),
    F("Syncope", "ESC 2018 Syncope · NICE CG109", [
        S("Transient loss of consciousness"),
        P("History (witness), examination, **lying & standing BP**, 12-lead ECG"),
        Q("Risk", [
            ("Low risk: reflex or orthostatic features, normal ECG", [P("Reassure, explain triggers, review drugs; discharge")]),
            ("High risk: exertional, supine, palpitations, structural heart disease, abnormal ECG, family sudden death", [P("Urgent assessment: monitoring, echo, ± EP study; pacing/ICD as indicated")]),
        ]),
        E("Unexplained and recurrent → implantable loop recorder · driving advice (DVLA)"),
    ]),
]

E_['cvsemq'] = [
    F("Murmur decoder", "Clinical examination", [
        S("Time the murmur against the carotid pulse"),
        Q("Timing", [
            ("Systolic", [
                P("Ejection, right 2nd ICS → carotids, slow-rising pulse: **AS**"),
                P("Ejection at LSE, louder on Valsalva/standing: **HOCM**"),
                P("Pansystolic apex → axilla: **MR** · lower LSE, louder on inspiration: **TR** · harsh with thrill: **VSD**")]),
            ("Diastolic", [
                P("Early, LSE, sitting forward, collapsing pulse: **AR** (+ Austin Flint rumble)"),
                P("Mid-diastolic apex, loud S1, opening snap: **MS** · early, with pulmonary hypertension: Graham Steell (PR)")]),
            ("Continuous", [P("Machinery murmur under left clavicle: **PDA** · AV fistula")]),
        ]),
        E("Next: echocardiography for every new murmur; ECG and CXR"),
    ]),
    F("Leg oedema and the JVP", "Clinical examination", [
        S("Bilateral leg oedema"),
        Q("JVP", [
            ("Raised, pulsatile", [P("Giant v waves → **TR** · rises on inspiration + knock → **constriction** · Beck's triad → **tamponade** · COPD + flap → **cor pulmonale** · crackles + S3 → **CCF**")]),
            ("Raised, non-pulsatile", [P("**SVC obstruction** (facial and arm swelling)")]),
            ("Normal", [P("Low albumin (nephrotic, liver) · drugs (**amlodipine**) · venous insufficiency · hypothyroidism")]),
        ]),
        E("Unilateral swollen leg → DVT (Wells score, ultrasound) · cellulitis · ruptured Baker's cyst"),
    ]),
]

# =================================================================== RESPIRATORY
E_['airway'] = [
    F("Asthma in adults: diagnosis and stepwise treatment", "BTS/NICE/SIGN 2024 · GINA 2025", [
        S("Suspected asthma: variable wheeze, cough, chest tightness"),
        P("Objective tests: **FeNO ≥ 50 ppb** (or raised eosinophils), bronchodilator reversibility ≥ 12% + 200 mL, PEF variability"),
        P("Step 1: **as-needed low-dose ICS–formoterol** (AIR) — no SABA-only treatment"),
        P("Step 2: **low-dose MART** (ICS–formoterol maintenance and reliever)"),
        P("Step 3: moderate-dose MART"),
        P("Step 4: check FeNO/eosinophils → specialist: biologics (anti-IL-5/5R, anti-IL-4R, anti-TSLP, anti-IgE) · if not type 2: trial LTRA or LAMA"),
        E("At every step: adherence, inhaler technique, triggers, written action plan · never LABA without ICS"),
    ]),
    F("Acute asthma", "BTS/SIGN · NICE", [
        S("Acute attack: PEF, SpO₂, RR, HR, speech"),
        Q("Severity", [
            ("Moderate: PEF > 50%", [P("Salbutamol via spacer; **prednisolone 40–50 mg** ≥ 5 days")]),
            ("Acute severe: PEF 33–50%, RR ≥ 25, HR ≥ 110, can't finish sentences", [P("O₂ to 94–98%, **nebulised salbutamol 5 mg** (back-to-back) + ipratropium, steroid")]),
            ("Life-threatening: PEF < 33%, SpO₂ < 92%, silent chest, normal PaCO₂, exhaustion", [P("As above + **IV magnesium 1.2–2 g**, ABG, senior & ICU review")]),
        ]),
        E("Rising PaCO₂ / drowsiness → intubate · discharge when PEF > 75%, on ICS, inhaler checked, review within 2 days"),
    ]),
    F("COPD: diagnosis and maintenance", "GOLD 2025 · NICE NG115", [
        S("Smoker/exposed with breathlessness, cough, sputum"),
        P("**Post-bronchodilator FEV1/FVC < 0.70** · grade GOLD 1–4 by FEV1"),
        P("Everyone: stop smoking · vaccines (flu, pneumococcal, COVID, RSV) · pulmonary rehab · SABA/SAMA reliever"),
        Q("GOLD group", [
            ("A: few symptoms, ≤ 1 moderate exacerbation", [P("A bronchodilator (LAMA or LABA)")]),
            ("B: mMRC ≥ 2 / CAT ≥ 10", [P("**LABA + LAMA**")]),
            ("E: ≥ 2 moderate or ≥ 1 hospitalised exacerbation", [P("LABA + LAMA; **+ ICS if eosinophils ≥ 300**")]),
        ]),
        P("Still exacerbating: azithromycin (ex-smokers) or roflumilast (FEV1 < 50%, chronic bronchitis); dupilumab if eosinophilic"),
        E("**LTOT** if stable PaO₂ < 7.3 kPa (or < 8 with oedema, polycythaemia, pulmonary hypertension) · home NIV for persistent hypercapnia · volume reduction in selected"),
    ]),
    F("COPD exacerbation", "GOLD 2025 · BTS NIV · NICE NG115", [
        S("Worse breathlessness, sputum volume or purulence"),
        P("SABA ± SAMA · **prednisolone 30–40 mg × 5 days** · antibiotic if purulent (amoxicillin, doxycycline, clarithromycin)"),
        P("Hospital: ABG, CXR, ECG · **controlled O₂ 24–28% → SpO₂ 88–92%**"),
        Q("ABG after 1 h of optimal therapy", [
            ("pH < 7.35 and PaCO₂ > 6.5 kPa", [P("**NIV (BiPAP)**; agree ceiling of care; intubate if NIV fails")]),
            ("pH ≥ 7.35", [P("Continue treatment; titrate O₂")]),
        ]),
        E("Before discharge: inhaler technique, rehab within 4 weeks, smoking cessation, follow-up"),
    ]),
    F("Bronchiectasis and cystic fibrosis", "BTS 2019 · NICE NG78", [
        S("Chronic productive cough, recurrent chest infections, haemoptysis"),
        P("**HRCT**: bronchus wider than its artery (signet ring), no tapering"),
        P("Find the cause: FBC, immunoglobulins, Aspergillus IgE/IgG (ABPA), sweat chloride/CFTR, ciliary tests, α1-antitrypsin"),
        Q("Situation", [
            ("Stable", [P("Daily **airway clearance** physiotherapy; ≥ 3 exacerbations/yr → long-term azithromycin or inhaled antibiotic; eradicate new Pseudomonas")]),
            ("Exacerbation", [P("**14 days** of antibiotic guided by sputum (Pseudomonas: ciprofloxacin or IV anti-pseudomonal)")]),
            ("Cystic fibrosis", [P("CFTR modulator (elexacaftor–tezacaftor–ivacaftor), dornase alfa, pancreatic enzymes, CF centre")]),
        ]),
        E("Massive haemoptysis → bronchial artery embolisation"),
    ]),
]

E_['resinf'] = [
    F("Community-acquired pneumonia", "NICE · BTS", [
        S("Acute LRTI symptoms + new shadowing on CXR"),
        P("Severity: **CURB-65** (confusion, urea > 7, RR ≥ 30, SBP < 90 or DBP ≤ 60, age ≥ 65); CRB-65 in the community"),
        Q("CURB-65", [
            ("0–1: low", [P("Home: **amoxicillin 5 days** (doxycycline or clarithromycin if allergic)")]),
            ("2: moderate", [P("Hospital: amoxicillin (+ clarithromycin if atypical suspected), 5 days")]),
            ("3–5: high", [P("**IV co-amoxiclav + clarithromycin**; blood cultures, urinary antigens; consider ICU")]),
        ]),
        P("Review at 48–72 h; switch IV to oral; stop at 5 days if stable"),
        E("Not improving → repeat CXR (effusion, empyema, abscess), unusual organisms (Legionella, S. aureus) · follow-up CXR at 6 weeks if symptoms persist or high cancer risk"),
    ]),
    F("Tuberculosis", "NICE NG33 · WHO 2022", [
        S("Cough > 2–3 weeks, fever, sweats, weight loss, haemoptysis; upper-zone shadowing"),
        P("Isolate · **3 sputum samples**: AFB smear, culture, NAAT (Xpert MTB/RIF detects rifampicin resistance) · HIV test"),
        Q("Result", [
            ("Drug-sensitive active TB", [P("**2 months RHZE → 4 months RH** + pyridoxine; baseline LFT, U&E, visual acuity; DOT if needed; CNS: 12 months + steroids")]),
            ("Rifampicin-resistant / MDR", [P("Specialist: **BPaLM** (bedaquiline, pretomanid, linezolid ± moxifloxacin) for 6 months")]),
            ("Latent (IGRA/TST +, normal CXR)", [P("3 months RH or 6 months isoniazid — essential before anti-TNF")]),
        ]),
        E("Toxicity: R orange fluids + enzyme induction · H neuropathy, hepatitis · Z hepatitis, gout · E optic neuritis · notify and trace contacts"),
    ]),
    F("Granulomatous and vasculitic lung disease", "ERS 2021 Sarcoidosis · EULAR 2022 Vasculitis", [
        S("Bilateral hilar nodes, nodules or pulmonary–renal picture"),
        P("CXR (Scadding 0–IV), HRCT, calcium, ACE, LFT, ECG, eye review; **EBUS-TBNA** for non-caseating granulomas (exclude TB, lymphoma)"),
        Q("Pattern", [
            ("Löfgren: erythema nodosum + BHL + arthritis", [P("NSAIDs, observe — usually remits")]),
            ("Organ-threatening sarcoid (falling lung function, eye, heart, CNS, hypercalcaemia)", [P("**Prednisolone 20–40 mg**; methotrexate as steroid-sparing")]),
            ("Haemoptysis + nodules ± AKI", [P("ANCA (PR3 → GPA, MPO → MPA), anti-GBM → steroids + rituximab/cyclophosphamide; plasma exchange for anti-GBM")]),
        ]),
        E("ABPA (asthma, IgE > 1000, fleeting infiltrates) → prednisolone ± itraconazole"),
    ]),
]

E_['crit'] = [
    F("Respiratory failure: reading the ABG", "BTS Oxygen 2017", [
        S("ABG: PaO₂ < 8 kPa = respiratory failure"),
        Q("PaCO₂", [
            ("Normal / low: type 1", [
                P("V/Q mismatch or shunt: pneumonia, PE, pulmonary oedema, ARDS, asthma"),
                E("O₂ to SpO₂ 94–98%, high-flow nasal oxygen, treat cause")]),
            ("> 6 kPa: type 2", [
                P("Hypoventilation: COPD, neuromuscular, chest wall, opioids, obesity"),
                E("Controlled O₂ to **88–92%**; **NIV** if pH < 7.35; naloxone for opioids")]),
        ]),
        P("A–a gradient: normal → pure hypoventilation (central/neuromuscular); raised → lung disease"),
        E("Chronic type 2: raised HCO₃⁻ with near-normal pH · acute-on-chronic: raised HCO₃⁻ and low pH"),
    ]),
    F("Acute respiratory distress syndrome", "Berlin + 2023 global definition · ESICM 2023 · ATS 2024", [
        S("Hypoxaemia within 1 week of an insult (sepsis, pneumonia, aspiration, pancreatitis, trauma)"),
        P("Bilateral opacities not explained by effusion/collapse · oedema not fully cardiac (echo)"),
        Q("PaO₂/FiO₂ (on PEEP/CPAP ≥ 5)", [
            ("201–300: mild", [P("High-flow nasal oxygen or NIV with close monitoring")]),
            ("101–200: moderate", [P("Intubate if failing: **Vt 6 mL/kg ideal body weight**, plateau ≤ 30 cmH₂O, higher PEEP, conservative fluids")]),
            ("≤ 100: severe", [P("+ **Prone 12–16 h/day** · neuromuscular blockade if dyssynchrony · VV-ECMO if refractory")]),
        ]),
        E("Treat the cause · consider corticosteroids (dexamethasone in COVID-19) · daily spontaneous breathing trial once FiO₂ ≤ 0.4, PEEP ≤ 8, off vasopressors"),
    ]),
]

E_['pleura'] = [
    F("Pleural effusion", "BTS Pleural 2023", [
        S("Effusion on CXR"),
        Q("Clear transudative cause? (bilateral, HF, cirrhosis, renal failure)", [
            ("Yes", [P("Treat the cause (diuretics); tap only if atypical or not responding")]),
            ("No / unilateral", [P("**Ultrasound-guided diagnostic aspiration**: pH, protein, LDH, glucose, cytology, MC&S ± AFB")]),
        ]),
        Q("Fluid", [
            ("Transudate (protein < 25 g/L, Light's negative)", [P("HF, cirrhosis, nephrotic syndrome, hypoalbuminaemia, hypothyroidism")]),
            ("Exudate (protein > 35 g/L or Light's positive)", [P("Contrast CT · cytology negative → **thoracoscopic or CT-guided biopsy** (TB, cancer, mesothelioma)")]),
            ("Infection: pus or pH < 7.2", [P("**Chest drain** + antibiotics with anaerobic cover; poor drainage → alteplase + DNase or surgery")]),
        ]),
        E("Recurrent malignant effusion → indwelling pleural catheter or talc pleurodesis"),
    ]),
    F("Pneumothorax", "BTS Pleural 2023", [
        S("Sudden pleuritic pain ± breathlessness; erect CXR"),
        P("**Tension** (hypotension, tracheal deviation, hypoxia) → immediate needle/finger decompression, then drain — do not wait for X-ray"),
        Q("Symptoms and high-risk features? (instability, significant hypoxia, bilateral, underlying lung disease, ≥ 50 + smoker, haemopneumothorax)", [
            ("Minimal symptoms, no high-risk features", [P("**Conservative** outpatient management, even if large")]),
            ("Symptomatic, no high-risk features", [P("Needle aspiration or **ambulatory valve device** — guided by patient priorities")]),
            ("High-risk / secondary pneumothorax", [P("Admit · **chest drain** (8–14 F) · surgery if air leak > 3–5 days")]),
        ]),
        E("Stop smoking · fly ≥ 1 week after resolution · no diving unless bilateral surgery · recurrence → VATS pleurectomy/abrasion"),
    ]),
]

E_['ild'] = [
    F("Interstitial lung disease", "ATS/ERS/JRS/ALAT 2022 · NICE TA", [
        S("Dry cough, exertional breathlessness, Velcro crackles, clubbing"),
        P("PFTs: restrictive with low TLCO · **HRCT** · CTD serology (ANA, RF, anti-CCP, myositis antibodies) · drug & exposure history (amiodarone, methotrexate, nitrofurantoin, birds, moulds, asbestos, silica)"),
        Q("HRCT pattern (MDT)", [
            ("UIP: basal subpleural honeycombing, no cause", [P("**IPF** — diagnosed without biopsy: **nintedanib or pirfenidone**; no steroids")]),
            ("Upper/mid zone, mosaic, air trapping + antigen", [P("**Hypersensitivity pneumonitis**: remove antigen; steroids if severe")]),
            ("NSIP / organising pneumonia / CTD-ILD", [P("Immunosuppression (mycophenolate, steroids); organising pneumonia is steroid-responsive")]),
        ]),
        P("Progressive pulmonary fibrosis of any cause → nintedanib"),
        E("All: stop smoking, rehab, oxygen, vaccines, early transplant & palliative referral · silicosis → screen for TB · asbestosis → compensation"),
    ]),
]

E_['pvasc'] = [
    F("Suspected pulmonary embolism", "NICE NG158 · ESC 2019 PE", [
        S("Suspected PE"),
        Q("Haemodynamically unstable? (SBP < 90 mmHg)", [
            ("Yes: high-risk", [P("Bedside echo (RV dysfunction) → UFH + **systemic thrombolysis** (alteplase); embolectomy if contraindicated")]),
            ("No", [P("**2-level Wells**: > 4 → CTPA (interim anticoagulation) · ≤ 4 → D-dimer → CTPA if positive")]),
        ]),
        P("V/Q scan if contrast allergy, renal failure, or pregnancy with normal CXR"),
        P("Risk-stratify (sPESI, RV strain, troponin): low risk → outpatient treatment"),
        E("Anticoagulate ≥ 3 months: **DOAC** (apixaban/rivaroxaban) · LMWH in pregnancy · unprovoked → consider long-term · IVC filter only if anticoagulation impossible"),
    ]),
    F("Pulmonary hypertension", "ESC/ERS 2022 PH", [
        S("Unexplained breathlessness, RV heave, loud P2, raised JVP"),
        P("Echo: TR velocity > 2.8 m/s → probability of PH"),
        P("Look first for left heart disease (group 2) and lung disease/hypoxia (group 3)"),
        P("**V/Q scan**: mismatched defects → CTEPH (group 4) → endarterectomy, balloon angioplasty, riociguat"),
        P("Right heart catheter: **mPAP > 20 mmHg**, PAWP ≤ 15, PVR > 2 WU = pre-capillary PH"),
        Q("Pulmonary arterial hypertension (group 1)", [
            ("Vasoreactive (idiopathic)", [P("High-dose calcium-channel blocker")]),
            ("Non-vasoreactive", [P("**ERA + PDE5 inhibitor** (e.g. ambrisentan + tadalafil); add prostacyclin pathway / sotatercept if high risk; transplant")]),
        ]),
        E("Cor pulmonale in COPD → LTOT and diuretics"),
    ]),
]

E_['lca'] = [
    F("Suspected lung cancer", "NICE NG122 (2024)", [
        S("Haemoptysis, persistent cough, weight loss, clubbing in a smoker > 40, or abnormal CXR"),
        P("Urgent CXR → **contrast CT chest + upper abdomen** (liver, adrenals) → lung cancer MDT"),
        P("Biopsy the site giving **diagnosis + highest stage with least risk** (node, effusion, EBUS-TBNA, CT-guided); PET-CT if curative treatment possible"),
        Q("NSCLC stage", [
            ("I–II, fit", [P("**Lobectomy** + nodal sampling (SABR if unfit); adjuvant chemo-immunotherapy or osimertinib if EGFR+")]),
            ("III", [P("Concurrent chemoradiotherapy → durvalumab; selected resectable → neoadjuvant chemo-immunotherapy")]),
            ("IV", [P("**Molecular testing** (EGFR, ALK, ROS1, KRAS…) → targeted drug; otherwise PD-L1 → immunotherapy ± chemotherapy")]),
        ]),
        E("Small cell: limited → chemoradiotherapy · extensive → platinum–etoposide + atezolizumab/durvalumab"),
    ]),
    F("Lung cancer emergencies and syndromes", "NICE NG234 · NICE NG122", [
        S("Patient with lung cancer becomes unwell"),
        Q("Problem", [
            ("SVC obstruction", [P("Head up; get tissue first; **endovascular stent** for rapid relief; treat tumour")]),
            ("Spinal cord compression", [P("**Dexamethasone 16 mg** now; whole-spine MRI within 24 h; surgery or radiotherapy")]),
            ("Hyponatraemia / hypercalcaemia", [P("SIADH (small cell): fluid restriction, hypertonic saline if seizures · Ca²⁺ (squamous, PTHrP): IV fluids + zoledronate")]),
        ]),
        E("Others: Lambert–Eaton (small cell) · ectopic ACTH · HPOA (non-small cell) · Pancoast tumour with Horner syndrome"),
    ]),
    F("Incidental pulmonary nodule", "BTS Pulmonary Nodules", [
        S("Solid nodule on CT"),
        Q("Size / appearance", [
            ("< 5 mm or benign calcification", [P("No follow-up")]),
            ("5–8 mm", [P("CT surveillance (volume doubling time)")]),
            ("≥ 8 mm: Brock risk > 10%", [P("**PET-CT** → Herder < 10% surveillance · 10–70% biopsy · > 70% resection")]),
        ]),
        E("Sub-solid nodules: longer surveillance (up to 4 years)"),
    ]),
]

E_['resx'] = [
    F("Sepsis", "Surviving Sepsis 2021 · NICE NG51", [
        S("Suspected infection + deterioration (NEWS2 ≥ 5)"),
        P("Sepsis = infection + organ dysfunction (SOFA ≥ 2)"),
        P("**Within 1 hour**: blood cultures, lactate, broad-spectrum antibiotics, fluids (30 mL/kg if hypotensive or lactate ≥ 4), O₂, urine output"),
        Q("After fluids", [
            ("MAP ≥ 65", [P("Sepsis: source control, review cultures at 48 h")]),
            ("Vasopressor needed + lactate > 2", [P("**Septic shock**: noradrenaline to MAP 65, ICU; hydrocortisone if ongoing vasopressor")]),
        ]),
        E("Glucose target 8–10 mmol/L (not tight) · transfuse at Hb < 70 g/L"),
    ]),
    F("Haemoptysis", "NICE NG12 · BTS", [
        S("Haemoptysis"),
        Q("Volume", [
            ("Massive (> 200 mL/24 h or compromise)", [P("Bleeding side down, secure airway, tranexamic acid → CT angiography → **bronchial artery embolisation**; rigid bronchoscopy")]),
            ("Non-massive", [P("CXR, CT chest; bronchoscopy if cancer risk")]),
        ]),
        P("Causes: cancer, bronchiectasis/CF, TB/aspergilloma, PE, vasculitis/anti-GBM, mitral stenosis, anticoagulation"),
        E("Unexplained haemoptysis ≥ 40 years → urgent suspected-cancer pathway"),
    ]),
    F("Obstructive sleep apnoea", "NICE NG202", [
        S("Snoring, witnessed apnoeas, daytime sleepiness"),
        P("Epworth score, STOP-BANG → **home sleep apnoea test** (polysomnography if complex)"),
        Q("AHI (events/hour)", [
            ("5–14: mild", [P("Weight loss, alcohol avoidance; CPAP if symptomatic; mandibular advancement device")]),
            ("≥ 15: moderate–severe", [P("**CPAP** first line")]),
        ]),
        E("Stop driving if excessively sleepy until treated (DVLA) · obesity hypoventilation (PaCO₂ > 6 kPa) → NIV"),
    ]),
]

E_['resemq'] = [
    F("Chest examination decoder", "Clinical examination", [
        S("Abnormal chest signs on one side"),
        Q("Percussion and breath sounds", [
            ("Dull + bronchial breathing, ↑ vocal resonance", [P("**Consolidation**")]),
            ("Stony dull, ↓ breath sounds, trachea away", [P("**Pleural effusion**")]),
            ("Dull, ↓ breath sounds, trachea towards", [P("**Collapse** (tumour, mucus plug)")]),
            ("Hyper-resonant, ↓ breath sounds", [P("**Pneumothorax** (trachea away + shock = tension)")]),
        ]),
        E("Fine Velcro crackles + clubbing → fibrosis · coarse crackles + clubbing → bronchiectasis · COPD alone does not cause clubbing"),
    ]),
    F("Chronic cough", "ERS 2020 · BTS", [
        S("Cough > 8 weeks"),
        P("**CXR + spirometry** for all · stop ACE inhibitor · stop smoking"),
        Q("Findings", [
            ("Red flags: haemoptysis, weight loss, smoker > 40, abnormal CXR", [P("CT ± bronchoscopy: cancer, TB, ILD, bronchiectasis")]),
            ("Normal CXR", [P("Asthma/eosinophilic bronchitis (FeNO → ICS trial) · rhinitis/upper airway (nasal steroid) · GORD (PPI if reflux symptoms)")]),
        ]),
        E("Refractory → neuromodulators (low-dose morphine, gabapentin), speech therapy"),
    ]),
    F("The child with cough or stridor", "NICE NG9 · RCPCH", [
        S("Child with cough or stridor"),
        Q("Picture", [
            ("Barking cough, stridor, 6 m–3 y", [P("**Croup**: oral dexamethasone 0.15 mg/kg; nebulised adrenaline if severe")]),
            ("Toxic, drooling, upright, unimmunised", [P("**Epiglottitis**: don't examine throat; anaesthetist/ENT airway; IV ceftriaxone")]),
            ("Sudden cough, unilateral signs, afebrile", [P("**Inhaled foreign body**: rigid bronchoscopy")]),
            ("Infant: coryza → wheeze + crackles", [P("**Bronchiolitis** (RSV): supportive; O₂ if SpO₂ < 90–92%")]),
        ]),
        E("Paroxysms + whoop / post-tussive vomiting → **pertussis**: macrolide, notify"),
    ]),
]

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'essentials.json')
json.dump(E_, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('chapters', len(E_), 'charts', sum(len(v) for v in E_.values()))
