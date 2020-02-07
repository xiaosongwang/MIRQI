# MIRQI - Evaluation metrics for radiological report generation
MIRQI-r,p,f provides a quanitative assessment of the quality of generated radiology reports. 

## Prerequisites
1. Make the virtual environment (python 3):
    
    `conda env create -f environment.yml`

2. Install NLTK data:
    
    `python -m nltk.downloader universal_tagset punkt wordnet`

3. Download the `GENIA+PubMed` parsing model:

```python
>>> from bllipparser import RerankingParser
>>> RerankingParser.fetch_and_load('GENIA+PubMed')
```

## Usage
Place reports in a headerless, single column csv `{reports_file_path}`. Each report must be contained in quotes if (1) it contains a comma or (2) it spans multiple lines. See the sample csv files in the folder for an example. 

`python evaluate.py --reports_path_gt {gt_reports_file_path} -- report_path_cand {generated_reports_file_path}`

Run `python evaluate.py --help` for descriptions of all of the command-line arguments.

## Contributions
This repository builds upon the work of [NegBio](https://negbio.readthedocs.io/en/latest/) and [CheXpert](https://stanfordmlgroup.github.io/competitions/chexpert/).

This tool was developed by Xiaosong Wang.

## Citing
If you're using MIRQI evaluation metrics, please cite 
#[this paper]():

```
@inproceedings{
}
```
