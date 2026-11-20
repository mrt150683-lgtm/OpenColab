"""Score both rounds of the 003 pilot from the committed verdict files."""
import json, os
H = os.path.dirname(os.path.abspath(__file__))
def load(p): return json.load(open(os.path.join(H, p)))
def report(name, key, flags, excl=()):
    ids = [i for i in key if i not in excl]
    m = [i for i in ids if key[i] == "mutant"]; f = [i for i in ids if key[i] == "faithful"]
    tp = [i for i in m if flags[i]]; fp = [i for i in f if flags[i]]
    print(f"  {name:28s} detected {len(tp)}/{len(m)}  false alarms {len(fp)}/{len(f)}"
          f"  missed {[i for i in m if not flags[i]]}  false {fp}")
# Round 1
k1 = {x["qid"]: x["truth"] for x in load("round1/answer-key.json")}
A1 = {}
for t in open(os.path.join(H, "round1/A_verdicts.txt")).read().strip().split("|"):
    q, v, p = t.split(); A1[q] = v == "U"
B1 = {x["qid"]: x["verdict"] == "UNFAITHFUL" for x in load("round1/B2_verdicts.json")}
C1 = {q: A1[q] or B1[q] for q in k1}
for excl, tag in [((), "all 60"), (("Q09", "Q45"), "Q09 and Q45 removed as equivalent mutants")]:
    print("Round 1 (syntactic mutations),", tag)
    report("direct judge", k1, A1, excl); report("back-translation", k1, B1, excl); report("either (registered combo)", k1, C1, excl)
# Round 2
k2 = {x["tid"]: x["truth"] for x in load("round2/round2_key.json")}
A2 = {x["tid"]: x["verdict"] == "UNFAITHFUL" for x in load("round2/R2_A_verdicts.json")}
B2 = {x["tid"]: x["verdict"] == "UNFAITHFUL" for x in load("round2/R2_B2_verdicts.json")}
C2 = {t: A2[t] or B2[t] for t in k2}
print("Round 2 (adversarial, subtle mutations), all 40")
report("direct judge", k2, A2); report("back-translation", k2, B2); report("either (registered combo)", k2, C2)
