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

## September 27, 2026 maintenance check

The prior `calculate()` result guard did not reject a non-finite derived diagnostic: in a controlled fault injection, a NaN returned by PySCF's spin diagnostic passed the comparison-based invariant checks and `calculate()` returned a point marked converged. The result guard now rejects non-finite scalar results, SCF energy history entries and natural occupations before returning a point. The injected fault now raises a runtime error; an in-process CLI run exits with code 2 and leaves the requested output directory absent. This verifies rejection of that fault, not that PySCF normally produces NaN there.

At the previously unrecorded 6-31G distance boundaries, 0.3 and 6 Å with a 1e-12 Eh tolerance, FCI agreed with the separately assembled dense Hamiltonian to 0 and 4.44e-16 Eh respectively. Residual norms were 1.32e-16 and 7.67e-16. At 6 Å, the atomic reference matched a separate one-electron UHF calculation exactly at the displayed precision; the FCI binding energy was −4.03e-9 Eh. At 5.9 Å / cc-pVDZ, dense FCI differed by 2.66e-15 Eh. These checks share PySCF's integral engine and do not establish experimental or complete-basis accuracy.

The local Python 3.13 environment passed 41 tests in 14.55 seconds after this change, including a CLI regression for the injected NaN and output preservation. The earlier 39-test record above describes the September 23 build. This maintenance record describes local source checks; release verification is recorded separately.

## October 1, 2026 report presentation check

The report now uses compact system typography, ruled sections and a white background. The checked-in demonstration was rendered with the new template and its existing embedded results. Numerical code, configuration, result JSON, CSV files and exported plots are unchanged. The JavaScript program and existing control IDs are unchanged byte for byte.

In the Codex in-app browser, the revised report was inspected at 1100 × 900 and 390 × 844. Document width and scroll width matched at both sizes. On mobile, charts remain 560 pixels wide inside 354-pixel scroll regions, with a visible scrolling hint and keyboard focus. Arrow keys moved a chart horizontally and back without widening the document. The previous mobile chart was 312 pixels wide: its 11-unit SVG labels scaled to about 4.9 pixels. The new 13-unit labels scale to about 10.4 pixels.

The geometry selector reached 4 Å on desktop and mobile; the displayed energies were RHF −0.6148700 Eh and FCI −0.9331714 Eh, with occupations 1.009 / 0.991. Both method toggles worked, including the explanation when both were hidden. Point diagnostics, runtime provenance and the 25-row scan table opened. The generated report passed the existing portable-report test (1 test, 10.59 seconds), and the extracted unchanged script passed `node --check`.

The result JSON button was clicked, but the in-app browser download event timed out after 15 seconds; receipt of a saved download remains unverified. Its program is unchanged. Neighboring JSON, CSV and plot assets were retrieved through the local report server and matched their existing bytes. No report warnings or errors were observed in the browser log. These are bounded presentation checks, not new physical validation or a screen-reader audit. The current desktop and [mobile](dashboard-mobile.jpg) screenshots accompany this check; the earlier PNG screenshots are retained as historical artifacts.
