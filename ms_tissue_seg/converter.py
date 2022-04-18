import shutil
from ms_tissue_seg.utils import runBash, runBash_parallel, Constants
from pathlib import Path
import os
from glob import glob
import json

constants = Constants()


def _update_conversion_config(subj: str, ses: str) -> Path:

    master_config_file = constants.src_dir / "dcm2bids_config.json"
    subj_config_file = Path(f"/tmp/_tmp_{subj}_{ses}_config.json")

    with open(master_config_file, "r") as file_in:
        data = json.load(file_in)
        for entry in data["descriptions"]:
            entry["criteria"]["SidecarFilename"] = f"*{ses}*"

    with open(subj_config_file, "w") as file_out:
        file_out.write(json.dumps(data))

    return subj_config_file


def extract_dcm(iso_objects: list, extract_iso: bool = True) -> list:
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

        # Append to list to process in parallel
        cmd = f"pycdlib-extract-files -path-type iso -extract-to {str(subj_ses)} {iso}"
        args.append(cmd)

        subjects.append(subj)
        sessions.append(ses)

    # Extract dicoms
    if extract_iso:
        runBash_parallel(func=os.system, args=args)

    return subjects, sessions


def dcm2bids(subjects: list, sessions: list):
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
        args.append(cmd)
        # runBash(cmd)

    runBash_parallel(func=os.system, args=args)

    shutil.rmtree(str(constants.bids_data_dir / "tmp_dcm2bids"))


#! ==========


# def dcm2bids(subjects: list, sessions: list):
#     """
#     Run conversion dicom to BIDS conversion. The below commands were
#     run outside the container to setup the /src/dcm2bids_heuristic.py
#     file. This file should be updated according to /data/bids_input/dicominfo.tsv
#     if the required scans change.

#     ```bash
#     docker run \
#         -v ${dicom_dir}:/base/dicom \
#         -v ${bids_dir}:/base/bids \
#             nipy/heudiconv:latest \
#             --dicom_dir_template "/base/dicom/{subject}/{session}/A/Z*" \
#             --outdir /base/bids/ \
#             --heuristic convertall \
#             --subjects "RR-241" \
#             --ses "2018-05-09" \
#             --converter none \
#             --overwrite
#     ```
#     """

#     args = []

#     for subj, ses in zip(subjects, sessions):
#         cmd = f"""heudiconv \
#                     --dicom_dir_template {str(constants.raw_data_dir)}/{{subject}}/{{session}}/A/Z* \
#                     --outdir {str(constants.bids_data_dir)} \
#                     --heuristic {str(constants.src_dir)}/dcm2bids_heuristic.py \
#                     --subjects {subj} \
#                     --ses {ses} \
#                     --converter dcm2niix -b \
#                     --overwrite"""
#         args.append(cmd)

#     runBash_parallel(func=os.system, args=args)
#     _tidy_file_names()


# def _tidy_files():

#     # Remove unused modalities
#     shutil.rmtree(str(constants.bids_data_dir / "tmp_dcm2bids"))

#     # Remove non-compressed files
#     files = glob(str(constants.bids_data_dir / "sub-*" / "ses-*" / "anat" / "*"))
#     for f in files:
#         if Path(f).suffix == ".nii":
#             os.remove(f)
#         # elif Path(f).suffix == ".json":
#         #     new_fname = (
#         #         str(Path(f).parent)
#         #         + "/"
#         #         + "_".join([i for i in Path(f).stem.split("_") if "heudiconv" not in i])
#         #         + ".json"
#         #     )
#         #     os.rename(f, new_fname)
#         # elif Path(f).suffixes == [".nii", ".gz"]:
#         #     new_fname = (
#         #         str(Path(f).parent)
#         #         + "/"
#         #         + "_".join(
#         #             [
#         #                 i
#         #                 for i in Path(f).stem.split(".")[0].split("_")
#         #                 if "heudiconv" not in i
#         #             ]
#         #         )
#         #         + ".nii.gz"
#         #     )
#         #     os.rename(f, new_fname)
