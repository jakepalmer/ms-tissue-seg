from pathlib import Path
from loguru import logger
import ants
from antspynet import preprocess_brain_image

from ms_tissue_seg.utils import Constants, gather_templates

constants = Constants()


class Preprocess:
    """
    Implements preprocessing described in:
    https://pubmed.ncbi.nlm.nih.gov/24879923/

    See documentation:
    https://github.com/ANTsX/ANTsPyNet/blob/master/antspynet/utilities/preprocess_image.py
    """

    def __init__(self, subjects, sessions, templates):
        self.subjects: list = subjects
        self.sessions: list = sessions
        self.templates: dict = templates

    def setup_subj_derivs(self) -> Path:
        outdir = constants.processed_data_dir / self.subject / self.session
        outdir.mkdir(parents=True, exist_ok=True)
        return outdir

    def preprocess(self, modality):

        if modality == "t1":
            img = ants.image_read(
                f"{constants.bids_data_dir}/{self.subject}/{self.session}/anat/{self.subject}_{self.session}_T1w.nii.gz"
            )
        elif modality == "flair":
            img = ants.image_read(
                f"{constants.bids_data_dir}/{self.subject}/{self.session}/anat/{self.subject}_{self.session}_FLAIR.nii.gz"
            )

        preprocessed: dict = preprocess_brain_image(
            img,
            truncate_intensity=(0.01, 0.99),
            brain_extraction_modality=modality,
            template_transform_type="Affine",  # "Affine" | "Rigid"
            template=self.templates["t1"],
            do_bias_correction=True,
            return_bias_field=False,
            do_denoising=True,
            intensity_matching_type=None,
            reference_image=None,
            intensity_normalization_type=None,  # "01" | "0mean"
            antsxnet_cache_directory=constants.tmp_dir,
            verbose=True,
        )

        # --- Write outputs

        preprocessed_img = preprocessed["preprocessed_image"]
        ants.image_write(
            preprocessed_img, f"{self.outdir}/preprocessed_{modality}.nii.gz"
        )

        brainmask = preprocessed["brain_mask"]
        ants.image_write(
            brainmask, f"{self.outdir}/preprocessed_{modality}_mask.nii.gz"
        )

        brain = ants.mask_image(preprocessed_img, brainmask)
        ants.image_write(
            brain, f"{self.outdir}/preprocessed_{modality}_brain.nii.gz")

        xfms = preprocessed["template_transforms"]
        fwd_xfm = ants.read_transform(xfms["fwdtransforms"][0])
        inv_xfm = ants.read_transform(xfms["invtransforms"][0])
        ants.write_transform(
            fwd_xfm, f"{self.outdir}/transform_{modality}_2_mni.mat")
        ants.write_transform(
            inv_xfm, f"{self.outdir}/transform_mni_2_{modality}.mat")

    def run(self):
        for subject, session in zip(self.subjects, self.sessions):

            logger.info(f">> {subject} {session}")

            self.subject: str = subject
            self.session: str = session
            self.outdir: Path = self.setup_subj_derivs()

            logger.debug(f">> {subject} {session}: Preprocess T1w...")
            self.preprocess(modality="t1")
            logger.debug(f">> {subject} {session}: Preprocess FLAIR...")
            self.preprocess(modality="flair")
