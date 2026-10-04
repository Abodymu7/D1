"""39th batch surgery exams — Surgery_Question_Bank.html (178 recalled items, no answer key supplied).
Files: Paper 1, Paper 2 (final), Surgery 1 Block 2, Surgery 1 Block 3, End-induction GS1 (Block A).
Keys are set and explained here; recall gaps (blank options) are completed with plausible distractors;
short-answer (OSCE task) items are recast as single-best-answer MCQs; the 8 unlabelled radiology images become image MCQs.
Group C/D task questions that repeat Group A/B ones are kept as deleted duplicates (they feed the 'repeated' note).

  python data/import/b39_surg_src.py   -> data/patches/400-39-batch-surgery.json
"""
import json, os, re, collections

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
BANK = '39th Batch Exams'
OUT = []
Q = json.load(open(os.path.join(ROOT, 'data', 'questions.json'), encoding='utf-8'))
NEXT = collections.Counter()
for q in Q:
    m = re.match(r'(\w+)-(\d+)$', q['id'])
    NEXT[m.group(1)] = max(NEXT[m.group(1)], int(m.group(2)))

PAPER = {'P1': ('Paper 1', 1), 'P2': ('Paper 2', 2), 'B2': ('Block 2', 3), 'B3': ('Block 3', 4), 'BA': ('End-induction Block A', 5)}


def nid(ch):
    NEXT[ch] += 1
    return '%s-%04d' % (ch, NEXT[ch])


def mcq(ch, src, num, case, q, options, answer, ex, topics=(), images=(), dup_of=None):
    label, k = PAPER[src]
    stem = (case.strip() + ' ' + q.strip()).strip() if case else q.strip()
    if isinstance(num, str):   # T = OSCE task (short answer recast), R = radiology image
        order = k * 1000 + (500 if num[0] == 'T' else 700) + int(num[1:])
        where = '39th batch %s %s %s' % (label, 'task' if num[0] == 'T' else 'radiology', num[1:])
    else:
        order, where = k * 1000 + num, '39th batch %s Q%s' % (label, num)
    rec = dict(id=nid(ch), chapter=ch, order=order, type='MCQ', bank=BANK, source=where,
               status='new', topics=list(topics), notes='', stem=stem, options=options, answer=answer, explanation=ex,
               images=['q/b39-%s.jpg' % i for i in images], src=dict(file='39-surgery', paper=label, num=num))
    if dup_of:
        rec.update(status='deleted', dup_of=dup_of)
    OUT.append(dict(new=rec, why='Added from 39th batch %s (recalled exam)' % label))
    return rec['id']


def emq(ch, src, theme, options, items, topics=()):
    label, k = PAPER[src]
    its = [dict(n=i + 1, stem=s, answer=a, explanation=e, images=[], src_num=n) for i, (n, s, a, e) in enumerate(items)]
    rec = dict(id=nid(ch), chapter=ch, order=k * 1000 + items[0][0], type='EMQ', bank=BANK,
               source='39th batch %s Q%s–%s' % (label, items[0][0], items[-1][0]), status='new', topics=list(topics), notes='',
               theme=theme, options=options, option_letters=[chr(65 + i) for i in range(len(options))], items=its,
               stem='', answer='', explanation='', images=[], src=dict(file='39-surgery', paper=label))
    OUT.append(dict(new=rec, why='Added from 39th batch %s (recalled exam)' % label))
    return rec['id']


# ============================================================ BREAST
C = ('A 28-year-old woman, a smoker with five children (all breast-fed), has had bloody nipple discharge from the right breast for 6 months. '
     'At times the area swells with a foul-smelling discharge; antibiotics did not help.')
mcq('bbreast', 'P1', 53, C, 'Tests show mildly dilated multiple lactiferous ducts. What is the management?',
    ['Lumpectomy', 'Simple mastectomy', 'Modified radical mastectomy', 'Reassurance, smoking cessation and follow-up', 'Drainage and antibiotics'], 'D',
    'Duct ectasia/periductal mastitis is benign: reassure, stop smoking and follow up; total duct excision only for persistent discharge or recurrent sepsis.',
    ['Duct ectasia'])
mcq('bbreast', 'P1', 54, C, 'Which of the following is NOT useful in investigating her condition?',
    ['Bilateral breast examination', 'Mammography', 'Breast MRI', 'Breast ultrasound', 'Cytology of the discharge'], 'C',
    'Triple assessment (examination, ultrasound/mammography, cytology) suffices; MRI adds nothing in benign duct ectasia.', ['Nipple discharge'])
mcq('bbreast', 'P1', 55, C, 'What is the diagnosis?',
    ['Duct ectasia', 'Ductal carcinoma', 'Lobular carcinoma', 'Breast abscess', 'Fibroadenoma'], 'A',
    'Smoking, multiparity and multiple dilated ducts with discharge and recurrent periareolar inflammation are typical of duct ectasia/periductal mastitis.',
    ['Duct ectasia'])
C = ('A 55-year-old woman has a 3-month painless lump in the upper outer quadrant of the left breast and nipple retraction for 2 weeks. '
     'Core biopsy of a palpable axillary node shows invasive carcinoma, hormone-receptor negative; PET shows no metastasis.')
mcq('bca', 'P1', 71, C, 'What is the best next step in management?',
    ['Wide local excision', 'Simple mastectomy', 'Modified radical mastectomy', 'Adjuvant chemotherapy', 'Radiotherapy'], 'C',
    'Node-positive cancer with nipple involvement needs mastectomy with axillary clearance; neoadjuvant chemotherapy is often given first for ER-negative disease.',
    ['Breast cancer'])
mcq('bca', 'P1', 72, '8 months after her surgery she has difficulty raising her arm and her medial scapula is prominent.',
    'What is the cause?', ['Frozen shoulder', 'Serratus anterior denervation', 'Tear of the long head of biceps', 'Supraspinatus tendon injury',
                          'Thoracodorsal nerve injury'], 'B',
    'Winging of the scapula follows injury to the long thoracic nerve (serratus anterior) during axillary dissection; thoracodorsal injury weakens latissimus dorsi.',
    ['Axillary clearance'])

# ============================================================ GIT
C = ('An elderly man with previous bloody stools and lower abdominal pain has a sudden attack of left iliac fossa pain with fever. '
     'Ultrasound shows thickening of the sigmoid colon.')
mcq('intest', 'P1', 102, C, 'What is the most likely diagnosis?',
    ['Diverticulitis', 'Ischaemic colitis', 'Sigmoid carcinoma', 'Crohn disease', 'Appendicitis'], 'A',
    'LIF pain, fever and sigmoid wall thickening in an older patient is acute diverticulitis.', ['Diverticulitis'])
mcq('intest', 'P1', 103, C, 'What is the best investigation now?',
    ['Colonoscopy', 'Barium enema', 'Contrast-enhanced CT', 'Plain abdominal X-ray', 'MRI'], 'C',
    'Contrast CT confirms diverticulitis and shows abscess or perforation; colonoscopy and barium enema are avoided acutely (perforation risk).',
    ['Diverticulitis'])
mcq('intest', 'P1', 104, C, 'What is the treatment?',
    ['Colostomy', 'Sigmoid colectomy', 'Bowel rest and antibiotics', 'Percutaneous drainage', 'Laparoscopic lavage'], 'C',
    'Uncomplicated diverticulitis is treated conservatively (bowel rest, fluids, antibiotics if systemically unwell); drainage is for abscess > 4 cm.',
    ['Diverticulitis'])
PER = ['Rubber band ligation', 'Stapled haemorrhoidopexy', 'Open (excisional) haemorrhoidectomy', 'Topical calcium channel blocker',
       'Botulinum toxin injection', 'Fistulotomy', 'Incision and drainage', 'Lateral internal sphincterotomy', 'Seton placement']
emq('gitemq', 'P2', 'Treatment of perianal disorders', PER, [
    (15, 'A woman with an anal fissure in whom conservative management has failed.', 'E',
     'After failed topical therapy, botulinum toxin is preferred in women (obstetric sphincter risk); lateral sphincterotomy is used in men or if Botox fails.'),
    (16, 'A patient with prolapsed haemorrhoids that need manual reduction or remain prolapsed.', 'C',
     'Grade III–IV haemorrhoids are treated by excisional haemorrhoidectomy; stapled haemorrhoidopexy is an alternative for grade III.'),
    (17, 'A man with fever and a fluctuant perianal mass.', 'G', 'A perianal abscess needs incision and drainage.'),
    (18, 'A man with Crohn disease and a low fistula-in-ano.', 'I',
     'Perianal Crohn fistulas are managed with a loose draining seton plus medical therapy to avoid incontinence and non-healing wounds.'),
    (19, 'A woman with painless haemorrhoids that prolapse on defecation and reduce spontaneously.', 'A',
     'Grade II haemorrhoids are treated by rubber band ligation.')], ['Haemorrhoids', 'Anal fissure'])
GIB = ['Peptic ulcer disease', 'Mallory–Weiss tear', 'Oesophageal varices', 'Gastric cancer', 'Dieulafoy lesion', 'Angiodysplasia',
       'Erosive gastritis', 'Aortoenteric fistula', 'Gastric antral vascular ectasia (watermelon stomach)']
emq('gitemq', 'BA', 'Upper gastrointestinal bleeding', GIB, [
    (11, 'A 52-year-old man with alcoholic cirrhosis has massive haematemesis and hypotension. He has spider naevi and ascites.', 'C',
     'Massive haematemesis with stigmata of chronic liver disease is bleeding oesophageal varices.'),
    (12, 'A 35-year-old man vomits blood-streaked material after several bouts of forceful retching following heavy drinking. He is stable and the bleeding stops spontaneously.', 'B',
     'Haematemesis after forceful retching that settles spontaneously is a Mallory–Weiss tear.'),
    (13, 'A 68-year-old man taking NSAIDs for osteoarthritis has melaena and anaemia. He is otherwise healthy.', 'A',
     'NSAID use with melaena and anaemia is a bleeding peptic ulcer.'),
    (14, 'A 65-year-old woman has fatigue and pallor and has neglected tarry stools for a year. There is a hard, non-tender lump above the left clavicle.', 'D',
     'Chronic melaena with a left supraclavicular (Virchow) node is gastric cancer.')], ['Upper GI bleeding'])
C = ('An elderly woman in a care home who takes antipsychotics and has chronic constipation presents with a distended, painless, non-tender abdomen. '
     'X-ray shows a hugely dilated sigmoid loop reaching the upper abdomen.')
mcq('intest', 'B2', 1, C, 'What is the diagnosis?',
    ['Sigmoid volvulus', 'Diverticular disease', 'Obstructing sigmoid tumour', 'Acute colonic pseudo-obstruction', 'Toxic megacolon'], 'A',
    'A huge sigmoid loop rising from the pelvis (coffee-bean sign) in an elderly, constipated, institutionalised patient is sigmoid volvulus.',
    ['Sigmoid volvulus'])
mcq('intest', 'B2', 2, C, 'Which procedure is both diagnostic and therapeutic?',
    ['Endoscopic (flexible sigmoidoscopic) decompression', 'Barium enema', 'CT abdomen', 'Laparotomy', 'Rectal tube without endoscopy'], 'A',
    'Flexible sigmoidoscopy confirms the twist, checks viability and decompresses with a flatus tube; elective sigmoid colectomy follows to prevent recurrence.',
    ['Sigmoid volvulus'])
mcq('intest', 'B2', 3, C, 'At surgery the descending and sigmoid colon are resected. Which artery is ligated?',
    ['Ileocolic', 'Superior mesenteric', 'Inferior mesenteric', 'Middle colic', 'Coeliac trunk'], 'C',
    'The descending and sigmoid colon are supplied by the inferior mesenteric artery (left colic and sigmoid branches).', ['Colonic blood supply'])
C = ('A 21-year-old man has incapacitating perianal pain for 3 days despite local ointment. There is a tender, fluctuant right perianal swelling '
     'with overlying erythema.')
mcq('anus', 'BA', 9, C, 'What is the most likely diagnosis?',
    ['Perianal abscess', 'Perianal haematoma', 'Pilonidal abscess', 'Strangulated piles', 'Fournier gangrene'], 'A',
    'A tender, fluctuant, erythematous swelling beside the anus is a perianal abscess.', ['Perianal abscess'])
mcq('anus', 'BA', 10, C, 'What is the best treatment now?',
    ['Antibiotics', 'Incision and drainage', 'Excision and primary repair', 'Haemorrhoidectomy', 'Local debridement'], 'B',
    'An abscess needs prompt incision and drainage; antibiotics alone are inadequate.', ['Perianal abscess'])
C = ('A 55-year-old man has had intermittent dysphagia for solids and liquids with central chest pain for 4 months. ECG and troponin are normal; '
     'sublingual nitrates relieve the pain.')
mcq('oeso', 'B3', 1, C, 'What is the diagnosis?',
    ['Achalasia', 'Diffuse oesophageal spasm', 'Oesophageal carcinoma', 'Plummer–Vinson syndrome', 'Gastro-oesophageal reflux disease'], 'B',
    'Intermittent dysphagia for solids and liquids with chest pain relieved by nitrates is diffuse oesophageal spasm (corkscrew oesophagus on barium).',
    ['Oesophageal dysmotility'])
mcq('oeso', 'B3', 2, C, 'Which investigation confirms the diagnosis?',
    ['Oesophageal manometry', 'Upper GI endoscopy', 'CT chest', 'Ultrasound', 'Laparotomy'], 'A',
    'High-resolution manometry shows premature simultaneous contractions; endoscopy is done first to exclude obstruction.', ['Oesophageal dysmotility'])
mcq('oeso', 'B3', 3, C, 'What is the best management now?',
    ['Calcium channel blocker', 'Peroral endoscopic myotomy (POEM)', 'Heller myotomy', 'Oesophagectomy', 'Proton-pump inhibitor alone'], 'A',
    'Oesophageal spasm is treated medically first (calcium channel blockers or nitrates); POEM is reserved for refractory cases.', ['Oesophageal dysmotility'])

# ============================================================ PAEDIATRIC
INF = ['Hirschsprung disease', 'Malrotation with midgut volvulus', 'Infantile hypertrophic pyloric stenosis', 'Meconium ileus', 'Duodenal atresia',
       'Jejunoileal atresia', 'Necrotising enterocolitis', 'Intussusception']
emq('paedemq', 'P2', 'The vomiting neonate and infant', INF, [
    (80, 'A 2-day-old infant with Down syndrome has projectile vomiting and a scaphoid abdomen. X-ray shows a double-bubble sign with no distal bowel gas.', 'E',
     'Double bubble without distal gas in a baby with Down syndrome is duodenal atresia (vomiting is usually bilious if post-ampullary).'),
    (81, 'A 2-week-old infant born at 28 weeks, in the NICU, develops sudden abdominal distension and bloody stool. X-ray shows gas in the bowel wall.', 'G',
     'Pneumatosis intestinalis with distension and bloody stool in a preterm neonate is necrotising enterocolitis.'),
    (82, 'A full-term 2-day-old has not passed meconium, vomits bile and is distended. Rectal examination produces an explosive release of gas and liquid stool.', 'A',
     'Delayed meconium with an explosive decompression on rectal examination is Hirschsprung disease; rectal suction biopsy confirms it.'),
    (83, 'A 5-day-old who was feeding well suddenly has bilious vomiting, tenderness and haemodynamic instability. Contrast shows the duodenojejunal flexure right of the spine with a corkscrew duodenum.', 'B',
     'Bilious vomiting with an abnormally placed DJ flexure and corkscrew duodenum is malrotation with midgut volvulus: emergency Ladd procedure.')],
    ['Neonatal intestinal obstruction'])
C = 'An 18-month-old child, born at 34 weeks, has had a groin lump for 1 week that enlarges on coughing and disappears spontaneously.'
mcq('paed', 'P1', 12, C, 'What is the most likely diagnosis?',
    ['Direct inguinal hernia', 'Indirect inguinal hernia', 'Femoral hernia', 'Hydrocele', 'Inguinal lymphadenopathy'], 'B',
    'Paediatric inguinal hernias are almost always indirect, through a patent processus vaginalis; prematurity increases the risk.', ['Paediatric hernia'])
mcq('paed', 'P1', 13, C, 'What is the best investigation?',
    ['Clinical examination', 'Abdominal ultrasound', 'Doppler ultrasound', 'CT abdomen', 'MRI'], 'A',
    'The diagnosis is clinical (history of a reducible lump with cough impulse); imaging is not needed.', ['Paediatric hernia'])
mcq('paed', 'P1', 14, C, 'What is the treatment?',
    ['Herniotomy', 'Mesh repair', 'Wait until 4 years of age', 'Hernioplasty', 'Hydrocelectomy'], 'A',
    'Herniotomy (high ligation of the sac) is done soon after diagnosis because of the high incarceration risk; mesh is not used in children.',
    ['Paediatric hernia'])
C = 'A baby a few months old has feeding difficulty, with milk coming out of the nose during feeds, coughing and choking. There is no excessive salivation.'
mcq('paed', 'P1', 90, C, 'What is the most likely diagnosis?',
    ['Cleft palate', 'Tracheo-oesophageal fistula', 'Gastro-oesophageal reflux disease', 'Choanal atresia', 'Laryngomalacia'], 'A',
    'Nasal regurgitation of milk without drooling suggests a cleft (often submucous) palate; TOF presents at birth with excessive salivation.',
    ['Cleft palate'])
mcq('paed', 'P1', 91, C, 'What is the optimal time of repair?',
    ['At birth', '1–3 months', '6–18 months', '3 years', '7 years'], 'C',
    'Cleft palate is repaired at about 6–12 months, before speech develops; cleft lip at about 3 months.', ['Cleft palate'])
mcq('paed', 'P1', 92, C, 'Which is NOT a complication of this condition?',
    ['Feeding difficulty', 'Speech difficulty', 'Recurrent otitis media', 'Recurrent chest infection', 'Oesophageal stricture'], 'E',
    'Cleft palate causes feeding and speech problems, otitis media (Eustachian dysfunction) and aspiration; it does not cause oesophageal stricture.',
    ['Cleft palate'])
C = ('An 18-hour-old girl born by spontaneous vaginal delivery has an imperforate anus with a rectovestibular fistula. She weighs 2750 g, '
     'looks healthy and has no associated defects.')
mcq('paed', 'BA', 1, C, 'Initial management includes all of the following EXCEPT:',
    ['IV fluids', 'IV antibiotics', 'Incubator care', 'Search for associated congenital anomalies (VACTERL)', 'Immediate surgery'], 'E',
    'First 24 h: fluids, antibiotics, NG decompression and VACTERL screening; surgery is planned once the anatomy and associated anomalies are known.',
    ['Anorectal malformation'])
mcq('paed', 'BA', 2, C, 'What is the most appropriate operation?',
    ['Diverting colostomy', 'Diverting ileostomy', 'Single-stage posterior sagittal anorectoplasty', 'Swenson pull-through',
     'Heineke–Mikulicz pyloroplasty'], 'C',
    'A healthy girl with a vestibular fistula can have a primary single-stage PSARP; a colostomy is reserved for sick babies or high defects.',
    ['Anorectal malformation'])
C = 'A 12-hour-old boy has an imperforate anus with an absent anal dimple and is passing meconium in his urine.'
mcq('paed', 'B2', 1, C, 'What is the next step?',
    ['Cross-table prone lateral X-ray', 'Plain abdominal X-ray', 'Wait until 24 hours', 'Diverting colostomy', 'Immediate PSARP'], 'D',
    'Meconium in the urine means a rectourinary fistula (high lesion), so a diverting colostomy is done; imaging and waiting 24 h are for unclear cases.',
    ['Anorectal malformation'])
mcq('paed', 'B2', 2, C, 'How is the type of imperforate anus defined before definitive repair?',
    ['High-pressure distal colostogram', 'Invertogram', 'Abdominal ultrasound', 'MRI spine', 'Contrast enema via the perineum'], 'A',
    'A high-pressure distal colostogram through the mucous fistula shows the rectal level and the fistula to the urinary tract.',
    ['Anorectal malformation'])
C = '4-month-old boy with effortless (sometimes forceful) non-bilious vomiting, fever to 39.5 °C and 4–6 green diarrhoeal stools a day.'
mcq('paed', 'B3', 1, 'A ' + C, 'All of the following are useful EXCEPT:',
    ['Full blood count', 'Abdominal X-ray', 'Ultrasound', 'Barium follow-through', 'Stool examination'], 'D',
    'Fever with vomiting and diarrhoea suggests gastroenteritis; FBC, stool tests and ultrasound help, but barium follow-through has no role.',
    ['Infant vomiting'])
mcq('paed', 'B3', 2, 'A ' + C, 'What is the diagnosis?',
    ['Pyloric stenosis', 'Viral gastroenteritis', 'Pyloric atresia', 'Oesophageal atresia', 'Mesenteric lymphadenitis'], 'B',
    'Fever, vomiting and diarrhoea point to infective (viral) gastroenteritis; pyloric stenosis causes vomiting without fever or diarrhoea.',
    ['Infant vomiting'])
mcq('paed', 'B3', 3, 'A ' + C, 'What is the management?',
    ['Watch and wait', 'Antibiotics', 'Supportive treatment (rehydration and symptom relief)', 'Pyloromyotomy', 'Laparotomy'], 'C',
    'Viral gastroenteritis is managed supportively with oral or IV rehydration; antibiotics and surgery have no role.', ['Infant vomiting'])

# ============================================================ ABDOMEN
C = ('A man has jaundice, weight loss and a cholestatic pattern (raised ALP and GGT). Ultrasound shows dilated intrahepatic ducts, '
     'a collapsed gallbladder and a normal pancreas.')
mcq('gb', 'P1', 15, C, 'What is the most likely diagnosis?',
    ['Perihilar cholangiocarcinoma', 'Pancreatic carcinoma', 'Periampullary cholangiocarcinoma', 'Hepatocellular carcinoma', 'Acute pancreatitis'], 'A',
    'Dilated intrahepatic ducts with a collapsed gallbladder put the block above the cystic duct: hilar (Klatskin) cholangiocarcinoma.',
    ['Cholangiocarcinoma'])
mcq('gb', 'P1', 16, C, 'Which tumour marker is associated?', ['AFP', 'CEA', 'CA 19-9', 'CA 125', 'PSA'], 'C',
    'CA 19-9 is the marker for cholangiocarcinoma and pancreatic cancer (it is also raised by cholestasis itself).', ['Cholangiocarcinoma'])
mcq('gb', 'P1', 17, C, 'What causes the itching?', ['Bile salts', 'Bilirubin', 'Urea', 'Histamine', 'Ammonia'], 'A',
    'Pruritus in obstructive jaundice is due to retained bile salts (and other pruritogens) in the skin, not bilirubin.', ['Obstructive jaundice'])
mcq('gb', 'P1', 18, C, 'What is the best non-invasive investigation for diagnosis?',
    ['ERCP', 'CT scan', 'MRCP', 'HIDA scan', 'Plain abdominal X-ray'], 'C',
    'MRCP maps the biliary tree non-invasively and defines the level and extent of a hilar stricture before any drainage.', ['Cholangiocarcinoma'])
mcq('gb', 'P1', 19, C, 'The patient remains jaundiced after two ERCP attempts. What is the next step?',
    ['Laparoscopic bypass', 'Percutaneous transhepatic cholangiography and drainage', 'Repeat ERCP', 'Liver transplantation', 'Observation'], 'B',
    'Hilar strictures that fail endoscopic stenting are drained percutaneously (PTC/PTBD).', ['Cholangiocarcinoma'])
C = ('A man has fever, malaise and tender hepatomegaly after diarrhoea following travel to Nasiriyah. Ultrasound shows a 7-cm cystic liver lesion; '
     'blood cultures are negative.')
mcq('liver', 'P1', 98, C, 'What is the most likely organism?',
    ['Entamoeba histolytica', 'Shigella', 'Echinococcus granulosus', 'Staphylococcus aureus', 'Escherichia coli'], 'A',
    'Fever, tender hepatomegaly and a liver abscess after dysentery with sterile blood cultures is an amoebic liver abscess.', ['Amoebic liver abscess'])
mcq('liver', 'P1', 99, C, 'How did the organism reach the liver?',
    ['Direct spread from an empyema', 'Haematogenous spread via the hepatic artery', 'Via the portal vein from the colon', 'Ascending infection via the bile duct',
     'Lymphatic spread'], 'C',
    'Trophozoites invade the colonic mucosa and travel in the portal venous blood to the liver (usually the right lobe).', ['Amoebic liver abscess'])
mcq('liver', 'P1', 100, C, 'He receives a second-generation cephalosporin and metronidazole, and the cyst is aspirated. What does the aspirate show?',
    ['Anchovy-sauce (paste) fluid', 'Clear hydatid fluid', 'Foul-smelling yellow pus', 'Blood-stained bile', 'Chylous fluid'], 'A',
    'Amoebic abscess fluid is odourless, reddish-brown "anchovy sauce" (liquefied liver); pyogenic abscesses contain yellow pus.', ['Amoebic liver abscess'])
mcq('liver', 'P1', 101, C, 'Which additional treatment is essential?',
    ['Diloxanide furoate', 'Long-term metronidazole', 'Praziquantel', 'Albendazole', 'Surgical drainage'], 'A',
    'After metronidazole, a luminal amoebicide (diloxanide furoate or paromomycin) is needed to clear intestinal cysts and prevent relapse.',
    ['Amoebic liver abscess'])
PAN = ['Acute pancreatitis', 'Chronic pancreatitis', 'Carcinoma of the pancreas', 'Intraductal papillary mucinous neoplasm', 'Gastrinoma', 'Somatostatinoma',
       'Glucagonoma', 'Ampullary tumour', 'Pancreatic pseudocyst', 'Pancreatic hydatid cyst', 'Insulinoma']
emq('abdemq', 'P2', 'Pancreatic disorders', PAN, [
    (45, 'A 50-year-old with vague abdominal pain has been treated for multiple gastric and duodenal ulcers.', 'E',
     'Multiple or recurrent peptic ulcers suggest Zollinger–Ellison syndrome from a gastrinoma.'),
    (46, 'A patient has recurrent episodes of loss of consciousness, sweating and dizziness, and eats large amounts of food.', 'K',
     'Fasting hypoglycaemia relieved by eating (Whipple triad) with weight gain is an insulinoma.'),
    (47, 'A patient has chronic malnutrition and says food always passes completely undigested.', 'B',
     'Steatorrhoea and maldigestion are exocrine failure from chronic pancreatitis.'),
    (48, 'A patient with a previously treated liver hydatid cyst has upper abdominal pain; imaging shows an additional cyst in the pancreas.', 'J',
     'A pancreatic cyst in a patient with liver hydatid disease is a pancreatic hydatid cyst.'),
    (49, 'A patient with gallstones for 10 years has recurrent upper abdominal pain and maldigestion.', 'B',
     'Recurrent attacks of gallstone pancreatitis can progress to chronic pancreatitis with exocrine insufficiency.'),
    (50, 'A patient has upper abdominal pain and fever. CT shows a markedly dilated main pancreatic duct with a filling defect.', 'D',
     'A markedly dilated main duct with filling defects (mucin) is a main-duct IPMN; it has high malignant potential and needs resection.')],
    ['Pancreatic tumours'])
C = 'A young woman has recurrent palpitations, headache and sweating. Her BP is 185 mmHg systolic despite a calcium channel blocker, an ACE inhibitor and a diuretic.'
mcq('adrenal', 'P1', 61, C, 'What is the most likely diagnosis?',
    ['Phaeochromocytoma', 'Conn syndrome', 'Hyperthyroidism', 'Renal artery stenosis', 'Cushing syndrome'], 'A',
    'Paroxysms of headache, palpitations and sweating with resistant hypertension is phaeochromocytoma.', ['Phaeochromocytoma'])
mcq('adrenal', 'P1', 62, C, 'Which test confirms the diagnosis?',
    ['Plasma free metanephrines', 'Thyroid function tests', 'Plasma renin', 'Overnight dexamethasone suppression test', 'Serum calcium'], 'A',
    'Plasma free (or 24-h urinary fractionated) metanephrines are the biochemical test; imaging (CT/MRI) follows.', ['Phaeochromocytoma'])
mcq('adrenal', 'P1', 63, C, 'Which drug should NOT be used (first) in this condition?',
    ['Labetalol', 'Metoprolol', 'Prazosin', 'Sodium nitroprusside', 'Hydralazine'], 'B',
    'A beta-blocker alone before alpha-blockade leaves alpha stimulation unopposed and can cause a hypertensive crisis; alpha-block first.',
    ['Phaeochromocytoma'])
RAD = ['Abdominal ultrasound', 'Intravenous urography (IVU)', 'Dynamic (triphasic) CT', 'Endoscopic ultrasound', 'Barium swallow', 'Barium meal',
       'Barium (contrast) enema', 'Barium follow-through']
emq('abdemq', 'P2', 'Surgical imaging', RAD, [
    (25, 'A child has bile-stained vomiting. What is the best initial imaging?', 'F',
     'Bilious vomiting needs an urgent upper GI contrast study to show the DJ flexure and exclude malrotation with volvulus.'),
    (26, 'A patient has a hydroureter but no stone is seen. Which study is best for diagnosis?', 'B',
     'Urography (IVU, or CT urography today) shows the level and cause of ureteric obstruction such as a stricture or filling defect.'),
    (27, 'A patient has rectal bleeding, weight loss and a rectal mass on DRE. Which test best shows the depth of invasion?', 'D',
     'Endorectal ultrasound (or pelvic MRI) gives local T staging of rectal cancer.'),
    (28, 'A 36-year-old woman has a 6-cm solitary liver mass found on an infertility ultrasound.', 'C',
     'A solid liver lesion is characterised by multiphase (triphasic) contrast CT or MRI.'),
    (29, 'A 2-month-old has episodes of crying, an empty right iliac fossa and a sausage-shaped mass. Which test is diagnostic and therapeutic?', 'G',
     'Intussusception is confirmed on ultrasound and reduced by air or contrast enema (diagnostic and therapeutic).')], ['Surgical imaging'])
JA = ['Viral hepatitis', 'Chronic liver disease', 'Choledocholithiasis', 'Carcinoma of the pancreas', 'Gilbert syndrome', 'Drug-induced hepatitis',
      'Hepatocellular carcinoma', 'Liver metastases', 'Primary sclerosing cholangitis', 'Common bile duct ligation', 'Mirizzi syndrome']
emq('abdemq', 'BA', 'Causes of jaundice', JA, [
    (15, 'A 22-year-old student develops mild jaundice during exam stress. LFTs and haemoglobin are normal; bilirubin is unconjugated and rises with fasting.', 'E',
     'Isolated unconjugated hyperbilirubinaemia worsened by fasting or stress is Gilbert syndrome; no treatment needed.'),
    (16, 'A 60-year-old man has painless progressive jaundice, dark urine, pale stools and weight loss, with a palpable non-tender gallbladder.', 'D',
     'Painless jaundice with a palpable gallbladder (Courvoisier law) suggests carcinoma of the pancreatic head.'),
    (17, 'A 30-year-old man has fatigue, nausea and yellow eyes for a week; ALT and AST exceed 1000 IU/L. Two colleagues have a similar illness.', 'A',
     'Very high transaminases with a cluster of cases is acute viral hepatitis (hepatitis A).')], ['Jaundice'])
ADR = ['Adrenal metastasis', 'Adrenal adenoma (non-functioning)', 'Cushing syndrome', 'Angiomyolipoma', 'Conn syndrome', 'Phaeochromocytoma', 'Adrenal haemorrhage']
emq('abdemq', 'B2', 'Adrenal disorders', ADR, [
    (1, 'Episodes of hypertension, sweating and palpitations.', 'F', 'Paroxysmal hypertension, sweating and palpitations is phaeochromocytoma.'),
    (2, 'Resistant hypertension with hypokalaemia.', 'E', 'Resistant hypertension with hypokalaemia is primary hyperaldosteronism (Conn syndrome).'),
    (3, 'Central obesity, striae and a buffalo hump.', 'C', 'Central obesity, purple striae and a buffalo hump are Cushing syndrome.'),
    (4, 'A patient with lung cancer has bilateral adrenal masses on CT; they secrete no hormones.', 'A',
     'Bilateral non-functioning adrenal masses in lung cancer are metastases (the adrenal is a common site).'),
    (5, 'A woman has an incidental 2-cm non-secreting adrenal mass on CT.', 'B',
     'A small (< 4 cm), non-functioning, homogeneous adrenal incidentaloma is an adenoma; follow-up only.')], ['Adrenal incidentaloma'])
JB = ['Cholangiocarcinoma', 'Ascending cholangitis', 'Drug-induced hepatitis', 'Choledocholithiasis', 'Mirizzi syndrome']
emq('abdemq', 'B2', 'Obstructive jaundice', JB, [
    (1, 'Fever, jaundice, right upper quadrant pain and a dilated bile duct.', 'B', 'Charcot triad (fever, jaundice, RUQ pain) with a dilated duct is ascending cholangitis.'),
    (2, 'Jaundice with a dilated bile duct on ultrasound, but the stone is in the gallbladder.', 'E',
     'A stone impacted in the gallbladder neck compressing the common hepatic duct is Mirizzi syndrome.'),
    (3, 'Jaundice with dilated intrahepatic ducts and a contracted gallbladder on ultrasound.', 'A',
     'Intrahepatic dilatation with a collapsed gallbladder means a hilar block: cholangiocarcinoma.'),
    (4, 'A patient on chemotherapy develops jaundice, fever and right upper quadrant pain.', 'C',
     'Jaundice during chemotherapy without biliary dilatation suggests drug-induced hepatitis.'),
    (5, 'A patient has jaundice and a dilated common bile duct on ultrasound.', 'D',
     'Jaundice with a dilated CBD most commonly means a CBD stone (choledocholithiasis).')], ['Jaundice'])
JC = ['Choledocholithiasis', 'Non-alcoholic fatty liver disease', 'Viral hepatitis', 'Cholangiocarcinoma', 'Liver metastases', 'Alcoholic liver disease',
      'Mirizzi syndrome', 'Stauffer syndrome']
emq('abdemq', 'B3', 'Liver and biliary disease', JC, [
    (1, 'A 30-year-old nurse has jaundice, hepatomegaly and ALT and AST > 1000 IU/L.', 'C',
     'Transaminases > 1000 in a healthcare worker suggest acute viral hepatitis (hepatitis B from needlestick).'),
    (2, 'A woman with gallstones for 4 years has acute abdominal pain for 24 h; the CBD is normal but ALP is raised.', 'G',
     'A raised ALP with a normal CBD in a patient with gallstones suggests extrinsic CHD compression by a stone in Hartmann pouch (Mirizzi).'),
    (3, 'A 40-year-old diabetic man has slightly raised ALT and AST (about 93 IU/L).', 'B',
     'Mildly raised transaminases in a diabetic (metabolic syndrome) is most often non-alcoholic fatty liver disease.'),
    (4, 'A patient with renal cell carcinoma has a 7-cm liver mass on ultrasound.', 'E',
     'A liver mass in a patient with a known primary cancer is most likely a metastasis; Stauffer syndrome causes abnormal LFTs without metastases.'),
    (5, 'A middle-aged man has painless jaundice, weight loss and a palpable, non-tender, distended gallbladder.', 'D',
     'Painless jaundice with a palpable gallbladder means distal biliary obstruction by tumour (distal cholangiocarcinoma or pancreatic head cancer).')],
    ['Jaundice'])
C = ('A 39-year-old woman with asymptomatic gallstones for 4 years has severe upper abdominal pain for 24 hours with nausea and vomiting, '
     'still painful despite NSAIDs and opiates. LFTs are normal.')
mcq('gb', 'BA', 3, C, 'All of the following are expected EXCEPT:',
    ['Normal CBD', 'Thickened gallbladder wall', 'Leucopenia', 'Hyperaesthesia below the right scapula (Boas sign)', 'Raised CRP'], 'C',
    'Acute cholecystitis gives a thick-walled gallbladder, raised CRP and leucocytosis (not leucopenia); the CBD is normal.', ['Acute cholecystitis'])
mcq('gb', 'BA', 4, C, 'What is the best treatment option now?',
    ['Open cholecystectomy', 'Laparoscopic cholecystectomy', 'Tube cholecystostomy', 'ERCP followed by surgery', 'Conservative treatment, then surgery after 6 weeks'], 'B',
    'Early laparoscopic cholecystectomy (within 72 h–1 week) is recommended for acute cholecystitis in fit patients (NICE).', ['Acute cholecystitis'])
mcq('gb', 'BA', 5, C, 'Five days after a difficult operation the drain shows 800 mL/day of bile-stained fluid. Which is NOT a likely cause?',
    ['Slipped cystic duct clip', 'Bile duct injury', 'Leak from a duct of Luschka', 'Duodenal injury', 'Intrahepatic cholestasis'], 'E',
    'Bile in the drain means a leak (cystic stump, duct of Luschka, bile-duct or duodenal injury); cholestasis does not cause bile leakage.',
    ['Bile leak'])
mcq('gb', 'BA', 6, C, 'What is the best treatment now?',
    ['ERCP (sphincterotomy and stent)', 'PTC', 'IV antibiotics and anticholinergics', 'Right hepatic lobectomy', 'Liver transplantation'], 'A',
    'A post-cholecystectomy bile leak with a drain in place is treated by ERCP with sphincterotomy and stent; major duct injury needs MRCP and repair.',
    ['Bile leak'])
C = 'A young woman has right iliac fossa pain, low-grade fever, anorexia and dysuria, and is diagnosed with appendicitis.'
mcq('acute', 'B2', 1, C, 'Which test is 100% reliable for diagnosing appendicitis?',
    ['CT', 'Ultrasound', 'Diagnostic laparoscopy (with histology)', 'Alvarado score', 'MRI'], 'C',
    'Imaging and scores support the diagnosis, but only direct inspection at laparoscopy with histology confirms it.', ['Appendicitis'])
mcq('acute', 'B2', 2, C, 'Given the presentation, where is the appendix?',
    ['Retrocaecal', 'Retroileal', 'Pre-ileal', 'Pelvic', 'Subhepatic'], 'D',
    'A pelvic appendix lies against the bladder and causes dysuria and frequency (and diarrhoea if near the rectum).', ['Appendicitis'])
mcq('acute', 'B2', 3, C, 'Which investigation will you request?',
    ['Complete blood count', 'Renal function tests', 'CRP', 'ESR', 'Serum amylase'], 'A',
    'The white-cell count (leucocytosis with left shift) is part of the Alvarado score; urinalysis and a pregnancy test are also essential.',
    ['Appendicitis'])
mcq('acute', 'B2', 'T1', '', 'Which two Alvarado (MANTRELS) criteria each score 2 points?',
    ['Migration of pain and anorexia', 'Right iliac fossa tenderness and leucocytosis', 'Nausea/vomiting and fever', 'Rebound tenderness and left shift',
     'Anorexia and fever'], 'B',
    'RIF tenderness and leucocytosis score 2 each; migration, anorexia, nausea/vomiting, rebound, fever and left shift score 1 (total 10).',
    ['Appendicitis'])
mcq('acute', 'B2', 'T2', '', 'Which is NOT an advantage of laparoscopic over open appendicectomy?',
    ['Fewer wound infections', 'Less postoperative pain', 'Shorter stay and earlier return to work', 'Allows inspection of the pelvis and other diagnoses',
     'Lower rate of intra-abdominal abscess'], 'E',
    'Laparoscopy reduces pain, wound infection and stay and is diagnostic; the intra-abdominal abscess rate is not lower (it may be slightly higher).',
    ['Appendicitis'])
mcq('gb', 'B2', 'T3', '', 'Which clinical triad defines ascending cholangitis?',
    ['Fever with rigors, jaundice and right upper quadrant pain', 'Jaundice, palpable gallbladder and weight loss', 'Fever, jaundice and pruritus',
     'Right upper quadrant pain, vomiting and positive Murphy sign', 'Jaundice, hypotension and confusion'], 'A',
    'Charcot triad is fever/rigors, jaundice and RUQ pain; adding hypotension and confusion gives Reynolds pentad (suppurative cholangitis).',
    ['Cholangitis'])
mcq('spleen', 'B2', 'T4', '', 'Which vaccines should be given around splenectomy?',
    ['Pneumococcal, Haemophilus influenzae b, meningococcal (ACWY and B) and annual influenza', 'BCG and oral polio', 'Hepatitis B and tetanus only',
     'Live typhoid and yellow fever', 'No vaccines if lifelong penicillin is taken'], 'A',
    'Give pneumococcal, Hib, meningococcal ACWY and B plus yearly influenza, 2 weeks before elective or 2 weeks after emergency splenectomy.',
    ['Post-splenectomy infection'])
C = 'A 71-year-old male smoker with hypertension and type 2 diabetes has felt a pulsating abdominal mass with dull pain radiating to the back for 2 months.'
mcq('acute', 'P1', 37, C, 'What is the most likely diagnosis?',
    ['Diverticulitis', 'Renal colic', 'Abdominal aortic aneurysm', 'Chronic pancreatitis', 'Mesenteric ischaemia'], 'C',
    'A pulsatile, expansile abdominal mass with back pain in an elderly hypertensive smoker is an abdominal aortic aneurysm.', ['Aortic aneurysm'])
mcq('acute', 'P1', 38, C, 'What is the gold-standard diagnostic test?',
    ['Doppler ultrasound', 'Abdominal X-ray', 'CT angiography', 'MRI', 'ECG'], 'C',
    'Ultrasound screens and follows AAA, but CT angiography defines size, extent and neck anatomy for repair planning.', ['Aortic aneurysm'])
mcq('acute', 'P1', 39, C, 'He suddenly develops pain in the right leg with an absent dorsalis pedis pulse. What is the most likely diagnosis?',
    ['Chronic limb ischaemia', 'Cellulitis', 'Acute limb ischaemia', 'Deep vein thrombosis', 'Compartment syndrome'], 'C',
    'Sudden pain with a lost pulse is acute limb ischaemia, here from embolism of aneurysm thrombus.', ['Acute limb ischaemia'])
mcq('acute', 'P1', 40, C, 'What is the first-line management of this complication?',
    ['Antiplatelet', 'Anticoagulation (IV heparin)', 'Antibiotics', 'Leg elevation', 'Fasciotomy'], 'B',
    'Give IV unfractionated heparin immediately to stop clot propagation, then embolectomy or thrombolysis according to limb viability.',
    ['Acute limb ischaemia'])
C = 'A patient has fever, abdominal pain and a perforated viscus.'

# ============================================================ UROLOGY
C = 'A mother brings her baby boy because of an abnormal downward urinary stream. The urethral opening is not in its normal position.'
mcq('congur', 'P1', 23, C, 'What is the most likely diagnosis?', ['Phimosis', 'Hypospadias', 'Epispadias', 'Meatal stenosis', 'Posterior urethral valves'], 'B',
    'A ventral ectopic meatus with a downward stream is hypospadias (often with chordee and a dorsal hooded foreskin).', ['Hypospadias'])
mcq('congur', 'P1', 24, C, 'Which associated abnormality is most common?',
    ['Undescended testis', 'Polydactyly', 'Coarctation of the aorta', 'Inguinal hernia', 'Renal agenesis'], 'A',
    'Undescended testis (≈ 10%) and inguinal hernia are the commonest associations; with both hypospadias and impalpable testes, exclude a DSD.',
    ['Hypospadias'])
mcq('congur', 'P1', 25, C, 'What is the most common complication after surgical repair?',
    ['Penile fracture', 'Urethrocutaneous fistula', 'Renal failure', 'Erectile dysfunction', 'Urinary retention'], 'B',
    'Urethrocutaneous fistula is the commonest complication of hypospadias repair; meatal stenosis and stricture also occur.', ['Hypospadias'])
C = ('A 61-year-old man has frequency, hesitancy and a weak stream. DRE shows a smooth, symmetrically enlarged prostate. '
     'He has also had erectile dysfunction for 6 months.')
mcq('prostate', 'P1', 41, C, 'What is the first-line management?', ['Tamsulosin', 'Finasteride', 'Doxazosin', 'Tadalafil', 'Prazosin'], 'D',
    'Tadalafil 5 mg daily treats both LUTS from BPH and erectile dysfunction; an alpha-blocker is first-line when ED is absent.', ['BPH'])
mcq('prostate', 'P1', 42, 'Eight years later his PSA is 16 ng/mL and the prostate is nodular and irregular. He has localised adenocarcinoma, Gleason 4+4, with no metastasis.',
    'What is the best treatment?', ['TURP', 'Radiotherapy', 'Radical prostatectomy', 'Chemotherapy', 'Bilateral orchidectomy'], 'C',
    'High-risk localised prostate cancer in a fit man is treated radically: radical prostatectomy, or radiotherapy with long-term ADT.', ['Prostate cancer'])
URO = ['Partial nephrectomy', 'Simple nephrectomy', 'Radical nephrectomy', 'Nephroureterectomy', 'Percutaneous nephrostomy', 'Ureteric (JJ) stent',
       'Ureteric reimplantation', 'Pyeloplasty']
emq('uroemq', 'P2', 'Urological operations', URO, [
    (40, 'A 55-year-old man has an incidental 3-cm enhancing mass in the upper pole of the kidney on CT; PET is negative.', 'A',
     'A small (T1a, ≤ 4 cm) renal cell carcinoma is treated by nephron-sparing partial nephrectomy.'),
    (41, 'A 48-year-old woman with chronic infections and recurrent stones has a left kidney contributing < 5% of total function on MAG3.', 'B',
     'A non-functioning, chronically infected kidney is removed by simple nephrectomy.'),
    (42, 'A 70-year-old man on IV antibiotics for 5 days has fever, rigors and flank pain; HR 120, BP 80/60. CT shows hydroureteronephrosis to the mid-ureter.', 'E',
     'An infected obstructed kidney with septic shock needs urgent decompression; percutaneous nephrostomy is safest in the unstable patient.'),
    (43, 'A 4-year-old girl has recurrent febrile UTIs despite long-term antibiotics; micturating cystogram shows a dilated, tortuous left ureter.', 'G',
     'High-grade vesicoureteric reflux with breakthrough febrile UTIs is treated by ureteric reimplantation.'),
    (44, 'A 44-year-old man has painless haematuria; CT shows a tumour of the left renal pelvis without metastasis.', 'D',
     'Upper-tract urothelial carcinoma is treated by nephroureterectomy with a bladder cuff.')], ['Urological surgery'])
UT = ['Acute pyelonephritis', 'Acute cystitis', 'Asymptomatic bacteriuria', 'Acute prostatitis', 'Urethritis', 'Pyonephrosis', 'Emphysematous pyelonephritis',
      'Vesicoureteric reflux']
emq('uroemq', 'BA', 'Urinary tract infection', UT, [
    (18, 'A 25-year-old woman has dysuria, frequency and suprapubic pain without fever or flank pain. Urine is cloudy with leucocytes and nitrites.', 'B',
     'Lower urinary symptoms without fever or loin pain are acute (uncomplicated) cystitis.'),
    (19, 'A 60-year-old man has fever, chills and perineal pain; DRE is difficult because of severe anterior rectal tenderness. Urine grows E. coli.', 'D',
     'Fever, perineal pain and an exquisitely tender prostate is acute bacterial prostatitis (avoid prostatic massage).'),
    (20, 'A 28-year-old diabetic woman has high fever, flank pain, vomiting and renal angle tenderness. CT shows pockets of gas and fluid in the left kidney.', 'G',
     'Gas within the renal parenchyma in a diabetic is emphysematous pyelonephritis: antibiotics, drainage, sometimes nephrectomy.')], ['UTI'])
C = 'An elderly man has haematuria; ultrasound shows a 2-cm tumour in the bladder.'
mcq('bladder', 'B2', 1, C, 'What is the next step?', ['Cystoscopy (with biopsy/TURBT)', 'CT scan', 'Urine cytology only', 'MRI pelvis', 'IVU'], 'A',
    'A bladder mass needs cystoscopy and transurethral resection for histology and staging; CT urography assesses the upper tracts.', ['Bladder cancer'])
mcq('bladder', 'B2', 2, C, 'What is the treatment?', ['TURBT', 'TURP', 'Radical cystectomy', 'Intravesical BCG alone', 'Radiotherapy'], 'A',
    'TURBT is diagnostic and therapeutic for non-muscle-invasive tumours; intravesical therapy follows according to risk.', ['Bladder cancer'])
C = 'A 25-year-old woman had a difficult caesarean section for bleeding. Ten days later she has severe right flank pain; ultrasound shows severe hydroureteronephrosis down to the pelvis with no stones.'
mcq('uroemerg', 'BA', 7, C, 'Which test best establishes the cause of obstruction?', ['CT urography', 'MRI', 'GUE', 'KUB', 'CBC'], 'A',
    'CT urography (or antegrade/retrograde study) shows the level of a ligated or injured ureter and any urinoma.', ['Ureteric injury'])
mcq('uroemerg', 'BA', 8, C, 'Ureteric ligation is suspected. All of the following are initial options EXCEPT:',
    ['IV fluids', 'IV antibiotics', 'Percutaneous nephrostomy', 'Ureteroscopy (attempted stenting)', 'Nephrectomy'], 'E',
    'Initial care is resuscitation, antibiotics and drainage (nephrostomy or retrograde stent); delayed reimplantation repairs it. Nephrectomy is not indicated.',
    ['Ureteric injury'])
C = 'A 4-year-old boy has left lower abdominal pain and is underweight. Ultrasound shows hydronephrosis and urinalysis shows mild painless pyuria.'
mcq('congur', 'B3', 1, C, 'Which investigation confirms the diagnosis?', ['IVU', 'Contrast CT', 'MRI (MR urography)', 'KUB', 'Ureteroscopy'], 'A',
    'PUJ obstruction is confirmed on urography (IVU, CT or MR urography) and a diuretic renogram; ureteroscopy has no role.', ['PUJ obstruction'])
mcq('congur', 'B3', 2, C, 'Which is the best test of split renal function and drainage?', ['DMSA scan', 'MAG3 diuretic renogram', 'Ultrasound', 'eGFR'], 'B',
    'A MAG3 diuretic renogram measures differential function and confirms obstruction; DMSA shows scarring and static function.', ['PUJ obstruction'])
mcq('congur', 'B3', 3, C, 'What is the best long-term management?',
    ['Percutaneous nephrostomy', 'Long-term antibiotics', 'Dismembered pyeloplasty', 'Ureteric stent', 'Nephrectomy'], 'C',
    'Symptomatic PUJ obstruction or falling function is treated by dismembered (Anderson–Hynes) pyeloplasty; nephrectomy only for a non-functioning kidney.',
    ['PUJ obstruction'])
# OSCE catheter tasks (Group A/B, repeated by Group C/D)
C = 'A 68-year-old man arrives in the emergency department with abdominal pain and a distended bladder.'
mcq('uroemerg', 'B2', 'T5', C, 'Which is the correct technique for male urethral catheterisation?',
    ['Aseptic technique, lidocaine gel, penis held upright, insert to the hub and see urine before inflating the balloon', 'Inflate the balloon as soon as resistance is felt',
     'Clean technique without lubrication', 'Use the largest catheter to overcome resistance', 'Insert only half the catheter length, then inflate'], 'A',
    'Insert the catheter fully to the bifurcation and inflate only once urine drains, so the balloon cannot be inflated in the urethra.',
    ['Urethral catheterisation'])
mcq('uroemerg', 'B2', 'T6', C, 'The catheter is passed but no urine drains. What is the most appropriate next step?',
    ['Inflate the balloon and wait', 'Check the position: advance fully, flush with sterile saline and confirm a full bladder (scan) before inflating',
     'Remove it and force a larger catheter', 'Give IV furosemide', 'Insert a suprapubic catheter at once'], 'B',
    'No urine means the catheter is in the urethra, blocked by gel, or the bladder is empty; check, flush and scan before inflating.',
    ['Urethral catheterisation'])
C = 'A patient needs a Foley catheter and develops haematuria during insertion.'
T7 = mcq('uroemerg', 'B2', 'T7', C, 'What is the most likely cause of the bleeding?',
         ['Urethral trauma (false passage or balloon inflated in the urethra)', 'Bladder carcinoma', 'Urinary tract infection', 'Ureteric stone', 'Renal trauma'], 'A',
         'Bleeding at catheterisation is usually urethral trauma (false passage) or a balloon inflated in the prostatic urethra.', ['Catheter trauma'])
T8 = mcq('uroemerg', 'B2', 'T8', C, 'How should it be managed?',
         ['Continue and inflate the balloon', 'Stop, deflate and remove; then one gentle attempt by a senior/urologist (coudé tip) or a suprapubic catheter',
          'Repeated forceful attempts', 'Start anticoagulation', 'Immediate open urethroplasty'], 'B',
         'Stop, deflate and withdraw; if retention persists use a suprapubic catheter or urology-guided catheterisation, and check Hb and urine.',
         ['Catheter trauma'])
C = 'A 72-year-old man with benign prostatic hyperplasia has acute urinary retention and severe suprapubic pain; bladder scan shows 900 mL.'
mcq('uroemerg', 'B2', 'T9', C, 'Which is the most common complication of a long-term indwelling catheter?',
    ['Catheter-associated urinary tract infection', 'Bladder cancer', 'Renal stones', 'Urethral stricture', 'Bladder perforation'], 'A',
    'Bacteriuria and CAUTI are universal with long-term catheters; encrustation, blockage, stricture and stones also occur.', ['Urethral catheterisation'])
mcq('uroemerg', 'B2', 'T10', C, 'Which is an absolute contraindication to urethral catheterisation?',
    ['Suspected urethral injury (blood at the meatus, pelvic fracture)', 'Acute urinary retention', 'Benign prostatic hyperplasia', 'Diabetes mellitus',
     'Previous TURP'], 'A',
    'Suspected urethral injury (blood at the meatus, high-riding prostate) contraindicates urethral catheterisation; a suprapubic catheter is used.',
    ['Urethral catheterisation'])
mcq('uroemerg', 'B2', 'T11', 'Haematuria develops after Foley catheter insertion.', 'What are the likely causes?',
    ['Urethral trauma or balloon inflated in the urethra', 'Bladder carcinoma', 'Urinary tract infection', 'Ureteric stone', 'Renal trauma'], 'A',
    'Bleeding at catheterisation is usually urethral trauma (false passage) or a balloon inflated in the prostatic urethra.', ['Catheter trauma'], dup_of=T7)
mcq('uroemerg', 'B2', 'T12', 'Haematuria develops after Foley catheter insertion.', 'How is it managed?',
    ['Continue and inflate the balloon', 'Stop, deflate and remove; then one gentle attempt by a senior/urologist (coudé tip) or a suprapubic catheter',
     'Repeated forceful attempts', 'Start anticoagulation', 'Immediate open urethroplasty'], 'B',
    'Stop, deflate and withdraw; if retention persists use a suprapubic catheter or urology-guided catheterisation.', ['Catheter trauma'], dup_of=T8)

# ============================================================ TRAUMA & CRITICAL CARE
C = ('A 75-year-old man with type 2 diabetes, hypertension and heart failure (EF 40%) was caught in a house fire when his clothes ignited. '
     'He has extensive white, leathery burns of the arms and legs with red blistered margins; pulse 110/min, BP 90/60 mmHg.')
mcq('trauma', 'P1', 1, C, 'What is the best initial management?',
    ['Apply silver sulfadiazine cream', 'Immediate grafting in theatre', 'Escharotomy only', 'Airway assessment and IV fluid resuscitation', 'Oral fluids and analgesia'], 'D',
    'Burns follow ATLS: secure the airway (inhalation risk) and start IV resuscitation; dressings and surgery come later.', ['Burns'])
mcq('trauma', 'P1', 2, C, 'What is the depth of these burns?',
    ['Superficial (first degree)', 'Superficial partial thickness', 'Deep partial thickness', 'Full thickness (third degree)', 'Fourth degree'], 'D',
    'White, leathery, painless skin is full-thickness burn; the red blistered margins are partial thickness.', ['Burns'])
mcq('trauma', 'P1', 3, C, 'What is the most common complication in the first 24 hours?',
    ['Hypovolaemic (burn) shock', 'Sepsis', 'Contracture', 'Contour deformity', 'ARDS'], 'A',
    'Capillary leak causes hypovolaemic burn shock in the first 24–48 h; sepsis and contractures come later.', ['Burns'])
mcq('trauma', 'P1', 4, C, 'Given his diabetes and heart failure, what is the key consideration in fluid resuscitation?',
    ['Use the standard formula without change', 'Avoid fluids; use vasopressors only', 'Start Parkland cautiously and titrate to urine output',
     'Replace fluids only after 24 hours', 'Give colloids only'], 'C',
    'Parkland is only a starting point; titrate to urine output 0.5 mL/kg/h to avoid both under-resuscitation and fluid overload in heart failure.',
    ['Burns'])
C = ('A 45-year-old man is brought after a car crash. The right chest moves paradoxically with bruising, reduced expansion and diminished breath sounds. '
     'He is conscious but distressed; BP 95/60 mmHg, SpO2 86%.')
mcq('trauma', 'P1', 5, C, 'What is the most likely diagnosis?',
    ['Tension pneumothorax', 'Flail chest', 'Massive haemothorax', 'Pulmonary contusion', 'Lung collapse'], 'B',
    'Paradoxical movement of a chest segment after blunt trauma is flail chest (two or more ribs broken in two or more places).', ['Chest trauma'])
mcq('trauma', 'P1', 6, C, 'Which mechanism mainly compromises his lungs?',
    ['Hyperventilation from pain', 'Underlying pulmonary contusion', 'Mediastinal shift', 'Air trapping on expiration', 'Diaphragmatic rupture'], 'B',
    'Hypoxia in flail chest is caused mainly by the underlying pulmonary contusion, aggravated by pain-limited ventilation.', ['Chest trauma'])
mcq('trauma', 'P1', 7, C, 'Chest X-ray and CT show a massive haemothorax. What is the next immediate step?',
    ['Urgent thoracotomy', 'Intubation and positive-pressure ventilation', 'Chest drain insertion', 'Needle decompression', 'Pericardiocentesis'], 'C',
    'Massive haemothorax is treated with a large-bore chest drain and resuscitation; thoracotomy if > 1500 mL initially or > 200 mL/h.',
    ['Chest trauma'])
mcq('trauma', 'P1', 8, C, 'He improves but remains hypoxic with paradoxical movement. What is the next definitive step?',
    ['Analgesia and oxygen only', 'Intubation and mechanical ventilation', 'Surgical rib fixation', 'Repeat chest X-ray after 24 hours', 'Chest strapping'], 'B',
    'Persistent hypoxia despite analgesia and oxygen needs intubation and ventilation (internal splinting); rib fixation is increasingly used to wean.',
    ['Chest trauma'])
mcq('trauma', 'P2', 79, '', 'An elderly patient has headache 3 weeks after a minor head injury; CT shows a crescent-shaped collection. What is the diagnosis?',
    ['Acute subdural haematoma', 'Chronic subdural haematoma', 'Idiopathic intracranial hypertension', 'Subarachnoid haemorrhage', 'Cerebral venous sinus thrombosis',
     'Intracerebral haemorrhage', 'Temporal arteritis', 'Brain tumour'], 'B',
    'A crescentic (hypodense) collection weeks after minor trauma in an elderly patient is a chronic subdural haematoma: burr-hole drainage.',
    ['Head injury'])
C = 'A man cuts his forearm on glass; the wound is not deep and its edges are everted.'
mcq('trauma', 'B2', 'T13', C, 'Which closure and immediate drug are most appropriate?',
    ['Simple interrupted non-absorbable monofilament (e.g. 4/0 nylon) sutures and tetanus prophylaxis', 'Absorbable braided sutures and IV antibiotics',
     'Leave open and give oral steroids', 'Staples and antiplatelet', 'Skin glue and anticoagulant'], 'A',
    'Superficial lacerations are closed with interrupted non-absorbable monofilament sutures; check tetanus status and give prophylaxis.', ['Wound care'])
mcq('trauma', 'B2', 'T14', C, 'If the wound is deep, how should it be closed?',
    ['Layered closure: absorbable subcutaneous sutures, then skin sutures', 'Skin sutures only', 'Leave open to heal by secondary intention',
     'Tight single-layer closure', 'Skin glue'], 'A',
    'Deep wounds need layered closure with absorbable (e.g. polyglactin) deep sutures to close dead space and reduce tension, haematoma and infection.',
    ['Wound care'])
C = ('A 28-year-old man is brought after a road traffic accident with a deep right-thigh laceration and pulsatile bleeding. '
     'He is pale and anxious; BP 85/60 mmHg, HR 130/min.')
mcq('shock', 'B2', 'T15', C, 'What type of bleeding is this?',
    ['Arterial: bright red and spurting in time with the pulse', 'Venous: dark red, steady flow', 'Capillary: oozing', 'Reactionary haemorrhage',
     'Secondary haemorrhage'], 'A',
    'Arterial bleeding is bright red and pulsatile; venous bleeding is dark and flows steadily. Control with direct pressure or a tourniquet.',
    ['Haemorrhage'])
mcq('shock', 'B2', 'T16', C, 'What is the maximum safe tourniquet time?',
    ['About 2 hours (note the time applied)', '15 minutes', '6 hours', '12 hours', 'No limit if the limb is cooled'], 'A',
    'Limit tourniquet time to about 2 h (record it); complications are nerve palsy, ischaemia, compartment syndrome and reperfusion injury.',
    ['Haemorrhage'])
C = 'A sedated, intubated patient in the ICU needs a nasogastric tube.'
T17 = mcq('metab', 'B2', 'T17', C, 'What is the most dangerous complication of insertion?',
          ['Misplacement into the tracheobronchial tree', 'Epistaxis', 'Sinusitis', 'Nasal discomfort', 'Hiccups'], 'A',
          'In a sedated, intubated patient the tube can pass into the airway unnoticed (no cough reflex); feeding into the lung is the danger.',
          ['Nasogastric tube'])
T18 = mcq('metab', 'B2', 'T18', C, 'After NG insertion and feeding he becomes hypotensive and desaturates with secretions around the mouth and tube. What happened?',
          ['Aspiration of feed into the lungs', 'Anaphylaxis', 'Pneumothorax', 'Septic shock', 'Myocardial infarction'], 'A',
          'This is aspiration: stop feeds and suction. Prevent it by checking aspirate pH ≤ 5.5 or X-ray before feeding and nursing 30–45° head-up.',
          ['Nasogastric tube'])
mcq('metab', 'B2', 'T19', 'A 72-year-old sedated, ventilated ICU patient needs an NG tube.', 'What are the possible complications and how are they minimised?',
    ['Misplacement into the tracheobronchial tree', 'Epistaxis', 'Sinusitis', 'Nasal discomfort', 'Hiccups'], 'A',
    'Misplacement into the airway is the major danger; confirm placement (pH ≤ 5.5 or X-ray) before use.', ['Nasogastric tube'], dup_of=T17)
mcq('metab', 'B2', 'T20', 'A 72-year-old sedated, ventilated ICU patient needs an NG tube.',
    'After feeding he desaturates with secretions. What happened and what is the immediate management?',
    ['Aspiration of feed into the lungs', 'Anaphylaxis', 'Pneumothorax', 'Septic shock', 'Myocardial infarction'], 'A',
    'Aspiration: stop feeds, suction and oxygen; confirm tube position before feeding.', ['Nasogastric tube'], dup_of=T18)
C = 'A 65-year-old man with distension, persistent vomiting and absent bowel sounds has intestinal obstruction; an NG tube is ordered for decompression.'
mcq('intest', 'B2', 'T21', C, 'How is NG tube placement confirmed?',
    ['Aspirate pH ≤ 5.5, or chest X-ray if no aspirate or pH is high', 'Auscultation of injected air (whoosh test)', 'Bubbling when the end is placed in water',
     'Litmus paper colour change to blue', 'Patient able to talk'], 'A',
    'Use gastric aspirate pH ≤ 5.5 first-line and X-ray if that fails; the whoosh and bubble tests are unreliable and unsafe.', ['Nasogastric tube'])
mcq('intest', 'B2', 'T22', C, 'Which is a contraindication to NG tube insertion?',
    ['Suspected basal skull fracture', 'Intestinal obstruction', 'Postoperative ileus', 'Upper GI bleeding', 'Gastric outlet obstruction'], 'A',
    'Basal skull or severe mid-face fractures risk intracranial passage, so use the orogastric route; recent oesophageal surgery or atresia are others.',
    ['Nasogastric tube'])

# --- extra-chapter EMQs
EL = ['Hyponatraemia', 'Hypernatraemia', 'Hypokalaemia', 'Hyperkalaemia', 'Hypocalcaemia', 'Hypercalcaemia', 'Hypomagnesaemia', 'Hypermagnesaemia']
emq('extraemq', 'P2', 'Electrolyte disturbances', EL, [
    (20, 'An elderly woman becomes confused 2 days after surgery; plasma osmolality is low.', 'A',
     'Postoperative confusion with low osmolality is hyponatraemia (ADH response plus hypotonic fluids).'),
    (21, 'A man with extensive muscle destruction has tall peaked T waves on ECG.', 'D',
     'Rhabdomyolysis releases potassium; peaked T waves signal hyperkalaemia (give IV calcium first).'),
    (22, 'A man has prominent U waves on ECG.', 'C', 'U waves, flat T waves and ST depression are signs of hypokalaemia.'),
    (23, 'A malnourished alcoholic given fluids and nutrition has hypokalaemia that does not correct despite repeated potassium infusions.', 'G',
     'Refractory hypokalaemia means hypomagnesaemia (renal K loss); replace magnesium first (and watch for refeeding).')], ['Electrolytes'])
FX = ['Avascular necrosis', 'Fat embolism syndrome', 'Pulmonary embolism', 'Post-traumatic osteoarthritis', 'Compartment syndrome', 'Volkmann ischaemic contracture',
      'Malunion', 'Delayed union', 'Nerve injury', 'Osteomyelitis', 'Gas gangrene', 'Sudeck atrophy (complex regional pain syndrome)']
emq('extraemq', 'P2', 'Complications of fractures', FX, [
    (35, 'A soil-contaminated open fracture from a farm accident develops, days later, rapidly spreading swelling, severe pain, systemic toxicity and sepsis.', 'K',
     'Rapid spreading swelling and toxicity in a soil-contaminated wound is clostridial gas gangrene: radical debridement, penicillin, clindamycin.'),
    (36, 'After multiple long-bone fractures a patient develops, within 24–72 hours, respiratory distress, confusion and a petechial rash.', 'B',
     'Hypoxia, neurological signs and petechiae 1–3 days after long-bone fractures is fat embolism syndrome.'),
    (38, 'A 19-year-old athlete with a tibial fracture has worsening pain hours later, worse on passive dorsiflexion; distal pulses are present.', 'E',
     'Pain out of proportion and on passive stretch is compartment syndrome; pulses persist until late. Urgent fasciotomy.')], ['Fractures'])
FL = ['Split-thickness skin graft', 'Full-thickness skin graft', 'Axial (pedicled) flap', 'Regional muscle flap', 'Free muscle flap', 'Free fasciocutaneous flap',
      'Local random-pattern flap', 'Healing by secondary intention', 'Delayed primary closure']
emq('extraemq', 'P2', 'Closure of skin defects', FL, [
    (51, 'A superficial 14 × 10 cm burn wound of the back, after debridement, with a healthy vascular bed and no exposed structures.', 'A',
     'A large wound with a healthy vascular bed is covered by split-thickness skin graft.'),
    (52, 'A small nasal ala defect after skin cancer excision needs excellent contour and minimal contraction.', 'B',
     'Full-thickness grafts contract little and match facial skin, so suit small facial defects (local flaps are an alternative).'),
    (53, 'A fingertip wound < 1 cm with no exposed bone.', 'H', 'Small fingertip wounds without exposed bone heal well by secondary intention.'),
    (54, 'A cheek defect closed by rotating a flap around a known vascular pedicle.', 'C', 'A flap based on a named vessel is an axial-pattern flap.'),
    (55, 'A 24-year-old has an avulsion over the anterior tibia; after debridement bone without periosteum is exposed and the surrounding tissue is traumatised and previously irradiated.', 'E',
     'Bare bone cannot take a graft and the local tissue is unusable, so a free muscle flap brings well-vascularised cover.')], ['Reconstruction'])
LI = ['Chronic atherosclerotic ischaemia', 'Acute limb ischaemia', 'Reperfusion injury (compartment syndrome)', 'Leriche syndrome', 'Buerger disease', 'Aortic dissection']
emq('extraemq', 'P2', 'Limb ischaemia', LI, [
    (70, 'A 65-year-old with a mechanical mitral valve and infective endocarditis suddenly has a cold, pale, pulseless right leg with sensory loss below the knee; motor function is intact.', 'B',
     'Sudden pain, pallor and pulselessness from an embolus is acute limb ischaemia; with intact motor function the limb is salvageable.'),
    (71, 'A patient has absent femoral pulses, buttock claudication and erectile dysfunction.', 'D',
     'Aorto-iliac occlusion gives Leriche syndrome: buttock claudication, impotence and absent femoral pulses.'),
    (72, 'A patient develops pain and a tense swollen leg after emergency embolectomy.', 'C',
     'Reperfusion after revascularisation causes oedema and compartment syndrome: fasciotomy.'),
    (73, 'A 30-year-old male smoker has ischaemia of the distal digits and previous superficial thrombophlebitis.', 'E',
     'Distal ischaemia with migratory thrombophlebitis in a young smoker is Buerger disease (thromboangiitis obliterans).')], ['Limb ischaemia'])
AN = ['GA with endotracheal intubation', 'GA with laryngeal mask airway', 'Spinal anaesthesia', 'Epidural anaesthesia', 'Peripheral nerve block',
      'Local anaesthesia with sedation', 'Bier block (IV regional)']
emq('extraemq', 'P2', 'Choice of anaesthesia', AN, [
    (93, 'An asthmatic patient with wheeze needs ureteroscopic stone extraction.', 'C',
     'Spinal anaesthesia avoids airway instrumentation (bronchospasm) and suits ureteroscopy.'),
    (94, 'A patient with COPD needs emergency laparotomy for a perforated viscus.', 'A',
     'Emergency laparotomy (full stomach) needs GA with rapid-sequence intubation to protect the airway.'),
    (95, 'A patient with heart failure and CKD needs elective inguinal hernia repair.', 'F',
     'Open inguinal hernia repair under local anaesthesia (± sedation) avoids GA risks in high-risk patients.'),
    (96, 'Wide local excision of a basal cell carcinoma of the cheek.', 'F', 'Small facial skin excisions are done under local anaesthesia ± sedation.')],
    ['Anaesthesia'])
NU = ['IV fluids only', 'Total parenteral nutrition', 'Oral feeding', 'Feeding jejunostomy', 'Gastrostomy (PEG)', 'Nasogastric feeding']
emq('extraemq', 'B3', 'Postoperative and surgical nutrition', NU, [
    (1, 'An elderly woman has inoperable oesophageal cancer with severe dysphagia.', 'E',
     'Inoperable oesophageal cancer needs long-term enteral access below the block: gastrostomy (or stent).'),
    (2, 'A man is stable after uncomplicated herniorrhaphy with normal bowel sounds.', 'C', 'After uncomplicated surgery, early oral feeding is resumed.'),
    (3, 'A patient has undergone a Whipple procedure.', 'D',
     'A feeding jejunostomy placed at pancreaticoduodenectomy allows early enteral feeding beyond the anastomoses.'),
    (4, 'A patient with multiple fractures has prolonged ileus.', 'B', 'A non-functioning gut (prolonged ileus) needs parenteral nutrition.'),
    (5, 'A patient with severe trauma and a liver injury.', 'F',
     'Critically ill trauma patients should start early enteral (nasogastric) feeding within 24–48 h if the gut works.')], ['Nutrition'])

# ============================================================ RADIOLOGY IMAGES (Block 2 groups A–D)
RQ = 'What is the most likely diagnosis on this image?'
mcq('oeso', 'B2', 'R1', 'A barium swallow is shown.', RQ,
    ['Achalasia', 'Oesophageal carcinoma', 'Diffuse oesophageal spasm', 'Pharyngeal pouch', 'Hiatus hernia'], 'A',
    'A grossly dilated oesophagus tapering smoothly at the cardia (bird beak) is achalasia.', ['Achalasia'], images=['p6-1'])
mcq('acute', 'B2', 'R2', 'An erect chest X-ray is shown.', RQ,
    ['Pneumoperitoneum from a perforated viscus', 'Bilateral pneumothorax', 'Chilaiditi sign', 'Subphrenic abscess', 'Pleural effusion'], 'A',
    'Free gas under both hemidiaphragms on an erect film means pneumoperitoneum, usually a perforated viscus.', ['Perforation'], images=['p6-2'])
mcq('intest', 'B2', 'R3', 'A plain abdominal X-ray of a distended elderly patient is shown.', RQ,
    ['Sigmoid volvulus', 'Small bowel obstruction', 'Caecal volvulus', 'Toxic megacolon', 'Gallstone ileus'], 'A',
    'A huge inverted-U (coffee-bean) loop arising from the pelvis is sigmoid volvulus.', ['Sigmoid volvulus'], images=['p6-3'])
mcq('liver', 'B2', 'R4', 'A contrast CT of the upper abdomen of a febrile patient is shown.', RQ,
    ['Liver abscess', 'Simple liver cyst', 'Hepatocellular carcinoma', 'Haemangioma', 'Hydatid cyst with daughter cysts'], 'A',
    'A large hypodense collection with an enhancing wall and necrotic debris in the right lobe is a liver abscess.', ['Liver abscess'], images=['p6-4'])
mcq('intest', 'B2', 'R5', 'An erect abdominal X-ray is shown.', RQ,
    ['Small bowel obstruction', 'Pneumoperitoneum', 'Sigmoid volvulus', 'Normal film', 'Paralytic ileus of the colon'], 'A',
    'Multiple central air–fluid levels in dilated small-bowel loops indicate small bowel obstruction.', ['Intestinal obstruction'], images=['p7-1'])
mcq('panc', 'B2', 'R6', 'A plain abdominal X-ray is shown.', RQ,
    ['Chronic calcific pancreatitis', 'Renal stones', 'Gallstones', 'Calcified lymph nodes', 'Splenic artery aneurysm'], 'A',
    'Speckled calcification across the line of the pancreas (L1–L2) is chronic calcific pancreatitis.', ['Chronic pancreatitis'], images=['p7-2'])
mcq('oeso', 'B2', 'R7', 'A barium swallow of a patient with progressive dysphagia and weight loss is shown.', RQ,
    ['Oesophageal carcinoma', 'Achalasia', 'Benign peptic stricture', 'Oesophageal web', 'Diffuse oesophageal spasm'], 'A',
    'An irregular stricture with shouldering and proximal dilatation is oesophageal carcinoma.', ['Oesophageal cancer'], images=['p7-3'])
mcq('gb', 'B2', 'R8', 'An MRCP of a jaundiced patient is shown.', RQ,
    ['Choledocholithiasis', 'Hilar cholangiocarcinoma', 'Choledochal cyst', 'Primary sclerosing cholangitis', 'Normal biliary tree'], 'A',
    'Filling defects within a dilated common bile duct on MRCP are CBD stones.', ['Choledocholithiasis'], images=['p7-4'])

if __name__ == '__main__':
    p = os.path.join(ROOT, 'data', 'patches', '400-39-batch-surgery.json')
    json.dump(OUT, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    n = collections.Counter(o['new']['type'] for o in OUT)
    items = sum(len(o['new'].get('items', [])) for o in OUT)
    print(p, len(OUT), dict(n), 'EMQ items', items, 'deleted-dups', sum(1 for o in OUT if o['new'].get('status') == 'deleted'))
