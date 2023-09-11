# PB-metagenomics-tools

Welcome! Here you can find a variety of tools and pipelines tailored to using PacBio HiFi Reads for metagenomics. In addition to the resources currently available, we will continue to add new tools as they are developed.

The current version is v2.1.0. Please see the [**release notes**](https://github.com/PacificBiosciences/pb-metagenomics-tools/releases) for changes.

## HiFi Metagenomic Datasets & Publications

Several publicly available HiFi shotgun metagenomics datasets are listed on the   [**PacBio-Data**](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/PacBio-Data.md) page. These include multiple mock communities, reference standards, and empirical samples (human, chicken, and sheep gut microbiome, and environmental samples). Associated publications are also listed here.

A running list of publications using HiFi sequencing for metagenomics can be found [**here**](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/HiFi-Metagenomics-Publications.md). 

## Available pipelines

+ [**HiFi-MAG-Pipeline**](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/HiFi-MAG-Pipeline): Identify high-quality MAGs from HiFi metagenomic assemblies. Streamlined workflow includes a custom "completeness-aware" strategy to identify and protect long and complete contigs. Binning is performed with MetaBAT2 and SemiBin2, bin merging occurs with DAS_Tool, QC with CheckM2, and taxonomic assignments with GTDB-Tk. Outputs include high-quality MAG sequences, summary figures, and associated metadata. 

+ [**Taxonomic-Profiling-Diamond-Megan**](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/Taxonomic-Profiling-Diamond-Megan): Perform translation alignment of HiFi reads to a **protein** database using DIAMOND and summarize with MEGAN-LR, for the purpose of taxonomic and functional profiling. Provides access to taxonomic annotations from NCBI and GTDB, and outputs NCBI taxonomic counts in kraken (kreport) and metaphlan (mpa) formats. Also provides functional annotations based on multiple databases (EC, SEED, InterPro2GO, eggNOG), with new KEGG option available.

+ [**Taxonomic-Profiling-Minimap-Megan**](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/Taxonomic-Profiling-Minimap-Megan): Align HiFi reads to a **nucleotide** database using minimap2 and summarize with MEGAN-LR, for the purpose of taxonomic profiling. Provides access to NCBI and GTDB taxonomic annotations. Outputs NCBI taxonomic counts in kraken (kreport) and metaphlan (mpa) formats.

+ [**Taxonomic-Profiling-Sourmash**](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/Taxonomic-Profiling-Sourmash): Obtain taxonomic proflies using `sourmash gather` --> `taxonomy` approach. Sourmash provides GTDB and NCBI databases, or you can build your own database.

Each of these pipelines can be found in their respective folders. They are made available as [Snakemake](https://snakemake.readthedocs.io/en/stable/index.html) workflows. Snakemake is a python-based workflow manager. Snakemake workflows are highly portable because dependencies and environments are automatically setup using [Anaconda](https://docs.anaconda.com/anaconda/)/[Conda](https://docs.conda.io/projects/conda/en/latest/index.html). Snakemake also allows reproducibility, checkpointing, and the ability to scale workflows using HPC and cloud environments. Snakemake v5+ is required, and the workflows have been tested using v5.26+. You can optionally install snakemake via the provided conda environment file via `conda env create -f environment.yml`, and then activate this environment via `conda activate pb-metagenomics-tools` when you want to run any of these workflows.

## Other tools

Scripts and tools for metagenomics tasks are available in the [**pb-metagenomics-scripts**](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/pb-metagenomics-scripts) folder. Currently, there are scripts or notebooks to perform the following tasks: 

+ Convert outputs from common metagenomics profiling/classification programs into standard formats, including kraken report (kreport) and metaphlan report (mpa) formats. 

+ Compare kraken report files across multiple samples, with several visualization options.

## Documentation 

All documentation for snakemake pipelines can be found in the `docs/` folder above. Links are also provided below.

Available pipeline documentation: 
- [**Tutorial: HiFi-MAG-Pipeline**](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/Tutorial-HiFi-MAG-Pipeline.md)
- [**Tutorial: Taxonomic-Profiling-Diamond-Megan**](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/Tutorial-Taxonomic-Profiling-Diamond-Megan.md)
- [**Tutorial: Taxonomic-Profiling-Minimap-Megan**](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/Tutorial-Taxonomic-Profiling-Minimap-Megan.md)
- [**Tutorial: Taxonomic-Profiling-Sourmash**](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/Tutorial-Taxonomic-Profiling-Sourmash.md)

The documentation for [pb-metagenomics-scripts](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/pb-metagenomics-scripts) is provided in the folder.



### DISCLAIMER
THIS WEBSITE AND CONTENT AND ALL SITE-RELATED SERVICES, INCLUDING ANY DATA, ARE PROVIDED "AS IS," WITH ALL FAULTS, WITH NO REPRESENTATIONS OR WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, ANY WARRANTIES OF MERCHANTABILITY, SATISFACTORY QUALITY, NON-INFRINGEMENT OR FITNESS FOR A PARTICULAR PURPOSE. YOU ASSUME TOTAL RESPONSIBILITY AND RISK FOR YOUR USE OF THIS SITE, ALL SITE-RELATED SERVICES, AND ANY THIRD PARTY WEBSITES OR APPLICATIONS. NO ORAL OR WRITTEN INFORMATION OR ADVICE SHALL CREATE A WARRANTY OF ANY KIND. ANY REFERENCES TO SPECIFIC PRODUCTS OR SERVICES ON THE WEBSITES DO NOT CONSTITUTE OR IMPLY A RECOMMENDATION OR ENDORSEMENT BY PACIFIC BIOSCIENCES.
