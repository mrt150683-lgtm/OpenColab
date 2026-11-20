"""003 pilot: build a blind faithful/mutant set from formal-conjectures statements.
Registered mutation operators (one per mutant, first applicable in a random order):"""
import json, random, re, hashlib
random.seed(2026)
items = json.load(open('fc_items.json'))
# keep only top-level problem statements (not variants) to reduce near-duplicates
items = [x for x in items if '.variants.' not in x['name'] and 'parts' not in x['name']]
random.shuffle(items)
OPS = {
 'strict_flip':  (r'(?<![≤≥<>])<(?![=])', '≤'),
 'nonstrict_flip': (r'≤', '<'),
 'forall_exists': (r'∀', '∃'),
 'exists_forall': (r'∃(?!ᶠ)', '∀'),
 'atTop_atBot':  (r'\batTop\b', 'atBot'),
 'and_or':       (r'∧', '∨'),
 'literal_bump': (r'(?<![\w.])([2-9])(?![\w.])', None),
 'negate':       (None, None),
}
def mutate(stmt, rng):
    ops = list(OPS); rng.shuffle(ops)
    for op in ops:
        if op == 'negate':
            # negate the conclusion after the leading binder colon
            if stmt.startswith(': ¬'):
                return op, ': ' + stmt[3:].lstrip()
            if stmt.startswith(': '):
                return op, ': ¬(' + stmt[2:] + ')'
            continue
        pat, rep = OPS[op]
        m = re.search(pat, stmt)
        if not m: continue
        if op == 'literal_bump':
            new = str(int(m.group(1)) + 1)
            return op, stmt[:m.start()] + new + stmt[m.end():]
        return op, stmt[:m.start()] + rep + stmt[m.end():]
    return None, None
rng = random.Random(7)
faithful, mutants = [], []
for x in items:
    if len(faithful) < 30:
        faithful.append({**x, 'truth': 'faithful', 'op': None}); continue
    if len(mutants) < 30:
        op, s = mutate(x['formal'], rng)
        if op:
            mutants.append({**x, 'formal_original': x['formal'], 'formal': s, 'truth': 'mutant', 'op': op})
    if len(mutants) >= 30: break
allx = faithful + mutants
random.Random(99).shuffle(allx)
for i, x in enumerate(allx): x['qid'] = f'Q{i+1:02d}'
key = [{'qid': x['qid'], 'truth': x['truth'], 'op': x['op'], 'name': x['name'], 'file': x['file']} for x in allx]
blind = [{'qid': x['qid'], 'informal': x['informal'], 'formal': x['formal']} for x in allx]
json.dump(key, open('key003/answer-key.json', 'w'), indent=1)
json.dump(blind, open('blind-003.json', 'w'), indent=1, ensure_ascii=False)
json.dump(allx, open('key003/full.json', 'w'), indent=1, ensure_ascii=False)
print('faithful', len(faithful), 'mutants', len(mutants))
from collections import Counter; print(Counter(m['op'] for m in mutants))
print('key sha256', hashlib.sha256(open('key003/answer-key.json','rb').read()).hexdigest())
