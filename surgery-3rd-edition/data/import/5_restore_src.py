"""Questions lost in the IDML parse and restored by the editor -> data/patches/500-restored.json"""
import json, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = [dict(new=dict(id='neck-0103', chapter='neck', order=54.5, type='MCQ', bank='Lange', source='', status='new', topics=['Medullary thyroid carcinoma'],
    notes='', images=[], src=dict(num=55),
    stem=('A 22-year-old man has a 2-cm thyroid nodule. His father, now deceased, had thyroid carcinoma and an abdominal tumour. '
          'Calcitonin is raised and fine-needle aspiration shows spindle cells with amyloid stroma. Which type of thyroid carcinoma is this?'),
    options=['Papillary carcinoma', 'Follicular carcinoma', 'Anaplastic carcinoma', 'Medullary carcinoma', 'Thyroid lymphoma'], answer='D',
    explanation='Raised calcitonin with amyloid stroma is medullary carcinoma (parafollicular C cells); a familial pattern suggests MEN2 (RET).'),
    why='Lange Q55 restored (lost in the IDML parse)')]
json.dump(OUT, open(os.path.join(ROOT, 'data', 'patches', '500-restored.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('restored', len(OUT))
