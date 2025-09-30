# MS Tissue and Lesion Segmentation

Tissue and lesion segmentation for modelling MS lesion progression.

## Project Organization

    ├── LICENSE
    ├── README.md                               <- The top-level README for using this project
    ├── docker-compose.yaml
    ├── Dockerfile
    ├── pyproject.toml                          <- Project dependencies
    ├── uv.lock                                 <- Project dependencies
    ├── run_pipeline.py                         <- Main script co-ordinating the analysis
    ├── data
    │   ├── bids_input                          <- BIDS compliant input files converted from `sourcedata`
    │   ├── derivatives                         <- Outputs of processing derived from bids_input
    │   ├── sourcedata                          <- The original, immutable data (here, *.iso files)
    │   ├── dcm2bids_config.json                <- Configuration for converting from `sourcedata` to BIDS
    ├── ms_tissue_seg                           <- Source code
    │   ├── __init__.py                         <- Makes ms_tissue_seg a Python module
    │   ├── converter.py                        <- Tools for converting from sourcedata to BIDS format
    │   ├── mriqc.py                            <- Basic wrapper to run MRIQC (see below for reference)
    │   ├── preprocess.py                       <- Tools for preparing input files (e.g. brain extract, denoise etc.)
    │   ├── segmentation.py                     <- N-tissue and lesion segmentation
    │   ├── utils.py                            <- General helper variables/functions (e.g. constant variables) 

## Overview

This analysis is packaged as a Docker container, so only requires Docker to be installed on your system. See [here](https://docs.docker.com/get-docker/) for instructions.

The pipeline has been written as an end-to-end pipeline that takes `.iso` files as the 'raw' inputs and outputs all processed files for each participant to the `/data/derivatives` directory.

Both a T1-weighted and FLAIR scan for each participant are required.

### Notes on the processing

1. The `check_timepoints` function in `ms_tissue_seg/converter.py` checks whether the `ProcedureStepDescription` field in the BIDs data JSON file (referred to as the sidecar) includes the string 'screen' so only scans from the screening time point of the study are included and treatment time points are excluded. If subjects are excluded they will be logged in `data/derivatives/log_not_screen_timepoint.log` and a message will be printed to the terminal, for example

```bash
2025-09-25 20:49:54.032 | WARNING  | src.converter:check_timepoints:158 - 1 subjects not from screening timepoint
2025-09-25 20:49:54.032 | WARNING  | src.converter:check_timepoints:160 - Deleting from BIDS data directory:
2025-09-25 20:49:54.032 | WARNING  | src.converter:check_timepoints:162 -  > sub-RR246 ses-20190211
```

2. If you want to convert additional scan types to BIDS, the `data/dcm2bids_config.json` needs to be updated. Follow the documentation for `dcm2bids` linked below and follow the patterns already there for T1w and FLAIR.

## Setup

> **NOTE:** These instructions are not for Mac's with Silicone chips.

### Clone the repo

`cd` to the directory where you want to clone the repo and run:

```bash
git clone https://github.com/jakepalmer/ms-tissue-seg.git
```

Then `cd` into the `ms-tissue-seg` directory. All following instructions assume they are being run from this directory.

### Docker

It is preferrable to run the pipeline using docker. Installation instructions:

* [Windows](https://docs.docker.com/desktop/install/windows-install/) via the download Docker Desktop button and [this](https://docs.docker.com/desktop/install/windows-install/#start-docker-desktop) section.

Once Docker is installed, we first need to build the Docker image.

```bash
docker compose build
```

Note that the first time you do this it may take quite a while to build as some of the neuroimaging dependencies can be large.

### Local

> **WARNING:** the setup has not been tested locally on Windows, only on Mac (Intel chip).

* Install `uv`: https://docs.astral.sh/uv/getting-started/installation/
* Install Python: `uv python install 3.11`
* Create a virtual environment: `uv venv`
* Activate the virtual environment: `source ./.venv/bin/activate`
* Install the dependencies: `uv sync`

## Usage

To execute this pipeline:

1. Add the `.iso` files into `/data/sourcedata` directory
2. In terminal, change directory to the cloned repo. For example on Mac or Linux:

    `cd /path/to/cloned/ms-tissue-seg`

3. Start processing by running:

    `docker compose run --rm ms-tissue-seg`

   Or if you are not using docker:

    `uv run python run_pipeline.py`

## Processing details and references

### Dicom to BIDS

BIDS is a standard for structuring neuroimaging datasets that allows a consistent interface and documentation of datasets. `dcm2bids` is a tool that facilitates the conversion according the the configurations set in `/data/dcm2bids_config.json`.

Documentation: <https://unfmontreal.github.io/Dcm2Bids/>
Citation: [10.5281/zenodo.4568180](https://doi.org/10.5281/zenodo.4568180)

### QC

MRIQC is a BIDS-app used run for automatic QC of input T1w images that facilitates visual inspection and generates a range of participant and group-level QC metrics.

Documentation: <https://mriqc.readthedocs.io/en/latest/>  
Citation: [10.1371/journal.pone.0184661](https://doi.org/10.1371/journal.pone.0184661)

### Preprocessing

T1w and FLAIR images were preprocessed using steps described in [Tustison et al.](https://doi.org/10.1016/j.neuroimage.2014.05.044), implemented in [ANTsPyNet](https://github.com/ANTsX/ANTsPyNet/blob/master/antspynet/utilities/preprocess_image.py). Steps included denoising, brain extraction, ANTs N4 bias field correction and affine registration to MNI template.

Documentation: <https://github.com/ANTsX/ANTsPyNet>  
Citation: [10.1016/j.neuroimage.2014.05.044](https://doi.org/10.1016/j.neuroimage.2014.05.044)

### Tissue segmentation

3-tissue segmentation was then run on preprocessed T1w images using ANTs [ATROPOS](https://antspy.readthedocs.io/en/latest/segmentation.html?highlight=atropos).

Documentation: <https://antspy.readthedocs.io/en/latest/>  
Citation: [10.1007/s12021-011-9109-y](https://doi.org/10.1007/s12021-011-9109-y)

### Lesion segmentation

Finally, automatic lesion segmentation was run using using `sysu_media` lesion segmentation as implemented in [ANTsPyNet](https://github.com/ANTsX/ANTsPyNet/blob/master/antspynet/utilities/white_matter_hyperintensity_segmentation.py) taking both preprocessed T1w and FLAIR as inputs.

Documentation: <https://github.com/ANTsX/ANTsPyNet>  
Citation: [10.1016/j.neuroimage.2018.07.005](https://doi.org/10.1016/j.neuroimage.2018.07.005) and [10.1109/TMI.2019.2905770](https://doi.org/10.1109/TMI.2019.2905770)

--------
Project based on the [cookiecutter data science project template](https://drivendata.github.io/cookiecutter-data-science/) #cookiecutterdatascience
