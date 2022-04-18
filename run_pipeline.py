"""
Main script to coordinate pipeline.
"""
from loguru import logger
from glob import glob
from time import time
from joblib import Parallel, delayed

from ms_tissue_seg.utils import constants
from ms_tissue_seg import converter, mriqc, preprocess, segmentation

# TODO: Add log to file
# TODO: Add joblib for entire pipeline after generating bids inputs

# def main():
logger.success(">> STARTING PROCESSING <<")

# --- Convert dicom to BIDS ---
logger.info("Dicom to BIDS conversion: Running")
start = time()

iso_objects = glob(f"{str(constants.raw_data_dir)}/*iso")
subjects, sessions = converter.extract_dcm(iso_objects, extract_iso=False)
# converter.dcm2bids(subjects, sessions)

logger.info("Dicom to BIDS conversion: Finished")

# --- Update subject and session IDs ---
# subjects = [f"sub-{s}" for s in subjects]
# sessions = [f"ses-{s}" for s in sessions]
# subjects = ["sub-RR215", "sub-RR241", "sub-RR242"]
# sessions = [
#     "ses-20180605",
#     "ses-20180509",
#     "ses-20180528",
# ]
subjects = ["sub-RR215"]
sessions = ["ses-20180605"]

assert len(subjects) == len(sessions), logger.error(
    "Mismatch in number of subjects and sessions!"
)

# for subj, ses in zip(subjects, sessions):
#     Parallel(n_jobs=constants.nthreads)(delayed(_process_runner) )

# def _process_runner(subj: str, ses: str):

# --- Quality control ---
logger.info("Quality control: Running")

mriqc.runQC()

logger.info("Quality control: Finished")

# --- Preprocess FLAIR and T1w ---
logger.info("Preprocessing: Running")

prep = preprocess.Preprocess(subjects, sessions)
prep.run()

logger.info("Preprocessing: Finished")

# --- Tissue and lesion segmentation ---
logger.info("Segmentation: Running")

seg = segmentation.SegmentationANTs(subjects, sessions)
seg.run()

logger.info("Segmentation: Finished")

logger.success(">> FINISHED <<")

# if __name__ == "__main__":
# main()
