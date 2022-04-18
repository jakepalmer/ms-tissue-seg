from pathlib import Path
import os
from multiprocessing import cpu_count
from joblib import Parallel, delayed
from templateflow import api as tflow
import ants


def _dload_templates():
    template_t1_file: Path = tflow.get(
        "MNI152NLin2009aAsym", resolution=1, suffix="T1w", extension="nii.gz"
    )
    template_t1: ants.ANTsImage = ants.image_read(str(template_t1_file))

    template_mask_file: Path = tflow.get(
        "MNI152NLin2009aAsym",
        resolution=1,
        desc="brain",
        suffix="mask",
        extension="nii.gz",
    )
    template_mask: ants.ANTsImage = ants.image_read(str(template_mask_file))

    template_wm_file: Path = tflow.get(
        "MNI152NLin2009aAsym",
        resolution=1,
        label="WM",
        suffix="probseg",
        extension="nii.gz",
    )
    template_wm: ants.ANTsImage = ants.image_read(str(template_wm_file))

    template_gm_file: Path = tflow.get(
        "MNI152NLin2009aAsym",
        resolution=1,
        label="GM",
        suffix="probseg",
        extension="nii.gz",
    )
    template_gm: ants.ANTsImage = ants.image_read(str(template_gm_file))

    template_csf_file: Path = tflow.get(
        "MNI152NLin2009aAsym",
        resolution=1,
        label="CSF",
        suffix="probseg",
        extension="nii.gz",
    )
    template_csf: ants.ANTsImage = ants.image_read(str(template_csf_file))

    # Need to create brain template
    template_brain_file: Path = Path(
        "/tmp/tpl-MNI152NLin2009aAsym_res-1_desc-brain.nii.gz"
    )
    _tmp_t1 = ants.image_read(str(template_t1_file))
    _tmp_mask = ants.image_read(str(template_mask_file))
    template_brain = ants.mask_image(image=_tmp_t1, mask=_tmp_mask)
    ants.image_write(template_brain, str(template_brain_file))

    return (
        template_t1,
        template_mask,
        template_wm,
        template_gm,
        template_csf,
        template_brain,
    )


class Constants:

    # Set paths
    local_base_dir = Path(os.getenv("LOCAL_BASE_DIR"))
    base_dir = Path(__file__).parent.parent
    raw_data_dir = base_dir / "data" / "sourcedata"
    # tmp_data_dir = base_dir / "data" / "interim"
    processed_data_dir = base_dir / "data" / "derivatives"
    bids_data_dir = base_dir / "data" / "bids_input"
    src_dir = base_dir / "ms_tissue_seg" / "src"

    # Set other parameters
    nthreads: int = cpu_count() - 2

    # Get template files
    (
        template_t1,
        template_mask,
        template_wm,
        template_gm,
        template_csf,
        template_brain,
    ) = _dload_templates()


# --- General helpers ---

constants = Constants()


def runBash_parallel(func, args: list):
    Parallel(n_jobs=constants.nthreads)(delayed(func)(arg) for arg in args)


def runBash(cmd: str):
    os.system(cmd)
