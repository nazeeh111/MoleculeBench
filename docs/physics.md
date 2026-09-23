# Model and independent numerical check

Atomic units set electron mass, elementary charge, ħ and Coulomb constant to one. PySCF's BOHR conversion is recorded in each result. For protons separated by R bohr, nuclear repulsion is 1/R hartree. Total energy includes this constant.

For orthonormal spatial orbitals and one alpha plus one beta electron, label the product basis |iα,jβ>. Its matrix is

`H[(i,j),(k,l)] = h[i,k] δ[j,l] + δ[i,k] h[j,l] + (ik|jl)`.

`h` contains electronic kinetic energy and attraction to both nuclei; `(ik|jl)` is a chemists' two-electron Coulomb integral. Opposite-spin electrons have no direct exchange term in this matrix. Fermionic symmetry is implicit in the alpha/beta determinant representation. The product space also contains Ms=0 triplet states; the lowest state for these bounded H₂ ground-state calculations is checked against the spin-singlet PySCF solver, and PySCF's ⟨S²⟩ is recorded.

MoleculeBench constructs this matrix using NumPy and solves its lowest eigenpair with SciPy `eigh`, without invoking PySCF's FCI matrix builders or contractions. It adds nuclear repulsion and compares with `pyscf.fci.direct_spin0.FCI`. Both routes use the same integrals and RHF orbital transformation, so agreement does not certify integral evaluation. A noninteracting analytic test sets the electron repulsion tensor to zero; the spectrum must be every pairwise sum of one-electron eigenvalues.

The isolated atom has one electron, hence no electron-electron contribution: solve `h C = S C ε` in its atomic basis. Twice the lowest energy is the same-basis separated-atom reference. At finite R, sharing atom-centered basis functions introduces basis-set superposition effects. No counterpoise correction is applied. The 6 Å STO-3G test verifies approach to the limit, not exact equality at finite separation.

RHF uses one occupied spatial orbital for both electrons. Its spin-restricted constraint becomes qualitatively wrong for dissociation, even when the SCF iteration is numerically converged. FCI allows multiple configurations. The natural occupations are eigenvalues of the spin-summed one-electron density matrix: each lies between zero and two, with trace two. Tighter tolerances and residuals measure numerical convergence. They are not uncertainties in the Hamiltonian, basis or measured chemistry.

The default scan is deliberately coarse. The report's minimum is one of its points, not a continuous geometry optimization. No force, vibration, spectroscopy or experimental accuracy is claimed.

## Primary references

- [PySCF self-consistent-field methods](https://pyscf.org/user/scf.html): RHF, convergence and the distinction between convergence and stability.
- [PySCF configuration interaction](https://pyscf.org/user/ci.html): FCI and spin-sector solvers.
- [PySCF molecular structure](https://pyscf.org/user/gto.html): molecular coordinates, basis and spin conventions.
- [PySCF FCI source](https://github.com/pyscf/pyscf/tree/master/pyscf/fci): solver APIs; no implementation is copied into this project.
