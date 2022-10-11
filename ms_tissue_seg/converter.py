import json
import os
import shutil
from pathlib import Path

from loguru import logger

from ms_tissue_seg.utils import Constants, runBash, runBash_parallel

constants = Constants()


def _update_conversion_config(subj: str, ses: str) -> Path:
    """Update the dcm2bids conversion configuration file with
    the subject specific session to match.

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
            been processed and don't want re-run lengthy process).
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
    """Convert the extract dicoms to BIDS structure.

    Commands run during setup:
    - `dcm2bids_scaffold /home/data` to setup data directory
    - `dcm2bids_helper -d /home/data/sourcedata/ -o /home/data/bids_input`

    Args:
        subjects (list): Subjects to convert
        sessions (list): Sessions corresponding to subjects
        parallel (bool): Whether to convert in parallel
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


def check_timepoints(subjects: list, sessions: list) -> tuple:
    """Check the subjects converted are from the screening time
    point only, removing those that are not.

    Args:
        subjects (list): Original subject list
        sessions (list): Original sessions corresponding to subjects

    Returns:
        tuple: Subjects/sessions from the screening time point to be kept
    """
    subjects_remove = []
    subjects_keep = []
    sessions_keep = []

    for subj, ses in zip(subjects, sessions):
        try:
            # Load BIDS json file
            bids_json_file = (
                constants.bids_data_dir / subj / ses / "anat" / f"{subj}_{ses}_T1w.json"
            )
            with open(bids_json_file, "r") as file_in:
                data = json.load(file_in)

            # Check it is the screening timepoint
            if "screen" in data["ProcedureStepDescription"].lower():
                subjects_keep.append(subj)
                sessions_keep.append(ses)
            else:
                subjects_remove.append((subj, ses))
        except FileNotFoundError as e:
            pass

    if subjects_remove:
        logger.warning(f"{len(subjects_remove)} subjects not from screening timepoint")

        logger.warning("Deleting from BIDS data directory:")
        for subj, ses in subjects_remove:
            logger.warning(f" > {subj} {ses}")
            shutil.rmtree(str(constants.bids_data_dir / subj))

        with open(
            f"{constants.processed_data_dir}/log_not_screen_timepoint.log", "w"
        ) as fp:
            for item in subjects_remove:
                fp.write(f"{item}\n")

    return subjects_keep, sessions_keep
