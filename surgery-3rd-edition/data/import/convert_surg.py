"""Convert the parsed Surgery 1 Version 2.0 IDML (data/source/parsed.json, made by data/source/readidml.py + parse.py) into data/questions.json + data/book.json."""
import json, os, re, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
SRC = os.path.join(ROOT, 'data', 'source', 'parsed.json')

PARTS = ['Neck Lumps & Endocrine', 'Breast', 'Gastrointestinal Tract', 'Paediatric Surgery', 'Abdomen', 'Urology', 'Trauma & Critical Care']
CH = [  # id, part index, title, short, colour, intro
    ('neck', 0, 'Neck Lumps, Thyroid & Parathyroid', 'Neck Lumps', '1F7A8C', 'Salivary, thyroid, parathyroid and other neck swellings: triangles of the neck, FNA, thyroid cancer and hyperparathyroidism.'),
    ('endo', 0, 'Endocrine Surgery', 'Endocrine', '2C6E91', 'Adrenal, pituitary and pancreatic endocrine tumours, MEN syndromes and the surgical endocrine work-up.'),
    ('neckemq', 0, 'Neck Lumps & Endocrine EMQs', 'Neck EMQs', '265F7E', 'Extended matching questions on neck swellings, dysphagia, thyroid disease and skin lumps.'),
    ('bbreast', 1, 'Benign Breast Disorders', 'Benign Breast', 'B8467A', 'Breast assessment and triple assessment, fibroadenoma, cysts, mastalgia, nipple discharge, infection and gynaecomastia.'),
    ('bca', 1, 'Breast Cancer', 'Breast Cancer', '9C2F62', 'Screening, risk and BRCA, DCIS and invasive cancer, staging, surgery, sentinel node biopsy and adjuvant therapy.'),
    ('breastemq', 1, 'Breast EMQs', 'Breast EMQs', '7F2853', 'Extended matching questions on breast lumps, nipple discharge, investigation and treatment of breast cancer.'),
    ('saliv', 2, 'Salivary Glands', 'Salivary', 'C0612B', 'Parotid and submandibular swellings: sialolithiasis, sialadenitis, pleomorphic adenoma, Warthin tumour and the facial nerve.'),
    ('oeso', 2, 'Oesophagus', 'Oesophagus', 'B4552A', 'Dysphagia, achalasia, reflux and hiatus hernia, Barrett oesophagus, perforation and oesophageal cancer.'),
    ('stom', 2, 'Stomach & Duodenum', 'Stomach', 'A44B27', 'Peptic ulcer and its complications, gastric outlet obstruction, gastric cancer, GIST and bariatric anatomy.'),
    ('intest', 2, 'Small & Large Intestine', 'Intestine', '944224', 'Intestinal obstruction, appendicitis, inflammatory bowel disease, diverticular disease, volvulus, polyps and colorectal cancer.'),
    ('anus', 2, 'Anorectal Disorders', 'Anorectal', '843A21', 'Haemorrhoids, fissure, abscess and fistula, pilonidal disease, prolapse and anal cancer.'),
    ('gibleed', 2, 'Gastrointestinal Bleeding', 'GI Bleeding', '74321E', 'Upper and lower GI bleeding: resuscitation, risk scores, endoscopy, varices, angiodysplasia and diverticular bleeding.'),
    ('gitum', 2, 'Gastrointestinal Tumours', 'GI Tumours', '6C2E1C', 'Oesophageal, gastric, small-bowel, colorectal and anal tumours: polyps, polyposis syndromes, staging and treatment.'),
    ('gitemq', 2, 'Gastrointestinal EMQs', 'GIT EMQs', '64291A', 'Extended matching questions on the acute abdomen, dysphagia, GI bleeding, hernias, anorectal and hepatobiliary disease.'),
    ('paed', 3, 'Paediatric Surgery', 'Paediatric', '3E8E4F', 'Pyloric stenosis, intussusception, malrotation, Hirschsprung disease, atresias, NEC, hernias and the neonatal abdomen.'),
    ('paedemq', 3, 'Paediatric Surgery EMQs', 'Paediatric EMQs', '2F7440', 'Extended matching questions on vomiting infants, neonatal obstruction and the paediatric acute abdomen.'),
    ('acute', 4, 'Acute Abdomen & Abdominal Trauma', 'Acute Abdomen', '5A4FA3', 'Assessment of the acute abdomen, peritonitis and perforation, and blunt and penetrating abdominal trauma.'),
    ('liver', 4, 'Liver', 'Liver', '50479A', 'Liver abscess, hydatid cyst, benign and malignant liver tumours, portal hypertension and liver trauma.'),
    ('gb', 4, 'Gallbladder & Biliary Tree', 'Biliary', '463F8E', 'Gallstones, cholecystitis, cholangitis, obstructive jaundice, bile-duct injury and cholangiocarcinoma.'),
    ('panc', 4, 'Pancreas', 'Pancreas', '3D3782', 'Acute and chronic pancreatitis, pseudocyst, pancreatic cancer and periampullary tumours.'),
    ('spleen', 4, 'Spleen', 'Spleen', '352F76', 'Splenic trauma, splenomegaly, indications for splenectomy and post-splenectomy sepsis.'),
    ('adrenal', 4, 'Adrenal Gland', 'Adrenal', '2E2869', 'Phaeochromocytoma, Conn and Cushing syndromes, incidentaloma and adrenal surgery.'),
    ('hernia', 4, 'Hernias & Abdominal Wall', 'Hernias', '27225C', 'Inguinal, femoral, umbilical, incisional and rare hernias: anatomy, complications and repair.'),
    ('abdemq', 4, 'Abdomen EMQs', 'Abdomen EMQs', '211D50', 'Extended matching questions on abdominal pain, masses, splenomegaly, pancreatic and hepatobiliary disease.'),
    ('uti', 5, 'Urinary Tract Infection', 'UTI', '1E8A87', 'Cystitis, pyelonephritis, prostatitis, renal abscess and urinary tuberculosis.'),
    ('stone', 5, 'Urinary Stones', 'Stones', '1A7B78', 'Renal colic, imaging, medical expulsive therapy, ESWL, ureteroscopy and PCNL.'),
    ('renal', 5, 'Renal Tumours', 'Renal Tumours', '176D6A', 'Renal cell carcinoma, Wilms tumour, angiomyolipoma and the renal mass.'),
    ('urogen', 5, 'Urological Investigation & Haematuria', 'Uro Investigation', '145F5C', 'Haematuria work-up, urinalysis, imaging and endoscopy of the urinary tract.'),
    ('uroemerg', 5, 'Urological Emergencies & Trauma', 'Uro Emergencies', '12524F', 'Urinary retention, testicular torsion, priapism, Fournier gangrene and renal, bladder and urethral injury.'),
    ('prostate', 5, 'Prostate', 'Prostate', '0F4643', 'Benign prostatic hyperplasia, LUTS, PSA and prostate cancer.'),
    ('congur', 5, 'Congenital Urology', 'Congenital Uro', '0D3B39', 'Undescended testis, hypospadias, PUJ obstruction, vesicoureteric reflux and posterior urethral valves.'),
    ('scrotum', 5, 'Scrotum & Testis', 'Scrotum', '0B3230', 'Hydrocele, varicocele, epididymo-orchitis, scrotal swellings and testicular tumours.'),
    ('bladder', 5, 'Bladder Tumours', 'Bladder', '0A2A28', 'Haematuria, transitional cell carcinoma, TURBT, cystectomy and urinary diversion.'),
    ('uroemq', 5, 'Urology EMQs', 'Urology EMQs', '082322', 'Extended matching questions on haematuria, LUTS, scrotal swellings, urological investigation and emergencies.'),
    ('trauma', 6, 'Trauma', 'Trauma', 'B23A3A', 'ATLS primary survey, airway, chest, head and limb injuries, and burns.'),
    ('metab', 6, 'Metabolic Response to Trauma', 'Metabolic', 'A03434', 'The stress response, fluids, electrolytes and nutrition in the surgical patient.'),
    ('shock', 6, 'Shock', 'Shock', '8E2E2E', 'Classes of haemorrhage, types of shock, resuscitation and transfusion.'),
    ('obesity', 6, 'Obesity & Bariatric Surgery', 'Obesity', '7C2828', 'Indications for bariatric surgery, operations and their complications.'),
    ('extraemq', 6, 'Trauma & Perioperative EMQs', 'Trauma EMQs', '6A2222', 'Extended matching questions on shock, trauma, burns, perioperative care and postoperative complications.'),
]
LOCAL = ['39th Batch Exams', 'Ministerial Exam', 'Formative', 'Previous Years']
BANKS = [('39th Batch Exams', 'Block, end-induction and final papers of the 39th batch, recalled'),
         ('Ministerial Exam', 'Ministerial evaluation examinations'),
         ('Formative', 'College formative examinations'),
         ('Previous Years', 'Previous-years college examinations'),
         ('Essay to MCQ', 'College essay questions converted to MCQs'),
         ('Bailey & Love', "After Bailey & Love's Short Practice of Surgery MCQs & EMQs"),
         ('Lange', 'After Lange Review of Surgery'),
         ('SBA', 'Single best answers in surgery'),
         ('Oxford', 'After the Oxford Specialty Training / Oxford surgery questions'),
         ('PreTest', 'After PreTest Surgery'),
         ('Get Ahead', 'After Get ahead! Surgery MCQs & EMQs'),
         ('Crash Course', 'After Crash Course Surgery SBAs & EMQs'),
         ('Irfan', 'Irfan surgery EMQ collection')]


def main():
    R = json.load(open(SRC, encoding='utf-8'))
    seq = collections.Counter()
    Q = []
    chapter_order = [c[0] for c in CH]
    for r in R:
        cid = r['chapter']
        seq[cid] += 1
        qid = '%s-%04d' % (cid, seq[cid])
        base = dict(id=qid, chapter=cid, order=r['order'], type=r['type'], bank=r['bank'], source=r.get('sub', ''),
                    status='expanded', topics=[], notes='', images=[])
        if r['type'] == 'MCQ':
            stem = r['stem']
            if r.get('case'):
                stem = r['case'].strip() + ' ' + stem
            base.update(stem=stem.strip(), options=r['options'], answer=r['answer'], explanation=r['explanation'].strip(),
                        images=['pic/' + x for x in r.get('images', [])], src=dict(num=r['num']))
            base['orig'] = dict(stem=base['stem'], options=list(r['options']), answer=r['answer'], explanation=base['explanation'])
        else:
            n = len(r['options'])
            items = [dict(n=i['n'], stem=i['stem'].strip(), answer=i['answer'], explanation=i['explanation'].strip(),
                          images=['pic/' + x for x in i.get('images', [])]) for i in r['items']]
            base.update(theme=r['theme'], options=r['options'], option_letters=[chr(65 + k) for k in range(n)], items=items,
                        stem='', answer='', explanation='', images=['pic/' + x for x in r.get('images', [])], src=dict(label=r['theme_label']))
            base['orig'] = dict(theme=r['theme'], options=list(r['options']), items=[dict(it) for it in items])
            if r.get('unparsed'):
                base['notes'] = 'unparsed: ' + ' | '.join(r['unparsed'])[:500]
        Q.append(base)
    json.dump(Q, open(os.path.join(ROOT, 'data', 'questions.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    book = dict(title='Surgery Bank', volume='Surgery 1 — General Surgery', edition='3rd Edition / 2026',
                authors=['Ruqaya Mohammed Kadhim', 'Abdullah Musab Jefferz'], team='118 Team', telegram='https://t.me/AR_med118',
                file_name='Surgery-Bank-Surgery-1-3rd-Edition', cover=dict(image='', credit=''), layout=dict(answers_every=25),
                banks=[dict(name=n, blurb=b) for n, b in BANKS],
                texts=dict(cover_lines=['SURGERY', 'BANK'],
                           tagline='MCQs and EMQs with short explanations and step-by-step management flowcharts.',
                           back_headline='Practise like the exam. Learn from every answer.',
                           back_points=['{total} questions across {chapters} chapters, numbered by source',
                                        'Management flowcharts updated to current guidelines in every chapter',
                                        'Two-to-three-line explanations',
                                        'Repeated questions merged with a note of where they were asked']),
                contributors=dict(data=['Huda Mahdi N.', 'Naqaa Zuhair Abod', 'Rafal Raheem M.', 'Russul Falah R.', 'Mariam Safeer D.'],
                                  participants=['Zahraa Mohammed Talib', 'Moheib Mohammed Burhan', 'Mohammed Ali Fadhil Hasson']),
                parts=PARTS,
                chapters=[dict(id=c[0], order=i + 1, part=PARTS[c[1]], title=c[2], short=c[3], color=c[4], intro=c[5], keywords=[],
                               divider=dict(image='', credit=''), summaries=[]) for i, c in enumerate(CH)])
    json.dump(book, open(os.path.join(ROOT, 'data', 'book.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(len(Q), collections.Counter(q['type'] for q in Q))


if __name__ == '__main__':
    main()
