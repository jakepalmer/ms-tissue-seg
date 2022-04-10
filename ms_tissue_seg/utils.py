from pathlib import Path
import os
from multiprocessing import cpu_count
from joblib import Parallel, delayed


class Constants:

    # Set paths
    base_dir = Path(__file__).parent.parent
    raw_data_dir = base_dir / "data" / "sourcedata"
    # tmp_data_dir = base_dir / "data" / "interim"
    processed_data_dir = base_dir / "data" / "derivatives"
    bids_data_dir = base_dir / "data" / "bids_input"
    src_dir = base_dir / "ms_tissue_seg" / "src"

    # Set other parameters
    nthreads: int = cpu_count() - 2


# --- General helpers ---

constants = Constants()


def runBash_parallel(func, args: list):
    Parallel(n_jobs=constants.nthreads)(delayed(func)(arg) for arg in args)


def runBash(cmd: str):
    os.system(cmd)
