import re, glob, json, random
items=[]
pat=re.compile(r'/--(.*?)-/\s*\n@\[category[^\]]*\]\s*\ntheorem\s+(\S+)(.*?):=\s*by\s*\n?\s*sorry', re.S)
for f in sorted(glob.glob('fc/FormalConjectures/ErdosProblems/*.lean')):
    src=open(f).read()
    # skip files with local defs / notation to keep statements self-contained
    if re.search(r'^(noncomputable )?(def|abbrev|structure|notation|local notation|variable)\b', src, re.M):
        continue
    for m in pat.finditer(src):
        doc=' '.join(m.group(1).split()); name=m.group(2); stmt=' '.join(m.group(3).split())
        if 'answer(' in stmt: continue
        if 60 < len(stmt) < 320 and 40 < len(doc) < 600:
            items.append({'file':f[3:],'name':name,'informal':doc,'formal':stmt})
print(len(items))
json.dump(items,open('fc_items.json','w'),indent=1)
