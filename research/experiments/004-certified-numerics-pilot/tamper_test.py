"""Negative controls: corrupted certificates that verify.py must REJECT.

A verifier that accepts everything is useless, so each case below changes
one thing that should break the certificate. Run: python tamper_test.py
"""
import copy
import json
import subprocess
import sys
import tempfile
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CERTS = os.path.join(HERE, "certificates")

def load(name):
    return json.load(open(os.path.join(CERTS, name + ".json")))

def bump(s, d):
    return repr(float(s) + d)

cases = []
c = load("allen-cahn-eps0.1"); c["abar"][0] = bump(c["abar"][0], 1e-6)
cases.append(("approximation moved by 1e-6, radius kept at 1e-12", c))
c = load("allen-cahn-eps0.1"); c["eps"] = "1/9"
cases.append(("different equation (eps 1/9) for the same solution", c))
# Note: scaling A_N by 0.5 is NOT a corruption. A is only a preconditioner and
# any A with Z < 1 gives a valid proof; the first draft of this test wrongly
# expected a rejection there. Scaling by 3 makes ||I - A DF|| about 2.
c = load("allen-cahn-eps0.1"); c["A_N"] = [[repr(float(x) * 3) for x in row] for row in c["A_N"]]
cases.append(("approximate inverse scaled by 3", c))
c = load("control-manufactured"); c["f_sine_coeffs_exact"][0] = "1/2"
cases.append(("forcing term changed", c))
c = load("grid3-swing"); c["alpha"] = repr(0.26)
cases.append(("claimed decay rate 0.26 exceeds the true 0.25", c))
c = load("grid3-swing"); c["theta_tilde"][0] = bump(c["theta_tilde"][0], 1e-6)
cases.append(("equilibrium moved by 1e-6, radius kept at 1e-12", c))
c = load("grid3-swing"); c["grid"]["P"]["2"] = "2.5"
cases.append(("injection 2.5 p.u. (no equilibrium near the old angles)", c))

fails = 0
with tempfile.TemporaryDirectory() as d:
    for i, (label, cert) in enumerate(cases):
        p = os.path.join(d, f"t{i}.json")
        json.dump(cert, open(p, "w"))
        out = subprocess.run([sys.executable, os.path.join(HERE, "verify.py"), p],
                             capture_output=True, text=True)
        rejected = out.returncode != 0 and out.stdout.startswith("REJECT")
        print(("ok   " if rejected else "FAIL ") + label)
        fails += not rejected
print(f"{len(cases) - fails}/{len(cases)} corrupted certificates rejected")
sys.exit(1 if fails else 0)
