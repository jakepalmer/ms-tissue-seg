# MS Tissue and Lesion Segmentation

:warning: This is a work in progress!

Tissue and lesion segmentation for modelling MS lesion progression.

## Project Organization

    ├── LICENSE
    ├── README.md                               <- The top-level README for developers using this project.
    ├── data
    │   ├── interim                             <- Intermediate data that has been transformed.
    │   ├── processed                           <- The final, canonical data sets for modeling.
    │   └── raw                                 <- The original, immutable data dump.
    ├── requirements.txt                        <- The requirements file for reproducing analysis environment
    ├── setup.py                                <- makes project pip installable (pip install -e .) so src can be imported
    ├── ms_tissue_seg                           <- Source code for use in this project.
    │   ├── __init__.py                         <- Makes ms_tissue_seg a Python module
    │   ├── utils                               <- General utilities
    │   │   └── constants.py
    │   ├── src                                 <- Supporting files
    │   │   └── generate_container_recipe.py    <- Neurodocker command to generate Docker container for analysis
    │   │   └── heuristic.py                    <- File required by Heudiconv for dicom to BIDS conversion

## Prerequisites

* Docker (add install instructions)

## Usage

* Clone repo
* Add `.iso` files into `/data/sourcedata` directory
* Run docker command `docker run --rm -it -v $PWD:/home ghcr.io/jakepalmer/ms-tissue-seg:dev`

## Processing details and references

### Environment

Docker container for end-to-end processing generated with [Neurodocker](https://www.repronim.org/neurodocker/index.html). See the `/ms_tissue_seg/src/generate_container_recipe.py` for command used.

### Dicom to BIDS

BIDS is a standard for structuring neuroimaging datasets that allows a consistent interface and documentation of datasets. `dcm2bids` is a tool that facilitates the 

<!-- HeuDiConv has been developed to automate the conversion from dicom to BIDS. It requires some setup (i.e. putting together a heuristic.py file to provide the rules for conversion), however this will generally only need to be setup once and has been done (see heudiconv_src/heuristic.py). This would need updating if the MRI sequences change. Example commands to help with the setup are included in the comments in the docstring for the runDcm2BIDS function in the run_pipeline.py file.

For more info see [BIDS](https://bids.neuroimaging.io/) and [HeuDiConv](https://heudiconv.readthedocs.io/en/latest/index.html) documentation, also [this HeuDiConv walkthrough](https://reproducibility.stanford.edu/bids-tutorial-series-part-2a/) and [wiki](https://github.com/bids-standard/bids-starter-kit). -->

#### Citation

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4568180.svg)](https://doi.org/10.5281/zenodo.4568180)

--------
Project based on the [cookiecutter data science project template](https://drivendata.github.io/cookiecutter-data-science/). #cookiecutterdatascience
