import numpy as np
import pytest
from moleculebench.engine import Config, calculate, two_electron_matrix


def test_product_hamiltonian_noninteracting_reference():
    h = np.diag([-1.0, 0.4])
    matrix = two_electron_matrix(h, np.zeros((2, 2, 2, 2)))
    np.testing.assert_allclose(np.linalg.eigvalsh(matrix), [-2, -.6, -.6, .8])


@pytest.fixture(scope="module")
def equilibrium():
    return calculate(.74, "sto-3g", 1e-10)


def test_h2_finite_basis_reference_and_invariants(equilibrium):
    p = equilibrium
    # Standard STO-3G H2 at 0.74 A; fixed regression values, not experiment.
    assert abs(p["rhf_hartree"] - (-1.1167593074)) < 2e-8
    assert abs(p["fci_hartree"] - (-1.1372838345)) < 2e-8
    assert p["fci_hartree"] <= p["rhf_hartree"]
    assert p["dense_fci_delta_hartree"] < 1e-9
    assert p["dense_residual_norm"] < 1e-9
    assert abs(p["electron_count"] - 2) < 1e-9
    assert abs(p["fci_spin_squared"]) < 1e-8
    assert p["scf_converged"] and p["fci_converged"]
    assert p["rhf_tight_delta_hartree"] < 1e-8
    assert p["scf_commutator_norm"] < 1e-7


def test_dissociation_approaches_two_atoms():
    p = calculate(6., "sto-3g", 1e-10)
    assert abs(p["fci_hartree"] - 2*p["atom_hartree"]) < 2e-6
    assert p["rhf_hartree"] - p["fci_hartree"] > .2


@pytest.mark.parametrize("kwargs", [
    {"points": True}, {"points": 2}, {"points": 82}, {"points": 3.5},
    {"start_angstrom": float("nan")}, {"stop_angstrom": float("inf")},
    {"start_angstrom": .1}, {"start_angstrom": 3., "stop_angstrom": 2.},
    {"scan_basis": "cc-pvtz"}, {"tolerance": 0}, {"tolerance": 1e-3},
    {"comparison_angstrom": "0.74"}, {"unexpected": 1},
])
def test_invalid_configuration(kwargs):
    with pytest.raises((ValueError, TypeError)):
        Config(**kwargs)


def test_units_nuclear_repulsion(equilibrium):
    assert abs(equilibrium["distance_bohr"] * .52917721092 - .74) < 1e-10
    assert abs(equilibrium["nuclear_repulsion_hartree"] - 1/equilibrium["distance_bohr"]) < 1e-12


def test_nonconverged_scf_is_rejected(monkeypatch):
    from pyscf.scf.hf import RHF
    def fail(self, *args, **kwargs):
        self.converged = False
        self.e_tot = -1.
    monkeypatch.setattr(RHF, "kernel", fail)
    with pytest.raises(RuntimeError, match="RHF failed to converge"):
        calculate(.74, "sto-3g")


@pytest.mark.parametrize("field", ["start_angstrom", "stop_angstrom", "comparison_angstrom", "tolerance"])
def test_huge_integer_config_is_validation_error(field):
    with pytest.raises(ValueError):
        Config(**{field: 10**400})


@pytest.mark.parametrize("kwargs", [{"distance": 10**400}, {"tolerance": 10**400}])
def test_huge_integer_calculation_is_validation_error(kwargs):
    args = {"distance": .74, "basis": "sto-3g", **kwargs}
    with pytest.raises(ValueError):
        calculate(**args)
