# Verification record

Observed locally on September 23, 2026: Python 3.13.2, macOS arm64; PySCF 2.14.0, NumPy 2.5.3, SciPy 1.18.1, Matplotlib 3.11.2, threadpoolctl 3.7.0. `requirements-tested.txt` records the installed dependency versions. Linux/Python 3.11 and 3.13 CI is configured, not claimed as locally executed.

- **39 tests passed** in 14.76 seconds: analytic noninteracting spectrum, fixed H2 STO-3G regression energies, 6 Å dissociation limit, electron counts, spin and occupations, independent FCI residual/agreement, RHF refinement, explicit unit/nuclear-repulsion consistency, nonconvergence rejection, invalid configuration and CLI inputs (including huge integers, duplicate fields, 16 KiB file-size bound and excessive nesting), complete portable report generation and existing-output preservation.
- **Default demonstration:** 25 STO-3G scan geometries plus four basis comparisons completed the numerical portion in 0.6425 seconds. Report/plot rendering and interpreter import time are excluded from this number and may dominate small runs.
- **Maximum independent FCI difference:** 2.842170943040401e-14 hartree over all 29 calculated geometries/bases.
- **Maximum tighter-RHF difference:** 4.440892098500626e-16 hartree. Maximum RHF electron-count error: 1.3322676295501878e-15.
- **Equilibrium fixture at 0.74 Å / STO-3G:** RHF −1.1167593074 Eh; FCI −1.1372838345 Eh. These are calculated finite-basis regression fixtures, not experimental values or an external independent replication.
- **Package:** source distribution and wheel built; wheel installed normally, not editable; CLI produced a fresh report while launched from `/tmp`, using the installed package and bundled HTML template. `pip check` passed.
- **Browser:** Chrome desktop and 390 × 844 mobile view inspected through native browser tools. Changing the geometry to 4 Å updated RHF/FCI energies and occupations; method toggles and the both-hidden explanatory state worked. Provenance disclosure opened. Mobile document width and scroll width both measured 390px. Desktop/mobile screenshots are included. The only observed console error originated from the browser extension, not the report.
- **JavaScript:** extracted dashboard script passed `node --check`.

The independent many-electron solver uses the same PySCF integrals. This is not an independent check of the integral engine. No physical experiment, hardware quantum execution, complete-basis extrapolation, nuclear-motion correction or universal chemical-accuracy claim is made. Solver tolerance comparisons are numerical sensitivity checks, not uncertainty intervals. Interactive controls browse precomputed points; they do not run new chemistry in the browser.

The default demo is deliberately small. Arbitrary molecules and larger basis sets are disallowed, and the maximum scan is 81 points in cc-pVDZ plus the fixed four-point basis comparison. Actual runtime varies by CPU and scientific-library build. Repeated results should agree within numerical tolerances; timestamps and measured durations intentionally differ.

Independent review also checked cc-pVDZ and cc-pVTZ at 0.3 Å and 6 Å; the reviewer reported passing invariants and independent FCI differences no larger than 2.4e-14 Eh. The reproduced huge-integer input overflow was fixed with six initially failing API cases plus CLI regressions. Numerical code for valid inputs is unchanged.
