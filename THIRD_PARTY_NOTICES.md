# Dependencies and scientific sources

MoleculeBench's original application code is MIT licensed, copyright nazeeh111. Dependency code is installed separately; its licenses and notices remain intact in the installed distributions. No dependency license is replaced by this project's license.

- [PySCF](https://github.com/pyscf/pyscf), Apache-2.0: molecular/basis construction, integrals, RHF, FCI and density diagnostics. Its distributed native dependencies and basis data retain their own notices. See the PySCF distribution and project license files.
- [NumPy](https://github.com/numpy/numpy), BSD-3-Clause: arrays and linear algebra.
- [SciPy](https://github.com/scipy/scipy), BSD-3-Clause: independent dense/generalized eigenproblems. Numerical runtime components retain their distributed notices.
- [Matplotlib](https://matplotlib.org/stable/project/license.html), Matplotlib license based on the PSF license: static figures.
- [threadpoolctl](https://github.com/joblib/threadpoolctl), BSD-3-Clause: bounded native numerical thread pools.
- pytest, build and setuptools are development/packaging dependencies; their original licenses apply.

Scientific documentation links and the independence limits of the validation are listed in docs/physics.md. Results are calculations produced by this application; no experimental dataset or third-party image is bundled.
