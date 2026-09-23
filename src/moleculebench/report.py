"""Portable artifacts from already-computed results; no browser computation."""
import csv
from importlib.resources import files
import json
import os
from pathlib import Path
import tempfile


def write_report(data, output):
    output = Path(output)
    # Refuse existing destinations, including empty ones and symbolic links.
    output.mkdir(parents=True, exist_ok=False)
    (output / "results.json").write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")
    columns = ["distance_angstrom", "basis", "rhf_hartree", "fci_hartree", "correlation_hartree",
               "atom_hartree", "fci_binding_hartree", "orbitals", "dense_fci_delta_hartree",
               "rhf_tight_delta_hartree", "scf_cycles", "scf_commutator_norm", "fci_spin_squared"]
    for name, rows in [("scan", data["scan"]), ("basis_comparison", data["basis_comparison"])]:
        with (output / f"{name}.csv").open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
    template = files("moleculebench").joinpath("templates/dashboard.html").read_text()
    encoded = json.dumps(data, allow_nan=False).replace("<", "\\u003c")
    (output / "index.html").write_text(template.replace("__RESULT_DATA__", encoded))
    # Use a transient writable config directory rather than depending on user's home.
    with tempfile.TemporaryDirectory(prefix="moleculebench-mpl-") as cache:
        previous = os.environ.get("MPLCONFIGDIR")
        os.environ["MPLCONFIGDIR"] = cache
        try:
            import matplotlib
            matplotlib.use("Agg")
            from matplotlib import pyplot as plt
            with plt.rc_context({"font.family": "sans-serif", "axes.spines.top": False,
                                 "axes.spines.right": False, "axes.grid": True, "grid.alpha": .15}):
                fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), layout="constrained")
                x = [p["distance_angstrom"] for p in data["scan"]]
                axes[0].plot(x, [p["rhf_hartree"] for p in data["scan"]], color="#977134", label="RHF")
                axes[0].plot(x, [p["fci_hartree"] for p in data["scan"]], color="#176b5a", label="FCI")
                axes[0].axhline(2*data["scan"][0]["atom_hartree"], color="#617781", linestyle="--", label="2 × isolated H")
                axes[0].set(xlabel="H–H distance (Å)", ylabel="Total energy (hartree)", title=f"H₂ · {data['config']['scan_basis'].upper()}")
                axes[0].legend()
                axes[1].plot(x, [-1000*p["correlation_hartree"] for p in data["scan"]], color="#176b5a")
                axes[1].set(xlabel="H–H distance (Å)", ylabel="RHF − FCI (millihartree)", title="Correlation missing from RHF")
                fig.suptitle("MoleculeBench · computed finite-basis results", fontsize=13)
                fig.savefig(output / "energy-curves.png", dpi=170)
                fig.savefig(output / "energy-curves.svg")
                plt.close(fig)
        finally:
            if previous is None:
                os.environ.pop("MPLCONFIGDIR", None)
            else:
                os.environ["MPLCONFIGDIR"] = previous
    return output
