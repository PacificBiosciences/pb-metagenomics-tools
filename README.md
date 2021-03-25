# PB-metagenomics-tools

Welcome! Here you can find a variety of tools and pipelines tailored to using PacBio HiFi Reads for metagenomics. In addition to the resources currently available, we will continue to add new tools as they are developed.

## Available pipelines

+ [**HiFi-MAG-Pipeline**](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/HiFi-MAG-Pipeline): (*previously called Genome-Binning-Pipeline*) Identify high-quality MAGs from HiFi metagenomic assemblies. Streamlined workflow includes steps with minimap2, MetaBAT2, CheckM, and GTDB-Tk. Outputs high-quality MAG sequences and associated metadata. 

+ [**Taxonomic-Functional-Profiling-Protein**](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/Taxonomic-Functional-Profiling-Protein): Align HiFi reads to a **protein** database using DIAMOND and prepare inputs for MEGAN6, for the purpose of taxonomic and functional profiling. Provides access to taxonomic analyses (NCBI and GTDB), and allows functional analyses based on annotations from several databases (EC, SEED, InterPro2GO, eggNOG). **Ideal for profiling metagenomic samples, but can also be used to identify and characterize microbial reads present in non-metagenomic datasets (such as plant/animal genome sequencing projects).**

+ [**Taxonomic-Profiling-Nucleotide**](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/Taxonomic-Profiling-Nucleotide): Align HiFi reads to a **nucleotide** database using minimap2 and prepare inputs for MEGAN6, for the purpose of taxonomic profiling. This only provides access to NCBI taxonomic analysis, but may give higher resolution than with protein alignments. The GTDB taxonomy and functional annotations are not accessible downstream. **Ideal for profiling metagenomic samples, but can also be used to identify and characterize microbial reads present in non-metagenomic datasets (such as plant/animal genome sequencing projects).**

+ [**MEGAN-RMA-Summary**](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/MEGAN-RMA-summary): Obtain functional and taxonomic class count summaries for a set of RMA files created from the above MEGAN6 pipelines. Outputs absolute read counts and normalized read counts across samples for classes of each database, and summarizes the proportion of HiFi reads receiving functional and taxonomic annotations. **New feature: Outputs NCBI taxonomic counts in kraken (kreport) and metaphlan (mpa) formats.** Workflows are available for both protein-based RMA files and for nucleotide-based RMA files. 

Each of these pipelines can be found in their respective folders. They are made available as [Snakemake](https://snakemake.readthedocs.io/en/stable/index.html) workflows. Snakemake is a python-based workflow manager. Snakemake workflows are highly portable because dependencies and environments are automatically setup using [Anaconda](https://docs.anaconda.com/anaconda/)/[Conda](https://docs.conda.io/projects/conda/en/latest/index.html). Snakemake also allows reproducibility, checkpointing, and the ability to scale workflows using HPC and cloud environments. Snakemake v5+ is required, and the workflows have been tested using v5.19+.

## Other tools

Scripts for metagenomics tasks are available in the [pb-metagenomics-scripts](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/pb-metagenomics-scripts) folder. Currently, there are several scripts to convert the outputs from metagenomics taxonomic profiling programs into standard formats, including kraken report (kreport) and metaphlan report (mpa) formats.

## Documentation 

All documentation for snakemake pipelines can be found in the `docs/` folder above. Links are also provided below.

Available pipeline documentation: 
- [**Tutorial: HiFi-MAG-Pipeline**](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/Tutorial-HiFi-MAG-Pipeline.md)
- [**Tutorial: Taxonomic-Functional-Profiling-Protein**](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/Tutorial-Taxonomic-Functional-Profiling-Protein.md)
- [**Tutorial: Taxonomic-Profiling-Nucleotide**](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/Tutorial-Taxonomic-Profiling-Nucleotide.md)
- [**Tutorial: MEGAN-RMA-Summary**](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/Tutorial-MEGAN-RMA-summary.md)

The documentation for [pb-metagenomics-scripts](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/pb-metagenomics-scripts) is available within that folder.



## DISCLAIMER
THIS WEBSITE AND CONTENT AND ALL SITE-RELATED SERVICES, INCLUDING ANY DATA, ARE PROVIDED "AS IS," WITH ALL FAULTS, WITH NO REPRESENTATIONS OR WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, ANY WARRANTIES OF MERCHANTABILITY, SATISFACTORY QUALITY, NON-INFRINGEMENT OR FITNESS FOR A PARTICULAR PURPOSE. YOU ASSUME TOTAL RESPONSIBILITY AND RISK FOR YOUR USE OF THIS SITE, ALL SITE-RELATED SERVICES, AND ANY THIRD PARTY WEBSITES OR APPLICATIONS. NO ORAL OR WRITTEN INFORMATION OR ADVICE SHALL CREATE A WARRANTY OF ANY KIND. ANY REFERENCES TO SPECIFIC PRODUCTS OR SERVICES ON THE WEBSITES DO NOT CONSTITUTE OR IMPLY A RECOMMENDATION OR ENDORSEMENT BY PACIFIC BIOSCIENCES.
