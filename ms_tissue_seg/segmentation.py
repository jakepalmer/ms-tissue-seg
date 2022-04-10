import shutil
import csv
from pathlib import Path
from loguru import logger
import ants
import antspynet

from ms_tissue_seg.utils import Constants, runBash

constants = Constants()


class SegmentationBIANCA:
    def __init__(self, subjects, sessions, threshold=[0.9], min_voxels=5) -> None:
        self.subjects: list = subjects
        self.sessions: list = sessions
        self.threshold: list = threshold
        self.min_voxels: int = min_voxels

    def setup_subj_derivs(self, subj, ses) -> Path:
        subj_outdir: Path = constants.processed_data_dir / subj / ses / "anat"
        subj_outdir.mkdir(exist_ok=True, parents=True)
        return subj_outdir

    def runMakeMasterfile(self, outdir):
        row = [
            f"{outdir}/flair.anat/T2_biascorr_wm.nii.gz",
            f"{outdir}/t1.anat/T1_biascorr_brain.nii.gz",
            f"{outdir}/flair2std.mat",  #! CHECK
        ]
        mfile = open(f"{outdir}/masterfile.txt", "w")
        for element in row:
            mfile.write(element + " ")
        mfile.close()

    def bianca(self, outdir):
        cmd = f"""bianca \
                    --singlefile={outdir}/masterfile.txt \
                    --querysubjectnum=1 \
                    --brainmaskfeaturenum=1 \
                    --featuresubset=1,2 \
                    --matfeaturenum=3 \
                    --spatialweight=2 \
                    --patchsizes=3 \
                    --loadclassifierdata=/opt/wmh_harmonisation/BIANCA_training_datasets/Mixed_WH-UKB_FLAIR_T1 \
                    -o {outdir}/wmh_mask_prob.nii.gz \
                    –v
        """
        runBash(cmd)
        for t in self.threshold:
            cmd = f"fslmaths {outdir}/wmh_mask_prob.nii.gz -thr {t} -bin {outdir}/wmh_mask_bin{t}.nii.gz"
            runBash(cmd)

    def bianca_stats(self, outdir, subj, ses):
        for t in self.threshold:
            cmd = f"bianca_cluster_stats {outdir}/wmh_mask_prob.nii.gz {t} {self.min_vocels} > {outdir}/wmh_mask_bin{t}_stats.txt"
            runBash(cmd)

            # Collate stats
            fields = [
                "ID",
                "probability_threshold_used",
                "min_cluster_size_used",
                "WMH_number",
                "WMH_volume",
            ]
            collated_file = Path("/tmp/output/WMHstats_collated.csv")

            with open(f"{outdir}/wmh_mask_bin{t}_stats.txt") as f:
                lines = f.readlines()
                for line in lines:
                    l = line.rstrip().split(" ")
                    if "number" in l:
                        n = l[-1]
                    elif "volume" in l:
                        v = l[-1]
                row = [[subj, ses, t, self.min_voxels, n, v]]
                if collated_file.is_file():
                    with open(collated_file, "a+") as file:
                        writer = csv.writer(file)
                        writer.writerows(row)
                else:
                    with open(collated_file, "w") as file:
                        writer = csv.writer(file)
                        writer.writerow(fields)
                        writer.writerows(row)

    # def tidy(outdir):
    #     shutil.rmtree(f"{outdir}/t1")
    #     shutil.rmtree(f"{outdir}/t1.anat")
    #     shutil.rmtree(f"{outdir}/flair")
    #     shutil.rmtree(f"{outdir}/flair.anat")

    def run(self):
        for subj, ses in zip(self.subjects, self.sessions):
            logger.info(f"Running {subj} {ses}")
            outdir = self.setup_subj_derivs(subj, ses)


class SegmentationANTs:
    def __init__(self, subjects, sessions) -> None:
        self.subjects: list = subjects
        self.sessions: list = sessions

    def setup_subj_derivs(self, subj, ses) -> Path:
        subj_outdir: Path = constants.processed_data_dir / subj / ses / "anat_ants"
        subj_outdir.mkdir(exist_ok=True, parents=True)
        return subj_outdir

    def flair_seg(self, subj, ses, outdir):

        anat = ants.image_read(
            f"{constants.bids_data_dir}/{subj}/{ses}/anat/{subj}_{ses}_T1w.nii.gz"
        )
        flair = ants.image_read(
            f"{constants.bids_data_dir}/{subj}/{ses}/anat/{subj}_{ses}_FLAIR.nii.gz"
        )

        wmh_segs = antspynet.sysu_media_wmh_segmentation(
            flair,
            t1=anat,
            use_ensemble=True,
            antsxnet_cache_directory=None,
            verbose=True,
        )

        ants.image_write(wmh_segs, f"{outdir}/wmh_prob_segs.nii.gz")

    def tissue_seg(self, subj, ses, outdir):
        """
        The labeling is as follows:
        Label 0 :  background
        Label 1 :  CSF
        Label 2 :  gray matter
        Label 3 :  white matter
        Label 4 :  deep gray matter
        Label 5 :  brain stem
        Label 6 :  cerebellum
        """
        tissue_types = {
            0: "background",
            1: "CSF",
            2: "gm",
            3: "wm",
            4: "deepgm",
            5: "brainstem",
            6: "cerebellum",
        }

        anat = ants.image_read(
            f"{constants.bids_data_dir}/{subj}/{ses}/anat/{subj}_{ses}_T1w.nii.gz"
        )

        tissue_segs = antspynet.deep_atropos(
            anat,
            do_preprocessing=True,
            use_spatial_priors=1,
            antsxnet_cache_directory=None,
            verbose=True,
        )

        segs = tissue_segs["segmentation_image"]
        ants.image_write(segs, f"{outdir}/wmh_prob_segs.nii.gz")

        for i in range(0, len(tissue_segs["probability_images"])):
            img = ants.threshold_image(
                tissue_segs["probability_images"], low_thresh=i, high_thresh=i
            )
            ants.image_write(
                img, f"{outdir}/atropos_{tissue_types[i]}_prob_segs.nii.gz"
            )

    def run(self):
        for subj, ses in zip(self.subjects, self.sessions):
            logger.info(f"Running {subj} {ses}")
            outdir = self.setup_subj_derivs(subj, ses)
            self.flair_seg(subj, ses, outdir)
