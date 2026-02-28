import os
import subprocess
import tempfile
from typing import Dict, List, Tuple


class SpiceEngine:
    """
    Very lightweight wrapper around ngspice / SPICE.

    For now this is intentionally simple:
    - Writes a .cir file to a temp directory
    - Runs ngspice in batch mode if available
    - Exposes a placeholder API so the rest of the app can call it safely
    """

    def __init__(self, backend: str = "ngspice"):
        self.backend = backend

    def is_available(self) -> bool:
        """Check if the configured backend is available on PATH."""
        if self.backend == "ngspice":
            try:
                completed = subprocess.run(
                    ["ngspice", "-v"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False,
                )
                return completed.returncode == 0
            except (FileNotFoundError, OSError):
                # ngspice binary not found on this system
                return False
        return False

    def run_netlist(self, netlist_text: str) -> Dict[str, Tuple[List[float], List[float]]]:
        """
        Run a SPICE netlist and return waveform data.

        For now, this returns an empty dict if ngspice is not installed
        or parsing is not implemented. This keeps the UI stable while
        giving us a hook to upgrade later.
        """
        if not self.is_available():
            return {}

        with tempfile.TemporaryDirectory() as tmpdir:
            cir_path = os.path.join(tmpdir, "circuit.cir")
            with open(cir_path, "w", encoding="utf-8") as f:
                f.write(netlist_text)

            # Basic batch run; output parsing can be added later
            try:
                subprocess.run(
                    ["ngspice", "-b", cir_path],
                    cwd=tmpdir,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
            except Exception:
                return {}

        # Placeholder: no parsed waveforms yet
        return {}

