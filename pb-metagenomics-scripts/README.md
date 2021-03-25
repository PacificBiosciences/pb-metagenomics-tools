# pb-metagenomics-scripts

Welcome! This repository contains a variety of scripts that are useful for metagenomics work. The scripts are listed by topic, with detailed usage instructions provided below.

## Contents <a name="TOP"></a>

**Converting output file formats for taxonomic profilers:**

+ [Convert_kreport_to_mpa.py](#ckm): Convert any kraken report (kreport) file into metaphlan (mpa) format.
+ [Convert_MEGAN-RMA-NCBI-c2c_to_kreport-mpa.py](#mckm): Convert taxonomic counts from MEGAN6 into kraken report (kreport) and metaphlan (mpa) formats.
+ [Convert_metamaps-KRONA_to_kreport-mpa.py](#mkkm): Convert the output of Metamaps into kraken report (kreport) and metaphlan (mpa) formats.
+ [Convert_metaphlan3_mpa_to_kreport](#mmkr): Convert the output of MetaPhlAn3 into kraken report (kreport) format.

---------------

## Convert_kreport_to_mpa.py <a name="ckm"></a>

This is a general use script that will convert any kraken report (kreport) file into metaphlan (mpa) format. Programs that output kreport formats include [Kraken](https://github.com/DerrickWood/kraken2), [Bracken](https://github.com/jenniferlu717/Bracken/), [Centrifuge](https://ccb.jhu.edu/software/centrifuge/manual.shtml), and [mmseqs2](https://github.com/soedinglab/MMseqs2). This script was primarily intended for use with `mmseqs2`. 

This script requires `python 3.7` and the python packages `ete3` and `pandas`. 

Output file is written to working directory (`label.mpa.txt`).

#### Basic Usage:

```
python Convert_kreport_to_mpa.py -i <kreport file> -f <choice> -l <label string>
```

#### Argument Explanations:

##### `-i <path-to-file>` or `--input <path-to-file>`

> **Required**: The kreport file name or the path to a kreport file.

##### `-f <choice>` or `--format <choice>`

> **Required**: The format of the kreport ranks. Choices = *kraken, mmseqs*.
> kraken format displays ranks as single characters: K, P, C, O, F, G, S, S1, etc.
> mmseqs format displays ranks as words: kingdom, phylum, class, etc.

##### `-l <string>` or `--label <string>`

> **Required**: A label used to name the output file: label.mpa.txt.

##### `--update`

> **Optional**: If this flag is provided, ete3 will update the local NCBI taxonomy database before using it to perform the format conversion.


#### Example Usage:

```
python Convert_kreport_to_mpa.py -i Sample1_mmseqs2_report.txt -f mmseqs -l Sample1
```

[Back to top](#TOP)

---------------

## Convert_MEGAN-RMA-NCBI-c2c_to_kreport-mpa.py <a name="mckm"></a>

This script can be used to convert an NCBI class2count (c2c) file obtained through MEGAN6  into kraken report (kreport) and metaphlan (mpa) formats. To obtain this c2c file, you can run MEGAN's `rma2info` program on a MEGAN read-count RMA file:

```
rma2info -i input.RMA -o NCBI.c2c.txt -c2c Taxonomy -n -r
```

Note that complete pipelines for aligning HiFi reads, annotation with MEGAN, and producing outputs files (including kreport and mpa files) are already available: [Taxonomic-Functional-Profiling-Protein](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/Taxonomic-Functional-Profiling-Protein), [Taxonomic-Profiling-Nucleotide](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/Taxonomic-Profiling-Nucleotide), and [MEGAN-RMA-summary](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/MEGAN-RMA-summary).

This script requires `python 3.7` and the python packages `ete3` and `pandas`. 

Output files are written to working directory (`label.megan-c2c.mpa.txt`, `label.megan-c2c.kreport.txt`, `label.intermediate.names.txt`, and `label.intermediate.taxid.txt`).

#### Basic Usage:

```
python Convert_MEGAN-RMA-NCBI-c2c_to_kreport-mpa.py -i <c2c file> -c <choice> -l <label string> -r <int>
```

#### Argument Explanations:

##### `-i <path-to-file>` or `--input <path-to-file>`

> **Required**: The MEGAN c2c file name or the path to a MEGAN c2c file.

##### `-c <choice>` or `--columns <choice>`

> **Required**: Whether the c2c file contains two columns (taxon, count) or three columns (rank, taxon, count).

##### `-l <string>` or `--label <string>`

> **Required**: A label used as a prefix to name the output files.

##### `-r <int>` or `--readcount <int>`

> **Required**: The total number of reads that were used for alignment (e.g. the number of starting reads).

##### `--update`

> **Optional**: If this flag is provided, ete3 will update the local NCBI taxonomy database before using it to perform the format conversion.

#### Example Usage:

```
python Convert_MEGAN-RMA-NCBI-c2c_to_kreport-mpa.py -i Sample1.NCBI.c2c.txt -c three -l Sample1 -r 1802756
```


[Back to top](#TOP)

---------------

## Convert_metamaps-KRONA_to_kreport-mpa.py <a name="mkkm"></a>

Metamaps is a metagenomics taxonomic profiler that was designed to be used with long reads. Currently, metamaps does not provide the option for kraken report (kreport) or metaphlan (mpa) formats. This script can be used to convert the KRONA output file from metamaps into kraken report (kreport) and metaphlan (mpa) formats. The krona file should have an extension that looks like `EM.reads2Taxon.krona`, and it is produced after running the `metamaps classify` module.

This script requires `python 3.7` and the python packages `ete3` and `pandas`. 

Output files are written to working directory (`label.metamaps-krona.mpa.txt`, `label.metamaps-krona.kreport.txt`, `label.intermediate.names.txt`, and `label.intermediate.taxid.txt`).

#### Basic Usage:

```
python Convert_metamaps-KRONA_to_kreport-mpa.py -i <krona file> -l <label string> -r <int>
```

#### Argument Explanations:

##### `-i <path-to-file>` or `--input <path-to-file>`

> **Required**: The `EM.reads2Taxon.krona` file name or the path to a `EM.reads2Taxon.krona` file.

##### `-l <string>` or `--label <string>`

> **Required**: A label used as a prefix to name the output files.

##### `-r <int>` or `--readcount <int>`

> **Required**: The total number of reads that were used for alignment (e.g. the number of starting reads).

##### `--update`

> **Optional**: If this flag is provided, ete3 will update the local NCBI taxonomy database before using it to perform the format conversion.

#### Example Usage:

```
python Convert_metamaps-KRONA_to_kreport-mpa.py -i Sample1.EM.reads2Taxon.krona -l Sample1 -r 1802756
```


[Back to top](#TOP)


---------------

## Convert_metaphlan3_mpa_to_kreport.py <a name="mmkr"></a>

MetaPhlAn3 is a short-read metagenomics taxonomic profiler. It outputs the metaphlan (mpa) format, but not a kraken report. This script can be used to convert the mpa output file from MetaPhlAn3 into a kraken report (kreport) format. Because the mpa format from MetaPhlAn3 provides proportions rather than absolute read counts, the proportions are converted into estimated read counts based on the number of reads that were successfully aligned (from the bowtie2 step). The number of starting reads must also be provided, so the percentages of reads calculated in the kraken report are accurate.

Note that differences in mpa and NCBI taxonomy may provide some inaccurate **level** counts for higher taxa in the kraken report (occasionally a negative number), but the **cumulative** counts will always be accurate.

This script requires `python 3.7` and the python packages `ete3` and `pandas`. 

Output files are written to working directory (`label.metamaps-krona.mpa.txt`, `label.metamaps-krona.kreport.txt`, `label.intermediate.names.txt`, and `label.intermediate.taxid.txt`).

#### Basic Usage:

```
python Convert_metaphlan3_mpa_to_kreport.py -i <mpa file> -l <label string> -r <int> -m <int>
```

#### Argument Explanations:

##### `-i <path-to-file>` or `--input <path-to-file>`

> **Required**: The map file name or the path to an mpa file.

##### `-l <string>` or `--label <string>`

> **Required**: A label used as a prefix to name the output files.

##### `-r <int>` or `--readcount <int>`

> **Required**: The total number of reads that were used for alignment (e.g. the number of starting reads).

##### `-m <int>` or `--mappedreads <int>`

> **Required**: The total number of unique reads that were successfully aligned (e.g. the number of unique reads with alignments from bowtie2). This number will always be less than the `readcount` value provided.

##### `--update`

> **Optional**: If this flag is provided, ete3 will update the local NCBI taxonomy database before using it to perform the format conversion.

#### Example Usage:

```
python Convert_metaphlan3_mpa_to_kreport.py -i Sample1-profiled_metagenome.mpa.txt -l Sample1 -r 1802756 -m 1407360
```


[Back to top](#TOP)

---------------

### DISCLAIMER
THIS WEBSITE AND CONTENT AND ALL SITE-RELATED SERVICES, INCLUDING ANY DATA, ARE PROVIDED "AS IS," WITH ALL FAULTS, WITH NO REPRESENTATIONS OR WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, ANY WARRANTIES OF MERCHANTABILITY, SATISFACTORY QUALITY, NON-INFRINGEMENT OR FITNESS FOR A PARTICULAR PURPOSE. YOU ASSUME TOTAL RESPONSIBILITY AND RISK FOR YOUR USE OF THIS SITE, ALL SITE-RELATED SERVICES, AND ANY THIRD PARTY WEBSITES OR APPLICATIONS. NO ORAL OR WRITTEN INFORMATION OR ADVICE SHALL CREATE A WARRANTY OF ANY KIND. ANY REFERENCES TO SPECIFIC PRODUCTS OR SERVICES ON THE WEBSITES DO NOT CONSTITUTE OR IMPLY A RECOMMENDATION OR ENDORSEMENT BY PACIFIC BIOSCIENCES.
