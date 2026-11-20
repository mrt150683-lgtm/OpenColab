"""Approximate solvers for the 004 pilot. Float64 only; produces certificate JSON.

Nothing here is trusted: verify.py recomputes every bound with interval
arithmetic and does not import this file.
"""
import json
import sys
import numpy as np

# ---------- sine-series problems:  eps u'' + u - u^3 = f on (0, pi), u(0)=u(pi)=0 ----------
# u = sum_{k=1..} a_k sin(kx).  Odd extension s_k = a_k, s_{-k} = -a_k.
# Sine coefficients of u*v*w are -(1/4) (s_u * s_v * s_w)_k.

def odd_ext(a, L):
    s = np.zeros(2 * L + 1)
    n = len(a)
    s[L + 1:L + 1 + n] = a
    s[L - n:L][::-1] = -a
    return s

def cube_coeffs(a, M):
    """Sine coefficients 1..M of u^3."""
    L = 3 * len(a) + 2
    s = odd_ext(a, L)
    c = np.convolve(np.convolve(s, s), s)  # centre at 3L
    ctr = 3 * L
    return -0.25 * c[ctr + 1:ctr + 1 + M]

def F(a, eps, f):
    N = len(a)
    k = np.arange(1, N + 1)
    lam = 1 - eps * k ** 2
    ff = np.zeros(N); ff[:min(N, len(f))] = f[:N]
    return lam * a - cube_coeffs(a, N) - ff

def DF(a, eps):
    N = len(a)
    J = np.zeros((N, N))
    # exact derivative: Lambda h - 3 * sin-coeffs(u^2 h), build column by column
    L = 3 * N + 2
    s = odd_ext(a, L)
    ss = np.convolve(s, s)  # centre 2L
    for j in range(1, N + 1):
        e = np.zeros(N); e[j - 1] = 1
        se = odd_ext(e, L)
        c = np.convolve(ss, se)
        ctr = 3 * L
        W = -0.25 * c[ctr + 1:ctr + 1 + N]
        J[:, j - 1] = -3 * W
        J[j - 1, j - 1] += 1 - eps * j ** 2
    return J

def newton(a, eps, f, iters=60):
    for _ in range(iters):
        step = np.linalg.solve(DF(a, eps), F(a, eps, f))
        a = a - step
        if np.max(np.abs(step)) < 1e-17:
            break
    return a

def sine_cert(name, eps_str, f_exact, a0, N, r):
    from fractions import Fraction
    eps = float(Fraction(eps_str))
    from fractions import Fraction; f = np.array([float(Fraction(x)) for x in f_exact]) if f_exact else np.zeros(0)
    a = np.zeros(N); a[:len(a0)] = a0
    a = newton(a, eps, f)
    A = np.linalg.inv(DF(a, eps))
    return {
        "problem": name, "kind": "sine-bvp",
        "eps": eps_str, "N": N,
        "f_sine_coeffs_exact": f_exact or [],
        "abar": [repr(float(x)) for x in a],
        "A_N": [[repr(float(x)) for x in row] for row in A],
        "claimed_radius": r,
        "residual_float_max": float(np.max(np.abs(F(a, eps, f)))),
    }

# ---------- 3-bus swing equation ----------
GRID = {
    "B": {"12": "1.0", "13": "0.8", "23": "0.6"},   # line susceptances, per unit
    "P": {"2": "0.5", "3": "-0.3"},                # injections; bus 1 is the slack
    "M": {"2": "0.1", "3": "0.08"},                # inertia
    "D": {"2": "0.05", "3": "0.04"},               # damping
}

def grid_cert(r_theta, alpha_frac):
    B = {k: float(v) for k, v in GRID["B"].items()}
    P2, P3 = float(GRID["P"]["2"]), float(GRID["P"]["3"])
    M = np.diag([float(GRID["M"]["2"]), float(GRID["M"]["3"])])
    D = np.diag([float(GRID["D"]["2"]), float(GRID["D"]["3"])])
    def g(t):
        t2, t3 = t
        return np.array([P2 - B["12"] * np.sin(t2) - B["23"] * np.sin(t2 - t3),
                         P3 - B["13"] * np.sin(t3) - B["23"] * np.sin(t3 - t2)])
    def Lmat(t):
        t2, t3 = t
        c12, c13, c23 = np.cos(t2), np.cos(t3), np.cos(t2 - t3)
        return np.array([[B["12"] * c12 + B["23"] * c23, -B["23"] * c23],
                         [-B["23"] * c23, B["13"] * c13 + B["23"] * c23]])
    t = np.zeros(2)
    for _ in range(50):
        t = t + np.linalg.solve(Lmat(t), g(t))   # dg/dt = -L
    C = np.linalg.inv(-Lmat(t))
    J = np.block([[np.zeros((2, 2)), np.eye(2)],
                  [-np.linalg.solve(M, Lmat(t)), -np.linalg.solve(M, D)]])
    abscissa = float(np.max(np.linalg.eigvals(J).real))
    alpha = alpha_frac * (-abscissa)
    Aa = J + alpha * np.eye(4)
    # Lyapunov: Aa^T P + P Aa = -I   via Kronecker form
    K = np.kron(np.eye(4), Aa.T) + np.kron(Aa.T, np.eye(4))
    P = np.linalg.solve(K, -np.eye(4).reshape(-1)).reshape(4, 4)
    P = (P + P.T) / 2
    return {
        "problem": "grid3-swing", "kind": "grid3",
        "grid": GRID,
        "theta_tilde": [repr(float(x)) for x in t],
        "C": [[repr(float(x)) for x in row] for row in C],
        "claimed_radius": r_theta,
        "alpha": repr(float(alpha)),
        "P_lyap": [[repr(float(x)) for x in row] for row in P],
        "numeric_spectral_abscissa": abscissa,
    }

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "certificates"
    import os
    os.makedirs(out, exist_ok=True)
    # P1 control: manufactured solution u* = 0.8 sin x + 0.1 sin 3x, eps = 1/10.
    # f = Lambda a* - cube(a*) computed exactly in verify.py from these rationals.
    from fractions import Fraction as Fr
    eps = "1/10"
    astar = {1: Fr(4, 5), 3: Fr(1, 10)}
    # exact f (computed here only to seed the solver; verify.py recomputes it)
    def exact_f():
        L = 12
        s = {}
        for k, v in astar.items():
            s[k] = v; s[-k] = -v
        conv = {}
        for i, x in s.items():
            for j, y in s.items():
                for l, z in s.items():
                    conv[i + j + l] = conv.get(i + j + l, 0) + x * y * z
        f = []
        for k in range(1, 10):
            lam = 1 - Fr(1, 10) * k * k
            f.append(lam * astar.get(k, 0) - Fr(-1, 4) * conv.get(k, 0))
        return [str(x) for x in f]
    # Seed near u*: expected to recover the known solution.
    cert1 = sine_cert("control-manufactured", eps, exact_f(), [0.75, 0, 0.1], 24, 1e-12)
    # Seed 0.5: in the first run this converged to a *different* solution of the
    # same forced problem. Kept as a second certificate; see README.
    cert1b = sine_cert("control-manufactured-seed05", eps, exact_f(), [0.5], 24, 1e-10)
    cert2 = sine_cert("allen-cahn-eps0.1", eps, None, [1.2, 0, 0.3, 0, 0.1], 64, 1e-12)
    # Stress test: thinner boundary layers need many more modes.
    cert2b = sine_cert("allen-cahn-eps0.02", "1/50", None, [1.2, 0, 0.3, 0, 0.1], 160, 1e-12)
    cert3 = grid_cert(1e-12, 0.9)
    for c in (cert1, cert1b, cert2, cert2b, cert3):
        with open(f"{out}/{c['problem']}.json", "w") as fh:
            json.dump(c, fh, indent=1)
        print(c["problem"], {k: v for k, v in c.items() if k in ("residual_float_max", "numeric_spectral_abscissa")})
