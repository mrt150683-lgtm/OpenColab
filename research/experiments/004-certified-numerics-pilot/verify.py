"""Independent verifier for 004 pilot certificates.

Uses only python-flint (Arb ball arithmetic) and the standard library.
It does not import solver.py. Every float in a certificate is read as the
exact binary number it denotes; every bound is an Arb enclosure.

Usage: python verify.py certificates/*.json
Exit code 0 only if every certificate is accepted.
"""
import json
import sys
import time
from fractions import Fraction
from flint import arb, arb_mat, ctx

ctx.prec = 128

def X(s):
    """Exact arb from a decimal float repr or a rational string."""
    if "/" in s:
        q = Fraction(s)
        return arb(q.numerator) / arb(q.denominator)
    # float repr -> exact binary value via Fraction(float)
    q = Fraction(float(s))
    return arb(q.numerator) / arb(q.denominator)

def upper(x):
    return x.mid() + x.rad()

# ---------------- sine-series BVP  eps u'' + u - u^3 = f -----------------

def odd(a):
    """dict k -> coeff for the odd extension, k in Z\\{0}."""
    s = {}
    for k, v in enumerate(a, start=1):
        s[k] = v
        s[-k] = -v
    return s

def conv(p, q):
    out = {}
    for i, x in p.items():
        for j, y in q.items():
            out[i + j] = out.get(i + j, arb(0)) + x * y
    return out

def sine_part(c, scale):
    """Sine coefficients k>=1 of a trilinear product given full convolution c."""
    return {k: scale * v for k, v in c.items() if k >= 1}

def verify_sine(c):
    eps = X(c["eps"])                   # exact rational string, e.g. "1/10"
    N = c["N"]
    a = [X(s) for s in c["abar"]]
    f = {k: X(s) for k, s in enumerate(c["f_sine_coeffs_exact"], start=1)}
    lam = lambda k: 1 - eps * k * k
    A = arb_mat([[X(s) for s in row] for row in c["A_N"]])
    r = arb(c["claimed_radius"])
    quarter = arb(1) / 4

    s = odd(a)
    ss = conv(s, s)                     # cosine coefficients * (-4) of u^2
    sss = conv(ss, s)
    cube = sine_part(sss, -quarter)     # sine coeffs of u^3, modes 1..3N

    # F(abar), modes 1..3N (f has finitely many modes)
    K = 3 * N
    Fv = {}
    for k in range(1, K + 1):
        ak = a[k - 1] if k <= N else arb(0)
        Fv[k] = lam(k) * ak - cube.get(k, arb(0)) - f.get(k, arb(0))
    for k in f:
        assert k <= K

    # tail of Lambda must be monotone with |lambda_k| > 0 for k > N
    assert eps * (N + 1) ** 2 > 1
    lamN1 = abs(lam(N + 1))

    # norms (nu = 1):  ||a|| = sum |a_k|
    norm_a = sum((abs(x) for x in a), arb(0))
    omega = quarter * sum((abs(v) for v in ss.values()), arb(0))  # ||W h|| <= omega ||h||

    # ||A||: max column sum of A_N, and 1/|lambda_k| on the tail
    colmax = arb(0)
    for j in range(N):
        cs = sum((abs(A[i, j]) for i in range(N)), arb(0))
        colmax = max(colmax, cs, key=upper)
    normA = max(colmax, 1 / lamN1, key=upper)

    # Y0 = ||A F(abar)||
    Ffin = arb_mat([[Fv[k]] for k in range(1, N + 1)])
    AF = A * Ffin
    Y0 = sum((abs(AF[i, 0]) for i in range(N)), arb(0))
    Y0 += sum((abs(Fv[k]) / abs(lam(k)) for k in range(N + 1, K + 1)), arb(0))

    # Z1 = ||I - A DF(abar)|| by columns
    def W_col(j):
        # sine coeffs of u^2 * sin(jx):  -(1/4) (ss * s_e)_k,  s_e = {j:1, -j:-1}
        out = {}
        for m, v in ss.items():
            out[m + j] = out.get(m + j, arb(0)) + v
            out[m - j] = out.get(m - j, arb(0)) - v
        return {k: -quarter * v for k, v in out.items() if k >= 1}
    Z1 = arb(0)
    for j in range(1, 3 * N + 1):
        W = W_col(j)
        DFj = {k: -3 * v for k, v in W.items()}
        DFj[j] = DFj.get(j, arb(0)) + lam(j)
        vec = arb_mat([[DFj.get(k, arb(0))] for k in range(1, N + 1)])
        fin = A * vec
        col = arb(0)
        for i in range(N):
            e = arb(1) if (i + 1) == j else arb(0)
            col += abs(e - fin[i, 0])
        for k, v in W.items():
            if k > N:
                col += abs(3 * v) / abs(lam(k))
        Z1 = max(Z1, col, key=upper)
    # columns j > 3N: only tail rows, ||3 W e_j|| / |lambda_{N+1}| bound
    Z1 = max(Z1, 3 * omega / lamN1, key=upper)

    Z = Z1 + 3 * normA * r * (2 * norm_a + r)
    p = Y0 + (Z - 1) * r
    ok = bool(p < 0) and bool(Z < 1)
    res = {"Y0": upper(Y0), "Z1": upper(Z1), "normA": upper(normA),
           "p(r)": upper(p), "radius": c["claimed_radius"]}
    # control: distance to the exact manufactured solution, if given
    if c["problem"].startswith("control"):
        astar = {1: arb(4) / 5, 3: arb(1) / 10}
        dist = sum((abs(a[k - 1] - astar.get(k, arb(0))) for k in range(1, N + 1)), arb(0))
        res["dist_to_ustar_upper"] = upper(dist)
        res["contains_ustar"] = bool(dist < r)
        res["excludes_ustar"] = bool(dist > r)
    # sup |u - ubar| <= sum |a_k - abar_k| <= r for the certified solution
    return ok, res

# ---------------- 3-bus swing equation -----------------

def verify_grid(c):
    G = c["grid"]
    B12, B13, B23 = (X(G["B"][k]) for k in ("12", "13", "23"))
    P2, P3 = X(G["P"]["2"]), X(G["P"]["3"])
    M2, M3 = X(G["M"]["2"]), X(G["M"]["3"])
    D2, D3 = X(G["D"]["2"]), X(G["D"]["3"])
    # decimal inputs like "0.1" are taken as the exact binary double nearest them;
    # the certificate is therefore about that exactly-specified model.
    t = [X(s) for s in c["theta_tilde"]]
    C = [[X(s) for s in row] for row in c["C"]]
    r = arb(c["claimed_radius"])

    def g(t2, t3):
        return [P2 - B12 * t2.sin() - B23 * (t2 - t3).sin(),
                P3 - B13 * t3.sin() - B23 * (t3 - t2).sin()]

    def Jg(t2, t3):
        c12, c13, c23 = t2.cos(), t3.cos(), (t2 - t3).cos()
        return [[-(B12 * c12 + B23 * c23), B23 * c23],
                [B23 * c23, -(B13 * c13 + B23 * c23)]]

    box = [ti + arb(0, r) for ti in t]           # theta_tilde +/- r
    gv = g(*t)
    Jb = Jg(*box)
    # Krawczyk: K = t - C g(t) + (I - C J(box)) (box - t)
    Kx = []
    for i in range(2):
        v = t[i] - (C[i][0] * gv[0] + C[i][1] * gv[1])
        for j in range(2):
            Iij = arb(1) if i == j else arb(0)
            m = Iij - (C[i][0] * Jb[0][j] + C[i][1] * Jb[1][j])
            v += m * arb(0, r)
        Kx.append(v)
    kraw_ok = all(bool(abs(Kx[i] - t[i]) < r) for i in range(2))

    # Linearisation on the whole box; state (theta2, theta3, w2, w3)
    L = [[-x for x in row] for row in Jb]
    alpha = X(c["alpha"])
    Jf = [[arb(0), arb(0), arb(1), arb(0)],
          [arb(0), arb(0), arb(0), arb(1)],
          [-L[0][0] / M2, -L[0][1] / M2, -D2 / M2, arb(0)],
          [-L[1][0] / M3, -L[1][1] / M3, arb(0), -D3 / M3]]
    for i in range(4):
        Jf[i][i] += alpha
    P = [[X(s) for s in row] for row in c["P_lyap"]]
    P = [[(P[i][j] + P[j][i]) / 2 for j in range(4)] for i in range(4)]
    Q = [[sum((Jf[k][i] * P[k][j] + P[i][k] * Jf[k][j] for k in range(4)), arb(0))
          for j in range(4)] for i in range(4)]

    def minors_positive(Mx):
        """Sylvester's criterion on an interval symmetric matrix: every leading
        minor enclosure is strictly positive, so every matrix in the box is
        positive definite."""
        dets = [arb_mat([row[:n] for row in Mx[:n]]).det() for n in range(1, 5)]
        return all(bool(d > 0) for d in dets), [str(d) for d in dets]

    p_ok, p_minors = minors_positive(P)
    q_ok, q_minors = minors_positive([[-x for x in row] for row in Q])
    ok = kraw_ok and p_ok and q_ok
    res = {"krawczyk_contained": kraw_ok, "P_posdef": p_ok, "negQ_posdef": q_ok,
           "certified_decay_rate_alpha": float(alpha.mid()), "theta_radius": c["claimed_radius"],
           "theta_enclosure": [str(b) for b in box]}
    return ok, res

def main(paths):
    all_ok = True
    for p in paths:
        c = json.load(open(p))
        t0 = time.time()
        ok, res = (verify_sine if c["kind"] == "sine-bvp" else verify_grid)(c)
        res["seconds"] = round(time.time() - t0, 2)
        print(("ACCEPT " if ok else "REJECT ") + c["problem"], json.dumps(res, default=str))
        all_ok &= ok
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
