"""Index topics for questions that have none: match a curated list of surgical terms against the key, explanation and stem.
Writes data/patches/600-topics.json (run after the other patches; rebuild_data.sh applies it).
"""
import json, os, re, collections

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
Q = json.load(open(os.path.join(ROOT, 'data', 'questions.json'), encoding='utf-8'))

# index heading: regex (case-insensitive)
T = [
    ('Thyroid nodule', r'thyroid nodule|solitary nodule'), ('Papillary thyroid carcinoma', r'papillary (thyroid )?carcinoma'),
    ('Follicular thyroid carcinoma', r'follicular (thyroid )?carcinoma|follicular neoplasm'), ('Medullary thyroid carcinoma', r'medullary'),
    ('Anaplastic thyroid carcinoma', r'anaplastic'), ('Thyroid lymphoma', r'thyroid lymphoma'), ('Graves disease', r'graves'),
    ('Toxic multinodular goitre', r'toxic multinodular|multinodular'), ('Goitre', r'goitre|goiter'), ('Thyroiditis', r'thyroiditis'),
    ('Thyroidectomy', r'thyroidectomy'), ('Recurrent laryngeal nerve', r'recurrent laryngeal'), ('Hypocalcaemia', r'hypocalc'),
    ('Thyroglossal cyst', r'thyroglossal'), ('Branchial cyst', r'branchial'), ('Cystic hygroma', r'cystic hygroma|lymphatic malformation'),
    ('Carotid body tumour', r'carotid body'), ('Lymphadenopathy', r'lymphadenopathy|cervical node|neck node'),
    ('Primary hyperparathyroidism', r'hyperparathyroidism|parathyroid adenoma'), ('Parathyroid', r'parathyroid'),
    ('MEN syndromes', r'\bMEN ?[12]|multiple endocrine neoplasia'), ('Phaeochromocytoma', r'ph(a)?eochromocytoma'),
    ('Primary hyperaldosteronism', r"conn'?s|hyperaldosteronism"), ('Cushing syndrome', r'cushing'), ('Adrenal incidentaloma', r'incidentaloma|adrenal (mass|adenoma)'),
    ('Insulinoma', r'insulinoma'), ('Gastrinoma', r'gastrinoma|zollinger'), ('Neuroendocrine tumour', r'neuroendocrine|carcinoid'),
    ('Fibroadenoma', r'fibroadenoma'), ('Breast cyst', r'breast cyst|\bcyst\b.*breast'), ('Duct ectasia', r'duct ectasia|periductal mastitis'),
    ('Intraductal papilloma', r'intraductal papilloma'), ('Breast abscess', r'breast abscess|lactational mastitis|mastitis'),
    ('Fat necrosis', r'fat necrosis'), ('Gynaecomastia', r'gyn(a)?ecomastia'), ('Mastalgia', r'mastalgia|breast pain'),
    ('Nipple discharge', r'nipple discharge'), ('Triple assessment', r'triple assessment'), ('Breast screening', r'mammograph|breast screening'),
    ('BRCA', r'brca'), ('DCIS', r'ductal carcinoma in situ|\bdcis\b'), ('Breast cancer', r'breast (cancer|carcinoma)|carcinoma of the breast'),
    ('Paget disease of the nipple', r"paget"), ('Inflammatory breast cancer', r'inflammatory breast'), ('Sentinel lymph node biopsy', r'sentinel'),
    ('Axillary clearance', r'axillary (clearance|dissection|node clearance)'), ('Mastectomy', r'mastectomy'), ('Tamoxifen', r'tamoxifen'),
    ('Aromatase inhibitors', r'aromatase|letrozole|anastrozole'), ('HER2', r'her2|trastuzumab'), ('Phyllodes tumour', r'phyllodes'),
    ('Parotid tumour', r'parotid|pleomorphic adenoma|warthin'), ('Sialolithiasis', r'sialolith|salivary (stone|calculus)|submandibular'),
    ('Facial nerve', r'facial nerve'), ('Achalasia', r'achalasia'), ('Oesophageal spasm', r'oesophageal spasm|esophageal spasm'),
    ('GORD', r'reflux|gord|gerd'), ('Hiatus hernia', r'hiatus hernia|hiatal hernia|para-?oesophageal'), ('Barrett oesophagus', r'barrett'),
    ('Oesophageal cancer', r'(o)?esophageal (cancer|carcinoma|adenocarcinoma|squamous)|carcinoma of the (o)?esophagus'),
    ('Oesophageal perforation', r'boerhaave|oesophageal perforation|esophageal perforation'), ('Pharyngeal pouch', r'pharyngeal pouch|zenker'),
    ('Plummer–Vinson syndrome', r'plummer'), ('Dysphagia', r'dysphagia'), ('Mallory–Weiss tear', r'mallory'),
    ('Oesophageal varices', r'varic(es|eal)'), ('Peptic ulcer', r'peptic ulcer|duodenal ulcer|gastric ulcer'),
    ('Perforated peptic ulcer', r'perforated (peptic|duodenal|gastric)'), ('Helicobacter pylori', r'pylori'),
    ('Gastric outlet obstruction', r'gastric outlet|pyloric stenosis'), ('Gastric cancer', r'gastric (cancer|carcinoma|adenocarcinoma)|carcinoma of the stomach'),
    ('GIST', r'\bgist\b|gastrointestinal stromal'), ('Upper GI bleeding', r'upper (gi|gastrointestinal) bleed|haematemesis|hematemesis|melaena|melena'),
    ('Lower GI bleeding', r'lower (gi|gastrointestinal) bleed|rectal bleeding'), ('Angiodysplasia', r'angiodysplasia'),
    ('Meckel diverticulum', r'meckel'), ('Small bowel obstruction', r'small[- ]bowel obstruction'), ('Large bowel obstruction', r'large[- ]bowel obstruction'),
    ('Intestinal obstruction', r'intestinal obstruction|bowel obstruction'), ('Adhesions', r'adhesion'), ('Paralytic ileus', r'\bileus\b'),
    ('Pseudo-obstruction', r'pseudo-?obstruction|ogilvie'), ('Sigmoid volvulus', r'sigmoid volvulus'), ('Caecal volvulus', r'ca?ecal volvulus'),
    ('Gallstone ileus', r'gallstone ileus'), ('Crohn disease', r'crohn'), ('Ulcerative colitis', r'ulcerative colitis'),
    ('Toxic megacolon', r'toxic megacolon'), ('Ischaemic colitis', r'isch(a)?emic colitis'), ('Mesenteric ischaemia', r'mesenteric (isch|angina|artery occlusion)'),
    ('Diverticular disease', r'diverticul(ar|osis|itis)'), ('Colorectal cancer', r'colorectal|colon(ic)? (cancer|carcinoma)|rectal (cancer|carcinoma)|ca?ecal carcinoma|sigmoid carcinoma'),
    ('Colorectal polyps', r'polyp|adenomatous|villous adenoma|tubular adenoma'), ('Familial adenomatous polyposis', r'familial adenomatous|\bfap\b'), ('Lynch syndrome', r'lynch|hnpcc'),
    ('Stoma', r'\bstoma|colostomy|ileostomy'), ('Hartmann procedure', r'hartmann'), ('Appendicitis', r'appendic'), ('Alvarado score', r'alvarado'),
    ('Haemorrhoids', r'h(a)?emorrhoid|piles'), ('Anal fissure', r'fissure'), ('Perianal abscess', r'perianal abscess|anorectal abscess|ischiorectal'),
    ('Fistula-in-ano', r'fistula[- ]in[- ]ano|anal fistula|fistulotomy|seton'), ('Pilonidal sinus', r'pilonidal'), ('Rectal prolapse', r'rectal prolapse'),
    ('Anal cancer', r'anal (cancer|carcinoma)|squamous cell carcinoma of the anus'), ('Pruritus ani', r'pruritus ani'),
    ('Intussusception', r'intussusception'), ('Pyloric stenosis', r'pyloric stenosis|pyloromyotomy'), ('Malrotation', r'malrotation|volvulus neonatorum|midgut volvulus'),
    ('Hirschsprung disease', r'hirschsprung'), ('Duodenal atresia', r'duodenal atresia|double bubble'), ('Necrotising enterocolitis', r'necroti[sz]ing enterocolitis|\bnec\b'),
    ('Oesophageal atresia', r'(o)?esophageal atresia|tracheo-?(o)?esophageal fistula'), ('Anorectal malformation', r'imperforate anus|anorectal malformation|psarp'),
    ('Gastroschisis', r'gastroschisis'), ('Exomphalos', r'exomphalos|omphalocele'), ('Congenital diaphragmatic hernia', r'diaphragmatic hernia|bochdalek'),
    ('Biliary atresia', r'biliary atresia'), ('Cleft lip and palate', r'cleft'), ('Peritonitis', r'peritonitis'), ('Acute abdomen', r'acute abdomen'),
    ('Abdominal aortic aneurysm', r'aortic aneurysm|\baaa\b'), ('Acute limb ischaemia', r'acute limb'), ('Abdominal trauma', r'abdominal trauma|blunt abdominal|penetrating abdominal|fast scan|\bfast\b'),
    ('Splenic injury', r'splenic (injury|rupture|laceration)|ruptured spleen'), ('Liver injury', r'liver (injury|laceration|trauma)'),
    ('Splenectomy', r'splenectomy'), ('Post-splenectomy sepsis', r'post-?splenectomy|opsi\b'), ('Hypersplenism', r'hypersplenism|splenomegaly'),
    ('Amoebic liver abscess', r'amoebic|amebic|entamoeba'), ('Pyogenic liver abscess', r'pyogenic (liver )?abscess|liver abscess'),
    ('Hydatid disease', r'hydatid|echinococc'), ('Hepatocellular carcinoma', r'hepatocellular|hepatoma'), ('Liver metastases', r'liver metasta|hepatic metasta'),
    ('Haemangioma', r'h(a)?emangioma'), ('Hepatic adenoma', r'hepatic adenoma|liver cell adenoma'), ('Focal nodular hyperplasia', r'focal nodular'),
    ('Portal hypertension', r'portal hypertension'), ('Cirrhosis', r'cirrho'), ('Budd–Chiari syndrome', r'budd'),
    ('Gallstones', r'gallstone|cholelithiasis'), ('Biliary colic', r'biliary colic'), ('Acute cholecystitis', r'cholecystitis'),
    ('Empyema of gallbladder', r'empyema of the gallbladder|mucoc(o)?ele'), ('Cholecystectomy', r'cholecystectomy'), ('Bile duct injury', r'bile duct injury|bile leak|bile duct injur'),
    ('Choledocholithiasis', r'choledocholithiasis|cbd stone|common bile duct stone|stones? in the (common )?bile duct'),
    ('Ascending cholangitis', r'cholangitis|charcot'), ('Obstructive jaundice', r'obstructive jaundice|cholestatic'), ('Jaundice', r'jaundice'),
    ('Mirizzi syndrome', r'mirizzi'), ('Cholangiocarcinoma', r'cholangiocarcinoma|klatskin'), ('Gallbladder cancer', r'gallbladder (cancer|carcinoma)|carcinoma of the gallbladder'),
    ('Choledochal cyst', r'choledochal'), ('Primary sclerosing cholangitis', r'sclerosing cholangitis'), ('ERCP', r'\bercp\b'), ('MRCP', r'\bmrcp\b'),
    ('Acute pancreatitis', r'acute pancreatitis|gallstone pancreatitis'), ('Chronic pancreatitis', r'chronic pancreatitis'), ('Pancreatic pseudocyst', r'pseudocyst'),
    ('Pancreatic cancer', r'pancreatic (cancer|carcinoma|adenocarcinoma)|carcinoma of the (head of the )?pancreas|periampullary'),
    ('IPMN', r'intraductal papillary mucinous|\bipmn\b'), ('Whipple procedure', r'whipple|pancreaticoduodenectomy'), ('Glasgow score', r'glasgow (score|criteria)|ranson'),
    ('Inguinal hernia', r'inguinal hernia|indirect inguinal|direct inguinal'), ('Femoral hernia', r'femoral hernia'), ('Umbilical hernia', r'umbilical hernia|paraumbilical'),
    ('Incisional hernia', r'incisional hernia'), ('Epigastric hernia', r'epigastric hernia'), ('Spigelian hernia', r'spigelian'), ('Obturator hernia', r'obturator hernia'),
    ('Richter hernia', r'richter'), ('Strangulated hernia', r'strangulat|incarcerat'), ('Hernia repair', r'lichtenstein|herniorrhaphy|hernioplasty|herniotomy|shouldice|mesh repair|\btep\b|\btapp\b'),
    ('Urinary tract infection', r'urinary tract infection|\buti\b|cystitis'), ('Acute pyelonephritis', r'pyelonephritis'), ('Prostatitis', r'prostatitis'),
    ('Tuberculosis', r'tuberculo|\btb\b'), ('Renal colic', r'renal colic|ureteric colic'), ('Urinary stones', r'(urinary|renal|ureteric|bladder|kidney|staghorn|struvite|cystine|uric acid|calcium oxalate) (stone|calcul)|urolithiasis|nephrolithiasis'),
    ('ESWL', r'eswl|lithotripsy'), ('PCNL', r'pcnl|percutaneous nephrolithotomy'), ('Ureteroscopy', r'ureteroscop'),
    ('Renal cell carcinoma', r'renal cell|hypernephroma|\brcc\b'), ('Wilms tumour', r'wilms|nephroblastoma'), ('Angiomyolipoma', r'angiomyolipoma'),
    ('Haematuria', r'h(a)?ematuria'), ('Bladder cancer', r'bladder (cancer|carcinoma|tumou?r)|transitional cell|urothelial|turbt'),
    ('Urinary retention', r'urinary retention|retention of urine|(acute|chronic) retention|clot retention'), ('Benign prostatic hyperplasia', r'benign prostatic|\bbph\b|\bluts\b|lower urinary tract symptoms'),
    ('Prostate cancer', r'prostat(e|ic) (cancer|carcinoma|adenocarcinoma)|gleason'), ('PSA', r'\bpsa\b|prostate-specific'), ('TURP', r'\bturp\b|transurethral resection of the prostate'),
    ('Urethral stricture', r'urethral stricture|stricture of the urethra'), ('Urethral injury', r'urethral (injury|rupture|trauma)|blood at the (urethral )?meatus'),
    ('Bladder injury', r'bladder (injury|rupture)'), ('Renal trauma', r'renal (injury|trauma)|kidney injury'), ('Ureteric injury', r'ureteric (injury|ligation)'),
    ('Testicular torsion', r'torsion'), ('Epididymo-orchitis', r'epididym'), ('Hydrocele', r'hydroc(o)?ele'), ('Varicocele', r'varic(o)?cele'),
    ('Testicular tumour', r'testicular (tumou?r|cancer)|seminoma|teratoma|germ cell'), ('Undescended testis', r'undescended|cryptorchid|orchidopexy'),
    ('Hypospadias', r'hypospadias'), ('Phimosis', r'phimosis|circumcision'), ('Priapism', r'priapism'), ('Fournier gangrene', r'fournier'),
    ('Vesicoureteric reflux', r'vesico-?ureteric reflux|\bvur\b'), ('PUJ obstruction', r'pelviureteric|puj|pyeloplasty'), ('Posterior urethral valves', r'posterior urethral valve'),
    ('Penile cancer', r'penile (cancer|carcinoma)|carcinoma of the penis'), ('Erectile dysfunction', r'erectile'),
    ('ATLS primary survey', r'primary survey|\batls\b|airway'), ('Tension pneumothorax', r'tension pneumothorax'), ('Haemothorax', r'h(a)?emothorax'),
    ('Flail chest', r'flail'), ('Cardiac tamponade', r'tamponade'), ('Head injury', r'head injur|glasgow coma|\bgcs\b|subdural|extradural|epidural ha'),
    ('Cervical spine injury', r'cervical spine|c-spine'), ('Burns', r'burn'), ('Wound healing', r'wound|suture|laceration'), ('Skin grafts and flaps', r'graft|flap'),
    ('Tetanus', r'tetanus'), ('Gas gangrene', r'gas gangrene|clostridi'), ('Compartment syndrome', r'compartment syndrome|fasciotomy'), ('Fat embolism', r'fat embol'),
    ('Hypovolaemic shock', r'hypovol|haemorrhagic shock|hemorrhagic shock|class (i|ii|iii|iv) h'), ('Septic shock', r'septic shock|sepsis'),
    ('Cardiogenic shock', r'cardiogenic'), ('Neurogenic shock', r'neurogenic'), ('Anaphylaxis', r'anaphyla'), ('Blood transfusion', r'transfusion|massive haemorrhage'),
    ('Fluid therapy', r'crystalloid|colloid|hartmann.s solution|normal saline|fluid (therapy|resuscitation|replacement)'),
    ('Hyponatraemia', r'hyponatr'), ('Hypernatraemia', r'hypernatr'), ('Hypokalaemia', r'hypokal'), ('Hyperkalaemia', r'hyperkal'), ('Hypomagnesaemia', r'hypomagn'),
    ('Acid–base disorders', r'acidosis|alkalosis'), ('Metabolic response to injury', r'metabolic response|stress response|catabol|ebb'),
    ('Enhanced recovery', r'enhanced recovery|\beras\b'), ('Nutrition', r'nutrition|\btpn\b|parenteral|enteral|jejunostomy|gastrostomy|refeeding'),
    ('Nasogastric tube', r'nasogastric|ng tube'), ('Urethral catheterisation', r'catheter'), ('Anaesthesia', r'an(a)?esthesia|an(a)?esthetic'),
    ('Postoperative complications', r'postoperative|post-?op'), ('Venous thromboembolism', r'thromboembolism|\bdvt\b|deep vein|pulmonary embol'),
    ('Bariatric surgery', r'bariatric|gastric bypass|sleeve gastrectomy|gastric band|obesity|\bbmi\b'), ('Leriche syndrome', r'leriche'), ('Buerger disease', r'buerger'),
]
PAT = [(h, re.compile(p, re.I)) for h, p in T]


def text_parts(q):
    if q['type'] == 'MCQ':
        key = ' '.join(q['options'][ord(c) - 65] for c in q['answer'] if ord(c) - 65 < len(q['options']))
        return [key, q.get('explanation', ''), q.get('stem', '')]
    return [q.get('theme', '')] + [it['explanation'] for it in q['items']] + [' '.join(q['options'])]


ops, cnt = [], collections.Counter()
for q in Q:
    if q.get('status') == 'deleted' or q.get('topics'):
        continue
    found = []
    for part in text_parts(q):
        hits = sorted(((m.start(), h) for h, p in PAT for m in [p.search(part or '')] if m), key=lambda x: x[0])
        for _, h in hits:
            if h not in found:
                found.append(h)
    # drop broad headings when a specific one exists
    broad = {'Jaundice', 'Urinary stones', 'Wound healing', 'Postoperative complications', 'Intestinal obstruction', 'Parathyroid', 'Dysphagia',
             'Urinary tract infection', 'Breast screening', 'Haematuria', 'Urethral catheterisation', 'ATLS primary survey'}
    spec = [h for h in found if h not in broad]
    topics = (spec or found)[:3] if q['type'] == 'MCQ' else (spec or found)[:4]
    if topics:
        ops.append(dict(id=q['id'], set=dict(topics=topics), why='index topics'))
        cnt['tagged'] += 1
    else:
        cnt['none'] += 1
json.dump(ops, open(os.path.join(ROOT, 'data', 'patches', '600-topics.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(dict(cnt))
