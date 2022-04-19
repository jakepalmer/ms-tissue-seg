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
    │   ├── bids_input                          <- BIDS compliant input files converted from sourcedata
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
    │   │   ├── dcm2bids_config.json            <- Configuration for converting from sourcedata to BIDS

## Prerequisites

* Docker and docker-compose (add install instructions)

## Usage

* Clone repo
* Add `.iso` files into `/data/sourcedata` directory
* Run docker command `docker-compose run --rm ms_tissue_seg`

## Processing details and references

### Environment

Docker container for end-to-end processing generated with [Neurodocker](https://www.repronim.org/neurodocker/index.html). See the `/ms_tissue_seg/src/generate_container_recipe.py` for command used.

### Dicom to BIDS

BIDS is a standard for structuring neuroimaging datasets that allows a consistent interface and documentation of datasets. `dcm2bids` is a tool that facilitates the conversion according the the configurations set in `/ms_tissue_seg/src/dcm2bids_config.json`.

Documentation: <https://unfmontreal.github.io/Dcm2Bids/>
Citation: [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4568180.svg)](https://doi.org/10.5281/zenodo.4568180)

### Preprocessing

Preprocessing steps as described in...using ANTsPy. Steps include...

### Tissue segmentation

3-tissue segmentation...

### Lesion segmentation

Lesion segmentation...

--------
Project based on the [cookiecutter data science project template](https://drivendata.github.io/cookiecutter-data-science/) #cookiecutterdatascience
