import shutil
import csv
from pathlib import Path
from loguru import logger
import ants
import antspynet

from ms_tissue_seg.utils import Constants, runBash

constants = Constants()


class SegmentationANTs:
    """
    Deep ATROPOS reference:
    https://link.springer.com/protocol/10.1007/978-1-4939-7647-8_2
    """

    def __init__(self, subjects, sessions) -> None:
        self.subjects: list = subjects
        self.sessions: list = sessions

    def setup_subj_derivs(self, subj, ses) -> Path:
        outdir = constants.processed_data_dir / subj / ses
        outdir.mkdir(exist_ok=True, parents=True)
        return outdir

    def tissue_seg(self, subj, ses, outdir):

        outdir = constants.processed_data_dir / subj / ses
        anat = ants.image_read(
            f"{constants.processed_data_dir}/{subj}/{ses}/preprocessed_t1_brain.nii.gz"
        )
        flair = ants.image_read(
            f"{constants.processed_data_dir}/{subj}/{ses}/preprocessed_flair_brain.nii.gz"
        )
        mask = ants.image_read(
            f"{constants.processed_data_dir}/{subj}/{ses}/preprocessed_t1_mask.nii.gz"
        )

        segmentations = ants.atropos(
            a=[anat, flair],
            x=mask,
            m="[0.3,1x1x1]",
            i=[constants.template_gm, constants.template_wm, constants.template_csf],
            priorweight=0.5,
            v=1,
        )

        tissue_segs = segmentations["segmentation"]
        ants.image_write(tissue_segs, f"{outdir}/tissue_segs.nii.gz")

        gm = segmentations["probabilityimages"][0]
        ants.image_write(gm, f"{outdir}/tissue_segs_gm_prob.nii.gz")

        wm = segmentations["probabilityimages"][1]
        ants.image_write(wm, f"{outdir}/tissue_segs_wm_prob.nii.gz")

        csf = segmentations["probabilityimages"][2]
        ants.image_write(csf, f"{outdir}/tissue_segs_csf_prob.nii.gz")

    def flair_seg(self, outdir):

        anat = ants.image_read(f"{outdir}/preprocessed_t1_brain.nii.gz")
        flair = ants.image_read(f"{outdir}/preprocessed_flair_brain.nii.gz")

        wmh_segs = antspynet.sysu_media_wmh_segmentation(
            flair,
            t1=anat,
            use_ensemble=True,
            antsxnet_cache_directory=None,
            verbose=True,
        )

        ants.image_write(wmh_segs, f"{outdir}/tissue_segs_lesion_prob.nii.gz")

    def run(self):
        for subj, ses in zip(self.subjects, self.sessions):
            logger.info(f">> {subj} {ses}")
            outdir = self.setup_subj_derivs(subj, ses)
            self.tissue_seg(subj, ses, outdir)
            self.flair_seg(outdir)
