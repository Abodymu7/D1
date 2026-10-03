"""'Essentials at a glance' — rebuilt natively from the summary pages of the 3rd edition
(PDF pp. 5–23 and 234–247), condensed, corrected and updated to current guidance.
Writes data/essentials.json  {chapter_id: [block, ...]}

Block types
  pairs : {"type","title","note","head":[a,b],"rows":[[left,[chip,...]],...]}   (finding -> condition chips)
  facts : {"type","title","rows":[[label,text],...]}                           (key-value list)
  ddx   : {"type","title","items":[{"name","what","clues","confirm","apart"}]}  (differential cards)
  flow  : {"type","title","steps":[[title,text],...]}                           (numbered line diagram)
  chips : {"type","title","chips":[...],"note"}
"""
import json, os

E = {}

# ------------------------------------------------------------------ CARDIOLOGY
E['cad'] = [
    {"type": "flow", "title": "Chest pain: from symptom to diagnosis", "steps": [
        ["Exertional chest pain", "Provoked by exertion or emotion, relieved within minutes by rest or GTN. Recent-onset angina is higher risk. Look for risk factors, anaemia, murmurs."],
        ["Baseline tests", "12-lead ECG, FBC, lipids, HbA1c, renal and thyroid function; echocardiography if a murmur or heart failure is suspected."],
        ["Stable chest pain", "CT coronary angiography is first line when typical or atypical angina cannot be excluded clinically; functional imaging if CAD is known or CT is non-diagnostic."],
        ["Pain at rest or prolonged", "Suspect ACS: ECG within 10 minutes and high-sensitivity troponin (0/1–3 h pathway). Repeat ECGs if the first is non-diagnostic."],
    ]},
    {"type": "facts", "title": "Acute coronary syndromes", "rows": [
        ["STEMI", "ST elevation or new LBBB with ischaemic symptoms → primary PCI if achievable within 120 min of diagnosis; otherwise fibrinolysis (tenecteplase) within 12 h of onset, then transfer."],
        ["NSTEMI", "Troponin rise and fall without persistent ST elevation; ST depression or T-wave inversion common. Invasive angiography within 24 h if high risk (GRACE > 140), immediately if unstable."],
        ["Unstable angina", "Ischaemic symptoms at rest or crescendo angina with normal troponin."],
        ["Initial therapy", "Aspirin 300 mg plus a second antiplatelet (ticagrelor or prasugrel), anticoagulation (fondaparinux/heparin), GTN; oxygen only if SpO₂ < 90%; opioid for severe pain."],
        ["Secondary prevention", "DAPT 12 months, high-intensity statin, ACE inhibitor, beta-blocker (especially if LVEF ≤ 40%), cardiac rehabilitation, smoking cessation."],
        ["Fibrinolysis contraindications", "Any previous intracranial haemorrhage, ischaemic stroke < 6 months, CNS tumour, active bleeding, suspected aortic dissection, recent major trauma or surgery."],
        ["Complications", "Arrhythmia (VF early, the commonest cause of death), heart failure and shock, papillary muscle rupture, VSD, free-wall rupture, LV aneurysm (persistent ST elevation), Dressler syndrome."],
    ]},
    {"type": "pairs", "title": "Localising the infarct on the ECG", "head": ["Leads with ST elevation", "Territory · artery"], "rows": [
        ["II, III, aVF", ["Inferior", "RCA (80%)"]],
        ["V1–V4", ["Anterior / septal", "LAD"]],
        ["I, aVL, V5–V6", ["Lateral", "Circumflex"]],
        ["V1–V3 ST depression, tall R, upright T", ["Posterior", "RCA / circumflex"]],
        ["V4R (with inferior MI)", ["Right ventricular infarct", "Proximal RCA"]],
    ]},
    {"type": "ddx", "title": "Leg pain on walking: vascular or not?", "items": [
        {"name": "Peripheral arterial disease", "clues": "Calf claudication relieved by standing still; weak pulses, bruits; smoker, diabetic", "confirm": "ABPI < 0.9; duplex, then CT/MR angiography before revascularisation", "apart": "Pain at a reproducible distance, not posture-dependent"},
        {"name": "Lumbar spinal stenosis", "clues": "Leg pain relieved by sitting or leaning forward; walking uphill easier", "confirm": "MRI lumbar spine", "apart": "Normal ABPI and pulses"},
        {"name": "Chronic venous insufficiency", "clues": "Heaviness and swelling worse on standing; varicosities, pigmentation", "confirm": "Venous duplex (reflux)", "apart": "Normal ABPI"},
        {"name": "Diabetic neuropathy", "clues": "Burning, stocking distribution, reduced reflexes and vibration", "confirm": "Clinical ± nerve conduction studies", "apart": "Symptoms at rest, not exertional"},
        {"name": "Popliteal entrapment", "clues": "Young athlete, exertional calf pain, normal resting pulses", "confirm": "Duplex with provocative manoeuvres, MRA", "apart": "No atherosclerotic risk factors"},
    ]},
    {"type": "facts", "title": "Managing claudication", "rows": [
        ["Everyone", "Stop smoking, supervised exercise programme, high-intensity statin, antiplatelet (clopidogrel preferred), control of BP and diabetes."],
        ["Drug for symptoms", "Naftidrofuryl (NICE) or cilostazol (not in heart failure) if exercise is insufficient."],
        ["Revascularisation", "Angioplasty/stent or bypass for lifestyle-limiting symptoms despite best medical therapy, or for critical limb-threatening ischaemia (rest pain, ulcers, gangrene)."],
    ]},
]

E['hf'] = [
    {"type": "facts", "title": "Heart failure in one page", "rows": [
        ["Definition", "A clinical syndrome of breathlessness, fatigue and fluid retention caused by a structural or functional cardiac abnormality, with raised natriuretic peptides or evidence of congestion."],
        ["HFrEF", "LVEF ≤ 40%. Causes: ischaemic heart disease (commonest), hypertension, dilated cardiomyopathy, valve disease, alcohol, chemotherapy, myocarditis."],
        ["HFmrEF · HFpEF", "LVEF 41–49% · ≥ 50% with raised filling pressures: older age, hypertension, AF, obesity, diabetes; infiltrative and restrictive disease."],
        ["High-output failure", "Anaemia, thyrotoxicosis, pregnancy, AV fistula, Paget disease, beriberi."],
        ["Left-sided features", "Exertional breathlessness, orthopnoea, PND, basal crackles, S3 gallop, pleural effusions."],
        ["Right-sided features", "Raised JVP, peripheral oedema, tender hepatomegaly, ascites."],
        ["Diagnosis", "NT-proBNP (> 400 ng/L chronic; > 2000 ng/L → echo within 2 weeks), echocardiography, ECG; CXR: cardiomegaly, upper-lobe diversion, Kerley B lines, bat-wing oedema, effusions."],
    ]},
    {"type": "flow", "title": "HFrEF: the four pillars and beyond", "steps": [
        ["Foundational drugs", "ACE inhibitor (or ARNI: sacubitril/valsartan), beta-blocker (bisoprolol, carvedilol), MRA (spironolactone/eplerenone) and SGLT2 inhibitor (dapagliflozin/empagliflozin) — all reduce mortality."],
        ["Symptoms", "Loop diuretic for congestion — improves symptoms, not survival; fluid and salt advice, daily weights."],
        ["Still symptomatic", "Switch ACE inhibitor to sacubitril/valsartan; ivabradine if sinus rhythm ≥ 70/min; hydralazine–nitrate; digoxin for symptoms or AF."],
        ["Devices", "ICD if LVEF ≤ 35% despite 3 months of therapy; CRT if LVEF ≤ 35% with LBBB QRS ≥ 150 ms."],
        ["Advanced", "LVAD or transplantation; palliative care."],
    ]},
    {"type": "facts", "title": "Acute decompensated heart failure", "rows": [
        ["Assess", "ECG, troponin, NT-proBNP, CXR, echo; look for the precipitant (ischaemia, arrhythmia, infection, non-adherence, NSAIDs)."],
        ["Treat", "Sit up; oxygen if SpO₂ < 90%; IV furosemide; IV nitrates if SBP > 110 mmHg; CPAP for respiratory distress; inotropes/vasopressors only in cardiogenic shock. Avoid routine opioids."],
    ]},
    {"type": "pairs", "title": "NYHA functional class", "head": ["Class", "Limitation"], "rows": [
        ["I", ["No limitation of ordinary activity"]],
        ["II", ["Slight limitation: ordinary activity causes symptoms"]],
        ["III", ["Marked limitation: less than ordinary activity causes symptoms"]],
        ["IV", ["Symptoms at rest"]],
    ]},
    {"type": "ddx", "title": "Myocardial disease: telling them apart", "items": [
        {"name": "Ischaemic cardiomyopathy", "clues": "Previous MI or angina; regional wall-motion abnormality", "confirm": "Coronary angiography / CT; late gadolinium in a subendocardial pattern", "apart": "Coronary disease explains the LV dysfunction"},
        {"name": "Dilated cardiomyopathy", "clues": "Dilated, globally hypokinetic LV; alcohol, familial, post-viral, peripartum, anthracyclines", "confirm": "Echo/CMR; exclude significant CAD", "apart": "Normal coronaries; genetic testing if familial"},
        {"name": "Hypertrophic cardiomyopathy", "clues": "Young, exertional syncope, family history of sudden death; ejection systolic murmur louder on standing/Valsalva", "confirm": "Wall thickness ≥ 15 mm (≥ 13 mm with family history) on echo/CMR; sarcomere gene testing", "apart": "Athlete's heart regresses with deconditioning; hypertensive LVH is concentric"},
        {"name": "Restrictive / infiltrative", "clues": "Amyloid, sarcoid, haemochromatosis; small LV, big atria, low-voltage ECG (amyloid)", "confirm": "CMR, technetium pyrophosphate scan, biopsy", "apart": "Constriction: thick pericardium, septal bounce, respiratory variation"},
        {"name": "Myocarditis", "clues": "Viral prodrome, chest pain, arrhythmia, troponin rise with normal coronaries", "confirm": "CMR (oedema + non-ischaemic late gadolinium); biopsy if fulminant", "apart": "Normal coronary angiography"},
    ]},
    {"type": "facts", "title": "Treatment of the cardiomyopathies", "rows": [
        ["Dilated", "Guideline-directed HFrEF therapy; ICD/CRT when indicated; abstinence from alcohol."],
        ["Hypertrophic", "Beta-blocker or non-dihydropyridine CCB; mavacamten for obstructive HCM; septal myectomy or alcohol ablation; ICD for high sudden-death risk; avoid dehydration, vasodilators and digoxin; screen first-degree relatives."],
        ["Myocarditis", "Supportive heart failure therapy, avoid competitive sport for 3–6 months; immunosuppression only for giant-cell or eosinophilic disease."],
    ]},
]

E['chd'] = [
    {"type": "pairs", "title": "Congenital heart disease: the clue decides", "head": ["Clue in the stem", "Lesion"], "rows": [
        ["Wide, fixed splitting of S2; pulmonary flow murmur", ["Atrial septal defect"]],
        ["Harsh pansystolic murmur, lower left sternal edge", ["Ventricular septal defect"]],
        ["Continuous 'machinery' murmur below the left clavicle, bounding pulses", ["Patent ductus arteriosus"]],
        ["Radio-femoral delay, arm hypertension, rib notching, murmur over the back", ["Coarctation of the aorta"]],
        ["Cyanosis on day 1; 'egg on a string' CXR", ["Transposition of the great arteries"]],
        ["Cyanotic spells, squatting; 'boot-shaped' heart", ["Tetralogy of Fallot"]],
        ["Cyanosis and clubbing in an adult with a known shunt", ["Eisenmenger syndrome"]],
    ]},
    {"type": "ddx", "title": "The common lesions", "items": [
        {"name": "VSD", "what": "Left-to-right shunt through the interventricular septum", "clues": "Pansystolic murmur LLSE; heart failure in infancy if large", "confirm": "Echo with Doppler", "apart": "S2 not fixed-split (ASD)"},
        {"name": "ASD (secundum)", "what": "Defect in the atrial septum; RA/RV volume overload", "clues": "Often silent until adulthood: fixed split S2, ejection murmur, RBBB, atrial arrhythmias, paradoxical embolism", "confirm": "TTE/TOE, bubble study", "apart": "No pansystolic murmur"},
        {"name": "PDA", "what": "Persistent ductus arteriosus (prematurity, rubella)", "clues": "Machinery murmur, wide pulse pressure", "confirm": "Echo with colour Doppler", "apart": "Continuous, not systolic, murmur"},
        {"name": "Tetralogy of Fallot", "what": "VSD, RV outflow obstruction, overriding aorta, RVH", "clues": "Cyanosis, 'tet spells', ejection murmur of pulmonary stenosis", "confirm": "Echo; CMR", "apart": "Cyanotic, unlike VSD/ASD"},
        {"name": "Coarctation", "what": "Aortic narrowing near the ductus; Turner syndrome, bicuspid valve", "clues": "Upper-limb hypertension, weak delayed femoral pulses", "confirm": "Echo, CT or MR angiography", "apart": "BP gradient arms > legs"},
    ]},
    {"type": "flow", "title": "Work-up and treatment", "steps": [
        ["Echocardiography", "TTE (± TOE) defines the anatomy, shunt direction and size, and pulmonary pressure."],
        ["ECG · CXR", "Chamber enlargement, conduction disease; boot shape, rib notching, pulmonary plethora or oligaemia."],
        ["CMR / CT · catheter", "Complex anatomy; catheterisation for pressures, shunt ratio and interventions."],
        ["Treatment", "Diuretics for volume overload; device or surgical closure (ASD, VSD, PDA), balloon/stent or repair (coarctation), complete repair (Fallot); endocarditis prophylaxis only for high-risk lesions."],
    ]},
]

E['arr'] = [
    {"type": "pairs", "title": "Reading the ECG", "head": ["Finding", "Think of"], "rows": [
        ["Saw-tooth flutter waves, often 2:1 at 150/min", ["Atrial flutter"]],
        ["Irregularly irregular, no P waves", ["Atrial fibrillation"]],
        ["Short PR, delta wave, broad QRS", ["Wolff–Parkinson–White"]],
        ["Bifid P (P mitrale) · peaked P (P pulmonale)", ["Left atrial enlargement", "Right atrial enlargement"]],
        ["Saddle-shaped ST elevation, PR depression", ["Acute pericarditis"]],
        ["Persistent ST elevation weeks after MI", ["LV aneurysm"]],
        ["S1 Q3 T3, sinus tachycardia, RV strain", ["Pulmonary embolism"]],
        ["Tall tented T, wide QRS → sine wave", ["Hyperkalaemia"]],
        ["Flat T, U waves, long QU", ["Hypokalaemia"]],
        ["Long QT", ["Hypocalcaemia", "Drugs", "Congenital LQTS"]],
        ["Short QT", ["Hypercalcaemia", "Digoxin"]],
        ["Reverse-tick ST depression", ["Digoxin effect"]],
        ["J (Osborn) waves", ["Hypothermia"]],
    ]},
    {"type": "facts", "title": "Palpitations and syncope", "rows": [
        ["Palpitations", "Capture the rhythm during symptoms: 12-lead ECG, Holter, event recorder or smartphone ECG. Palpitations with syncope, exertion, structural heart disease or a family history of sudden death need urgent assessment."],
        ["Reflex syncope", "Prodrome (warmth, nausea), trigger (standing, pain, micturition), rapid recovery."],
        ["Cardiac syncope", "Exertional or supine, no prodrome, palpitations, known heart disease, abnormal ECG — admit and monitor."],
        ["Orthostatic", "Fall in SBP ≥ 20 mmHg on standing: drugs, volume depletion, autonomic failure."],
    ]},
    {"type": "flow", "title": "Tachyarrhythmia — ALS logic", "steps": [
        ["Adverse features?", "Shock, syncope, myocardial ischaemia, severe heart failure → synchronised DC cardioversion (up to 3 shocks), then amiodarone 300 mg."],
        ["Stable, broad QRS", "Regular: VT → amiodarone. Irregular: AF with BBB, pre-excited AF (avoid AV-node blockers), or torsades (magnesium)."],
        ["Stable, narrow regular", "Vagal manoeuvres → adenosine 6–12–18 mg (verapamil if asthma); flutter → rate control."],
        ["Stable, narrow irregular", "Probable AF: rate control (beta-blocker/diltiazem); anticoagulate by CHA₂DS₂-VASc; cardiovert if onset < 48 h."],
    ]},
]

E['valv'] = [
    {"type": "ddx", "title": "Murmurs and heart sounds", "items": [
        {"name": "Aortic stenosis", "clues": "Slow-rising pulse, narrow pulse pressure, heaving undisplaced apex, soft S2, ejection systolic murmur radiating to the carotids", "confirm": "Echo: severe = Vmax ≥ 4 m/s, mean gradient ≥ 40 mmHg, AVA < 1 cm²", "apart": "Symptoms (angina, syncope, breathlessness) → TAVI or surgical AVR"},
        {"name": "Aortic regurgitation", "clues": "Collapsing pulse, wide pulse pressure, displaced apex, early diastolic murmur at LSE (sitting forward, expiration)", "confirm": "Echo", "apart": "Signs: Corrigan, de Musset, Quincke, Traube"},
        {"name": "Mitral stenosis", "clues": "Malar flush, AF, tapping apex, loud S1, opening snap, mid-diastolic rumble at the apex (left lateral, expiration)", "confirm": "Echo: severe when MVA < 1.5 cm²", "apart": "Rheumatic history; balloon valvotomy if anatomy suitable"},
        {"name": "Mitral regurgitation", "clues": "Displaced apex, soft S1, pansystolic murmur at the apex radiating to the axilla", "confirm": "Echo (TOE for repair planning)", "apart": "Repair preferred; surgery if symptoms, LVEF ≤ 60% or LVESD ≥ 40 mm"},
        {"name": "Tricuspid regurgitation", "clues": "Large v waves, pulsatile liver, pansystolic murmur at LLSE louder on inspiration", "confirm": "Echo", "apart": "Often functional (pulmonary hypertension); IV drug use → endocarditis"},
        {"name": "Ventricular septal defect", "clues": "Harsh pansystolic murmur LLSE with a thrill; parasternal heave", "confirm": "Echo", "apart": "Not louder on inspiration"},
    ]},
    {"type": "pairs", "title": "Eponymous signs", "head": ["Sign", "Condition"], "rows": [
        ["Malar flush", ["Mitral stenosis"]],
        ["Pulsatile hepatomegaly", ["Tricuspid regurgitation"]],
        ["Corrigan (visible carotid pulsation) · de Musset (head nodding)", ["Aortic regurgitation"]],
        ["Quincke (nail-bed pulsation) · Traube (pistol-shot femorals)", ["Aortic regurgitation"]],
        ["Roth spots · Osler nodes (painful) · Janeway lesions (painless)", ["Infective endocarditis"]],
    ]},
    {"type": "facts", "title": "Mitral valve disease", "rows": [
        ["Mitral stenosis — cause", "Rheumatic heart disease (almost always); annular calcification in the elderly."],
        ["Pathophysiology", "Symptoms once the orifice falls below about 2 cm²: raised LA pressure → pulmonary congestion, AF, pulmonary hypertension, RV failure."],
        ["Symptoms", "Exertional breathlessness, fatigue, palpitations, haemoptysis, systemic embolism."],
        ["Treatment", "Rate control and anticoagulation (warfarin in moderate–severe MS with AF — not a DOAC), diuretics; percutaneous balloon valvotomy, or replacement."],
        ["Mitral regurgitation — causes", "Prolapse (degenerative), LV dilatation (functional), rheumatic disease, endocarditis, papillary muscle rupture after MI (acute MR → pulmonary oedema)."],
        ["Treatment", "Diuretics, heart failure therapy for secondary MR; repair or replacement for severe primary MR; transcatheter edge-to-edge repair in selected secondary MR."],
    ]},
]

E['peri'] = [
    {"type": "facts", "title": "Diseases of the pericardium", "rows": [
        ["Normal pericardium", "A two-layer sac with about 50 mL of fluid; congenital absence is usually harmless."],
        ["Causes", "Viral/idiopathic (commonest), bacterial, tuberculosis; post-MI (early, or Dressler), post-cardiac surgery, uraemia, SLE, rheumatoid arthritis, malignancy, radiotherapy, trauma."],
        ["Acute pericarditis", "Sharp pleuritic central chest pain eased by sitting forward, friction rub, widespread saddle ST elevation with PR depression. Treat with high-dose NSAID or aspirin plus colchicine for 3 months; avoid steroids first line."],
        ["Pericardial effusion", "Soft heart sounds, low-voltage ECG, globular heart on CXR; confirm with echo."],
        ["Cardiac tamponade", "Beck triad (hypotension, raised JVP, muffled heart sounds), pulsus paradoxus, electrical alternans → urgent echo-guided pericardiocentesis."],
        ["Tuberculous pericarditis", "Common where TB or HIV is prevalent; treat with antituberculous therapy — risk of constriction."],
        ["Constrictive pericarditis", "Right-heart congestion (ascites, hepatomegaly, oedema), Kussmaul sign, pericardial knock, calcification on CXR/CT. Treatment: diuretics, pericardiectomy."],
    ]},
    {"type": "facts", "title": "Infective endocarditis", "rows": [
        ["At risk", "Prosthetic valves, previous endocarditis, congenital and rheumatic heart disease, IV drug use, intravascular devices, haemodialysis."],
        ["Organisms", "S. aureus (commonest; acute, IV drug users → tricuspid valve), viridans streptococci (subacute, dental), enterococci, S. gallolyticus (bovis) → colonoscopy, coagulase-negative staphylococci (early prosthetic), HACEK and Coxiella (culture-negative)."],
        ["Clinical", "Fever plus a new murmur; splinter haemorrhages, Osler nodes, Janeway lesions, Roth spots, splenomegaly, microscopic haematuria, emboli."],
        ["Diagnosis", "Modified Duke criteria: ≥ 3 sets of blood cultures before antibiotics; TTE first, TOE if prosthetic valve, TTE negative or complications suspected."],
        ["Treatment", "Prolonged IV bactericidal antibiotics guided by culture (empirically amoxicillin ± gentamicin or vancomycin by setting); surgery for heart failure, abscess, uncontrolled infection or large vegetations with emboli."],
        ["Prevention", "Good dental hygiene; antibiotic prophylaxis only for high-risk patients undergoing dental procedures (ESC)."],
    ]},
    {"type": "facts", "title": "Rheumatic fever and rheumatic heart disease", "rows": [
        ["Who", "Children aged 5–15 years after group A streptococcal pharyngitis; endemic in South Asia, Africa, the Middle East and the Pacific."],
        ["Mechanism", "Molecular mimicry: antibodies cross-react with cardiac, joint and neural tissue; Aschoff bodies."],
        ["Major criteria (Jones)", "Carditis, polyarthritis, Sydenham chorea, erythema marginatum, subcutaneous nodules."],
        ["Minor criteria", "Fever, arthralgia, raised ESR/CRP, prolonged PR interval. Plus evidence of recent streptococcal infection (ASO titre, throat culture)."],
        ["Treatment", "Penicillin to eradicate streptococci, aspirin or NSAID for arthritis, steroids for severe carditis; then secondary prophylaxis with benzathine penicillin."],
        ["Rheumatic heart disease", "Develops in many with carditis; the mitral valve is involved most — mitral regurgitation early, mitral stenosis later."],
    ]},
]

E['htn'] = [
    {"type": "facts", "title": "Diagnosis and targets", "rows": [
        ["Confirm", "Clinic BP ≥ 140/90 mmHg → ambulatory (or home) monitoring: hypertension if daytime average ≥ 135/85 mmHg (NICE)."],
        ["Assess", "Urine albumin:creatinine ratio and dipstick, U&E and eGFR, HbA1c, lipids, ECG, fundoscopy; cardiovascular risk (QRISK3)."],
        ["Treat", "Stage 2 (≥ 150/95 ABPM) for all; stage 1 if under 80 with target-organ damage, CVD, renal disease, diabetes or 10-year risk ≥ 10%."],
        ["Targets", "Clinic < 140/90 (< 150/90 if 80 or older); ESC suggests 120–129 systolic if tolerated."],
    ]},
    {"type": "flow", "title": "Drug steps (NICE NG136)", "steps": [
        ["Step 1", "Under 55 and not of Black African/Caribbean family origin, or type 2 diabetes at any age: ACE inhibitor or ARB. Aged 55 or over, or of Black African/Caribbean family origin, without diabetes: calcium-channel blocker."],
        ["Step 2", "ACE inhibitor/ARB + CCB (or thiazide-like diuretic). In Black patients prefer an ARB to an ACE inhibitor."],
        ["Step 3", "ACE inhibitor/ARB + CCB + thiazide-like diuretic (indapamide)."],
        ["Step 4 — resistant", "Check adherence and secondary causes; K⁺ ≤ 4.5 mmol/L → spironolactone; K⁺ > 4.5 → alpha- or beta-blocker; seek specialist advice."],
    ]},
    {"type": "ddx", "title": "Secondary hypertension", "items": [
        {"name": "Renal parenchymal disease", "clues": "Proteinuria, haematuria, raised creatinine, oedema; glomerulonephritis, polycystic kidneys", "confirm": "Urinalysis, eGFR, renal ultrasound", "apart": "Treat the kidney; ACE inhibitor/ARB for proteinuria"},
        {"name": "Primary hyperaldosteronism", "clues": "Resistant hypertension, hypokalaemia, metabolic alkalosis (K⁺ can be normal)", "confirm": "Raised aldosterone:renin ratio → confirmatory suppression test → adrenal CT and venous sampling", "apart": "Adenoma → adrenalectomy; hyperplasia → spironolactone"},
        {"name": "Renovascular disease", "clues": "Flash pulmonary oedema, abdominal bruit, creatinine rise on ACE inhibitor; young woman → fibromuscular dysplasia", "confirm": "Duplex, CT or MR angiography", "apart": "Angioplasty for FMD; medical therapy for atheroma"},
        {"name": "Phaeochromocytoma", "clues": "Paroxysmal headache, sweating, palpitations, labile BP", "confirm": "Plasma free (or urine) metanephrines → CT/MRI", "apart": "Alpha-blockade (phenoxybenzamine) before beta-blockade, then adrenalectomy"},
        {"name": "Others", "clues": "Cushing syndrome, coarctation, obstructive sleep apnoea, thyroid disease, drugs (NSAIDs, steroids, COCP, liquorice)", "confirm": "Targeted tests", "apart": "Consider in young (< 40) or resistant hypertension"},
    ]},
]

E['cpharm'] = [
    {"type": "pairs", "title": "Classic adverse effects", "head": ["Adverse effect", "Drug"], "rows": [
        ["Bronchospasm, cold peripheries, fatigue, erectile dysfunction, masked hypoglycaemia", ["Beta-blockers"]],
        ["Dry cough, angio-oedema, hyperkalaemia, first-dose hypotension", ["ACE inhibitors"]],
        ["Gynaecomastia", ["Spironolactone", "Digoxin"]],
        ["Thyroid dysfunction, corneal deposits, pulmonary fibrosis, photosensitivity, hepatitis", ["Amiodarone"]],
        ["Constipation, bradycardia", ["Verapamil"]],
        ["Flushing, headache, ankle oedema", ["Nifedipine", "Amlodipine"]],
        ["Gout, hyponatraemia, hypokalaemia, hyperglycaemia", ["Thiazides"]],
        ["Ototoxicity (high dose), hypokalaemia", ["Furosemide"]],
        ["Hirsutism", ["Minoxidil"]],
        ["Drug-induced lupus", ["Hydralazine", "Procainamide"]],
        ["Myalgia, raised CK, rhabdomyolysis", ["Statins"]],
        ["Dyspnoea, bradyarrhythmia", ["Ticagrelor"]],
        ["Nausea, xanthopsia, arrhythmias (worse with low K⁺)", ["Digoxin toxicity"]],
        ["Genital thrush, euglycaemic ketoacidosis", ["SGLT2 inhibitors"]],
    ]},
]

E['cvsemq'] = [
    {"type": "pairs", "title": "EMQ decoder — the pulse", "head": ["Pulse in the stem", "Condition"], "rows": [
        ["Irregularly irregular", ["Atrial fibrillation"]],
        ["Slow-rising", ["Aortic stenosis"]],
        ["Collapsing (water-hammer)", ["Aortic regurgitation", "PDA"]],
        ["Bounding", ["CO₂ retention", "Liver failure", "Sepsis"]],
        ["Radio-femoral delay", ["Coarctation of the aorta"]],
        ["Jerky", ["HOCM"]],
        ["Bisferiens", ["Mixed aortic valve disease", "HOCM"]],
        ["Pulsus paradoxus", ["Cardiac tamponade", "Severe asthma"]],
        ["Pulsus alternans", ["Severe LV failure"]],
    ]},
    {"type": "pairs", "title": "EMQ decoder — the JVP", "head": ["JVP in the stem", "Condition"], "rows": [
        ["Raised, fixed, non-pulsatile", ["SVC obstruction"]],
        ["Rises on inspiration (Kussmaul)", ["Constrictive pericarditis", "Restrictive cardiomyopathy", "RV infarction"]],
        ["Large v waves", ["Tricuspid regurgitation"]],
        ["Absent a waves", ["Atrial fibrillation"]],
        ["Cannon a waves", ["Complete heart block", "VT (AV dissociation)"]],
        ["Giant a waves", ["Pulmonary hypertension", "Pulmonary or tricuspid stenosis"]],
        ["Steep y descent", ["Constrictive pericarditis"]],
    ]},
]

E['cvsx'] = [
    {"type": "ddx", "title": "Presenting problems in cardiology", "items": [
        {"name": "Exertional chest pain", "clues": "Reproducible with exertion, relieved by rest or GTN", "confirm": "ECG, bloods; CT coronary angiography first line", "apart": "Murmur → echo (aortic stenosis, HCM)"},
        {"name": "Acute chest pain", "clues": "Prolonged or at rest, sweating, pallor, arrhythmia, hypotension", "confirm": "ECG within 10 min, high-sensitivity troponin", "apart": "Tearing pain to the back → dissection; pleuritic → PE, pericarditis"},
        {"name": "Breathlessness", "clues": "Orthopnoea, PND, oedema, murmurs, AF", "confirm": "NT-proBNP, echo, CXR", "apart": "Many causes are respiratory; normal NT-proBNP makes HF unlikely"},
        {"name": "Syncope", "clues": "Exertional, no prodrome, known heart disease, family history", "confirm": "ECG, echo, ambulatory monitoring", "apart": "Reflex syncope: trigger, prodrome, quick recovery"},
        {"name": "Palpitations", "clues": "Describe rhythm and onset/offset; triggers", "confirm": "ECG during symptoms, Holter, event recorder", "apart": "Usually benign; urgent if with syncope or structural disease"},
    ]},
]

# ------------------------------------------------------------------ RESPIRATORY
E['airway'] = [
    {"type": "ddx", "title": "Wheeze and breathlessness: which airway disease?", "items": [
        {"name": "Asthma", "clues": "Episodic wheeze, cough worse at night or with triggers, atopy, variability", "confirm": "Raised FeNO (≥ 50 ppb in adults), bronchodilator reversibility (FEV₁ ↑ ≥ 12% and ≥ 200 mL), PEF variability, eosinophils", "apart": "Normal gas transfer; symptom-free intervals"},
        {"name": "COPD", "clues": "Smoker > 40 years, persistent productive cough, exertional breathlessness, hyperinflation", "confirm": "Post-bronchodilator FEV₁/FVC < 0.70 (GOLD); CXR; FBC; alpha-1 antitrypsin if young or non-smoker", "apart": "Limited reversibility; reduced TLCO in emphysema"},
        {"name": "Bronchiectasis", "clues": "Daily purulent sputum, recurrent infections, haemoptysis, coarse crackles, clubbing", "confirm": "HRCT: bronchi wider than the artery (signet ring), no tapering, wall thickening", "apart": "Look for the cause: post-infective, CF, immunodeficiency, ABPA, PCD"},
        {"name": "Cystic fibrosis", "clues": "Young, recurrent chest infections, failure to thrive, steatorrhoea, male infertility", "confirm": "Sweat chloride ≥ 60 mmol/L; CFTR genotyping", "apart": "Pseudomonas and S. aureus colonisation"},
        {"name": "Heart failure", "clues": "Orthopnoea, PND, oedema, crackles, cardiac history", "confirm": "NT-proBNP, echo", "apart": "'Cardiac asthma' improves with diuretics"},
        {"name": "Vocal cord dysfunction", "clues": "Inspiratory stridor, throat tightness, no response to inhalers", "confirm": "Flattened inspiratory loop; laryngoscopy during symptoms", "apart": "Normal spirometry between episodes"},
    ]},
    {"type": "flow", "title": "Asthma treatment (BTS/NICE/SIGN 2024 · GINA)", "steps": [
        ["Reliever alone is not enough", "Every adult with asthma needs an inhaled corticosteroid; SABA-only treatment is no longer recommended."],
        ["Start", "As-needed low-dose ICS–formoterol (anti-inflammatory reliever, AIR); or low-dose MART if symptoms are frequent."],
        ["Step up", "Moderate-dose MART; then add LTRA or LAMA; check inhaler technique, adherence and triggers at every step."],
        ["Specialist", "Uncontrolled on moderate-dose MART → FeNO/eosinophils → biologics (anti-IgE, anti-IL-5, anti-IL-4R, anti-TSLP)."],
    ]},
    {"type": "facts", "title": "Acute asthma severity", "rows": [
        ["Moderate", "PEF 50–75% best or predicted, speech normal."],
        ["Acute severe", "PEF 33–50%, RR ≥ 25, HR ≥ 110, cannot complete sentences."],
        ["Life-threatening", "PEF < 33%, SpO₂ < 92%, PaO₂ < 8 kPa, 'normal' PaCO₂ (4.6–6.0 kPa), silent chest, cyanosis, poor effort, arrhythmia, hypotension, exhaustion, confusion."],
        ["Near-fatal", "Raised PaCO₂ or need for mechanical ventilation."],
        ["Treatment", "Oxygen to SpO₂ 94–98%, nebulised salbutamol (back-to-back) + ipratropium, prednisolone 40–50 mg (or IV hydrocortisone), IV magnesium sulfate if severe; ICU for life-threatening features. NIV is not recommended."],
    ]},
    {"type": "flow", "title": "COPD treatment (GOLD 2025 · NICE)", "steps": [
        ["For everyone", "Smoking cessation, vaccination (influenza, pneumococcal, RSV, COVID-19), pulmonary rehabilitation if MRC ≥ 3, SABA/SAMA as needed."],
        ["Initial maintenance", "LABA + LAMA for most symptomatic patients; add ICS (LABA+LAMA+ICS) if exacerbations with blood eosinophils ≥ 300/µL or asthmatic features."],
        ["Still exacerbating", "Eosinophils ≥ 100 → add ICS; roflumilast (chronic bronchitis, FEV₁ < 50%), azithromycin (ex-smokers), dupilumab or mepolizumab for eosinophilic COPD with exacerbations."],
        ["Advanced", "Long-term oxygen if PaO₂ < 7.3 kPa (or < 8 kPa with polycythaemia, cor pulmonale, pulmonary hypertension) and non-smoker; home NIV for persistent hypercapnia; lung volume reduction, transplantation."],
    ]},
    {"type": "facts", "title": "Exacerbations of COPD", "rows": [
        ["Treatment", "Bronchodilators, prednisolone 30–40 mg for 5 days, antibiotics if purulent sputum or pneumonia; controlled oxygen to SpO₂ 88–92%."],
        ["NIV", "Persistent respiratory acidosis (pH < 7.35, PaCO₂ > 6.5 kPa) despite optimal medical therapy."],
    ]},
]

E['resinf'] = [
    {"type": "pairs", "title": "Pneumonia: clue → organism", "head": ["Clue in the stem", "Organism"], "rows": [
        ["Commonest community-acquired; rusty sputum, lobar consolidation", ["Streptococcus pneumoniae"]],
        ["Positive cold agglutinins, haemolysis, erythema multiforme, young adult", ["Mycoplasma pneumoniae"]],
        ["Air-conditioning or water systems, hyponatraemia, diarrhoea, confusion", ["Legionella pneumophila"]],
        ["Cavitation after influenza", ["Staphylococcus aureus"]],
        ["Alcoholic, upper-lobe cavitation, redcurrant-jelly sputum", ["Klebsiella pneumoniae"]],
        ["Contact with birds (parrots)", ["Chlamydia psittaci"]],
        ["Farm animals, Q fever", ["Coxiella burnetii"]],
        ["HIV (CD4 < 200), bilateral perihilar ground-glass, desaturation on exercise", ["Pneumocystis jirovecii"]],
        ["COPD exacerbation", ["Haemophilus influenzae", "Moraxella catarrhalis"]],
        ["Cystic fibrosis, bronchiectasis", ["Pseudomonas aeruginosa"]],
        ["Aspiration, foul sputum, right lower lobe", ["Anaerobes"]],
    ]},
    {"type": "flow", "title": "Community-acquired pneumonia (BTS/NICE)", "steps": [
        ["Confirm", "CXR; FBC, U&E, CRP; pulse oximetry and ABG if SpO₂ < 94%; blood and sputum cultures, pneumococcal and Legionella urinary antigens if moderate–severe."],
        ["Score severity", "CURB-65: Confusion, Urea > 7 mmol/L, RR ≥ 30, BP < 90 systolic or ≤ 60 diastolic, age ≥ 65. 0–1 home; 2 consider admission; 3–5 severe (consider ICU). CRB-65 in the community."],
        ["Treat", "Low severity: amoxicillin (doxycycline or clarithromycin if penicillin-allergic) for 5 days. High severity: co-amoxiclav + clarithromycin (IV)."],
        ["Follow up", "Repeat CXR at 6 weeks if symptoms persist or there is a high risk of malignancy (smoker, > 50)."],
    ]},
    {"type": "ddx", "title": "Tuberculosis and its mimics", "items": [
        {"name": "Pulmonary tuberculosis", "clues": "Chronic cough, haemoptysis, fever, night sweats, weight loss; upper-lobe cavitation", "confirm": "Sputum × 3 for smear, culture and NAAT (Xpert MTB/RIF Ultra); IGRA/TST only for latent infection", "apart": "Caseating granulomas; offer HIV test"},
        {"name": "Sarcoidosis", "clues": "Bilateral hilar lymphadenopathy, erythema nodosum, uveitis, hypercalcaemia, raised ACE", "confirm": "EBUS-TBNA or biopsy: non-caseating granulomas; exclude TB", "apart": "Often asymptomatic; many remit spontaneously"},
        {"name": "Lung cancer", "clues": "Smoker, older, haemoptysis, weight loss, cavitating squamous tumour", "confirm": "CT, PET-CT, tissue biopsy", "apart": "No response to antituberculous therapy"},
        {"name": "Histoplasmosis / fungal", "clues": "Endemic exposure, bat or bird droppings, calcified granulomas", "confirm": "Antigen tests, culture, serology", "apart": "Negative mycobacterial tests"},
    ]},
    {"type": "facts", "title": "Treating tuberculosis", "rows": [
        ["Standard regimen", "2 months of rifampicin, isoniazid, pyrazinamide and ethambutol (RHZE), then 4 months of rifampicin + isoniazid; 12 months for CNS TB (with steroids). Directly observed therapy where adherence is uncertain."],
        ["Drug-resistant", "Rifampicin-resistant/MDR-TB: 6-month BPaLM (bedaquiline, pretomanid, linezolid ± moxifloxacin) — WHO."],
        ["Isoniazid", "Peripheral neuropathy (give pyridoxine), hepatitis."],
        ["Rifampicin", "Orange urine and tears, hepatitis, enzyme induction (contraceptive pill, warfarin fail)."],
        ["Pyrazinamide", "Hepatitis, gout (hyperuricaemia), arthralgia."],
        ["Ethambutol", "Optic neuritis — red–green colour vision loss; check visual acuity first."],
    ]},
]

E['crit'] = [
    {"type": "facts", "title": "Respiratory failure and blood gases", "rows": [
        ["Type 1", "PaO₂ < 8 kPa with normal or low PaCO₂: V/Q mismatch — pneumonia, pulmonary oedema, PE, asthma, ARDS, ILD."],
        ["Type 2", "PaO₂ < 8 kPa with PaCO₂ > 6.5 kPa: alveolar hypoventilation — COPD, neuromuscular disease, chest wall deformity, obesity, sedatives."],
        ["Acute vs chronic type 2", "Acute: low pH, normal bicarbonate. Chronic: near-normal pH, raised bicarbonate (renal compensation)."],
        ["Oxygen targets", "94–98% for most; 88–92% if at risk of hypercapnic failure (COPD, obesity, neuromuscular disease)."],
        ["NIV (BiPAP)", "Acute hypercapnic respiratory acidosis (pH < 7.35, PaCO₂ > 6.5 kPa) in COPD, obesity or neuromuscular disease; CPAP for type 1 failure in pulmonary oedema."],
    ]},
    {"type": "ddx", "title": "ARDS and its mimics", "items": [
        {"name": "ARDS", "what": "Diffuse inflammatory lung injury with non-cardiogenic oedema", "clues": "Within 1 week of an insult (sepsis, pneumonia, aspiration, pancreatitis, trauma, transfusion); bilateral opacities; refractory hypoxaemia", "confirm": "Berlin: PaO₂/FiO₂ ≤ 300 mmHg on PEEP ≥ 5 (mild 200–300, moderate 100–200, severe ≤ 100)", "apart": "Normal LV function; oedema not explained by heart failure"},
        {"name": "Cardiogenic pulmonary oedema", "clues": "Orthopnoea, S3, cardiac history, bat-wing oedema, effusions", "confirm": "Echo, NT-proBNP", "apart": "Improves quickly with diuretics and nitrates"},
        {"name": "Severe pneumonia", "clues": "Fever, purulent sputum, focal consolidation", "confirm": "CXR, cultures, antigens", "apart": "Focal rather than diffuse"},
        {"name": "Diffuse alveolar haemorrhage", "clues": "Haemoptysis, falling haemoglobin, vasculitis or anti-GBM disease", "confirm": "BAL: progressively bloodier returns; ANCA, anti-GBM", "apart": "Raised KCO"},
    ]},
    {"type": "flow", "title": "Managing ARDS", "steps": [
        ["Treat the cause", "Source control and antibiotics for sepsis; supportive care in ICU."],
        ["Protective ventilation", "Tidal volume 6 mL/kg predicted body weight, plateau pressure < 30 cmH₂O, adequate PEEP."],
        ["Moderate–severe", "Prone positioning 12–16 h/day; neuromuscular blockade early in selected patients."],
        ["Fluids and rescue", "Conservative fluid strategy once shock resolves; steroids in selected cases; VV-ECMO for refractory hypoxaemia."],
    ]},
]

E['pleura'] = [
    {"type": "flow", "title": "Pleural effusion (BTS 2023)", "steps": [
        ["Is it obvious?", "Bilateral effusions with heart failure, cirrhosis or renal failure: treat the cause; tap only if atypical or not resolving."],
        ["Ultrasound-guided diagnostic aspiration", "Protein, LDH, pH, glucose, cytology, Gram stain, culture (and AFB if TB risk)."],
        ["Light criteria", "Exudate if fluid:serum protein > 0.5, fluid:serum LDH > 0.6, or fluid LDH > ⅔ upper limit of normal serum LDH."],
        ["Still no diagnosis", "Contrast CT thorax, then pleural biopsy (image-guided or thoracoscopic)."],
    ]},
    {"type": "pairs", "title": "Pleural fluid clues", "head": ["Fluid", "Think of"], "rows": [
        ["Transudate", ["Heart failure", "Cirrhosis", "Nephrotic syndrome", "Hypothyroidism"]],
        ["Exudate", ["Parapneumonic / empyema", "Malignancy", "TB", "PE", "Rheumatoid arthritis"]],
        ["pH < 7.2 or frank pus", ["Empyema → chest drain"]],
        ["Very low glucose", ["Rheumatoid arthritis", "Empyema"]],
        ["Lymphocyte-rich exudate", ["TB", "Malignancy", "Lymphoma"]],
        ["Milky, triglycerides > 1.24 mmol/L", ["Chylothorax"]],
        ["Raised amylase", ["Pancreatitis", "Oesophageal rupture"]],
        ["Haematocrit > 50% of blood", ["Haemothorax"]],
    ]},
    {"type": "facts", "title": "Pneumothorax (BTS 2023)", "rows": [
        ["Primary", "Young, tall, smoker. Minimal symptoms → conservative management with follow-up; symptomatic → needle aspiration or ambulatory device; chest drain if these fail."],
        ["Secondary", "Underlying lung disease (COPD, CF, ILD): admit; chest drain for most, aspiration if 1–2 cm."],
        ["Tension", "Hypotension, tracheal deviation away, hyper-resonance → immediate needle or finger thoracostomy, then drain."],
        ["Recurrence", "Surgical pleurodesis (VATS) for a second episode, persistent air leak, or high-risk occupations; no flying until resolved; no diving ever unless definitive surgery."],
    ]},
]

E['ild'] = [
    {"type": "ddx", "title": "Interstitial lung disease", "items": [
        {"name": "Idiopathic pulmonary fibrosis", "clues": "Older man, progressive breathlessness, dry cough, clubbing, fine bibasal 'velcro' crackles", "confirm": "HRCT: UIP — subpleural basal reticulation with honeycombing (± MDT, biopsy rarely)", "apart": "No exposure or CTD; restrictive spirometry, low TLCO"},
        {"name": "NSIP", "clues": "Younger, often connective tissue disease (scleroderma, myositis)", "confirm": "HRCT: symmetrical ground-glass with sub-pleural sparing, little honeycombing", "apart": "Autoantibodies positive; responds to immunosuppression"},
        {"name": "Hypersensitivity pneumonitis", "clues": "Birds, mouldy hay, humidifiers; symptoms hours after exposure", "confirm": "HRCT: centrilobular nodules, ground-glass, mosaic attenuation; BAL lymphocytosis; serum IgG to the antigen", "apart": "Improves with antigen avoidance"},
        {"name": "Sarcoidosis", "clues": "Young adult, BHL, erythema nodosum, uveitis, hypercalcaemia", "confirm": "Biopsy: non-caseating granulomas", "apart": "Upper-zone and perilymphatic distribution"},
        {"name": "Occupational / drug", "clues": "Asbestos (lower zones, pleural plaques), silica and coal (upper zones); amiodarone, methotrexate, nitrofurantoin, bleomycin", "confirm": "History + HRCT", "apart": "Exposure history"},
    ]},
    {"type": "facts", "title": "Treating ILD", "rows": [
        ["IPF", "Antifibrotics (pirfenidone or nintedanib, NICE when FVC 50–80% predicted); pulmonary rehabilitation, oxygen, transplantation; no steroids."],
        ["Progressive pulmonary fibrosis", "Nintedanib for other fibrosing ILDs that progress despite treatment."],
        ["NSIP / CTD-ILD", "Corticosteroids, mycophenolate, rituximab."],
        ["Hypersensitivity pneumonitis", "Antigen avoidance first; corticosteroids if severe."],
        ["Sarcoidosis", "Observe if asymptomatic; steroids for organ-threatening disease; methotrexate as steroid-sparing."],
        ["All", "Vaccination, smoking cessation, oxygen, monitoring with spirometry, TLCO and HRCT."],
    ]},
]

E['pvasc'] = [
    {"type": "flow", "title": "Suspected pulmonary embolism (NICE/ESC)", "steps": [
        ["Unstable?", "Shock → bedside echo (RV dilatation) or CTPA if immediately available → systemic thrombolysis."],
        ["Two-level Wells score", "PE likely (> 4): CTPA (start anticoagulation if delayed). PE unlikely (≤ 4): D-dimer (age-adjusted over 50) → CTPA if positive."],
        ["CTPA contraindicated", "V/Q scan (renal impairment, contrast allergy, pregnancy); leg duplex if DVT symptoms."],
        ["Risk-stratify", "PESI/sPESI, RV dysfunction on echo/CT, troponin; low-risk patients can be treated at home."],
    ]},
    {"type": "ddx", "title": "Mimics of pulmonary embolism", "items": [
        {"name": "Pneumonia", "clues": "Fever, purulent sputum, focal crackles", "confirm": "CXR consolidation, raised CRP", "apart": "PE may also cause fever and infarction — keep it in mind"},
        {"name": "Acute coronary syndrome", "clues": "Central pressure-like pain, sweating", "confirm": "ECG changes, troponin rise and fall", "apart": "Troponin also rises in PE with RV strain"},
        {"name": "Pneumothorax", "clues": "Sudden pleuritic pain, reduced breath sounds, hyper-resonance", "confirm": "CXR or ultrasound", "apart": "Visible pleural line"},
        {"name": "Panic attack", "clues": "Tingling, carpopedal spasm, sense of doom", "confirm": "Diagnosis of exclusion", "apart": "Normal SpO₂, A–a gradient and investigations"},
    ]},
    {"type": "facts", "title": "Treatment", "rows": [
        ["Anticoagulation", "DOAC (apixaban or rivaroxaban) for most; LMWH in pregnancy and active cancer (or DOAC); warfarin if antiphospholipid syndrome."],
        ["Duration", "3 months if provoked by a transient factor; long-term if unprovoked, recurrent or ongoing risk (active cancer)."],
        ["High-risk PE", "Thrombolysis (alteplase); surgical or catheter embolectomy if contraindicated."],
        ["IVC filter", "Only when anticoagulation is contraindicated in acute proximal DVT/PE."],
        ["Pulmonary hypertension", "Mean PA pressure > 20 mmHg; group by cause (left heart, lung disease, CTEPH — look for it after PE); echo, V/Q scan, right-heart catheterisation."],
    ]},
]

E['lca'] = [
    {"type": "facts", "title": "Lung cancer essentials (NICE NG122)", "rows": [
        ["Refer urgently (2 weeks)", "CXR suggestive of cancer, or age ≥ 40 with unexplained haemoptysis. Urgent CXR for ≥ 40 with two symptoms (or one if ever smoked): cough, fatigue, breathlessness, chest pain, weight loss, appetite loss."],
        ["Diagnose and stage", "Contrast CT chest and upper abdomen → PET-CT → least invasive sampling that gives both diagnosis and stage (EBUS-TBNA for nodes)."],
        ["Non-small-cell (≈ 85%)", "Adenocarcinoma (commonest; non-smokers, peripheral; EGFR, ALK, ROS1 targets), squamous (central, cavitates, hypercalcaemia)."],
        ["Small-cell (≈ 15%)", "Central, smokers, early spread, SIADH, ectopic ACTH, Lambert–Eaton; chemo-immunotherapy ± radiotherapy."],
        ["Treatment NSCLC", "Stage I–II: lobectomy or SABR; stage III: chemoradiotherapy ± durvalumab or surgery; stage IV: targeted therapy or immunotherapy according to biomarkers (PD-L1)."],
    ]},
    {"type": "pairs", "title": "Paraneoplastic and local effects", "head": ["Feature", "Think of"], "rows": [
        ["Hypercalcaemia (PTHrP)", ["Squamous cell carcinoma"]],
        ["Hyponatraemia (SIADH), Cushing (ectopic ACTH)", ["Small-cell carcinoma"]],
        ["Proximal weakness improving with exercise", ["Lambert–Eaton (small-cell)"]],
        ["Clubbing, hypertrophic pulmonary osteoarthropathy", ["NSCLC (adenocarcinoma, squamous)"]],
        ["Horner syndrome, arm pain, T1 wasting", ["Pancoast tumour"]],
        ["Facial swelling, distended neck veins", ["SVC obstruction → stent, steroids, treat tumour"]],
        ["Hoarse voice", ["Left recurrent laryngeal nerve palsy"]],
        ["Pleural mass, asbestos exposure", ["Mesothelioma"]],
    ]},
]

E['resx'] = [
    {"type": "pairs", "title": "Chest X-ray phrases", "head": ["Phrase in the stem", "Think of"], "rows": [
        ["Kerley B lines, bat-wing shadowing, upper-lobe diversion", ["Heart failure"]],
        ["Tram-lines and ring shadows", ["Bronchiectasis"]],
        ["Miliary shadowing", ["Miliary TB"]],
        ["Wedge-shaped peripheral opacity", ["Pulmonary infarction (PE)"]],
        ["Ground-glass → honeycombing", ["Pulmonary fibrosis"]],
        ["Bilateral hilar lymphadenopathy", ["Sarcoidosis", "Lymphoma", "TB"]],
        ["Lobulated pleural mass, plaques", ["Mesothelioma", "Asbestos exposure"]],
        ["Upper-lobe cavity", ["TB", "Squamous carcinoma", "Klebsiella"]],
        ["Meniscus / air-crescent in a cavity", ["Aspergilloma"]],
    ]},
    {"type": "pairs", "title": "Respiratory drugs: adverse effects", "head": ["Adverse effect", "Drug"], "rows": [
        ["Tremor, tachycardia, hypokalaemia", ["Salbutamol"]],
        ["Oral candidiasis, dysphonia; pneumonia in COPD", ["Inhaled corticosteroids"]],
        ["Dry mouth, urinary retention", ["Ipratropium", "Tiotropium"]],
        ["Nausea, arrhythmia, seizures (narrow therapeutic range)", ["Theophylline"]],
        ["Neuropsychiatric events", ["Montelukast"]],
        ["Diarrhoea, weight loss", ["Roflumilast"]],
        ["Nausea, vivid dreams", ["Varenicline"]],
    ]},
]

E['resemq'] = [
    {"type": "pairs", "title": "EMQ decoder — the chest examination", "head": ["Finding", "Diagnosis"], "rows": [
        ["Hyperexpanded chest, prolonged expiration", ["COPD", "Chronic asthma"]],
        ["Flapping tremor, bounding pulse, warm hands", ["CO₂ retention"]],
        ["Stony dull percussion, absent breath sounds", ["Pleural effusion"]],
        ["Dull, bronchial breathing, crackles", ["Consolidation"]],
        ["Hyper-resonance, absent breath sounds", ["Pneumothorax"]],
        ["Fine end-inspiratory crackles", ["Pulmonary fibrosis", "Pulmonary oedema"]],
        ["Coarse crackles, copious sputum", ["Bronchiectasis"]],
        ["Pleuritic chest pain", ["PE", "Pneumonia", "Pneumothorax"]],
        ["Stridor", ["Upper airway obstruction"]],
        ["Trachea pulled towards the lesion", ["Collapse", "Upper-lobe fibrosis"]],
    ]},
    {"type": "chips", "title": "Clubbing in the respiratory patient", "chips": ["Lung cancer (NSCLC)", "Bronchiectasis", "Lung abscess", "Empyema", "Cystic fibrosis", "Idiopathic pulmonary fibrosis", "Asbestosis", "Mesothelioma"], "note": "Not a feature of asthma or uncomplicated COPD — in a smoker with COPD, new clubbing means cancer until proved otherwise."},
    {"type": "pairs", "title": "EMQ decoder — the history", "head": ["Clue", "Condition"], "rows": [
        ["Early emphysema (basal) with liver disease", ["Alpha-1 antitrypsin deficiency"]],
        ["Fever and breathlessness hours after exposure to hay or birds", ["Hypersensitivity pneumonitis"]],
        ["Bilateral hilar nodes, erythema nodosum, raised ACE", ["Sarcoidosis"]],
        ["Recurrent chest infections, failure to thrive, steatorrhoea", ["Cystic fibrosis"]],
        ["Night sweats, weight loss, haemoptysis, AFB on Ziehl–Neelsen", ["Tuberculosis"]],
        ["Swinging fever, copious foul sputum after aspiration", ["Lung abscess"]],
    ]},
]

out = os.path.join(os.path.dirname(__file__), '..', 'essentials.json')
json.dump(E, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('chapters', len(E), 'blocks', sum(len(v) for v in E.values()))
