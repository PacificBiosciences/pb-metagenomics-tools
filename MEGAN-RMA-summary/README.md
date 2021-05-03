# MEGAN-RMA-Summary

Summarize information contained within RMA format files intended for MEGAN-LR. This workflow is intended to be used after running the [Taxonomic-Functional-Profiling-Protein](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/Taxonomic-Functional-Profiling-Protein) pipeline or the [Taxonomic-Profiling-Nucleotide](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/Taxonomic-Profiling-Nucleotide) pipeline. 

For protein RMA files, this workflow will output absolute and normalized read counts of the EC, EGGNOG, INTERPRO2GO, and SEED functional classes, along with read counts of the NCBI (full database and bacteria-only) and GTDB taxonomy classes. A summary file and several plots will be created showing the number of reads assigned to functional and taxonomic databases, the total classes represented per database, and average annotations per read. 

For nucleotide RMA files, this workflow will output absolute and normalized read counts of the NCBI taxonomy classes. A summary file and plots will be created showing the number of reads assigned to the NCBI taxonomic database and the total NCBI classes represented.

This directory contains all the materials needed to run this snakemake workflow.

[Documentation for the MEGAN-RMA-Summary pipeline is available here](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/Tutorial-MEGAN-RMA-summary.md).


## DISCLAIMER
THIS WEBSITE AND CONTENT AND ALL SITE-RELATED SERVICES, INCLUDING ANY DATA, ARE PROVIDED "AS IS," WITH ALL FAULTS, WITH NO REPRESENTATIONS OR WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, ANY WARRANTIES OF MERCHANTABILITY, SATISFACTORY QUALITY, NON-INFRINGEMENT OR FITNESS FOR A PARTICULAR PURPOSE. YOU ASSUME TOTAL RESPONSIBILITY AND RISK FOR YOUR USE OF THIS SITE, ALL SITE-RELATED SERVICES, AND ANY THIRD PARTY WEBSITES OR APPLICATIONS. NO ORAL OR WRITTEN INFORMATION OR ADVICE SHALL CREATE A WARRANTY OF ANY KIND. ANY REFERENCES TO SPECIFIC PRODUCTS OR SERVICES ON THE WEBSITES DO NOT CONSTITUTE OR IMPLY A RECOMMENDATION OR ENDORSEMENT BY PACIFIC BIOSCIENCES.
