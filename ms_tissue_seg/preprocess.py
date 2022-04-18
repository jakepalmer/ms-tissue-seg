from pathlib import Path
from attr import field
from loguru import logger
import ants
from antspynet import preprocess_brain_image
from antspynet import brain_extraction
from numpy import fix

from ms_tissue_seg.utils import Constants

constants = Constants()


class Preprocess:
    """
    Implements preprocessing described in:
    https://pubmed.ncbi.nlm.nih.gov/24879923/

    See documentation:
    https://github.com/ANTsX/ANTsPyNet/blob/master/antspynet/utilities/preprocess_image.py
    """

    def __init__(self, subjects, sessions):
        self.subjects: list = subjects
        self.sessions: list = sessions

    def setup_subj_derivs(self, subj, ses) -> Path:
        outdir = constants.processed_data_dir / subj / ses
        outdir.mkdir(parents=True, exist_ok=True)
        return outdir

    # def preprocess(self, subj, ses, modality, outdir, verbose=True):

    #     logger.info(f"  >> {subj} {ses}: Preprocessing {modality}")

    #     # --- Load data ---
    #     if modality == "t1":
    #         img_in = ants.image_read(
    #             f"{constants.bids_data_dir}/{subj}/{ses}/anat/{subj}_{ses}_T1w.nii.gz"
    #         )
    #     elif modality == "flair":
    #         img_in = ants.image_read(
    #             f"{constants.bids_data_dir}/{subj}/{ses}/anat/{subj}_{ses}_FLAIR.nii.gz"
    #         )
    #     img = ants.image_clone(img_in)

    #     # --- Truncate intensity ---
    #     quantiles = (img_in.quantile(0.1), img_in.quantile(0.99))
    #     img[img < quantiles[0]] = quantiles[0]
    #     img[img > quantiles[1]] = quantiles[1]

    #     # --- Brain extraction ---
    #     probability_mask = brain_extraction(
    #         img,
    #         modality=modality,
    #         antsxnet_cache_directory="/tmp",
    #         verbose=verbose,
    #     )

    #     mask = ants.threshold_image(probability_mask, 0.5, 1, 1, 0)
    #     mask = ants.morphology(mask, "close", 6).iMath_fill_holes()

    #     # --- Bias correction ---
    #     img = ants.n4_bias_field_correction(img, mask, shrink_factor=4, verbose=verbose)

    #     # --- Denoise ---
    #     img = ants.denoise_image(img, shrink_factor=1)

    #     # --- Derive MNI warps ---
    #     if modality == "flair":

    #         # Template to flair
    #         warped: dict = ants.registration(
    #             fixed=img, moving=constants.template_brain, type_of_transform="SyN"
    #         )
    #         fwdxfm = ants.read_transform(warped["fwdtransforms"])
    #         invxfm = ants.read_transform(warped["invtransforms"])
    #         ants.write_transform(fwdxfm, f"{outdir}/transform_mni2flair.mat")
    #         ants.write_transform(invxfm, f"{outdir}/transform_flair2mni.mat")
    #         ants.image_write(warped["warpedmovout"], f"{outdir}/mni2flair.nii.gz")

    #         # T1 to flair
    #         t1 = ants.image_read(f"{outdir}/preprocessed_t1_brain.nii.gz")
    #         warped: dict = ants.registration(
    #             fixed=img, moving=t1, type_of_transform="SyN"
    #         )
    #         fwdxfm = ants.read_transform(warped["fwdtransforms"])
    #         invxfm = ants.read_transform(warped["invtransforms"])
    #         ants.write_transform(fwdxfm, f"{outdir}/transform_anat2flair.mat")
    #         ants.write_transform(invxfm, f"{outdir}/transform_flair2anat.mat")
    #         ants.image_write(
    #             warped["warpedmovout"], f"{outdir}/preprocessed_anat2flair.nii.gz"
    #         )

    #     # --- Write preprocessed files ---
    #     ants.image_write(img, f"{outdir}/preprocessed_{modality}_brain.nii.gz")
    #     ants.image_write(mask, f"{outdir}/preprocessed_{modality}_mask.nii.gz")

    def preprocess(self, subj, ses, modality, outdir):

        if modality == "t1":
            img = ants.image_read(
                f"{constants.bids_data_dir}/{subj}/{ses}/anat/{subj}_{ses}_T1w.nii.gz"
            )
        elif modality == "flair":
            img = ants.image_read(
                f"{constants.bids_data_dir}/{subj}/{ses}/anat/{subj}_{ses}_FLAIR.nii.gz"
            )

        preprocessed: dict = preprocess_brain_image(
            img,
            truncate_intensity=(0.01, 0.99),
            brain_extraction_modality=modality,
            template_transform_type="Affine",  # "Affine" | "Rigid"
            template=constants.template_t1,
            do_bias_correction=True,
            return_bias_field=False,
            do_denoising=True,
            intensity_matching_type=None,
            reference_image=None,
            intensity_normalization_type=None,  # "01" | "0mean"
            antsxnet_cache_directory="/tmp",
            verbose=True,
        )

        # --- Write outputs

        preprocessed_img = preprocessed["preprocessed_image"]
        ants.image_write(preprocessed_img, f"{outdir}/preprocessed_{modality}.nii.gz")

        brainmask = preprocessed["brain_mask"]
        ants.image_write(brainmask, f"{outdir}/preprocessed_{modality}_mask.nii.gz")

        brain = ants.mask_image(preprocessed_img, brainmask)
        ants.image_write(brain, f"{outdir}/preprocessed_{modality}_brain.nii.gz")

        xfms = preprocessed["template_transforms"]
        fwd_xfm = ants.read_transform(xfms["fwdtransforms"][0])
        inv_xfm = ants.read_transform(xfms["invtransforms"][0])
        ants.write_transform(fwd_xfm, f"{outdir}/transform_{modality}_2_mni.mat")
        ants.write_transform(inv_xfm, f"{outdir}/transform_mni_2_{modality}.mat")

    # def t1_to_flair(outdir):
    #     flair = ants.image_read(f"{outdir}/preprocessed_flair_brain.nii.gz")
    #     t1 = ants.image_read(f"{outdir}/preprocessed_t1_brain.nii.gz")

    #     warped: dict = ants.registration(
    #         fixed=flair, moving=t1, type_of_transform="SyN"
    #     )
    #     fwd_xfm = ants.read_transform(warped["fwdtransforms"])
    #     inv_xfm = ants.read_transform(warped["invtransforms"])
    #     ants.write_transform(fwd_xfm, f"{outdir}/transform_t1_2_flair.mat")
    #     ants.write_transform(inv_xfm, f"{outdir}/transform_flair_2_t1.mat")

    def run(self):
        for subj, ses in zip(self.subjects, self.sessions):
            logger.info(f">> {subj} {ses}")
            outdir = self.setup_subj_derivs(subj, ses)
            self.preprocess(subj, ses, "t1", outdir)
            self.preprocess(subj, ses, "flair", outdir)


#! === FSL ===
# class Preprocess:
#     def __init__(self, subjects, sessions):
#         self.subjects: list = subjects
#         self.sessions: list = sessions

#     def setup_subj_derivs(self, subj, ses) -> Path:
#         outdir = constants.processed_data_dir / subj / ses / "anat"
#         outdir.mkdir(parents=True, exist_ok=True)
#         return outdir

#     def t1_prep(self, subj, ses, outdir):
#         logger.info("T1 preprocessing...")
#         cmd = f"""fsl_anat \
#                     -i {constants.bids_data_dir}/{subj}/{ses}/anat/{subj}_{ses}_T1w.nii.gz \
#                     -o {outdir}/t1 \
#                     -t T1"""
#         # runBash(cmd)

#     def flair_prep(self, subj, ses, outdir):
#         logger.info("FLAIR preprocessing...")
#         cmd = f"""fsl_anat \
#                     -i {constants.bids_data_dir}/{subj}/{ses}/anat/{subj}_{ses}_FLAIR.nii.gz \
#                     -o {outdir}/flair \
#                     -t T2 \
#                     --nononlinreg \
#                     --nosubcortseg \
#                     --noseg"""
#         runBash(cmd)

#     def gen_mask(self, outdir):
#         cmd = f"""make_bianca_mask \
#                     {outdir}/t1.anat/T1_biascorr \
#                     {outdir}/t1.anat/T1_fast_pve_0.nii.gz \
#                     {outdir}/t1.anat/MNI_to_T1_nonlin_field.nii.gz"""
#         runBash(cmd)

#     def apply_mask(self, outdir):
#         cmd_mask_brain = f"fslmaths {outdir}/flair.anat/T2_biascorr.nii.gz -mas {outdir}/t1.anat/T1_biascorr_brain_mask.nii.gz {outdir}/flair.anat/T2_biascorr_brain.nii.gz"
#         cmd_mask_wm = f"fslmaths {outdir}/flair.anat/T2_biascorr.nii.gz -mas {outdir}/t1.anat/T1_biascorr_bianca_mask.nii.gz {outdir}/flair.anat/T2_biascorr_wm.nii.gz"

#         runBash(cmd_mask_brain)
#         runBash(cmd_mask_wm)

#     def run(self):
#         for subj, ses in zip(self.subjects, self.sessions):
#             logger.info(f"Running {subj}_{ses}")
#             outdir = self.setup_subj_derivs(subj, ses)
#             self.t1_prep(subj, ses, outdir)
#             self.flair_prep(subj, ses, outdir)
#             self.gen_mask(outdir)
#             self.apply_mask(outdir)
