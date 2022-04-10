"""
Command line call to generate Dockerfile with Neurodocker.
"""
import os
from ms_tissue_seg.utils import Constants

constants = Constants()

dockerfile = constants.base_dir / "Dockerfile"

cmd = f"""docker run --rm repronim/neurodocker:master generate docker \
            --base=python:3.9-slim-buster \
            --pkg-manager=apt \
            --dcm2niix version=v1.0.20201102 method=source \
            --fsl version=6.0.1 method=binaries \
            --afni method=binaries version=latest \
            --ants version=2.3.4 \
            --run "pip3 install \
                    loguru \
                    black \
                    scipy \
                    mriqc \
                    antspyx \
                    antspynet \
                    pycdlib \
                    dcm2bids" \
            --run "git clone https://git.fmrib.ox.ac.uk/open-science/analysis/wmh_harmonisation.git /opt/wmh_harmonisation" \
            --run "curl -fsSLO https://get.docker.com/builds/Linux/x86_64/docker-17.04.0-ce.tgz && \
                    tar xzvf docker-17.04.0-ce.tgz && \
                    mv docker/docker /usr/local/bin && \
                    rm -r docker docker-17.04.0-ce.tgz" > {str(dockerfile)}"""

os.system(cmd)
