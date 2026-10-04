"""39th batch final papers (Paper 1 and Paper 2) — the cardiovascular and respiratory questions.
Source: Cardiovascular_Respiratory_Questions.html (recalled papers; no answer key supplied).
Only the cardiorespiratory questions of Paper 1/2 are taken; the other four files in that HTML
(4th midterm, Block D, Medicine 2 Block 2, Medicine 2) are already in the bank as '39 Blocks Questions'.
Recall gaps (blank options) are completed with plausible distractors; keys are set and explained here.

  python data/import/b39_papers_src.py   -> data/patches/303-39-batch-papers.json
"""
import json, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
BANK = '39th Batch Final Papers'
OUT = []
NEXT = {'peri': 87, 'cad': 154, 'pleura': 46, 'airway': 88, 'resinf': 126, 'lca': 56, 'crit': 21, 'cvsemq': 69, 'resemq': 48}


def nid(ch):
    n = NEXT[ch]; NEXT[ch] += 1
    return '%s-%04d' % (ch, n)


def mcq(ch, paper, num, case, q, options, answer, ex, topics, notes=''):
    stem = (case + ' ' + q).strip() if case else q
    rec = dict(id=nid(ch), chapter=ch, order=paper * 1000 + num, type='MCQ', bank=BANK, source='39th batch Paper %d Q%d' % (paper, num),
               status='new', topics=topics, notes=notes, stem=stem, options=options, answer=answer, explanation=ex, images=[],
               src=dict(file='39-papers', paper=paper, num=num))
    OUT.append(dict(new=rec, why='Added from 39th batch Paper %d (recalled exam)' % paper))
    return rec['id']


def emq(ch, paper, first, theme, options, items, topics, notes=''):
    L = [chr(65 + i) for i in range(len(options))]
    its = []
    for k, (num, stem, ans, ex) in enumerate(items):
        its.append(dict(n=k + 1, stem=stem, answer=ans, explanation=ex, images=[], src_num=num))
    rec = dict(id=nid(ch), chapter=ch, order=paper * 1000 + first, type='EMQ', bank=BANK,
               source='39th batch Paper %d Q%d–%d' % (paper, items[0][0], items[-1][0]), status='new', topics=topics, notes=notes,
               theme=theme, options=options, option_letters=L, items=its, stem='', answer='', explanation='', images=[],
               src=dict(file='39-papers', paper=paper))
    OUT.append(dict(new=rec, why='Added from 39th batch Paper %d (recalled exam)' % paper))
    return rec['id']


# ===================================================================== PAPER 1 — MCQs
# --- infective endocarditis (Q26–29) -> peri
IE = ('A 51-year-old man with mitral valve prolapse and type 2 diabetes has had intermittent fever, night sweats and fatigue for 10 days, '
      'with mild exertional breathlessness and occasional palpitations. He recently had a dental extraction. T 38.9 °C, pulse 122/min, '
      'BP 105/65 mmHg, RR 22/min. There is a pansystolic murmur at the apex radiating to the axilla and tender erythematous nodules on his fingertips.')
q26 = mcq('peri', 1, 26, IE, 'What is the most likely causative organism?',
          ['Staphylococcus aureus', 'Viridans streptococci', 'Enterococcus faecalis', 'Staphylococcus epidermidis', 'Streptococcus pyogenes'], 'B',
          'Subacute endocarditis on a prolapsing mitral valve after dental extraction is caused by oral viridans streptococci. '
          'S. aureus is acute and fulminant; S. epidermidis infects prosthetic valves.',
          ['Infective endocarditis', 'Viridans streptococci', 'Dental procedures'])
mcq('peri', 1, 27, IE, 'Which of the following findings is most specific to this disease?',
    ['Fever and fatigue', 'Shortness of breath', 'Splinter haemorrhages', 'Splenomegaly', 'Tachycardia'], 'C',
    'Only the vascular signs (splinter haemorrhages, like his Osler nodes) point specifically to endocarditis; '
    'fever, dyspnoea, tachycardia and splenomegaly are non-specific.',
    ['Infective endocarditis', 'Splinter haemorrhages', 'Osler nodes'])
mcq('peri', 1, 28, IE, 'The initial step of management should include:',
    ['Antipyretics', 'Empirical intravenous antibiotics', 'Immediate surgical valve replacement', 'Anticoagulation', 'Antiarrhythmic drugs'], 'B',
    'Take three sets of blood cultures, then start empirical IV antibiotics and tailor to the organism. Surgery is for heart failure, '
    'uncontrolled infection or large emboli.',
    ['Infective endocarditis', 'Blood cultures', 'Empirical antibiotics'])
mcq('peri', 1, 29, IE, 'Which of the following is the most serious potential complication of this disease?',
    ['Acute heart failure', 'Pulmonary embolism', 'Viral myocarditis', 'Chronic liver disease', 'Hypertension'], 'A',
    'Leaflet or chordal destruction causes acute regurgitation and heart failure, the commonest cause of death in IE and the main '
    'reason for urgent surgery. Pulmonary emboli come from tricuspid IE.',
    ['Infective endocarditis', 'Acute heart failure', 'Complications of endocarditis'])

# --- AAA and acute limb ischaemia (Q37–40) -> cad
AAA = ('A 71-year-old male smoker with hypertension and type 2 diabetes has noticed a pulsating abdominal mass and has had dull abdominal pain '
       'radiating to the back for 2 months.')
mcq('cad', 1, 37, AAA, 'What is the most likely diagnosis?',
    ['Diverticulitis', 'Ureteric colic', 'Abdominal aortic aneurysm', 'Chronic pancreatitis', 'Mesenteric ischaemia'], 'C',
    'An expansile (pulsatile) mass with back pain in an older male smoker is an abdominal aortic aneurysm; new or persistent pain '
    'suggests expansion and needs urgent imaging.',
    ['Abdominal aortic aneurysm'])
mcq('cad', 1, 38, AAA, 'What is the gold-standard diagnostic test?',
    ['Doppler ultrasound', 'Abdominal X-ray', 'CT angiography', 'MRI', 'ECG'], 'C',
    'Ultrasound is for screening and surveillance; CT angiography is the reference test, measuring the aneurysm, its extent and any '
    'leak, and planning EVAR or open repair.',
    ['Abdominal aortic aneurysm', 'CT angiography'])
mcq('cad', 1, 39, AAA, 'He suddenly develops pain in his right leg, and the dorsalis pedis pulse is absent. What is the most likely diagnosis?',
    ['Chronic limb ischaemia', 'Cellulitis', 'Acute limb ischaemia', 'Deep vein thrombosis', 'Compartment syndrome'], 'C',
    'Sudden pain with a lost pulse is acute limb ischaemia, here from an embolus of mural thrombus in the aneurysm. Look for the 6 Ps '
    '(pain, pallor, pulselessness, perishing cold, paraesthesia, paralysis).',
    ['Acute limb ischaemia', 'Abdominal aortic aneurysm'])
mcq('cad', 1, 40, AAA, 'What is the first-line management for this complication?',
    ['Antiplatelet therapy', 'Anticoagulation', 'Antibiotics', 'Leg elevation', 'Fasciotomy'], 'B',
    'Give IV unfractionated heparin at once to stop clot propagation, then revascularise (embolectomy or thrombolysis). '
    'Elevation worsens ischaemia.',
    ['Acute limb ischaemia', 'Heparin'])

# --- familial hypercholesterolaemia (Q56–60) -> cad
FH = ('A 25-year-old man has exertional chest pain. His father died of a myocardial infarction at the age of 44. Fasting lipids: '
      'total cholesterol 550 mg/dL, LDL cholesterol 280 mg/dL, HDL cholesterol 35 mg/dL, triglycerides 120 mg/dL.')
mcq('cad', 1, 56, FH, 'What is the most likely diagnosis?',
    ['Familial hypercholesterolaemia', 'Familial hypertriglyceridaemia', 'Familial combined hyperlipidaemia', 'Familial chylomicronaemia',
     'Raised lipoprotein(a)'], 'A',
    'Very high LDL, normal triglycerides and premature coronary disease in a first-degree relative is familial hypercholesterolaemia '
    '(LDL-receptor defect).',
    ['Familial hypercholesterolaemia', 'Dyslipidaemia'])
mcq('cad', 1, 57, FH, 'If untreated, what is the most likely complication?',
    ['Premature coronary artery disease and myocardial infarction', 'Childhood stroke', 'Acute pancreatitis', 'Hypothyroidism', 'Gallstones'], 'A',
    'Lifelong high LDL causes premature atherosclerosis and MI decades early. Pancreatitis complicates severe '
    'hypertriglyceridaemia, not high LDL.',
    ['Familial hypercholesterolaemia', 'Premature coronary artery disease'])
mcq('cad', 1, 58, FH, 'What is the best initial treatment?',
    ['Lifestyle modification only', 'Statin therapy', 'Fibrate therapy', 'Niacin', 'PCSK9 inhibitor monotherapy'], 'B',
    'Start a high-intensity statin (atorvastatin 40–80 mg) with lifestyle advice; diet alone cannot correct a genetic LDL excess. '
    'Fibrates target triglycerides.',
    ['Familial hypercholesterolaemia', 'Statins'])
mcq('cad', 1, 59, FH, 'Despite adherence to a high-intensity statin for 3 months, his LDL cholesterol remains above target. What is the next step?',
    ['Add ezetimibe', 'Switch to a fibrate', 'Add niacin', 'Add a fish-oil supplement', 'Return to lifestyle modification only'], 'A',
    'Add ezetimibe (blocks intestinal cholesterol absorption) to the statin; if LDL is still above target, add a PCSK9 inhibitor. '
    'Niacin and fish oil do not reduce events here.',
    ['Familial hypercholesterolaemia', 'Ezetimibe'])
mcq('cad', 1, 60, FH, 'What is the mode of inheritance of this disorder?',
    ['Autosomal dominant', 'Autosomal recessive', 'X-linked recessive', 'Mitochondrial', 'Sporadic mutation'], 'A',
    'FH is autosomal dominant (LDLR, APOB or PCSK9 variants), so half of first-degree relatives are affected and cascade testing '
    'of the family is recommended.',
    ['Familial hypercholesterolaemia', 'Autosomal dominant inheritance'])

# --- chest trauma (Q5–8) -> pleura
TR = ('A 45-year-old man is brought to the emergency department after a car accident. There is bruising over the right chest with paradoxical '
      'movement of a segment of the right chest wall, reduced expansion and diminished breath sounds on the right. He is conscious but in '
      'respiratory distress; BP 95/60 mmHg, SpO2 86% on air.')
mcq('pleura', 1, 5, TR, 'What is the most likely diagnosis?',
    ['Tension pneumothorax', 'Flail chest', 'Massive haemothorax', 'Pulmonary contusion', 'Lung collapse'], 'B',
    'A segment moving paradoxically (in on inspiration) means two or more ribs broken in two or more places: a flail chest. '
    'Tension pneumothorax would shift the trachea and cause severe shock.',
    ['Flail chest', 'Chest trauma'])
mcq('pleura', 1, 6, TR, 'Which of the following is the main reason his lung function is compromised?',
    ['Hyperventilation due to pain', 'Underlying pulmonary contusion', 'Mediastinal shift', 'Air trapping during expiration', 'Diaphragmatic rupture'], 'B',
    'Hypoxaemia in flail chest comes mainly from the contused lung beneath the segment (alveolar haemorrhage and oedema), '
    'worsened by pain-limited breathing.',
    ['Flail chest', 'Pulmonary contusion'])
mcq('pleura', 1, 7, TR, 'Chest X-ray and CT show a massive haemothorax. What is the next immediate step?',
    ['Urgent thoracotomy', 'Endotracheal intubation and positive-pressure ventilation', 'Large-bore chest drain insertion',
     'Needle decompression in the second intercostal space', 'Observation and repeat chest X-ray in 6 hours'], 'C',
    'Resuscitate and insert a large-bore chest drain. Thoracotomy is needed if >1500 mL drains at once or >200 mL/h continues '
    'for 2–4 hours; needle decompression is for tension pneumothorax.',
    ['Haemothorax', 'Chest drain', 'Chest trauma'])
mcq('pleura', 1, 8, TR, 'His condition improves, but he remains hypoxic with persistent paradoxical chest movement despite oxygen and analgesia. What is the next definitive step?',
    ['Analgesia and oxygen only', 'Intubation with mechanical ventilation', 'Surgical fixation of the ribs', 'Repeat chest X-ray after 24 hours',
     'External strapping of the chest wall'], 'B',
    'Respiratory failure despite oxygen and analgesia needs intubation and positive-pressure ventilation, which splints the segment '
    'internally; rib fixation suits selected patients.',
    ['Flail chest', 'Mechanical ventilation', 'Respiratory failure'])

# --- COPD with cor pulmonale (Q48–52) -> airway
CP = ('A 62-year-old man has had progressive breathlessness and a productive cough for 8 years, with thick whitish sputum that is worst in the '
      'morning; his symptoms have recently worsened. He has a 40 pack-year smoking history. He is cyanosed with a raised JVP and bilateral pitting '
      'ankle oedema, and coarse crackles and rhonchi are heard over both lungs. RR 22/min, BP 145/85 mmHg; PaO2 55 mmHg, PaCO2 66 mmHg, '
      'haemoglobin 18 g/dL.')
mcq('airway', 1, 48, CP, 'What is the most likely diagnosis?',
    ['Bronchial asthma', 'COPD with cor pulmonale', 'Bronchiectasis', 'Interstitial lung disease', 'Idiopathic pulmonary fibrosis'], 'B',
    'Chronic bronchitis in a heavy smoker with hypoxaemia, hypercapnia, cyanosis, raised JVP and oedema is COPD complicated by '
    'cor pulmonale (right heart failure from hypoxic pulmonary vasoconstriction).',
    ['COPD', 'Cor pulmonale'])
mcq('airway', 1, 49, CP, 'What is the most important risk factor for this condition?',
    ['Cigarette smoking', 'Occupational silica exposure', 'Alpha-1 antitrypsin deficiency', 'Viral infection', 'Air pollution'], 'A',
    'Tobacco smoking causes most COPD and stopping is the single intervention that slows FEV1 decline. Alpha-1 antitrypsin deficiency '
    'explains early, basal emphysema in a minority.',
    ['COPD', 'Smoking'])
mcq('airway', 1, 50, CP, 'The raised haemoglobin is most likely due to:',
    ['Bone marrow malignancy', 'Infection', 'Secondary polycythaemia due to chronic hypoxia', 'Acute blood loss', 'Iron deficiency anaemia'], 'C',
    'Chronic hypoxaemia drives renal erythropoietin release, giving secondary polycythaemia; it raises viscosity and is reduced by '
    'long-term oxygen. Polycythaemia vera would have a low EPO.',
    ['Secondary polycythaemia', 'COPD'])
mcq('airway', 1, 51, CP, 'The raised JVP is most likely caused by:',
    ['Left-sided heart failure', 'Right-sided heart failure', 'Renal failure', 'Liver failure', 'Deep vein thrombosis'], 'B',
    'Hypoxic pulmonary vasoconstriction causes pulmonary hypertension and right ventricular failure (cor pulmonale), seen as a raised '
    'JVP, hepatomegaly and peripheral oedema.',
    ['Cor pulmonale', 'Right heart failure'])
q52 = mcq('airway', 1, 52, CP, 'What is the most appropriate long-term management for this patient?',
          ['Long-term corticosteroid therapy', 'Long-term antibiotic therapy', 'Long-term oxygen therapy (LTOT)', 'Intermittent nebulised bronchodilators',
           'Mucolytic therapy alone'], 'C',
          'LTOT for ≥15 h/day prolongs survival when PaO2 is <7.3 kPa (55 mmHg), or <8 kPa with oedema, polycythaemia or pulmonary '
          'hypertension, once he has stopped smoking.',
          ['Long-term oxygen therapy', 'COPD', 'Cor pulmonale'])

# --- severe pneumonia (Q73–75) -> resinf
PN = ('A 24-year-old man has fever and cough productive of sputum after a recent influenza-like illness. He is unwell but alert and orientated; '
      'BP 80/60 mmHg, RR 35/min, urea 55 mg/dL (9.2 mmol/L). Chest X-ray shows multilobar consolidation with several thin-walled pneumatoceles.')
mcq('resinf', 1, 73, PN, 'What is the most likely causative organism?',
    ['Staphylococcus aureus', 'Streptococcus pneumoniae', 'Klebsiella pneumoniae', 'Legionella pneumophila', 'Mycoplasma pneumoniae'], 'A',
    'Necrotising pneumonia with pneumatoceles after influenza is typical of S. aureus (including PVL strains). Pneumococcus is '
    'commoner overall but rarely cavitates.',
    ['Staphylococcal pneumonia', 'Pneumatoceles', 'Community-acquired pneumonia'])
mcq('resinf', 1, 74, PN, 'What is his CURB-65 score?',
    ['1', '2', '3', '4', '5'], 'C',
    'Urea >7 mmol/L (1), RR ≥30 (1) and SBP <90 mmHg (1) score; he is not confused and is under 65. CURB-65 = 3, high severity: '
    'admit and consider critical care.',
    ['CURB-65', 'Community-acquired pneumonia'])
mcq('resinf', 1, 75, PN, 'What is the best initial treatment?',
    ['Vancomycin plus ceftriaxone', 'Ceftriaxone plus azithromycin', 'Levofloxacin alone', 'Flucloxacillin alone', 'Doxycycline'], 'A',
    'Severe CAP needs a beta-lactam plus macrolide, but pneumatoceles after influenza suggest S. aureus, so add anti-MRSA cover '
    '(vancomycin or linezolid) until cultures return.',
    ['Staphylococcal pneumonia', 'Severe pneumonia', 'MRSA'],
    notes='Recalled stem: chest X-ray with pneumatoceles was given "in one version" of the paper.')

# --- lung cancer (Q76–79) -> lca
LC = ('An elderly man who is a heavy smoker has weight loss, haemoptysis, fatigue, constipation and thirst; he has diabetes mellitus. '
      'Chest X-ray shows a right hilar mass, and PET-CT shows no distant metastasis.')
mcq('lca', 1, 76, LC, 'What is the most likely type of lung cancer?',
    ['Adenocarcinoma', 'Small cell carcinoma', 'Large cell carcinoma', 'Carcinoid tumour', 'Squamous cell carcinoma'], 'E',
    'A central (hilar) tumour in a smoker with hypercalcaemia (thirst, constipation) is squamous cell carcinoma, which secretes PTH-related '
    'peptide. Small cell causes SIADH and ectopic ACTH instead.',
    ['Squamous cell carcinoma', 'Hypercalcaemia', 'Lung cancer'])
mcq('lca', 1, 77, LC, 'What is the most likely cause of his hypercalcaemia?',
    ['Bone metastases', 'Paraneoplastic secretion of PTH-related peptide', 'Primary hyperparathyroidism', 'Vitamin D toxicity',
     'Milk-alkali syndrome'], 'B',
    'With no metastases on PET, hypercalcaemia is humoral: PTHrP from the squamous tumour, with a suppressed PTH. Treat with IV '
    'saline then a bisphosphonate.',
    ['Hypercalcaemia of malignancy', 'PTH-related peptide', 'Paraneoplastic syndromes'])
mcq('lca', 1, 78, LC + ' Lung function tests show good pulmonary reserve.', 'What is the most appropriate management?',
    ['Chemotherapy', 'Radiotherapy', 'Surgical resection', 'Immunotherapy', 'Best supportive care'], 'C',
    'Non-metastatic non-small cell cancer in a patient fit for surgery (adequate FEV1/TLCO) is resected, usually by lobectomy with '
    'nodal sampling.',
    ['Non-small cell lung cancer', 'Lung cancer surgery'])
mcq('lca', 1, 79, LC + ' Lung function tests show good pulmonary reserve. One year later he develops contralateral chest pain; a pleural effusion '
    'is found and aspiration confirms malignant cells.', 'What is the best treatment to prevent recurrence of the effusion?',
    ['Pleurodesis', 'Systemic chemotherapy', 'Repeated therapeutic aspiration', 'Diuretics', 'Radiotherapy to the chest wall'], 'A',
    'A symptomatic recurrent malignant effusion is drained and then controlled by talc pleurodesis (or an indwelling pleural '
    'catheter if the lung is trapped). Repeated aspiration only buys days.',
    ['Malignant pleural effusion', 'Pleurodesis'])

# --- tuberculosis (Q88–89) -> resinf
mcq('resinf', 1, 88, 'A patient is suspected of having pulmonary tuberculosis.', 'How is the diagnosis confirmed?',
    ['Sputum acid-fast bacilli smear, culture and GeneXpert (NAAT)', 'Blood culture', 'Chest X-ray', 'Tuberculin skin test',
     'Interferon-gamma release assay'], 'A',
    'Sputum for AFB smear, culture and a rapid NAAT (GeneXpert, which also detects rifampicin resistance) confirms active TB. '
    'Skin tests and IGRAs show infection only.',
    ['Tuberculosis', 'Sputum smear', 'GeneXpert'])
mcq('resinf', 1, 89, '', 'Which antituberculous drug causes peripheral neuropathy and requires pyridoxine (vitamin B6) supplementation?',
    ['Isoniazid', 'Rifampicin', 'Ethambutol', 'Streptomycin', 'Pyrazinamide'], 'A',
    'Isoniazid depletes pyridoxine and causes peripheral neuropathy, so pyridoxine is co-prescribed. Ethambutol causes optic '
    'neuritis; pyrazinamide causes gout.',
    ['Isoniazid', 'Pyridoxine', 'Antituberculous drugs'])

# --- blood gases in COPD (Q93–94) -> crit
AB = ('A man with an exacerbation of COPD has shallow breathing at 10 breaths/min. Arterial blood gases: pH 7.31, PaCO2 70 mmHg (9.3 kPa), '
      'HCO3− 33 mmol/L (reference 22–26).')
mcq('crit', 1, 93, AB, 'What is the acid–base disturbance?',
    ['Respiratory acidosis', 'Respiratory alkalosis', 'Mixed metabolic and respiratory acidosis', 'Metabolic acidosis', 'Metabolic alkalosis'], 'A',
    'Low pH with high PaCO2 is respiratory acidosis from hypoventilation (type 2 failure). The raised bicarbonate matches chronic '
    'compensation, so it is not a separate metabolic disorder.',
    ['Respiratory acidosis', 'Type 2 respiratory failure', 'Arterial blood gases'])
mcq('crit', 1, 94, AB, 'What does the raised bicarbonate indicate?',
    ['No compensation', 'Renal (metabolic) compensation', 'Lactic acidosis', 'Hyperventilation', 'Laboratory error'], 'B',
    'Over days the kidneys retain bicarbonate (about 3.5 mmol/L per 10 mmHg rise in PaCO2), so the high HCO3− shows chronic CO2 '
    'retention with renal compensation.',
    ['Renal compensation', 'Chronic respiratory acidosis', 'Arterial blood gases'])

# ===================================================================== PAPER 2 — EMQs
emq('cvsemq', 2, 1, 'Lipid treatment',
    ['Atorvastatin', 'Ezetimibe', 'Fenofibrate', 'Nicotinic acid (niacin)', 'PCSK9 inhibitor (evolocumab)', 'Omega-3 fatty acids', 'Lifestyle modification'],
    [(1, 'A 45-year-old man with coronary artery disease still has a high LDL cholesterol despite taking a statin. What is the next treatment?', 'B',
      'With LDL above target on a maximally tolerated statin, add ezetimibe first; a PCSK9 inhibitor follows if LDL remains high.'),
     (2, 'A 30-year-old man has isolated hypertriglyceridaemia. Which drug acts by stimulating lipoprotein lipase?', 'C',
      'Fibrates activate PPAR-α, increasing lipoprotein lipase activity and lowering triglycerides by up to 50%.'),
     (3, 'A patient with hyperlipidaemia is started on a drug that inhibits HMG-CoA reductase and can lower LDL cholesterol by up to 60%.', 'A',
      'High-intensity statins (atorvastatin 40–80 mg) inhibit HMG-CoA reductase and cut LDL by about 50–60%.')],
    ['Lipid-lowering drugs', 'Statins', 'Fibrates'],
    notes='The paper listed both "nicotinic acid" and "niacin" (the same drug); the second was replaced by a PCSK9 inhibitor.')

emq('cvsemq', 2, 56, 'Cyanosis',
    ['Tetralogy of Fallot', 'Transposition of the great arteries', 'Bronchopneumonia', 'COPD', 'ARDS', 'Atrial septal defect',
     'Ventricular septal defect', 'Patent ductus arteriosus', 'Methaemoglobinaemia', 'Cold exposure', 'Pulmonary hypertension',
     'Total anomalous pulmonary venous return'],
    [(56, 'A 4-month-old infant has cyanosis and breathlessness. The chest X-ray shows a "boot-shaped" heart.', 'A',
      'A boot-shaped heart (upturned RV apex, concave pulmonary bay) with cyanosis in infancy is tetralogy of Fallot.'),
     (57, 'A 44-year-old patient has progressive breathlessness and central cyanosis. The ECG shows right ventricular hypertrophy and the chest X-ray shows enlarged pulmonary arteries.', 'K',
      'Progressive dyspnoea with RV hypertrophy and enlarged central pulmonary arteries is pulmonary hypertension; echo then right heart catheter.'),
     (58, 'A 60-year-old smoker has chronic cough, wheeze and cyanosis. The chest X-ray shows hyperinflated lungs.', 'D',
      'Chronic cough and wheeze in a smoker with hyperinflation is COPD; confirm with post-bronchodilator FEV1/FVC < 0.7.'),
     (59, 'A 30-year-old patient has a sudden fever, productive cough and cyanosis. The chest X-ray shows bilateral patchy infiltrates.', 'C',
      'Acute fever and cough with bilateral patchy shadowing is bronchopneumonia; ARDS needs a precipitant and refractory hypoxaemia.'),
     (60, 'A 6-year-old child has cyanosis. The chest X-ray shows a "snowman" (figure-of-eight) heart.', 'L',
      'The snowman heart is supracardiac total anomalous pulmonary venous return; TGA gives an "egg on a string".')],
    ['Cyanosis', 'Congenital heart disease', 'Chest X-ray signs'],
    notes='Recalled theme: the "snowman" scenario had no matching option in the recall, so total anomalous pulmonary venous return was added (L).')

emq('cvsemq', 2, 70, 'Limb ischaemia',
    ['Chronic atherosclerotic ischaemia', 'Acute limb ischaemia', 'Reperfusion injury', 'Leriche syndrome', 'Buerger disease', 'Aortic dissection'],
    [(70, 'A 65-year-old man with a mechanical mitral valve, receiving IV antibiotics for infective endocarditis, suddenly develops severe pain in his right leg while watching television. The leg is cold, pale and pulseless with loss of sensation below the knee; motor function is intact.', 'B',
      'Sudden cold, pale, pulseless leg from an embolus (vegetation or valve thrombus) is acute limb ischaemia; heparin and urgent embolectomy.'),
     (71, 'A man has bilateral buttock and thigh claudication, absent femoral pulses and erectile dysfunction.', 'D',
      'Aorto-iliac occlusion gives the Leriche triad: claudication, absent femoral pulses and impotence.'),
     (72, 'After an emergency embolectomy the patient develops increasing pain, swelling and a tense calf.', 'C',
      'Reperfusion causes oedema and compartment syndrome; measure compartment pressure and perform fasciotomy.'),
     (73, 'A 30-year-old male smoker develops ischaemia of the distal digits. He has previously had superficial thrombophlebitis.', 'E',
      'Distal ischaemia with migratory thrombophlebitis in a young male smoker is thromboangiitis obliterans; stop smoking completely.')],
    ['Limb ischaemia', 'Buerger disease', 'Leriche syndrome'])

emq('cvsemq', 2, 84, 'Cardiac emergencies',
    ['Aspirin 300 mg', 'Primary PCI', 'IV adenosine', 'Oxygen', 'IV low-molecular-weight heparin', 'Thrombolysis',
     'Synchronised DC cardioversion', 'Beta-blocker', 'Calcium-channel blocker', '100% oxygen', 'IV morphine'],
    [(84, 'A patient with an acute STEMI in a rural area can be taken for PCI within 90 minutes.', 'B',
      'Primary PCI is the reperfusion of choice when it can be delivered within 120 min of diagnosis (ideally <90 min).'),
     (85, 'A patient with an acute STEMI presents to you; the nearest hospital with PCI is 3 hours away. What is the best treatment?', 'F',
      'When PCI cannot be achieved within 120 min, give fibrinolysis (e.g. tenecteplase) within 10 min, then transfer for angiography.'),
     (86, 'A patient has palpitations; the ECG shows a regular narrow-complex tachycardia (SVT) and he is haemodynamically stable.', 'C',
      'Stable SVT: vagal manoeuvres first, then IV adenosine 6 mg, then 12 mg, as a rapid bolus.'),
     (87, 'A patient has an irregular tachycardia at 146/min with hypotension and chest pain.', 'G',
      'An unstable tachyarrhythmia (shock, ischaemia, syncope, heart failure) needs synchronised DC cardioversion under sedation.')],
    ['STEMI reperfusion', 'Supraventricular tachycardia', 'Cardioversion'],
    notes='Recalled stem for item 4 read "irregular pulse, unstable, HR 46"; with these options (no atropine or pacing) the intended rate is taken as 146/min.')

emq('cvsemq', 2, 88, 'Chest pain',
    ['ST-elevation myocardial infarction', 'Stable angina', 'Acute pericarditis', 'Tietze syndrome', 'Pneumothorax', 'Pulmonary embolism',
     'Herpes zoster', 'Prinzmetal (vasospastic) angina', 'Gastro-oesophageal reflux disease', 'Aortic dissection', 'Boerhaave syndrome'],
    [(88, 'A patient has typical central chest pain at rest radiating to the left arm.', 'A',
      'Ischaemic pain at rest radiating to the arm is an acute coronary syndrome; of these options it is STEMI, so get an ECG within 10 min.'),
     (89, 'A patient on long-term steroids has chest pain after meals and on lying down that is partly relieved by a proton-pump inhibitor.', 'I',
      'Postprandial, positional burning pain relieved by a PPI is gastro-oesophageal reflux, aggravated by steroids.'),
     (90, 'A patient has chest pain relieved by sitting forward; the ECG shows ST elevation with PR depression.', 'C',
      'Pleuritic pain eased by leaning forward with saddle ST elevation and PR depression is acute pericarditis: NSAID plus colchicine.'),
     (91, 'A 50-year-old woman has central chest pain at rest with ST elevation on the ECG that resolves spontaneously.', 'H',
      'Transient ST elevation with rest pain resolving spontaneously is coronary vasospasm (Prinzmetal); calcium-channel blockers and nitrates.'),
     (92, 'A patient has tearing chest pain radiating to the back.', 'J',
      'Tearing pain radiating to the back is aortic dissection; check both arms\' BP and arrange urgent CT aortography.')],
    ['Chest pain', 'Acute pericarditis', 'Prinzmetal angina'],
    notes='Option A (STEMI) was missing from the extracted list and was restored from the source page.')

emq('resemq', 2, 102, 'Management of cough',
    ['Inhaled corticosteroid', 'Short-acting beta2-agonist', 'Long-acting beta2-agonist', 'Proton-pump inhibitor', 'Antihistamine plus decongestant',
     'Antituberculous therapy', 'Stop the current medication', 'Reduce exposure', 'Loop diuretic', 'Anticoagulant', 'Antibiotics', 'Antifibrotic therapy'],
    [(102, 'A 68-year-old diabetic smoker has chronic productive cough and progressive breathlessness; spirometry shows persistent airflow limitation. He takes empagliflozin and metformin.', 'C',
      'COPD: stop smoking, then a long-acting bronchodilator (LABA, with a LAMA); his diabetes drugs do not cause cough.'),
     (103, 'A 22-year-old woman has a chronic dry cough that is worse at night with occasional wheeze; the chest X-ray is normal and spirometry shows reversible obstruction.', 'A',
      'Nocturnal cough with reversible obstruction is asthma; treatment is based on inhaled corticosteroid (ICS–formoterol per GINA).'),
     (104, 'A 45-year-old man taking steroids for glomerulonephritis has a chronic cough that is worse after meals and on lying flat; chest examination is normal.', 'D',
      'Cough after meals and when lying flat suggests reflux, made worse by steroids: give a trial of a proton-pump inhibitor.'),
     (105, 'A 52-year-old has a chronic cough with a sensation of postnasal drip and frequent throat clearing, especially at night.', 'E',
      'Upper-airway cough syndrome (postnasal drip) is treated with an antihistamine–decongestant or intranasal steroid.'),
     (106, 'A 60-year-old hypertensive man taking ramipril has had a dry cough for 4 weeks.', 'G',
      'ACE-inhibitor cough (bradykinin) settles after stopping ramipril; switch to an ARB.'),
     (107, 'A 40-year-old woman has a chronic cough with night sweats, weight loss and haemoptysis.', 'F',
      'Night sweats, weight loss and haemoptysis suggest pulmonary TB: confirm on sputum, then 6 months of RIPE therapy.'),
     (108, 'A 65-year-old man has a dry cough and exertional breathlessness with fine inspiratory crackles and finger clubbing.', 'L',
      'Dry cough, Velcro crackles and clubbing suggest IPF; after HRCT confirmation, give an antifibrotic (pirfenidone or nintedanib).'),
     (109, 'A 58-year-old man who works in a cement factory has a chronic cough; the chest X-ray shows diffuse nodular opacities.', 'H',
      'Dust-related pneumoconiosis (e.g. silicosis) has no specific drug treatment; remove him from exposure.'),
     (110, 'A 50-year-old woman has acute fever, cough with purulent sputum, pleuritic chest pain and bronchial breathing.', 'K',
      'Lobar pneumonia: assess CURB-65 and start antibiotics (amoxicillin for low severity).'),
     (111, 'A 72-year-old woman coughs when lying flat and has frothy sputum, bilateral basal crackles and ankle swelling.', 'I',
      'Orthopnoea, frothy sputum, basal crackles and oedema mean heart failure: give a loop diuretic.')],
    ['Chronic cough', 'Cough management', 'Asthma', 'COPD'])

# ===================================================================== repeats
# P1 Q52 (LTOT in COPD with cor pulmonale) repeats airway-0004, an earlier local (39 Blocks) question: keep airway-0004.
OUT.append(dict(id=q52, delete=True, dup_of='airway-0004', why='Same idea as airway-0004 (LTOT for hypoxaemic COPD with cor pulmonale); 39 Blocks comes first'))
# Crash Course peri-0070 (MVP + dental extraction -> viridans streptococci) repeats P1 Q26, which comes earlier in the chapter.
OUT.append(dict(id='peri-0070', delete=True, dup_of=q26, why='Same idea as 39th batch Paper 1 Q26 (endocarditis after dental extraction = viridans streptococci); local source first'))

if __name__ == '__main__':
    p = os.path.join(ROOT, 'data', 'patches', '303-39-batch-papers.json')
    json.dump(OUT, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    n_m = sum(1 for o in OUT if 'new' in o and o['new']['type'] == 'MCQ')
    n_e = sum(len(o['new']['items']) for o in OUT if 'new' in o and o['new']['type'] == 'EMQ')
    print(p, 'MCQ', n_m, 'EMQ items', n_e, 'ops', len(OUT))
