import shutil
from ms_tissue_seg.utils import runBash, runBash_parallel, Constants
from pathlib import Path
import os
from glob import glob
import json

constants = Constants()


def _update_conversion_config(subj: str, ses: str) -> Path:
    """Update the dcm2bids conversion configuration file with
    the subject specific session to match. This is required as
    the input .iso files are labelled with a single session date
    (the session to be matched), but include multiple sessions for
    the same subject.

    Args:
        subj (str): Subject ID
        ses (str): Session identifier from the .iso file name

    Returns:
        Path: Updated conversion configuration file
    """
    master_config_file = constants.src_dir / "dcm2bids_config.json"
    subj_config_file = Path(f"/tmp/_tmp_{subj}_{ses}_config.json")

    with open(master_config_file, "r") as file_in:
        data = json.load(file_in)
        for entry in data["descriptions"]:
            entry["criteria"]["SidecarFilename"] = f"*{ses}*"

    with open(subj_config_file, "w") as file_out:
        file_out.write(json.dumps(data))

    return subj_config_file


def extract_dcm(
    iso_objects: list, extract_iso: bool = True, parallel: bool = True
) -> list:
    """Extract dicom files from ISO (CDROM) objects.

    Args:
        iso_objects (list): ISO objects to extract dicoms from.
        extract_iso (bool, optional): Run extraction or not
            (mainly useful for testing when dicoms have already
            been processed and don't want re-run length process).
            Defaults to True.

    Returns:
        list: Lists of subject ID's and corresponding sessions.
    """

    args = []
    subjects = []
    sessions = []

    for iso in iso_objects:
        # Generate subject ID
        id = str(Path(iso).stem)
        subj = "".join(ch for ch in id.split("_")[-1] if ch.isalnum())
        ses = "".join(ch for ch in id.split("_")[0] if ch.isalnum())
        subj_ses = Path(iso).parent / subj / ses

        # Mkdir to extract dicoms to
        Path(subj_ses).mkdir(parents=True, exist_ok=True)

        subjects.append(subj)
        sessions.append(ses)

        cmd = f"pycdlib-extract-files -path-type iso -extract-to {str(subj_ses)} {iso}"

        if parallel:
            args.append(cmd)
        else:
            runBash(cmd)

    # Extract dicoms
    if extract_iso and parallel:
        runBash_parallel(func=os.system, args=args)

    return subjects, sessions


def dcm2bids(subjects: list, sessions: list, parallel: bool = True) -> None:
    """
    Commands run during setup:
    - `dcm2bids_scaffold /home/data` to setup data directory
    - `dcm2bids_helper -d /home/data/sourcedata/ -o /home/data/bids_input`
    """
    args = []

    for subj, ses in zip(subjects, sessions):

        subj_config_file: Path = _update_conversion_config(subj, ses)

        # Run conversion
        cmd = f"""dcm2bids \
                    -d {str(constants.raw_data_dir)} \
                    -p {subj} \
                    -s {ses} \
                    -o {str(constants.bids_data_dir)} \
                    -c {str(subj_config_file)}"""

        if parallel:
            args.append(cmd)
        else:
            runBash(cmd)

    if parallel:
        runBash_parallel(func=os.system, args=args)

    shutil.rmtree(str(constants.bids_data_dir / "tmp_dcm2bids"))
