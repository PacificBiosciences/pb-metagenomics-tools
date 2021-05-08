# pb-metagenomics-scripts

Welcome! This repository contains a variety of scripts that are useful for metagenomics work. Detailed usage instructions can be found within the folders.

## Contents <a name="TOP"></a>

### [Compare-kreport-taxonomic-profiles](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/pb-metagenomics-scripts/Compare-kreport-taxonomic-profiles)

Contains a Jupyter notebook ([**Compare-kreport-taxonomic-profiles.html**](http://htmlpreview.github.io/?https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/pb-metagenomics-scripts/Compare-kreport-taxonomic-profiles/Compare-kreport-taxonomic-profiles.html)) demonstrating how to compare kraken reports across multiple samples for specified taxonomic ranks, including how to:

+ Generate and save a combined taxon count table for a particular taxonomic rank
+ Create and save stacked barplots showing relative or absolute abundances of taxa across samples
+ Perform analyses at different taxonomic ranks (strains, species, genera, families, etc.)

### [Convert-to-kreport-mpa](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/pb-metagenomics-scripts/Convert-to-kreport-mpa) 

Contains several scripts for converting the output file formats for taxonomic profilers to kraken and metaphlan report formats:

+ `Convert_kreport_to_mpa.py`: Convert any kraken report (kreport) file into metaphlan (mpa) format.
+ `Convert_MEGAN-RMA-NCBI-c2c_to_kreport-mpa.py`: Convert taxonomic counts from MEGAN6 into kraken report (kreport) and metaphlan (mpa) formats.
+ `Convert_metamaps-WIMP_to_kreport-mpa`: Convert the output of Metamaps into kraken report (kreport) and metaphlan (mpa) formats.
+ `Convert_metaphlan3_mpa_to_kreport`: Convert the output of MetaPhlAn3 into kraken report (kreport) format.

---------------


[Back to top](#TOP)

---------------

### DISCLAIMER
THIS WEBSITE AND CONTENT AND ALL SITE-RELATED SERVICES, INCLUDING ANY DATA, ARE PROVIDED "AS IS," WITH ALL FAULTS, WITH NO REPRESENTATIONS OR WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, ANY WARRANTIES OF MERCHANTABILITY, SATISFACTORY QUALITY, NON-INFRINGEMENT OR FITNESS FOR A PARTICULAR PURPOSE. YOU ASSUME TOTAL RESPONSIBILITY AND RISK FOR YOUR USE OF THIS SITE, ALL SITE-RELATED SERVICES, AND ANY THIRD PARTY WEBSITES OR APPLICATIONS. NO ORAL OR WRITTEN INFORMATION OR ADVICE SHALL CREATE A WARRANTY OF ANY KIND. ANY REFERENCES TO SPECIFIC PRODUCTS OR SERVICES ON THE WEBSITES DO NOT CONSTITUTE OR IMPLY A RECOMMENDATION OR ENDORSEMENT BY PACIFIC BIOSCIENCES.
