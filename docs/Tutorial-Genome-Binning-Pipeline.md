# Genome-Binning-Pipeline <a name="TOP"></a>

## **Table of Contents**

+ [Genome-Binning-Pipeline Overview](#PO)
+ [Quick Start](#QS)
+ [1. Snakemake Contents](#SMC)
+ [2. Requirements for Running](#RFR)
+ [3. Configuring the Analysis](#CTA)
+ [4. Executing Snakemake](#EXS)
+ [5. Outputs](#OTPS)
+ [6. Usage Details for Main Programs](#UDMP)


---------------

# **Genome-Binning-Pipeline Overview** <a name="PO"></a>

The purpose of this snakemake workflow is to obtain high-quality metagenome-assembled genomes (MAGs) from previously generated assemblies. The general steps of the Genome-Binning-Pipeline are shown below:

![GBSteps](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/Genome-Binning-Steps.png)

HiFi reads are mapped to contigs using minimap2 to generate BAM files. The BAM files are used to obtain coverage estimates for the contigs. The coverages and contigs are used as inputs to MetaBAT2, which constructs the genome bins. CheckM is used to assess the quality of the resulting genome bins. It provides measures of genome completeness, contamination, and other useful metrics. A custom filtering step is used to eliminate genome bins with <70% genome completeness, >10% genome contamination, and >10 contigs per bin. These are default values, and they can be changed. The genome bins which pass the default thresholds can be considered high-quality MAGs. Finally, the Genome Taxonomy Database Toolkit (GTDB-Tk) is used to identify the closest reference match to each high-quality MAG. It will report the taxonomy of the closest reference. This does not guarantee the identity of the MAG, but serves as a starting point for understanding which genus, species, or strain it is most closely related to.

[Back to top](#TOP)

---------------

# **Quick Start** <a name="QS"></a>

This workflow requires Anaconda/Conda and Snakemake to be installed, and will require 45-150GB memory and >250GB temporary disk space. All dependencies in the workflow are installed using conda and the environments are activated by snakemake for relevant steps.

- Clone the Genome-Binning-Pipeline directory.
- Download and unpack the databases for CheckM and GTDB. Specify paths to each database in `config.yaml`.
- Include all input HiFi fasta files (`SAMPLE.fasta`) and contig fasta files (`SAMPLE.contigs.fasta`) in the `inputs/` folder. These can be files or symlinks. 
- Edit sample names in `Sample-Config.yaml` configuration file in `configs/` for your project. 
- Execute snakemake using the general commands below: 
```
snakemake --snakefile Snakefile-genomebinning --configfile configs/Sample-Config.yaml --use-conda [additional args for local setup or cluster configuration]
```


[Back to top](#TOP)

---------------

# **1. Snakemake Contents** <a name="SMC"></a>

To run the workflow, you will need to obtain all contents within the [Genome-Binning-Pipeline folder](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/Genome-Binning-Pipeline). The default contents should look like this:

```
Genome-Binning-Pipeline
│
├── configs/
│	└── Sample-Config-Example.yaml
│
├── envs/
│	└── general.yml
│
├── inputs/
│	└── README.md (this is just a placeholder file, and not required)
│
├── scripts/
│	├── CheckM-to-batch-GTDB.py
│	├── genome-binning-summarizer.py
│	└── Metabat-Plot.py
│
├── Snakefile-genomebinning
│
└── config.yaml
```
The `Snakefile-genomebinning` file is the Snakefile for this snakemake workflow. It contains all of the rules of the workflow. 

The `config.yaml` file is the main configuration file used in the snakemake workflow. It contains the main settings that will be used for various programs. 

The `configs/` directory contains an example configuration file for specifying which samples are to be run. The configuration file can be renamed. It must be specified in the command line call for snakemake for any samples to be run.

The `inputs/` directory should contain all of the required input files for each sample. In this workflow there must be a `SAMPLE.fasta` file of HiFi reads and a `SAMPLE.contigs.fasta` file that contains the assembled contigs. These can be the actual files, or symbolic links to the files (for example using `ln -s source_file symbolic_name`). 

The `scripts/` directory contains a few Python scripts required for the workflow. These are involved with formatting, filtering, plotting, and summarizing. They are called in different steps of the workflow.

Finally, the `envs/` directory contains the `general.yml` file which is needed to install all dependencies through conda. This environment is activated for each step of the workflow. The dependencies are installed from bioconda and conda-forge and include: `samtools 1.10`, `minimap2 2.17`, `metabat2 2.15`, `checkm-genome 1.1.2`, `gtdbtk 1.3.0`, `numpy`, `pandas`, `seaborn`, `matplotlib`, and `biopython`.

[Back to top](#TOP)

---------------

# **2. Requirements for Running** <a name="RFR"></a>

Running certain steps in this pipeline will require ~45GB of memory. There is a step in GTDB-Tk (pplacer) that can require large amounts memory (~150GB) and disk space (~250GB). This workflow allows writing temporary files in GTDB-Tk using the `--scratch_dir /scratch` setting, which reduces the memory requirements drastically (e.g., 150GB rather than 1TB). These are known issues with pplacer. If run into memory issues with this step please see the discussion [here](https://github.com/Ecogenomics/GTDBTk/issues/124) for potential solutions.

There are also a few steps that must be completed prior to running the snakemake workflow.

## Dependencies

In order to run a snakemake workflow, you will need to have an anaconda or conda installation. Conda is essential because it will be used to install the dependencies within the workflow and setup the correct environments. 

Snakemake will also need to be installed. Instructions for installing snakemake using conda can be found [here](https://snakemake.readthedocs.io/en/stable/getting_started/installation.html). 

If you intend to generate a graphic for the snakemake workflow graph, you will also need graphviz installed.

## Generate assemblies

For assembly of metagenomic samples with HiFi reads, we strongly recommend using Canu v2.1 with the following settings:

```
canu -d DIRECTORY -p OUTPUT_NAME -pacbio-hifi FQ_DATA genomeSize=100m maxInputCoverage=1000 batMemory=200
```

The additional batOptions previously recommended for Canu 2.0 (`batOptions=-eg 0.0 -sb 0.001 -dg 0 -db 3 -dr 0 -ca 2000 -cp 200`) are no longer necessary if using Canu 2.1.

## Download required databases

Two databases must be downloaded prior to running analyses, one for `CheckM` and one for `GTDB-Tk`.

**CheckM database**

Complete instructions for the CheckM database can be found at: https://github.com/Ecogenomics/CheckM/wiki/Installation

Briefly, the CheckM database can be obtained from: https://data.ace.uq.edu.au/public/CheckM_databases/

The downloaded file must be decompressed to use it. The contents will be ~1.7GB in size. The path to the directory containing the decompressed contents must be specified in the main configuration file (`config.yaml`). The decompressed file should result in several folders (`distributions/`, `genome_tree/`, `hmms/`, `hmms_ssu/`, `img/`, `pfam/`, `test_data/`) and two tsv files.

**GTDB-Tk database**

Complete instructions for the GTDB-Tk database can be found at: https://ecogenomics.github.io/GTDBTk/installing/index.html

The current GTDB release can be downloaded from: https://data.ace.uq.edu.au/public/gtdb/data/releases/release95/95.0/auxillary_files/gtdbtk_r95_data.tar.gz

It must also be decompressed prior to usage. The contents will be ~27GB in size. The path to the directory containing the decompressed contents must be specified in the main configuration file (`config.yaml`). The decompressed file should result in several folders (`fastani/`, `markers/`, `masks/`, `metadata/`, `mrca_red/`, `msa/`, `pplacer/`, `radii/`, `taxonomy/`).


[Back to top](#TOP)

---------------

# **3. Configuring the Analysis** <a name="CTA"></a>

To configure the analysis, the main configuration file (`config.yaml`) and sample configuration file (`configs/Sample-Config.yaml`) should be edited. 

## Main configuration file
The main configuration file contains several parameters, each of which is described in the configuration file. Depending on your system resources, you may choose to change the number of threads used in the minimap, metabat, checkm, or gtdbtk settings. In particular, the use of `pplacer` in gtdbtk can cause very high memory/disk usage depending on the threads used (see [here](https://github.com/Ecogenomics/GTDBTk/issues/124)). You may wish to change this setting if you encounter issues.

**You must specify the full paths to the databases that were downloaded for checkm and gtdbtk**. In the configuration file, this is the `datapath` parameter in the checkm settings, and the `gtdbtk_data` parameter in the gtdbtk settings. See above section for where to obtain these databases.

You may also wish to change the thresholds for filtering in the gtdbtk settings: `min_completeness` (default 70), `max_contamination` (default 10), and `max_contigs` (default 10).

## Sample configuration file
The example sample configuration file is called `Sample-Config.yaml` and is located in the `configs/` directory. Here you should specify the sample names that you wish to include in the analysis. 

For the Genome-Binning-Pipeline, all samples specified in the sample configuration file must have two corresponding files in the `inputs/` folder. These include the fasta file of HiFi reads (`SAMPLE.fasta`) and the assembled contigs (`SAMPLE.contig.fasta`). Here, the `SAMPLE` component is a name included in the sample configuration file. The pipeline can be run for any number of samples. You can also configure the file to only run for a subset of the samples present in the `inputs/` folder. Please note that if the input files do not follow these naming conventions (`SAMPLE.fasta`, `SAMPLE.contig.fasta`), they will not be recognized by the workflow. You can use the actual files or symlinks to those files, both are compatible with snakemake.

[Back to top](#TOP)

---------------

# **4. Executing Snakemake** <a name="EXS"></a>

Before attempting to run this snakemake analysis, please ensure that the pre-analysis requirements have been satisfied, the analysis has been configured properly (using the general and sample configuration files), and the input files are available in the `inputs/` folder. 

There are several ways to execute the workflow. The easiest way is to run snakemake on HPC using an interactive session. The most efficient way is to use cluster configuration so that snakemake can schedule its own jobs on the HPC. 

## Local execution

**Given the large memory requirements for several programs used in the workflow, execution of this mode is only recommended with interactive HPC sessions.**

Snakemake can be run "locally" (e.g., without cluster configuration). Snakemake will automatically determine how many jobs can be run simultaneously based on the resources specified. This type of snakemake analysis can be run on a local system, but ideally it should be executed using an interactive HPC session (for example, `qrsh` with SGE or the SLURM equivalent).

The workflow must be executed from within the directory containing all the snakemake contents for the genome-binning-pipeline. 

### Test workflow
It is a good idea to test the workflow for errors before running it. This can be done with the following command:
```
snakemake -np --snakefile Snakefile-genomebinning --configfile configs/Sample-Config.yaml
```

Let's unpack this command:
- `snakemake` calls snakemake.
- `-np` performs a 'dry-run' where the rule compatibilities are tested but they are not executed.
- `--snakefile Snakefile-genomebinning` tells snakemake to run this particular snakefile.
- `--configfile configs/Sample-Config.yaml` tells snakemake to include the samples listed in the sample configuration file.

The dry run command should result in the jobs being displayed on screen. 

### Create workflow figure
If there are no errors, you may wish to generate a figure of the directed acyclic graph (the workflow steps). You can do this using the following command:
```
snakemake --dag --snakefile Snakefile-genomebinning --configfile configs/Sample-Config.yaml | dot -Tsvg > genome-binning_analysis.svg
```
Here the `--dag` flag creates an output that is piped to `dot`, and an svg file called `genome-binning_analysis.svg` is created. This will show the workflow visually.

### Execute workflow
Finally, you can execute the workflow using:
```
snakemake --snakefile Snakefile-genomebinning --configfile configs/Sample-Config.yaml -j 48 --use-conda
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
snakemake --snakefile Snakefile-genomebinning --configfile configs/Sample-Config.yaml --use-conda --cluster "qsub -q default -pe smp {threads} -V -cwd -S /bin/bash" -j 5 --jobname "{rule}.{wildcards}.{jobid}" --latency-wait 60 
```

Let's unpack this command:
- `snakemake` calls snakemake.
- `--snakefile Snakefile-genomebinning` tells snakemake to run this particular snakefile.
- `--configfile configs/Sample-Config.yaml` tells snakemake to use this sample configuration file in the `configs/` directory. This file can have any name, as long as that name is provided here.
-  `--use-conda` this allows conda to install the programs and environments required for each step. It is essential.
- `--cluster "qsub -q default -pe smp {threads} -V -cwd -S /bin/bash"` are the settings for execution with SGE, where 'default' is the name of the machine. The threads argument will be automatically filled based on threads assigned to each rule. Note that the entire section in quotes can be replaced with a SLURM equivalent.
- `-j 5` will tell snakemake to run a maximum of 5 jobs simultaneously on the cluster. You can adjust this as needed.
- `--jobname "{rule}.{wildcards}.{jobid}"` provides convenient names for your snakemake jobs running on the cluster.
- `--latency-wait 60` this is important to include because there may be some delay in file writing between steps, and this prevents errors if files are not immediately found.

Upon the first execution, conda will download packages and create the correct environment. After, the jobs should begin scheduling and running. You can see the progress on screen in the interactive session, and also be able to monitor snakemake jobs running on the cluster. 


[Back to top](#TOP)

---------------

## **5. Outputs** <a name="OTPS"></a>

Successful runs will result in several new directories:

```
Genome-Binning-Pipeline
│
├── configs/
├── envs/
├── inputs/
├── scripts/
├── Snakefile-genomebinning
├── config.yaml
│
├── 1-bam/
│
├── 2-metabat-bins/
│
├── 3-checkm/
│
├── 4-checkm-summary/
│
├── 5-gtdb-individual/
│
├── 6-gtdb-combined-Full/
│
└── 7-summary/
```

- `1-bam/` contains the sorted bam files from mapping reads to contigs using minimap2.
- `2-metabat-bins/` contains the outputs from metabat2, per sample.
- `3-checkm/` contains outputs from checkm, per sample.
- `4-checkm-summary/` contains intermediate files.
- `5-gtdb-individual/` contains gtdb-tk results for each sample as run independently.
- `6-gtdb-combined-[Full]/` contains the gtdb-tk results for the combined sample set.
- `7-summary/` contains the main output files of interest.

Within `7-summary/`, there are folders for each sample. Within a sample folder there is:
+ A main summary file that brings together information from metabats2, checkm, and gtdb-tk for all MAGs that pass the filtering step. 
+ A folder `binplots` that contains several plots. One set of plots is for the unfiltered genome bins (e.g., all bins from metabat2), and the other is for the filtered high-quality MAGs. These plots compare % genome completeness vs. % contamination, with variations including bin name labels or the number of contigs per bin labeled.
+ A folder `bin-ref-pairs` which contains a subfolder for each high-quality MAG. Inside each is a MAG fasta file and the closest reference fasta file (inferred by GTDK-Tk). This can be useful for downstream genome alignments or further characterization.


[Back to top](#TOP)

---------------

## **6. Usage Details for Main Programs** <a name="UDMP"></a>

In this section, additional details are provided for the main programs used in the workflow. The commands to call these programs are provided here for quick reference. Curly braces are sections filled automatically by snakemake. For additional details on other steps, please refer to the Snakefile-genomebinning file.

### Minimap2

Map HiFi reads to contigs using minimap2 metagenomic HiFi settings, pipe output to samtools sort, write output bam file:
```
minimap2 -a -k 19 -w 10 -I 10G -g 5000 -r 2000 -N 100 --lj-min-ratio 0.5 -A 2 -B 5 -O 5,56 -E 4,1 -z 400,50 --sam-hit-only -t {threads} {input.contigs} {input.reads} 2> {log} | samtools sort -@ {threads} -o {output}"
```

### MetaBAT2

Convert bam file to depth file for metabat2 using metabat2 helper tool:
```
jgi_summarize_bam_contig_depths --outputDepth {output} {input.bam} 2> {log}
```

Running metabat2:
```
metabat2 -i {input.contigs} -a {input.depths} -o {params.prefix} -t {threads} -v &> {log}
```

### CheckM

Set the datapath for checkm database and then run checkm:
```
checkm data setRoot {params.datapath} &> {log.root} && checkm lineage_wf -x fa -t {threads} --pplacer_threads {params.ppthreads} --tmpdir /scratch {params.indir} {params.outdir} &> {log.run}
```

Summarize results in tabular format:
```
checkm qa -o2 {input} {params.outdir} -f {output} --tab_table &> {log}
```

### GTDB-Tk
Set datapath and run gtdbtk:
```
GTDBTK_DATA_PATH={params.gtdbtk_data:q} gtdbtk classify_wf --batchfile {input} --out_dir {params.outdir} -x fa --prefix {wildcards.sample} --cpus {threads} --pplacer_cpus {params.ppthreads} --scratch_dir /scratch &> {log}
```

[Back to top](#TOP)

---------------
