import shutil
from pathlib import Path

import ants
from antspynet import sysu_media_wmh_segmentation as wmh_segmentation
from loguru import logger
from scipy.io import savemat

from ms_tissue_seg.utils import Constants, gather_templates

constants = Constants()


class Segmentation:
    def __init__(self, subjects, sessions, templates) -> None:
        self.subjects: list = subjects
        self.sessions: list = sessions
        self.templates: dict = templates

    def setup_subj_derivs(self) -> Path:
        outdir = constants.processed_data_dir / self.subject / self.session
        outdir.mkdir(exist_ok=True, parents=True)
        return outdir

    def tissue_seg(self) -> None:
        outdir = constants.processed_data_dir / self.subject / self.session
        anat = ants.image_read(
            f"{constants.processed_data_dir}/{self.subject}/{self.session}/preprocessed_t1_brain.nii.gz"
        )
        flair = ants.image_read(
            f"{constants.processed_data_dir}/{self.subject}/{self.session}/preprocessed_flair_brain.nii.gz"
        )
        mask = ants.image_read(
            f"{constants.processed_data_dir}/{self.subject}/{self.session}/preprocessed_t1_mask.nii.gz"
        )

        segmentations = ants.atropos(
            a=[anat, flair],
            x=mask,
            m="[0.3,1x1x1]",
            i=[self.templates["gm"], self.templates["wm"], self.templates["csf"]],
            priorweight=0.5,
            v=1,
        )

        tissue_segs = segmentations["segmentation"]
        ants.image_write(tissue_segs, f"{self.outdir}/tissue_segs.nii.gz")
        savemat(f"{self.outdir}/tissue_segs.mat", {"data": tissue_segs.numpy()})

        gm = segmentations["probabilityimages"][0]
        ants.image_write(gm, f"{self.outdir}/tissue_segs_gm_prob.nii.gz")
        savemat(f"{self.outdir}/tissue_segs_gm_prob.mat", {"data": gm.numpy()})

        wm = segmentations["probabilityimages"][1]
        ants.image_write(wm, f"{self.outdir}/tissue_segs_wm_prob.nii.gz")
        savemat(f"{self.outdir}/tissue_segs_wm_prob.mat", {"data": wm.numpy()})

        csf = segmentations["probabilityimages"][2]
        ants.image_write(csf, f"{self.outdir}/tissue_segs_csf_prob.nii.gz")
        savemat(f"{self.outdir}/tissue_segs_csf_prob.mat", {"data": csf.numpy()})

    def flair_seg(self):
        anat = ants.image_read(f"{self.outdir}/preprocessed_t1_brain.nii.gz")
        flair = ants.image_read(f"{self.outdir}/preprocessed_flair_brain.nii.gz")

        wmh_segs = wmh_segmentation(
            flair,
            t1=anat,
            use_ensemble=True,
            antsxnet_cache_directory=None,
            verbose=True,
        )

        ants.image_write(wmh_segs, f"{self.outdir}/tissue_segs_lesion_prob.nii.gz")
        savemat(
            f"{self.outdir}/tissue_segs_lesion_prob.mat", {"data": wmh_segs.numpy()}
        )

    def run(self):
        for subject, session in zip(self.subjects, self.sessions):

            logger.info(f">> {subject} {session}")

            self.subject: str = subject
            self.session: str = session
            self.outdir: Path = self.setup_subj_derivs()

            logger.debug(f">> {subject} {session}: 3-tissue anatomical segmentation...")
            self.tissue_seg()
            logger.debug(f">> {subject} {session}: Lesion segmentation...")
            self.flair_seg()
