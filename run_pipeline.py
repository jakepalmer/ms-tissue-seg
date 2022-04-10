"""
Main script to coordinate pipeline.
"""
from loguru import logger
from glob import glob
from time import time

from ms_tissue_seg.utils import constants
from ms_tissue_seg import converter, mriqc, preprocess, segmentation

# if __name__ == "__main__":

# TODO: Add log to file

logger.success(">> STARTING PROCESSING <<")

# --- Convert dicom to BIDS ---
logger.info("Dicom to BIDS conversion: Running...")
start = time()

iso_objects = glob(f"{str(constants.raw_data_dir)}/*iso")
subjects, sessions = converter.extract_dcm(iso_objects, extract_iso=False)
# converter.dcm2bids(subjects, sessions)

# BIDS-ify subject and session IDs
subjects = [f"sub-{s}" for s in subjects]
sessions = [f"ses-{s}" for s in sessions]

logger.info("Dicom to BIDS conversion: Finished")

# --- Quality control ---
# logger.info("Quality control: Running...")

# mriqc.runQC()

# logger.info("Quality control: Finished")

# --- Preprocess FLAIR and T1w ---
logger.info("Preprocessing: Running...")

prep = preprocess.Preprocess(subjects, sessions)
# prep.run()

logger.info("Preprocessing: Finished")

# --- Lesion segmentation ---
logger.info("Lesion segmentation: Running...")

seg = segmentation.SegmentationBIANCA(subjects, sessions)
# seg = segmentation.SegmentationANTs(subjects, sessions)
seg.run()

logger.info("Lesion segmentation: Finished")

logger.success(">> FINISHED <<")
