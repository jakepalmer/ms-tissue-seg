"""
Run participant and group level QC with MRIQC.
"""
from ms_tissue_seg.utils import Constants, runBash

constants = Constants()


def runQC():

    mriqc_dir = constants.local_base_dir / "data" / "derivatives" / "mriqc"
    mriqc_dir.mkdir(exist_ok=True, parents=True)

    cmd_base = f"""docker run --rm \
        -v {str(constants.local_base_dir)}/data/bids_input:/data:ro \
        -v {str(mriqc_dir)}:/out \
        -v /var/run/docker.sock:/var/run/docker.sock \
        nipreps/mriqc:latest /data /out """
    options = f" -w {constants.tmp_dir} --nprocs {constants.nthreads} --no-sub"

    cmd = cmd_base + "participant" + options
    runBash(cmd)

    cmd = cmd_base + "group" + options
    runBash(cmd)
