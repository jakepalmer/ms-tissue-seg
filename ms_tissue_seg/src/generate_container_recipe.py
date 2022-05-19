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
                --ants version=2.3.4 \
                --run "curl -fsSLO https://get.docker.com/builds/Linux/x86_64/docker-17.04.0-ce.tgz && \
                        tar xzvf docker-17.04.0-ce.tgz && \
                        mv docker/docker /usr/local/bin && \
                        rm -r docker docker-17.04.0-ce.tgz" \
                --run "pip3 install \
                        loguru \
                        black \
                        scipy \
                        antspyx \
                        antspynet \
                        pycdlib \
                        dcm2bids \
                        templateflow" > {str(dockerfile)}"""

os.system(cmd)
