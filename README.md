# PB-metagenomics-tools

Welcome! Here you can find a variety of tools and pipelines tailored to using PacBio HiFi reads for metagenomics.

## Available tools and pipelines

+ **`Genome-Binning-Pipeline`**: Perform genome binning and MAG assessment on HiFi assemblies with a streamlined workflow. Includes steps with minimap2, MetaBAT2, CheckM, and GTDB-Tk.

+ **`Taxonomic-Functional-Profiling-Protein`**: Align HiFi reads to a **protein** database using DIAMOND and prepare inputs for MEGAN6, for the purpose of taxonomic and functional profiling. 

+ **`Taxonomic-Functional-Profiling-Nucelotide`**: Align HiFi reads to a **nucleotide** database using minimap2 and prepare inputs for MEGAN6, for the purpose of taxonomic and functional profiling.


These pipelines can be found in their respective folders. They are available as Snakemake workflows.

## Documentation 

All documentation can be found in the `docs/` folder located [here](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/docs). 

Currently available documentation: 
- [Genome-Binning-Pipeline tutorial](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/Tutorial-Genome-Binning-Pipeline.md)

Tutorials for the remaining pipelines are currently being written. We intend to have all pipelines fully documented by the end of September 2020. Advanced Snakemake users can look in the snake files for a complete picture of the workflow, including the commands used to call all respective programs. For others, we encourage you to please check back soon!


## DISCLAIMER
THIS WEBSITE AND CONTENT AND ALL SITE-RELATED SERVICES, INCLUDING ANY DATA, ARE PROVIDED "AS IS," WITH ALL FAULTS, WITH NO REPRESENTATIONS OR WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, ANY WARRANTIES OF MERCHANTABILITY, SATISFACTORY QUALITY, NON-INFRINGEMENT OR FITNESS FOR A PARTICULAR PURPOSE. YOU ASSUME TOTAL RESPONSIBILITY AND RISK FOR YOUR USE OF THIS SITE, ALL SITE-RELATED SERVICES, AND ANY THIRD PARTY WEBSITES OR APPLICATIONS. NO ORAL OR WRITTEN INFORMATION OR ADVICE SHALL CREATE A WARRANTY OF ANY KIND. ANY REFERENCES TO SPECIFIC PRODUCTS OR SERVICES ON THE WEBSITES DO NOT CONSTITUTE OR IMPLY A RECOMMENDATION OR ENDORSEMENT BY PACIFIC BIOSCIENCES.
