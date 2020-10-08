# Tutorial for Taxonomic-Profiling-Nucleotide <a name="TOP"></a>

## **Table of Contents**

+ [Taxonomic-Profiling-Nucleotide Overview](#PO)
+ [Quick Start](#QS)
+ [1. Snakemake Contents](#SMC)
+ [2. Requirements for Running](#RFR)
+ [3. Configuring the Analysis](#CTA)
+ [4. Executing Snakemake](#EXS)
+ [5. Outputs](#OTPS)
+ [6. Usage Details for Main Programs](#UDMP)


---------------

# **Taxonomic-Profiling-Nucleotide Overview** <a name="PO"></a>

The purpose of this snakemake workflow is to perform alignment of HiFi reads to a nucleotide database, and convert the resulting alignments to RMA input files for MEGAN6. This allows interactive taxonomic analyses to be performed across samples. The general steps of the Taxonomic-Profiling-Nucleotide pipeline are shown below:

![GBSteps](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/Taxonomic-Profiling-Nucleotide-Steps.png)

To make an RMA file, it is required to have the reads and alignments in the exact same order. To prevent errors, the first step is to sort the HiFi reads fasta file by read name. The sorted reads fasta file is then split into two chunks for parallel processing. This allows a speedup when jobs are run simultaneously, and also reduces the resources required to run the alignments sequentially. Minimap2 is used to align the HiFi reads files to a nucleotide database. The two resulting SAM files (per sample) are then sorted by read names, and subsequently merged. The resulting sorted SAM file is converted into long-read RMA format using the sam2rma tool distributed with MEGAN6. Each input file of HiFi reads will produce a corresponding output RMA file, ready to use with MEGAN6.  

**Please note that nucleotide alignments to the NCBI nt database will only provide access to NCBI taxonomy analyses in MEGAN6. Using protein alignments to the NCBI nr database will provide access to the NCBI taxonomy, functional annotations (SEED, InterPro2GO, eggNOG) and the option to use GTDB taxonomy instead. The protein version of this pipeline is described [here](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/Tutorial-Taxonomic-Functional-Profiling-Protein.md).**

[Back to top](#TOP)

---------------

# **Quick Start** <a name="QS"></a>

This workflow requires [Anaconda](https://docs.anaconda.com/anaconda/)/[Conda](https://docs.conda.io/projects/conda/en/latest/index.html) and [Snakemake](https://snakemake.readthedocs.io/en/stable/) to be installed, and will require ~60GB memory and 50-400GB disk space per sample (see [Requirements section](#RFR)). All dependencies in the workflow are installed using conda and the environments are activated by snakemake for relevant steps. Snakemake v5+ is required, and the workflows have been tested using v5.19.3.

- Clone the Taxonomic-Profiling-Nucleotide directory.
- Download MEGAN6 community edition from the [MEGAN download page](https://software-ab.informatik.uni-tuebingen.de/download/megan6/welcome.html) to obtain `sam2rma`. 
- Download and unpack the newest MEGAN mapping file for genomic DNA accessions from the [MEGAN download page](https://software-ab.informatik.uni-tuebingen.de/download/megan6/welcome.html).
- Download the NCBI-nt database from: ftp://ftp.ncbi.nlm.nih.gov/blast/db/FASTA/nt.gz*
- Index the NCBI-nt database with minimap2 using `minimap2 -k 19 -w 10 -d mm2_nt_db.mmi nt.gz`. This will result in a `mm_nt_db.mmi` file that is ~850GB.
- Specify the full path to `sam2rma`, full path to the MEGAN database file , and full path to the indexed NCBI-nt database in `config.yaml`.
- Include all input HiFi fasta files (`SAMPLE.fasta`) in the `inputs/` folder. These can be files or symlinks. 
- Edit sample names in `Sample-Config.yaml` configuration file in `configs/` for your project. 
- Execute snakemake using the general commands below: 
```
snakemake --snakefile Snakefile-taxnuc --configfile configs/Sample-Config.yaml --use-conda [additional arguments for local/HPC execution]
```
The choice of additional arguments to include depends on where and how you choose to run snakemake. Please refer to the [Executing Snakemake](#EXS) section for more details.

[Back to top](#TOP)

---------------

# **1. Snakemake Contents** <a name="SMC"></a>

To run the workflow, you will need to obtain all contents within the [Taxonomic-Profiling-Nucleotide folder](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/Taxonomic-Profiling-Nucleotide). The default contents should look like this:

```
Taxonomic-Profiling-Nucleotide
│
├── configs/
│	└── Sample-Config.yaml
│
├── envs/
│	└── general.yml
│
├── inputs/
│	└── README.md (this is just a placeholder file, and not required)
│
├── scripts/
│	├── sam-merger-minimap.py
│	└── Sort-Fasta-Records-BioPython.py
│
├── Snakefile-taxnuc
│
└── config.yaml
```
The `Snakefile-taxnuc` file is the Snakefile for this snakemake workflow. It contains all of the rules of the workflow. 

The `config.yaml` file is the main configuration file used in the snakemake workflow. It contains the main settings that will be used for various programs. 

The `configs/` directory contains an example configuration file for specifying which samples are to be run. It must be referenced in the command line call for snakemake for any samples to be run.

The `inputs/` directory should contain all of the required input files for each sample. In this workflow there must be a `SAMPLE.fasta` file of HiFi reads per sample. These can be the actual files, or symbolic links to the files (for example using `ln -s source_file symbolic_name`). 

The `scripts/` directory contains two Python scripts required for the workflow. `Sort-Fasta-Records-BioPython.py` is used to sort the HiFi reads fasta by read names, and `sam-merger-minimap.py` is used to merge SAM files.

Finally, the `envs/` directory contains the `general.yml` file which is needed to install all dependencies through conda. This environment is activated for each step of the workflow. The dependencies are installed from bioconda and conda-forge and include `exonerate 2.4.0`, `minimap2 2.17`, and several packages for Python3.

[Back to top](#TOP)

---------------

# **2. Requirements for Running** <a name="RFR"></a>


## Memory and disk space requirements

Running this pipeline using the default settings should require <60GB of memory. Approximately 850GB disk space is required for the minimap2-indexed NCBI-nt database. Additionally, depending on the size of the HiFi reads fasta file, 50-400GB disk space may be required per sample: 
- Very large HiFi reads fasta files (>2 million reads @ 10kb) can produce SAM outputs 200-350GB in size, which can result in RMA files 15-30GB in size (**200-400GB total**).
- Smaller HiFi reads fasta files (<1 million reads @ 8kb) can produce SAM outputs 50-120GB in size, which can result in RMA files 3-10GB in size (**50-130GB total**).

After completion, the very large SAM files and the sorted HiFi reads fasta files can be deleted. These files are not removed automatically in case different formats of RMA files need to be produced by the user, as sam2rma requires both the sorted reads and the SAM files. If disk space is an issue, you may choose to run one sample at a time.

## Dependencies

In order to run a snakemake workflow, you will need to have an anaconda or conda installation. Conda is essential because it will be used to install the dependencies within the workflow and setup the correct environments. 

Snakemake will also need to be installed. Instructions for installing snakemake using conda can be found [here](https://snakemake.readthedocs.io/en/stable/getting_started/installation.html). Snakemake v5+ is required, and the workflows have been tested using v5.19.3.

If you intend to generate a graphic for the snakemake workflow graph, you will also need graphviz installed.

## Download MEGAN6 and MEGAN database file

MEGAN6 community edition should be downloaded from the [MEGAN download page](https://software-ab.informatik.uni-tuebingen.de/download/megan6/welcome.html). The `sam2rma` binary is required for this pipeline. The `sam2rma` binary should be present in the `tools` bin distributed with MEGAN. **The full path to `sam2rma` must be specified in `config.yaml`.**

The newest MEGAN mapping file for genomic DNA accessions should also be downloaded from the [MEGAN download page](https://software-ab.informatik.uni-tuebingen.de/download/megan6/welcome.html). It must be unpacked to use it. The current unpacked file is ~4.5GB. **The full path to the unpacked database file (ending with `.db`) must be specified in `config.yaml`.**

## Download and index the NCBI-nt database

The NCBI-nt database is available at: ftp://ftp.ncbi.nlm.nih.gov/blast/db/FASTA/nt.gz*

The gzipped database (`nt.gz`) is ~82GB in size.

The database must be indexed with minimap2 prior to running the pipeline. This can be accomplished using the following command:
`minimap2 -k 19 -w 10 -d mm2_nt_db.mmi nt.gz`. 

Note that only 3 threads can be used for this step and that it will take a couple hours. Please also note that the `-k` and `-w` settings used here will override settings used during alignment, if they are not the same. The alignments use `-k 19 -w 10` and these values must be used here for correct indexing. 

This command will result in a `mm2_nt_db.mmi` file that is ~860GB. **The full path to the `mm2_nt_db.mmi` file must be specified in `config.yaml`.**

You can always use a customized nt database, for example a subset of the NCBI nt database. 


[Back to top](#TOP)

---------------

# **3. Configuring the Analysis** <a name="CTA"></a>

To configure the analysis, the main configuration file (`config.yaml`) and sample configuration file (`configs/Sample-Config.yaml`) should be edited. 

#### Main configuration file (`config.yaml`)
The main configuration file contains several parameters, each of which is described in the configuration file. Depending on your system resources, you may choose to change the number of threads used in the minimap2 and sam2rma settings.

**You must also specify the full paths to `sam2rma`, the MEGAN mapping database file, and the indexed NCBI-nt database**. 

#### Sample configuration file (`configs/Sample-Config.yaml`)
The example sample configuration file is called `Sample-Config.yaml` and is located in the `configs/` directory. Here you should specify the sample names that you wish to include in the analysis. 

For the Taxonomic-Profiling-Nucleotide pipeline, all samples specified in the sample configuration file must have a fasta file of HiFi reads (`SAMPLE.fasta`) in the `inputs/` folder. The pipeline can be run for any number of samples (though be aware of disk space requirements). You can also configure the file to only run for a subset of the samples present in the `inputs/` folder. Please note that if the input files do not follow the naming convention (`SAMPLE.fasta`), they will not be recognized by the workflow. You can use the actual files or symlinks to those files, both are compatible with snakemake.

[Back to top](#TOP)

---------------

# **4. Executing Snakemake** <a name="EXS"></a>

Before attempting to run this snakemake analysis, please ensure that the pre-analysis requirements have been satisfied, the analysis has been configured properly (using the general and sample configuration files), and the input files are available in the `inputs/` folder. 

There are several ways to execute the workflow. The easiest way is to run snakemake on HPC using an interactive session. The most efficient way is to use cluster or cloud configuration so that snakemake can schedule and run jobs on HPC or cloud environments. 

## Local execution

Snakemake can be run "locally" (e.g., without cluster configuration). Snakemake will automatically determine how many jobs can be run simultaneously based on the resources specified. This type of snakemake analysis can be run on a local system, but ideally it should be executed using an interactive HPC session (for example, `qrsh` with SGE or the SLURM equivalent).

The workflow must be executed from within the directory containing all the snakemake contents for the Taxonomic-Profiling-Nucleotide pipeline. 

### Test workflow
It is a good idea to test the workflow for errors before running it. This can be done with the following command:
```
snakemake -np --snakefile Snakefile-taxnuc --configfile configs/Sample-Config.yaml
```

Let's unpack this command:
- `snakemake` calls snakemake.
- `-np` performs a 'dry-run' where the rule compatibilities are tested but they are not executed.
- `--snakefile Snakefile-taxnuc` tells snakemake to run this particular snakefile.
- `--configfile configs/Sample-Config.yaml` tells snakemake to include the samples listed in the sample configuration file.

The dry run command should result in a sequence of jobs being displayed on screen. 

### Create workflow figure
If there are no errors, you may wish to generate a figure of the directed acyclic graph (the workflow steps). You can do this using the following command:
```
snakemake --dag --snakefile Snakefile-taxnuc --configfile configs/Sample-Config.yaml | dot -Tsvg > taxfunc_analysis.svg
```
Here the `--dag` flag creates an output that is piped to `dot`, and an svg file called `genome-binning_analysis.svg` is created. This will show the workflow visually.

### Execute workflow
Finally, you can execute the workflow using:
```
snakemake --snakefile Snakefile-taxnuc --configfile configs/Sample-Config.yaml -j 48 --use-conda
```

There are a couple important arguments that were added here:

- `-j 48` specifies that there are 48 threads available to use. You should change this to match the resources available. If more threads are specified in the configuration file than are available here, snakemake automatically scales them down to this number.
-  `--use-conda` allows conda to install the programs and environments required for each step. This is essential.

Upon execution, the first step will be conda downloading packages and creating the correct environment. After, the jobs should begin running. You will see the progress on screen.


## Cluster Configuration

Executing snakemake on HPC with cluster configuration allows it schedule jobs and run  steps in parallel. This is the most efficient way to run snakemake.

There are several ways to run snakemake on HPC. There are limited instructions on cluster execution in the snakemake documentation [here](https://snakemake.readthedocs.io/en/stable/executing/cluster.html).

One easy way to run snakemake is to start an interactive session, and execute snakemake with the relevant cluster settings as described in the documentation. In this case, only a few threads are required for the interactive session, since most jobs will be run elsewhere. Snakemake will act as a job scheduler and also run local jobs from this location, until all jobs are complete. This can take a while, so it is best to use a detachable screen with the interactive session. 

The same general commands are used as with "local" execution, but with some additional arguments to support cluster configuration. Below is an example of cluster configuration using SGE:

```
snakemake --snakefile Snakefile-taxnuc --configfile configs/Sample-Config.yaml --use-conda --cluster "qsub -q default -pe smp {threads} -V -cwd -S /bin/bash" -j 5 --jobname "{rule}.{wildcards}.{jobid}" --latency-wait 60 
```

Let's unpack this command:
- `snakemake` calls snakemake.
- `--snakefile Snakefile-taxnuc` tells snakemake to run this particular snakefile.
- `--configfile configs/Sample-Config.yaml` tells snakemake to use this sample configuration file in the `configs/` directory. This file can have any name, as long as that name is provided here.
-  `--use-conda` this allows conda to install the programs and environments required for each step. It is essential.
- `--cluster "qsub -q default -pe smp {threads} -V -cwd -S /bin/bash"` are the settings for execution with SGE, where 'default' is the name of the machine. The threads argument will be automatically filled based on threads assigned to each rule. Note that the entire section in quotes can be replaced with a SLURM equivalent.
- `-j 5` will tell snakemake to run a maximum of 5 jobs simultaneously on the cluster. You can adjust this as needed.
- `--jobname "{rule}.{wildcards}.{jobid}"` provides convenient names for your snakemake jobs running on the cluster.
- `--latency-wait 60` this is important to include because there may be some delay in file writing between steps, and this prevents errors if files are not immediately found.

Upon the first execution, conda will download packages and create the correct environment. After, the jobs should begin scheduling and running. You can see the progress on screen in the interactive session, and also be able to monitor snakemake jobs running on the cluster. 


## Cloud Configuration

For information on how to run snakemake with AWS (Amazon Web Services), Google Cloud Life Sciences, or generic cloud computing, please see the snakemake documentation [here](https://snakemake.readthedocs.io/en/stable/executing/cloud.html).

[Back to top](#TOP)

---------------

## **5. Outputs** <a name="OTPS"></a>

Successful runs will result in several new directories:

```
Taxonomic-Profiling-Nucleotide
│
├── configs/
├── envs/
├── inputs/
├── scripts/
├── Snakefile-genomebinning
├── config.yaml
│
├── benchmarks/
├── logs/
│
├── 1-fasta-sort/
│
├── 2-chunks/
│
├── 3-minimap/
│
├── 4-sorted/
│
├── 5-merged/
│
└── 6-rma/
```

- `benchmarks/` contains benchmark information on memory usage and I/O for each rule executed.
- `logs/` contains log files for each rule executed. 
- `1-fasta-sort/` contains the sorted HiFi reads fasta files. *These can be deleted if no other RMA files will be created.*
- `2-chunks/` temporarily holds the two chunks for each sorted input reads file. Will be empty if no errors occur.
- `3-minimap/` temporarily holds the two unsorted SAM files generated per sample (e.g., the direct outputs from minimap2). Will be empty if no errors occur.
- `4-sorted/` temporarily holds the two sorted SAM files generated per sample. Will be empty if no errors occur.
- `5-merged/` contains the sorted and merged SAM files for each sample. *These can be deleted if no other RMA files will be created.*
- `6-rma/` contains final RMA files for MEGAN. **These are the main files of interest.**

If no additional RMA files are to be generated, you should remove all the sorted fasta files in `1-fasta-sort/` and the large SAM files from the `5-merged/` folder. 

[Back to top](#TOP)

---------------

## **6. Usage Details for Main Programs** <a name="UDMP"></a>

In this section, additional details are provided for the main programs used in the workflow. The commands to call these programs are provided here for quick reference. Curly braces are sections filled automatically by snakemake. For additional details on other steps, please refer to the Snakefile-taxnuc file.


### exonerate

Exonerate is used to split the fasta file into chunks, specifically using the `fastasplit` module:

```
fastasplit -c 2 -f {input} -o 2-chunks/
```

Chunks are named as `SAMPLE.fasta_chunk_0000000` and `SAMPLE.fasta_chunk_0000001`.   

### Minimap2

Minimap2 is used to align the HiFi reads to the nucleotide database. Here we are using settings appropriate for HiFi data:
```
minimap2 -a -k 19 -w 10 -I 10G -g 5000 -r 2000 -N 100 --lj-min-ratio 0.5 -A 2 -B 5 -O 5,56 -E 4,1 -z 400,50 --sam-hit-only -t {threads} {params.db} {input} 1> {output} 2> {log}
```

Note that the `-k 19` and `-w 10` are actually implemented when the database is indexed, which is why it is important to use `minimap2 -k 19 -w 10 -d mm2_nt_db.mmi nt.gz` for this purpose. If any other values are used during the indexing step, they will be automatically used here too (e.g., overriding `-k 19 -w 10`).

**The most important flag for metagenomics is `-N 100`, which allows up to 100 secondary alignments in addition to the primary alignment.** This is critical for obtaining relevant hits that are used downstream in MEGAN.

### sam2rma

Run the sam2rma tool with long read settings (`-alg longReads`). The default readAssignmentMode (`-ram`) for long reads is `alignedBases`, and `readCount` for all else. This controls whether or not the abundance counts rely on the total number of bases, or the number of reads. I prefer the number of reads, but this option can be changed in the `config.yaml` file to use `alignedBases` instead.

```
sam2rma -i {input.sam} -r {input.reads} -o {output} -lg -alg longReads -t {threads} -mdb {params.db} -ram {params.ram} -v 2> {log}
```

In this case, we are using a MEGAN database that maps genomic DNA accessions to taxonomic classes.

[Back to top](#TOP)

---------------
