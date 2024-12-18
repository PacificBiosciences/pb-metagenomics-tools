<h1 align="center"><img width="300px" src="docs/logo_pb-metagenomics-tools.svg"/></h1>

<h1 align="center">pb-metagenomics-tools</h1>

<h3 align="center">Tools for performing metagenomic analyses using HiFi sequencing data.</h3>

Welcome! Here you can find a variety of tools and pipelines for HiFi metagenomics. In addition to the resources currently available, we will continue to add new tools as they are developed.

The current version is v3.2.0. Please see the [**release notes**](https://github.com/PacificBiosciences/pb-metagenomics-tools/releases) for changes.

## HiFi Metagenomic Datasets & Publications

Several publicly available HiFi shotgun metagenomics datasets are listed on the   [**PacBio-Data**](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/PacBio-Data.md) page. These include multiple mock communities, reference standards, and empirical samples (human, chicken, and sheep gut microbiome, and environmental samples). Associated publications are also listed here.

A running list of publications using HiFi sequencing for metagenomics can be found [**here**](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/HiFi-Metagenomics-Publications.md). 

## Available pipelines

+ [**HiFi-MAG-Pipeline**](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/HiFi-MAG-Pipeline): Identify high-quality MAGs from HiFi metagenomic assemblies. Streamlined workflow includes a custom "completeness-aware" strategy to identify and protect long and complete contigs. Binning is performed with MetaBAT2 and SemiBin2, bin merging occurs with DAS_Tool, QC with CheckM2, and taxonomic assignments with GTDB-Tk. Outputs include high-quality MAG sequences, summary figures, and associated metadata. 

+ [**pb-MAG-mirror**](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/pb-MAG-mirror): Compare two sets of MAGs to quantify the numbers of highly similar, mixed, and unique MAGs, and consolidate the sets into a single non-redundant set. This workflow can be used to compare MAGs (intended use-case) or bins, but it requires the contigs to originate from the same assembly method.

+ [**Taxonomic-Profiling-Sourmash**](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/Taxonomic-Profiling-Sourmash): Obtain taxonomic proflies using `sourmash gather` --> `taxonomy` approach. Sourmash provides GTDB and NCBI databases, or you can build your own database.

+ [**Taxonomic-Profiling-Diamond-Megan**](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/Taxonomic-Profiling-Diamond-Megan): Perform translation alignment of HiFi reads to a **protein** database using DIAMOND and summarize with MEGAN-LR, for the purpose of taxonomic and functional profiling. Provides access to taxonomic annotations from NCBI and GTDB, and outputs NCBI taxonomic counts in kraken (kreport) and metaphlan (mpa) formats. Also provides functional annotations based on multiple databases (EC, SEED, InterPro2GO, eggNOG), with new KEGG option available.

+ [**Taxonomic-Profiling-Minimap-Megan**](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/Taxonomic-Profiling-Minimap-Megan): Align HiFi reads to a **nucleotide** database using minimap2 and summarize with MEGAN-LR, for the purpose of taxonomic profiling. Provides access to NCBI and GTDB taxonomic annotations. Outputs NCBI taxonomic counts in kraken (kreport) and metaphlan (mpa) formats.

Each of these pipelines can be found in their respective folders. They are made available as [Snakemake](https://snakemake.readthedocs.io/en/stable/index.html) workflows. Snakemake is a python-based workflow manager. Snakemake workflows are highly portable because dependencies and environments are automatically setup using [Anaconda](https://docs.anaconda.com/anaconda/)/[Conda](https://docs.conda.io/projects/conda/en/latest/index.html). Snakemake also allows reproducibility, checkpointing, and the ability to scale workflows using HPC and cloud environments. 

**Snakemake v8+ is now required**. Please note there are some major command-line changes for v8+ (outlined here). You can optionally install snakemake 8.25+ via the provided conda environment file via `conda env create -f environment.yml`, and then activate this environment via `conda activate pb-metagenomics-tools` to run the workflows.

## Documentation 

All documentation for snakemake pipelines can be found in the `docs/` folder above. Links are also provided below.

Available pipeline documentation: 
- [**Tutorial: HiFi-MAG-Pipeline**](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/Tutorial-HiFi-MAG-Pipeline.md)
- [**Tutorial: pb-MAG-mirror**](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/Tutorial-pb-MAG-mirror.md)
- [**Tutorial: Taxonomic-Profiling-Sourmash**](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/Tutorial-Taxonomic-Profiling-Sourmash.md)
- [**Tutorial: Taxonomic-Profiling-Diamond-Megan**](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/Tutorial-Taxonomic-Profiling-Diamond-Megan.md)
- [**Tutorial: Taxonomic-Profiling-Minimap-Megan**](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/Tutorial-Taxonomic-Profiling-Minimap-Megan.md)

## Citation

The taxonomic profiling and classification workflows (including [Taxonomic-Profiling-Sourmash](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/Taxonomic-Profiling-Sourmash), [Taxonomic-Profiling-Diamond-Megan](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/Taxonomic-Profiling-Diamond-Megan), and [Taxonomic-Profiling-Minimap-Megan](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/Taxonomic-Profiling-Minimap-Megan)) were created for the following publication:

> Portik DM, Brown CT, and NT Pierce-Ward. 2022. Evaluation of taxonomic classification and profiling methods for long-read shotgun metagenomic sequencing datasets. BMC Bioinformatics, 23: 541. https://doi.org/10.1186/s12859-022-05103-0

The [HiFi-MAG-Pipeline](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/HiFi-MAG-Pipeline)(v2+) and [pb-MAG-mirror](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/pb-MAG-mirror) were created for the following pre-print:

> Portik DM, Feng X, Benoit G, Nasko DJ, Auch B, Bryson SJ, Cano R, Carlin M, Damerum A, Farthing B, Grove JR, Islam M, Langford KW, Liachko I, Locken K, Mangelson H, Tang S, Zhang S, Quince C, and JE Wilkinson. 2024. Highly accurate metagenome-assembled genomes from human gut microbiota using long-read assembly, binning, and consolidation methods. bioRxiv, https://doi.org/10.1101/2024.05.10.593587


## Other tools

Scripts and tools for metagenomics tasks are available in the [**pb-metagenomics-scripts**](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/pb-metagenomics-scripts) folder. Currently, there are scripts or notebooks to perform the following tasks: 

+ Convert outputs from common metagenomics profiling/classification programs into standard formats, including kraken report (kreport) and metaphlan report (mpa) formats. 

+ Compare kraken report files across multiple samples, with several visualization options.

The documentation for is provided in the folder.



### DISCLAIMER
THIS WEBSITE AND CONTENT AND ALL SITE-RELATED SERVICES, INCLUDING ANY DATA, ARE PROVIDED "AS IS," WITH ALL FAULTS, WITH NO REPRESENTATIONS OR WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, ANY WARRANTIES OF MERCHANTABILITY, SATISFACTORY QUALITY, NON-INFRINGEMENT OR FITNESS FOR A PARTICULAR PURPOSE. YOU ASSUME TOTAL RESPONSIBILITY AND RISK FOR YOUR USE OF THIS SITE, ALL SITE-RELATED SERVICES, AND ANY THIRD PARTY WEBSITES OR APPLICATIONS. NO ORAL OR WRITTEN INFORMATION OR ADVICE SHALL CREATE A WARRANTY OF ANY KIND. ANY REFERENCES TO SPECIFIC PRODUCTS OR SERVICES ON THE WEBSITES DO NOT CONSTITUTE OR IMPLY A RECOMMENDATION OR ENDORSEMENT BY PACIFIC BIOSCIENCES.
