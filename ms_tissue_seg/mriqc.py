"""
Run participant and group level QC with MRIQC.
"""
import os
from ms_tissue_seg.utils import constants, runBash, runBash_parallel


def runQC():

    mriqc_dir = constants.local_base_dir / "data" / "derivatives" / "mriqc"
    mriqc_dir.mkdir(exist_ok=True, parents=True)

    args = []

    cmd_base = f"""docker run --rm \
        -v {str(constants.local_base_dir)}/data/bids_input:/data:ro \
        -v {str(mriqc_dir)}:/out \
        -v /var/run/docker.sock:/var/run/docker.sock \
        nipreps/mriqc:latest \
            /data /out """

    cmd = cmd_base + "participant"

    args.append(cmd)
    runBash_parallel(func=os.system, args=args)
    # runBash(cmd)

    cmd = cmd_base + "group"
    runBash(cmd)
