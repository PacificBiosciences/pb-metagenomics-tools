# Taxonomic-Profiling-Nucleotide

Use sourmash to decompose reads into k-mers (`sketch`), find the smallest set of reference genome matches (`gather`), and build a taxonomic profile via Lowest Common Ancestor (LCA) summarization. Sourmash provides GTDB and NCBI databases, which can be downloaded from ["Prepared Databases"](https://sourmash.readthedocs.io/en/latest/databases.html) section of the documentation. At least one database is required for this workflow.

This directory contains all the materials needed to run this snakemake workflow.

[Documentation for the Taxonomic-Profiling-sourmash pipeline is available here](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/Tutorial-Taxonomic-Profiling-sourmash.md).


## DISCLAIMER
THIS WEBSITE AND CONTENT AND ALL SITE-RELATED SERVICES, INCLUDING ANY DATA, ARE PROVIDED "AS IS," WITH ALL FAULTS, WITH NO REPRESENTATIONS OR WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, ANY WARRANTIES OF MERCHANTABILITY, SATISFACTORY QUALITY, NON-INFRINGEMENT OR FITNESS FOR A PARTICULAR PURPOSE. YOU ASSUME TOTAL RESPONSIBILITY AND RISK FOR YOUR USE OF THIS SITE, ALL SITE-RELATED SERVICES, AND ANY THIRD PARTY WEBSITES OR APPLICATIONS. NO ORAL OR WRITTEN INFORMATION OR ADVICE SHALL CREATE A WARRANTY OF ANY KIND. ANY REFERENCES TO SPECIFIC PRODUCTS OR SERVICES ON THE WEBSITES DO NOT CONSTITUTE OR IMPLY A RECOMMENDATION OR ENDORSEMENT BY PACIFIC BIOSCIENCES.
