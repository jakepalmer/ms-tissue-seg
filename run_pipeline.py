"""
Main entrypoint for processing pipeline.
"""
from loguru import logger
from glob import glob
from joblib import Parallel, delayed

from ms_tissue_seg.utils import constants, gather_templates
from ms_tissue_seg import converter, mriqc
from ms_tissue_seg.preprocess import Preprocess
from ms_tissue_seg.segmentation import Segmentation

logger.add(f"{constants.processed_data_dir}/log_run_pipeline.log", level="DEBUG")


@logger.catch
def main():
    logger.success(">> STARTING PROCESSING <<")

    # --- Convert dicom to BIDS ---
    logger.info("Dicom to BIDS conversion: Running")

    iso_objects = glob(f"{str(constants.raw_data_dir)}/*iso")
    subjects, sessions = converter.extract_dcm(iso_objects, extract_iso=False)
    # converter.dcm2bids(subjects, sessions)

    # Update subject and session IDs to BIDS structure
    subjects = [f"sub-{s}" for s in subjects]
    sessions = [f"ses-{s}" for s in sessions]

    logger.info("Confirming only correct timepoints are included...")
    subjects, sessions = converter.check_timepoints(subjects, sessions)

    assert len(subjects) == len(sessions), logger.error(
        "Mismatch in number of subjects and sessions!"
    )

    logger.info("Dicom to BIDS conversion: Finished")

    # --- Quality control ---
    # try:
    #     logger.info("Quality control: Running")

    #     mriqc.runQC()

    #     logger.info("Quality control: Finished")
    # except Exception as e:
    #     logger.error(e)
    #     logger.warning("MRIQC failed - skipping...")

    # --- Download templates to be used in processing ---
    logger.info("Download template files: Running")

    templates: dict = gather_templates()

    logger.info("Download template files: Finished")

    # --- Preprocess FLAIR and T1w ---
    logger.info(f"Running {len(subjects)} subjects:")
    logger.info(dict(zip(subjects, sessions)))

    logger.info("Preprocessing: Running")

    prep = Preprocess(subjects, sessions, templates)
    prep.run()

    logger.info("Preprocessing: Finished")

    # --- Tissue and lesion segmentation ---
    logger.info("Segmentation: Running")

    seg = Segmentation(subjects, sessions, templates)
    seg.run()

    logger.info("Segmentation: Finished")

    logger.success(">> FINISHED <<")


if __name__ == "__main__":
    main()
