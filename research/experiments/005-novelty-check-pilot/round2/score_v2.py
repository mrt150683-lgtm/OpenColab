"""Score round 2 of the 005 pilot (54 items) per PROTOCOL-v2.md."""
import json, os
H = os.path.dirname(os.path.abspath(__file__))
L = lambda p: json.load(open(os.path.join(H, p)))
key = {k["sid"]: k for k in L("key_v2.json")}
r1 = {x["sid"]: x for f in ("../out005_pipeline_0.json", "../out005_pipeline_1.json") for x in L(f)}
pipe = {s: r1[s] for s in key if s in r1}
pipe.update({x["sid"]: x for x in L("out005_v2_pipeline_new.json")})
base = {x["sid"]: x for x in L("../out005_baseline.json") if x["sid"] in key}
abl = {x["sid"]: x for x in L("out005_v2_ablation_a.json") + L("out005_v2_ablation_b.json")}
# Hand-judged matches: the cited paper is (one of) the labelled prior works.
MATCH = {
 "pipeline": {"S04","S07","S09","S10","S13","S15","S21","S22","S23","S26","S30","S31","S33","S37","S39",
              "S40","S41","S43","S44","S45","S52"},
 "baseline": {"S30","S39"},          # S23 (survey) and S33 (related paper) are lenient matches only
 "ablation": {"S13","S15","S22","S33","S37","S39","S41","S52"},
}
# S23 in the ablation was found with a query naming authors not yet seen in results,
# which breaks the ablation rule, so it is not counted.
def score(out, name, items):
    prior = [s for s in items if key[s]["label"] == "PRIOR"]; new = [s for s in items if key[s]["label"] == "NEW"]
    hit = [s for s in prior if out[s]["verdict"] == "PRIOR" and s in MATCH[name]]
    ff = [s for s in new if out[s]["verdict"] == "PRIOR"]
    print(f"{name:9s} on {len(items)} items: detection {len(hit)}/{len(prior)} = {100*len(hit)/len(prior):.0f}%,"
          f" false flags {len(ff)}/{len(new)} {ff}")
    return len(hit) / len(prior), len(ff) / len(new)
allitems = sorted(key); r1items = [s for s in allitems if int(s[1:]) < 40]
print("Primary (all 54 items)")
d, f = score(pipe, "pipeline", allitems); score(abl, "ablation", allitems)
print("Round-1 items kept (36), where the baseline exists")
score(pipe, "pipeline", r1items); score(base, "baseline", r1items); score(abl, "ablation", r1items)
print("Sensitivity: S47 removed (its labelled prior work is from 2025, outside the pre-2025 search rule)")
score(pipe, "pipeline", [s for s in allitems if s != "S47"])
print("Decision rule (>=70% detection, <=20% false flags):", "MET" if d >= 0.70 and f <= 0.20 else "NOT MET")
