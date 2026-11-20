"""Score the 005 pilot. A flag counts as a hit only if its item is labelled PRIOR
and the cited work was judged (by hand, see MATCHES) to contain the result."""
import json, os
H = os.path.dirname(os.path.abspath(__file__))
key = {k["sid"]: k for k in json.load(open(os.path.join(H, "benchmark-labels.json")))}
pipe = {x["sid"]: x for f in ("out005_pipeline_0.json", "out005_pipeline_1.json")
        for x in json.load(open(os.path.join(H, f)))}
base = {x["sid"]: x for x in json.load(open(os.path.join(H, "out005_baseline.json")))}
# Hand judgement of whether each PRIOR flag names a paper containing the labelled result.
# "strict": the cited paper is (one of) the labelled prior works.
# "lenient": also accept a survey or related paper that plausibly contains it.
MATCHES = {
    "pipeline": {s: "strict" for s in ["S04", "S07", "S09", "S10", "S13", "S15", "S21", "S22",
                                         "S23", "S26", "S30", "S31", "S33", "S37", "S39"]},
    "baseline": {"S30": "strict", "S39": "strict", "S23": "lenient", "S33": "lenient"},
}
def score(out, name):
    prior = [s for s in key if key[s]["label"] == "PRIOR"]
    new = [s for s in key if key[s]["label"] == "NEW"]
    flags = [s for s in out if out[s]["verdict"] == "PRIOR"]
    strict = [s for s in flags if s in prior and MATCHES[name].get(s) == "strict"]
    lenient = [s for s in flags if s in prior and MATCHES[name].get(s) in ("strict", "lenient")]
    false = [s for s in flags if s in new]
    print(f"{name:9s} detection strict {len(strict)}/{len(prior)} ({100*len(strict)/len(prior):.0f}%), "
          f"lenient {len(lenient)}/{len(prior)}; false flags {len(false)}/{len(new)}")
    print("          missed PRIOR:", ", ".join(f"{s}(#{key[s]['id']})" for s in prior if s not in lenient))
score(pipe, "pipeline")
score(base, "baseline")
