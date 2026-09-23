# MoleculeBench implementation contract

Original experiment orchestration, independent two-electron solver, reporting and UI by nazeeh111. PySCF supplies Gaussian basis data, integrals, RHF and FCI. No upstream source is copied.

The fixed system is two neutral hydrogen nuclei and two electrons, spin singlet, nonrelativistic clamped-nuclei Born–Oppenheimer Hamiltonian. Distances are input in angstrom, converted by PySCF's BOHR constant; energy outputs are hartree and include nuclear repulsion. Restricted Hartree–Fock is deliberately retained on dissociation to illustrate its limitation. FCI is exact only within the chosen finite orbital basis and numerical tolerance.

Default scan: 0.4 to 4.0 angstrom, 25 points, STO-3G. Basis comparison at 0.74 angstrom: STO-3G, 6-31G, cc-pVDZ, cc-pVTZ. A separate two-electron product-basis Hamiltonian is diagonalized with SciPy and compared with PySCF FCI. Shared integrals mean this validates many-electron assembly/solution, not independent integral evaluation. One-electron hydrogen atomic reference uses generalized diagonalization. Tighter RHF solves quantify numerical sensitivity, not model uncertainty.

Bounded work: scan bases only STO-3G/6-31G/cc-pVDZ, 3–81 points, bond lengths 0.3–6 angstrom, one numerical thread. No arbitrary atom/basis injection. Runtime provenance includes configuration hash, versions, platform, units, timings and convergence checks. Nonconvergence or invariant failure aborts rather than emitting apparently validated results. Outputs are written to a new directory; existing user files are never overwritten.

Implementation sequence: scientific/validation tests first, numerical engine, output and offline dashboard, CLI tests, documentation, package verification and fresh independent review. Dashboard consumes actual embedded calculation JSON, requires no server/CDN, and offers method visibility, point selection, basis table, diagnostics and data downloads. No simulated chemistry animation substitutes for results.
