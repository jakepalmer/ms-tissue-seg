# MS Tissue and Lesion Segmentation

:warning: This is a work in progress!

Tissue and lesion segmentation for modelling MS lesion progression.

## Project Organization

    ├── LICENSE
    ├── README.md                               <- The top-level README for using this project
    ├── docker-compose.yaml
    ├── Dockerfile
    ├── setup.py                                <- Makes project pip installable (pip install -e .)
    ├── data
    │   ├── bids_input                          <- BIDS compliant input files converted from `sourcedata`
    │   ├── derivatives                         <- Outputs of processing derived from bids_input
    │   ├── sourcedata                          <- The original, immutable data (here, *.iso files)
    ├── ms_tissue_seg                           <- Source code
    │   ├── __init__.py                         <- Makes ms_tissue_seg a Python module
    │   ├── converter.py                        <- Tools for converting from sourcedata to BIDS format
    │   ├── mriqc.py                            <- Basic wrapper to run MRIQC (see below for reference)
    │   ├── preprocess.py                       <- Tools for preparing input files (e.g. brain extract, denoise etc.)
    │   ├── segmentation.py                     <- N-tissue and lesion segmentation
    │   ├── utils.py                            <- General helper variables/functions (e.g. constant variables)
    │   ├── src                                 <- Supporting files
    │   │   ├── generate_container_recipe.py    <- Neurodocker command to generate Dockerfile for analysis
    │   │   ├── dcm2bids_config.json            <- Configuration for converting from `sourcedata` to BIDS

## Overview

This analysis is packaged as a Docker container, so only requires Docker to be installed on your system. See [here](https://docs.docker.com/get-docker/) for instructions.

The pipeline has been written as an end-to-end pipeline that takes `.iso` files as the 'raw' inputs and outputs all processed files for each participant to the `/data/derivatives` directory.

Both a T1-weighted and FLAIR scan for each participant are required.

## Usage

To execute this pipeline:

1. Clone the repo locally.
2. Add the `.iso` files into `/data/sourcedata` directory
3. In terminal, change directory to the cloned repo. For example on Mac or Linux:

    `cd /path/to/clone/repo`

4. Start processing by running:

    `docker-compose run --rm ms_tissue_seg`

## Processing details and references

### Environment

Docker container generated with [Neurodocker](https://www.repronim.org/neurodocker/index.html). See the `/ms_tissue_seg/src/generate_container_recipe.py` for command used.

### Dicom to BIDS

BIDS is a standard for structuring neuroimaging datasets that allows a consistent interface and documentation of datasets. `dcm2bids` is a tool that facilitates the conversion according the the configurations set in `/ms_tissue_seg/src/dcm2bids_config.json`.

Documentation: <https://unfmontreal.github.io/Dcm2Bids/>
Citation: [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4568180.svg)](https://doi.org/10.5281/zenodo.4568180)

### QC

MRIQC is a BIDS-app used run for automatic QC of input T1w images that facilitates visual inspection and generates a range of participant and group-level QC metrics.

Documentation: <https://mriqc.readthedocs.io/en/latest/>
Citation: [![DOI](https://doi.org/10.1371/journal.pone.0184661.svg)](https://doi.org/10.1371/journal.pone.0184661)

### Preprocessing

T1w and FLAIR images were preprocessed using steps described in [Tustison et al.](https://doi.org/10.1016/j.neuroimage.2014.05.044), implemented in [ANTsPyNet](https://github.com/ANTsX/ANTsPyNet/blob/master/antspynet/utilities/preprocess_image.py). Steps included denoising, brain extraction, ANTs N4 bias field correction and affine registration to MNI template.

Documentation: <https://github.com/ANTsX/ANTsPyNet>
Citation: [![DOI](https://doi.org/10.1016/j.neuroimage.2014.05.044)](https://doi.org/10.1016/j.neuroimage.2014.05.044)

### Tissue segmentation

3-tissue segmentation was then run on preprocessed T1w images using ANTs [ATROPOS](https://antspy.readthedocs.io/en/latest/segmentation.html?highlight=atropos).

Documentation: <https://antspy.readthedocs.io/en/latest/>
Citation: [![DOI](https://doi.org/10.1007/s12021-011-9109-y)](https://doi.org/10.1007/s12021-011-9109-y)

### Lesion segmentation

Finally, automatic lesion segmentation was run using using `sysu_media` lesion segmentation as implemented in [ANTsPyNet](https://github.com/ANTsX/ANTsPyNet/blob/master/antspynet/utilities/white_matter_hyperintensity_segmentation.py) taking both preprocessed T1w and FLAIR as inputs.

Documentation: <https://github.com/ANTsX/ANTsPyNet>
Citation: [![DOI](https://doi.org/10.1016/j.neuroimage.2018.07.005)](https://doi.org/10.1016/j.neuroimage.2018.07.005) and [![DOI](https://doi.org/10.1109/TMI.2019.2905770)](https://doi.org/10.1109/TMI.2019.2905770)

--------
Project based on the [cookiecutter data science project template](https://drivendata.github.io/cookiecutter-data-science/) #cookiecutterdatascience
