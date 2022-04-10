from pathlib import Path
from loguru import logger

from ms_tissue_seg.utils import Constants, runBash

constants = Constants()


class Preprocess:
    def __init__(self, subjects, sessions):
        self.subjects: list = subjects
        self.sessions: list = sessions

    def setup_subj_derivs(self, subj, ses) -> Path:
        outdir = constants.processed_data_dir / subj / ses / "anat"
        outdir.mkdir(parents=True, exist_ok=True)
        return outdir

    def t1_prep(self, subj, ses, outdir):
        logger.info("T1 preprocessing...")
        cmd = f"""fsl_anat \
                    -i {constants.bids_data_dir}/{subj}/{ses}/anat/{subj}_{ses}_T1w.nii.gz \
                    -o {outdir}/t1 \
                    -t T1"""
        # runBash(cmd)

    def flair_prep(self, subj, ses, outdir):
        logger.info("FLAIR preprocessing...")
        cmd = f"""fsl_anat \
                    -i {constants.bids_data_dir}/{subj}/{ses}/anat/{subj}_{ses}_FLAIR.nii.gz \
                    -o {outdir}/flair \
                    -t T2 \
                    --nononlinreg \
                    --nosubcortseg \
                    --noseg"""
        runBash(cmd)

    def gen_mask(self, outdir):
        cmd = f"""make_bianca_mask \
                    {outdir}/t1.anat/T1_biascorr \
                    {outdir}/t1.anat/T1_fast_pve_0.nii.gz \
                    {outdir}/t1.anat/MNI_to_T1_nonlin_field.nii.gz"""
        runBash(cmd)

    def apply_mask(self, outdir):
        cmd_mask_brain = f"fslmaths {outdir}/flair.anat/T2_biascorr.nii.gz -mas {outdir}/t1.anat/T1_biascorr_brain_mask.nii.gz {outdir}/flair.anat/T2_biascorr_brain.nii.gz"
        cmd_mask_wm = f"fslmaths {outdir}/flair.anat/T2_biascorr.nii.gz -mas {outdir}/t1.anat/T1_biascorr_bianca_mask.nii.gz {outdir}/flair.anat/T2_biascorr_wm.nii.gz"

        runBash(cmd_mask_brain)
        runBash(cmd_mask_wm)

    def run(self):
        for subj, ses in zip(self.subjects, self.sessions):
            logger.info(f"Running {subj}_{ses}")
            outdir = self.setup_subj_derivs(subj, ses)
            self.t1_prep(subj, ses, outdir)
            self.flair_prep(subj, ses, outdir)
            self.gen_mask(outdir)
            self.apply_mask(outdir)
