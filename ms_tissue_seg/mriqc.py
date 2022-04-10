"""
Run participant and group level QC with MRIQC.
"""
from ms_tissue_seg.utils import constants, runBash


def runQC():
    cmd_base = f"""docker run -it --rm \
        -v {str(constants.bids_data_dir)}:/data:ro \
        -v {str(constants.processed_data_dir)}:/out \
        nipreps/mriqc:latest \
            /data /out """
    # cmd_base = f"""mriqc \
    #                 {str(constants.bids_data_dir)} \
    #                 {str(constants.processed_data_dir)} \
    #                 --no-sub \
    #                 -w /tmp """
    cmd = cmd_base + "participant"
    runBash(cmd)

    cmd = cmd_base + "group"
    runBash(cmd)
