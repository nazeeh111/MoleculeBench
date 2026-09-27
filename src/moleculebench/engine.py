"""Clamped-nuclei H2 calculations and an independent two-electron solve."""
from dataclasses import asdict, dataclass
import hashlib
import importlib.metadata
import json
import math
import platform
import time
from datetime import datetime, timezone

import numpy as np
from scipy.linalg import eigh
from pyscf import ao2mo, fci, gto, scf
from threadpoolctl import threadpool_limits
from pyscf.lib.parameters import BOHR

from . import __version__

SCAN_BASES = ("sto-3g", "6-31g", "cc-pvdz")
COMPARISON_BASES = (*SCAN_BASES, "cc-pvtz")


def _finite_number(value):
    # Python integers are finite but may be too large for conversion to float.
    # Leave integer bounds to exact comparisons below, avoiding isfinite overflow.
    return (not isinstance(value, bool) and isinstance(value, (int, float))
            and (isinstance(value, int) or math.isfinite(value)))


@dataclass(frozen=True)
class Config:
    start_angstrom: float = .4
    stop_angstrom: float = 4.
    points: int = 25
    scan_basis: str = "sto-3g"
    comparison_angstrom: float = .74
    tolerance: float = 1e-10

    def __post_init__(self):
        for name in ("start_angstrom", "stop_angstrom", "comparison_angstrom", "tolerance"):
            value = getattr(self, name)
            if not _finite_number(value):
                raise ValueError(f"{name} must be a finite number")
        if type(self.points) is not int or not 3 <= self.points <= 81:
            raise ValueError("points must be an integer between 3 and 81")
        if not .3 <= self.start_angstrom < self.stop_angstrom <= 6:
            raise ValueError("scan distances must satisfy 0.3 <= start < stop <= 6 angstrom")
        if not .3 <= self.comparison_angstrom <= 6:
            raise ValueError("comparison_angstrom must be between 0.3 and 6")
        if self.scan_basis not in SCAN_BASES:
            raise ValueError(f"scan_basis must be one of {SCAN_BASES}")
        if not 1e-12 <= self.tolerance <= 1e-8:
            raise ValueError("tolerance must be between 1e-12 and 1e-8 hartree")


def two_electron_matrix(h, eri):
    """H_(ij,kl) = h_ik δ_jl + δ_ik h_jl + (ik|jl).

    Orthonormal spatial orbitals, one alpha and one beta electron. No PySCF
    FCI Hamiltonian construction or contraction routines are used here.
    """
    n = h.shape[0]
    identity = np.eye(n)
    matrix = (np.einsum("ik,jl->ijkl", h, identity)
              + np.einsum("ik,jl->ijkl", identity, h)
              + eri.transpose(0, 2, 1, 3)).reshape(n*n, n*n)
    if not np.allclose(matrix, matrix.T, atol=1e-10, rtol=0):
        raise RuntimeError("independent Hamiltonian is not symmetric")
    return matrix


def _rhf(mol, tolerance):
    mf = scf.RHF(mol)
    mf.conv_tol = tolerance
    mf.conv_tol_grad = 1e-8
    mf.max_cycle = 100
    mf.chkfile = None
    history = []
    mf.callback = lambda env: history.append(float(env["e_tot"]))
    mf.kernel()
    if not mf.converged or not math.isfinite(mf.e_tot):
        raise RuntimeError("RHF failed to converge; no validated report was written")
    return mf, history


@threadpool_limits.wrap(limits=1)
def calculate(distance, basis, tolerance=1e-10):
    """Return a validated point; only declared small H2 systems are supported."""
    if not _finite_number(distance) or not .3 <= distance <= 6:
        raise ValueError("distance must be finite and between 0.3 and 6 angstrom")
    if basis not in COMPARISON_BASES:
        raise ValueError("unsupported basis")
    if not _finite_number(tolerance) or not 1e-12 <= tolerance <= 1e-8:
        raise ValueError("invalid solver tolerance")
    # Resource limit is deliberate: determinism and no nested BLAS oversubscription.
    start = time.perf_counter()
    mol = gto.M(atom=[("H", (0, 0, -distance/2)), ("H", (0, 0, distance/2))],
                basis=basis, unit="Angstrom", charge=0, spin=0, verbose=0)
    mf, history = _rhf(mol, tolerance)
    tighter, _ = _rhf(mol, min(tolerance/10, 1e-12))
    orbitals = mf.mo_coeff
    n = orbitals.shape[1]
    h = orbitals.T @ mf.get_hcore() @ orbitals
    eri = ao2mo.restore(1, ao2mo.kernel(mol, orbitals), n)
    solver = fci.direct_spin0.FCI(mol)
    solver.conv_tol = min(tolerance, 1e-11)
    solver.max_cycle = 100
    energy, ci = solver.kernel(h, eri, n, (1, 1), ecore=mol.energy_nuc())
    if not solver.converged or not math.isfinite(energy):
        raise RuntimeError("FCI failed to converge; no validated report was written")
    matrix = two_electron_matrix(h, eri)
    values, vectors = eigh(matrix, subset_by_index=(0, 0))
    dense_energy = float(values[0] + mol.energy_nuc())
    residual = float(np.linalg.norm(matrix @ vectors[:, 0] - values[0]*vectors[:, 0]))
    overlap = mf.get_ovlp()
    dm = mf.make_rdm1()
    fock = mf.get_fock(dm=dm)
    occupations = np.linalg.eigvalsh(solver.make_rdm1(ci, n, (1, 1)))
    spin_squared = float(fci.spin_op.spin_square(ci, n, (1, 1))[0])
    # One electron: no electron-electron term. Generalized eigenproblem is exact
    # in the atomic basis, so its lowest eigenvalue is an independent atomic HF reference.
    atom = gto.M(atom="H 0 0 0", basis=basis, spin=1, verbose=0)
    atom_h = atom.intor("int1e_kin") + atom.intor("int1e_nuc")
    atom_energy = float(eigh(atom_h, atom.intor("int1e_ovlp"), eigvals_only=True)[0])
    result = {
        "distance_angstrom": float(distance), "distance_bohr": float(distance/BOHR), "basis": basis,
        "orbitals": n, "two_electron_dimension": n*n, "rhf_hartree": float(mf.e_tot),
        "fci_hartree": float(energy), "correlation_hartree": float(energy-mf.e_tot),
        "nuclear_repulsion_hartree": float(mol.energy_nuc()), "atom_hartree": atom_energy,
        "fci_binding_hartree": float(energy-2*atom_energy),
        "dense_fci_hartree": dense_energy, "dense_fci_delta_hartree": abs(dense_energy-float(energy)),
        "dense_residual_norm": residual, "rhf_tight_delta_hartree": abs(float(mf.e_tot-tighter.e_tot)),
        "scf_converged": bool(mf.converged), "fci_converged": bool(solver.converged),
        "scf_cycles": len(history), "scf_energy_history_hartree": history,
        "scf_commutator_norm": float(np.linalg.norm(fock @ dm @ overlap - overlap @ dm @ fock)),
        "electron_count": float(np.trace(dm @ overlap)), "fci_electron_count": float(sum(occupations)),
        "natural_occupations": occupations[::-1].tolist(), "fci_spin_squared": spin_squared,
        "overlap_min_eigenvalue": float(np.linalg.eigvalsh(overlap)[0]),
        "elapsed_seconds": time.perf_counter()-start,
    }
    if (any(not math.isfinite(value) for value in result.values()
            if isinstance(value, (int, float)))
        or any(not math.isfinite(value) for field in
               ("scf_energy_history_hartree", "natural_occupations")
               for value in result[field])):
        raise RuntimeError(f"non-finite numerical result at {distance} angstrom / {basis}")
    if (result["dense_fci_delta_hartree"] > 1e-7 or residual > 1e-8
        or abs(result["electron_count"]-2) > 1e-8 or abs(sum(occupations)-2) > 1e-8
        or occupations.min() < -1e-8 or occupations.max() > 2+1e-8
        or abs(spin_squared) > 1e-7 or energy > mf.e_tot+1e-8
        or result["scf_commutator_norm"] > 1e-6
        or result["rhf_tight_delta_hartree"] > 1e-7):
        raise RuntimeError(f"numerical invariant failed at {distance} angstrom / {basis}")
    return result


def run(config=Config()):
    start = time.perf_counter()
    settings = asdict(config)
    scan = [calculate(float(r), config.scan_basis, config.tolerance)
            for r in np.linspace(config.start_angstrom, config.stop_angstrom, config.points)]
    comparison = [calculate(config.comparison_angstrom, basis, config.tolerance)
                  for basis in COMPARISON_BASES]
    all_points = scan + comparison
    return {
        "schema_version": 1, "project": "MoleculeBench", "version": __version__,
        "calculation": "H2 clamped-nuclei nonrelativistic electronic structure; not experiment",
        "units": {"distance": "angstrom", "energy": "hartree", "time": "second", "bohr_angstrom": BOHR},
        "config": settings,
        "provenance": {
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "configuration_sha256": hashlib.sha256(json.dumps(settings, sort_keys=True).encode()).hexdigest(),
            "python": platform.python_version(), "platform": platform.platform(),
            "dependencies": {name: importlib.metadata.version(name) for name in ("pyscf", "numpy", "scipy", "matplotlib", "threadpoolctl")},
            "numerical_threads": 1, "randomness": "none; deterministic fixed geometries and solver initialization",
            "elapsed_seconds": time.perf_counter()-start,
        },
        "summary": {
            "sampled_minimum": min(scan, key=lambda p: p["fci_hartree"]),
            "max_dense_fci_delta_hartree": max(p["dense_fci_delta_hartree"] for p in all_points),
            "max_rhf_tight_delta_hartree": max(p["rhf_tight_delta_hartree"] for p in all_points),
            "all_converged": all(p["scf_converged"] and p["fci_converged"] for p in all_points),
        },
        "scan": scan, "basis_comparison": comparison,
    }
