# Tutorial for HiFi-MAG-Pipeline <a name="TOP"></a>

## **Table of Contents**

+ [HiFi-MAG-Pipeline Overview](#PO)
+ [Quick Start](#QS)
+ [1. Snakemake Contents](#SMC)
+ [2. Requirements for Running](#RFR)
+ [3. Configuring the Analysis](#CTA)
+ [4. Executing Snakemake](#EXS)
+ [5. Outputs](#OTPS)


---------------

# **HiFi-MAG-Pipeline Overview** <a name="PO"></a>

The purpose of this snakemake workflow is to obtain high-quality metagenome-assembled genomes (MAGs) from previously generated assemblies. This workflow received major improvements in v2.0 (Feb 2023). The new steps of the HiFi-MAG-Pipeline are shown below:

![GBSteps](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/Image-HiFi-MAG-Summary.png)

### "Completeness-aware" strategy

The new version of this workflow is "completeness-aware". Long contigs >500kb are identified and placed in individual fasta files. They are then examined using CheckM2 to determine percent completeness. All long contigs that are >93% complete are then moved directly to the final MAG set. 

The long contigs that are <93% complete are pooled with other shorter incomplete contigs from the starting set, and this contig set is subjected to binning. Binning algorithms include MetaBat2 and SemiBin2 (using long read settings). The two bin sets are compared and merged using DAS_Tool. 

The dereplicated bin set consists of the merged bin set from above and all long complete contigs found. The dereplicated bin set is examined using CheckM2, and subsequently filtered based on several qualities (defaults = >70% completeness, <10% contamination, <20 contigs). 

All bins/MAGs passing filtering undergo taxonomic assignment using GTDB-Tk. The final MAGs are written as a set of fasta files, several figures are produced, and a summary file of metadata is generated.

### Benchmarking improvements

The new "completeness-aware" strategy is highly effective at preventing improper binning of complete contigs. It is more effective than the previous "circular-aware" binning used in v1.5 and v1.6. Compared to a standard binning pipeline (e.g., MetaBat2), it results in a 14-67% increase in total MAGs (average 36%) and 13-186% increase in single contig MAGs (average 87%). Compared to the "circular-aware" binning in v1.5, it results in a 14-39% increase in total MAGs (average 27%) and 10-28% increase in single contig MAGs (average 20%). The figure below shows side-by-side comparisons for several publicly available datasets (listed [here](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/PacBio-Data.md)). 

![Improvement](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/Image-HiFi-MAG-Pipeline-Update.png)


### Additional improvements

Beyond the "completeness-aware" strategy, there are several other important updates to this pipeline. 
+ It now uses CheckM2 instead of CheckM, and no longer requires the manual download of the Checkm database.
+ For binning, Concoct and MaxBin2 have been retired, and SemiBin2 is used  in conjunction with MetaBat2. SemiBin2 is highly effective at binning contigs from long-read assemblies and obtains better results.
+ This version also introduces checkpoints to create forked workflows depending on the properties of the sample, thereby preventing crashes when no bins pass filtering. This applies to the long contig completeness evaluation stage and the binning of incomplete contigs.
+ New figures are produced as part of the long contig evaluations and final summary steps, as shown below.

Figures associated with long contig completeness evaluation:

![Longbins](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/Image-HiFi-MAGs-Example-Outputs-LongBins.png)

Figures associated with final summary steps:

![Longbins](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/Image-HiFi-MAGs-Example-Outputs-Summary.png)

For explanations of these figures, please see the [5. Outputs](#OTPS) section below.

[Back to top](#TOP)

---------------

# **Quick Start** <a name="QS"></a>

This workflow requires [Anaconda](https://docs.anaconda.com/anaconda/)/[Conda](https://docs.conda.io/projects/conda/en/latest/index.html) and [Snakemake](https://snakemake.readthedocs.io/en/stable/) to be installed, and will require 45-150GB memory and >250GB temporary disk space (see [Requirements section](#RFR)). All dependencies in the workflow are installed using conda and the environments are activated by snakemake for relevant steps. Snakemake v5+ is required, and the workflows have been tested using v5.19.3.

- Clone the HiFi-MAG-Pipeline directory.
- Download and unpack the database for GTDB (~66GB). The current requirement is for GTDB-Tk v 2.1.1, which requires database R207_v2. Specify the path to the database in `config.yaml`. **Starting with version 2.0, there is no need to download the CheckM database.**
- Include all input HiFi fasta files (`SAMPLE.fasta`) and contig fasta files (`SAMPLE.contigs.fasta`) in the `inputs/` folder. These can be files or symlinks.
- Edit sample names in `Sample-Config.yaml` configuration file in `configs/` for your project. 
- Check settings in `config.yaml`, and ensure the `tmpdir` argument is set correctly in `config.yaml`. The default is `/scratch`.
- Execute snakemake using the general commands below: 
```
snakemake --snakefile Snakefile-hifimags.smk --configfile configs/Sample-Config.yaml --use-conda [additional arguments for local/HPC execution]
```
The choice of additional arguments to include depends on where and how you choose to run snakemake. Please refer to the [4. Executing Snakemake](#EXS) section for more details.

[Back to top](#TOP)

---------------

# **1. Snakemake Contents** <a name="SMC"></a>

To run the workflow, you will need to obtain all contents within the [HiFi-MAG-Pipeline folder](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/HiFi-MAG-Pipeline). The default contents should look like this:

```
HiFi-MAG-Pipeline
│
├── configs/
│	└── Sample-Config.yaml
│
├── envs/
│	├── checkm2.yml
│	├── dastool.yml
│	├── gtdbtk.yml
│	├── metabat.yml
│	├── python.yml
│	├── samtools.yml
│	└── semibin.yml
│
├── inputs/
│	└── README.md (this is just a placeholder file, and not required)
│
├── scripts/
│	├── Convert-JGI-Coverages.py
│	├── Copy-Final-MAGs.py
│	├── Fasta-Make-Long-Seq-Bins.py
│	├── Filter-Checkm2-Bins.py
│	├── Filter-Complete-Contigs.py
│	├── GTDBTk-Organize.py
│	├── MAG-Summary.py
│	├── Make-Incomplete-Contigs.py
│	├── Maxbin2-organize-outputs.py
│	└── Plot-Figures.py
│
├── Snakefile-hifimags.smk
│
└── config.yaml
```
The `Snakefile-hifimags.smk` file is the Snakefile for this snakemake workflow. It contains all of the rules of the workflow. 

The `config.yaml` file is the main configuration file used in the snakemake workflow. It contains the main settings that will be used for various programs. 

The `configs/` directory contains an example configuration file for specifying which samples are to be run. The configuration file can be renamed. It must be specified in the command line call for snakemake for any samples to be run.

The `inputs/` directory should contain all of the required input files for each sample. In this workflow there must be a `SAMPLE.fasta` file of HiFi reads and a `SAMPLE.contigs.fasta` file that contains the assembled contigs. These can be the actual files, or symbolic links to the files (for example using `ln -s source_file symbolic_name`).

The `scripts/` directory contains a few Python scripts required for the workflow. These are involved with formatting, filtering, plotting, and summarizing. They are called in different steps of the workflow.

Finally, the `envs/` directory contains the several files which are needed to install all dependencies through conda. These environments are activated for each step of the workflow.

[Back to top](#TOP)

---------------

# **2. Requirements for Running** <a name="RFR"></a>

## Memory and disk space requirements

Running certain steps in this pipeline will potentially require ~45GB of memory. The step in GTDB-Tk (pplacer) that used to require large amounts memory (~150GB) and temporary disk space (~250GB) has been fixed in the v2.+ release.

## Dependencies

In order to run a snakemake workflow, you will need to have an anaconda or conda installation. Conda is essential because it will be used to install the dependencies within the workflow and setup the correct environments. 

Snakemake will also need to be installed. Instructions for installing snakemake using conda can be found [here](https://snakemake.readthedocs.io/en/stable/getting_started/installation.html). Snakemake v5+ is required, and the workflows have been tested using v5.19.3.

If you intend to generate a graphic for the snakemake workflow graph, you will also need graphviz installed.

## Generate assemblies

For assembly of metagenomic samples with HiFi reads, you can use [hifiasm-meta](https://github.com/xfengnefx/hifiasm-meta), [metaFlye](https://github.com/fenderglass/Flye), or [HiCanu](https://github.com/marbl/canu). 

For hifiasm-meta, the default settings work very well. For very large datasets (>100Gb total data), you may benefit from using the `-S` flag to invoke read selection. It will reduce memory requirements.

For metaFlye the defaults also work well, but of course make sure to use the `--pacbio-hifi` and `--meta` flags! 

For Canu v2.1, we strongly recommend the following settings:

```
canu -d DIRECTORY -p OUTPUT_NAME -pacbio-hifi FQ_DATA genomeSize=100m maxInputCoverage=1000 batMemory=200
```

The additional batOptions previously recommended for metagenomics with Canu 2.0 (`batOptions=-eg 0.0 -sb 0.001 -dg 0 -db 3 -dr 0 -ca 2000 -cp 200`) are apparently no longer necessary if using Canu 2.1. For a brief discussion on these Canu metagenomics assembly settings, please see [here](https://github.com/marbl/canu/issues/1796).

## Download required databases

The database for for `GTDB-Tk` must be downloaded prior to running analyses. The CheckM database is no longer required as of HiFi-MAG-Pipeline v2.0.

**GTDB-Tk database**

Complete instructions for the GTDB-Tk database can be found at: https://ecogenomics.github.io/GTDBTk/installing/index.html

**This workflow currently uses GTDB-Tk v 2.1.1, which requires database R207_v2.**

The current GTDB release can be downloaded from: 
https://data.gtdb.ecogenomic.org/releases/latest/auxillary_files/gtdbtk_data.tar.gz

```
wget https://data.gtdb.ecogenomic.org/releases/latest/auxillary_files/gtdbtk_v2_data.tar.gz
tar -xvzf gtdbtk_data.tar.gz  
```

It must also be decompressed prior to usage. The unpacked contents will be ~66GB in size. The path to the directory containing the decompressed contents must be specified in the main configuration file (`config.yaml`). The decompressed file should result in several folders (`fastani/`, `markers/`, `masks/`, `metadata/`, `mrca_red/`, `msa/`, `pplacer/`, `radii/`, `taxonomy/`).


[Back to top](#TOP)

---------------

# **3. Configuring the Analysis** <a name="CTA"></a>

To configure the analysis, the main configuration file (`config.yaml`) and sample configuration file (`configs/Sample-Config.yaml`) should be edited. 

#### Main configuration file (`config.yaml`)
The main configuration file contains several parameters, each of which is described in the configuration file. Depending on your system resources, you may choose to change the number of threads used in minimap, MetaBat2, SemiBin2, CheckM2, or GTDB-Tk. 

Please also check that the `tmpdir` argument is set correctly. The default is `/scratch`, which may be available to most users on HPC. This can be changed if `/scratch` is not available, or if you are running snakemake locally. Change it to a valid output directory that can be used to write many large files. This is used in conjunction with the `--tmpdir` flag in CheckM2, the `--tmpdir` in SemiBin2, and the `--scratch_dir` flag in GTDB-Tk. 

It is not recommended to change settings related to the long contig binning step. However,  you may wish to change the thresholds for filtering bins: `min_completeness` (default 70), `max_contamination` (default 10), and `max_contigs` (default 10).

For SemiBin2, you may wish to change the model flag. The default is set to run a general pre-computed model (`--environment=global`). This can be changed to one of several pre-computed models (`human_gut`, `human_oral`, `dog_gut`, `cat_gut`, `mouse_gut`, `pig_gut`, `chicken_caecum`, `ocean`, `soil`, `built_environment`, `wastewater`,  `global`). To enable a new model to be trained from your dataset, this should be changed to an empty string (`""`). Doing so will invoke the self-supervised learning approach. However, please be aware that this can add a *significant* amount fo run-time to the analysis (~15 additional hours per sample was not uncommon in my tests). The de novo model will likely obtain more bins than a pre-computed model, but this is highly dependent on your dataset. To read more about this, please see the pre-print [**here**](https://www.biorxiv.org/content/10.1101/2023.01.09.523201v1).

**You must specify the full path to the GTDB-TK database**. In the configuration file, this is the `gtdbtk_data` parameter. See above section for where to obtain the database.


#### Sample configuration file (`configs/Sample-Config.yaml`)
The example sample configuration file is called `Sample-Config.yaml` and is located in the `configs/` directory. Here you should specify the sample names that you wish to include in the analysis. 

All samples specified in the sample configuration file must have two corresponding files in the `inputs/` folder. These include the fasta file of HiFi reads (`SAMPLE.fasta`) and the assembled contigs (`SAMPLE.contig.fasta`). Here, the `SAMPLE` component is a name included in the sample configuration file. The pipeline can be run for any number of samples. You can also configure the file to only run for a subset of the samples present in the `inputs/` folder. Please note that if the input files do not follow these naming conventions (`SAMPLE.fasta`, `SAMPLE.contig.fasta`), they will not be recognized by the workflow. You can use the actual files or symlinks to those files, both are compatible with snakemake. If you used metaFlye for assembly, you must also include the `SAMPLE-assembly_info.txt` file here.

[Back to top](#TOP)

---------------

# **4. Executing Snakemake** <a name="EXS"></a>

Before attempting to run this snakemake analysis, please ensure that the pre-analysis requirements have been satisfied, the analysis has been configured properly (using the general and sample configuration files), and the input files are available in the `inputs/` folder. 

There are several ways to execute the workflow. The easiest way is to run snakemake on HPC using an interactive session. The most efficient way is to use cluster or cloud configuration so that snakemake can schedule and run jobs on HPC or cloud environments. 

## Local execution

**Given the large memory requirements for some programs used in the workflow, execution of this mode is only recommended with interactive HPC sessions.**

Snakemake can be run "locally" (e.g., without cluster configuration). Snakemake will automatically determine how many jobs can be run simultaneously based on the resources specified. This type of snakemake analysis can be run on a local system, but ideally it should be executed using an interactive HPC session (for example, `qrsh` with SGE or the SLURM equivalent).

The workflow must be executed from within the directory containing all the snakemake contents for the HiFi-MAG-Pipeline. 

### Test workflow
It is a good idea to test the workflow for errors before running it. This can be done with the following command:
```
snakemake -np --snakefile Snakefile-hifimags.smk --configfile configs/Sample-Config.yaml
```

Let's unpack this command:
- `snakemake` calls snakemake.
- `-np` performs a 'dry-run' where the rule compatibilities are tested but they are not executed.
- `--snakefile Snakefile-hifimags.smk` tells snakemake to run this particular snakefile.
- `--configfile configs/Sample-Config.yaml` tells snakemake to include the samples listed in the sample configuration file.

The dry run command should result in the jobs being displayed on screen. 

### Create workflow figure
If there are no errors, you may wish to generate a figure of the directed acyclic graph (the workflow steps). You can do this using the following command:
```
snakemake --dag --snakefile Snakefile-hifimags.smk --configfile configs/Sample-Config.yaml | dot -Tsvg > hifimags_analysis.svg
```
Here the `--dag` flag creates an output that is piped to `dot`, and an svg file is created. This will show the workflow visually.

### Execute workflow
Finally, you can execute the workflow using:
```
snakemake --snakefile Snakefile-hifimags.smk --configfile configs/Sample-Config.yaml -j 48 --use-conda
```

There are a couple important arguments that were added here:

- `-j 48` specifies that there are 48 threads available to use. You should change this to match the resources available. If more threads are specified in the configuration file than are available here, snakemake automatically scales them down to this number.
-  `--use-conda` allows conda to install the programs and environments required for each step. This is essential.

Upon execution, the first step will be conda downloading packages and creating the correct environment. After, the jobs should begin running. You will see the progress on screen.


## Cluster Configuration

Executing snakemake on HPC with cluster configuration allows it schedule jobs and run  steps in parallel. This is the most efficient way to run snakemake.

There are several ways to run snakemake on HPC. There are limited instructions on cluster execution in the snakemake documentation [here](https://snakemake.readthedocs.io/en/stable/executing/cluster.html).

One easy way to run snakemake is to start an interactive session, and execute snakemake with the relevant cluster settings as described in the documentation. In this case, only a few threads are required for the interactive session, since most jobs will be run elsewhere. Snakemake will act as a job scheduler and also run local jobs from this location, until all jobs are complete. This can take a while, so it is best to use a detachable screen with the interactive session. 

The same general commands are used as with "local" execution, but with some additional arguments to support cluster configuration. Below is an example of cluster configuration using SLURM:

```
snakemake --snakefile Snakefile-hifimags.smk --configfile configs/Sample-Config.yaml --use-conda --cluster "sbatch --partition=compute --cpus-per-task={threads}" -j 5 --jobname "{rule}.{wildcards}.{jobid}" --latency-wait 60 
```

Let's unpack this command:
- `snakemake` calls snakemake.
- `--snakefile Snakefile-hifimags.smk` tells snakemake to run this particular snakefile.
- `--configfile configs/Sample-Config.yaml` tells snakemake to use this sample configuration file in the `configs/` directory. This file can have any name, as long as that name is provided here.
-  `--use-conda` this allows conda to install the programs and environments required for each step. It is essential.
- `--cluster "sbatch --partition=compute --cpus-per-task={threads}"` are the settings for execution with SLURM, where 'compute' is the name of the machine. The threads argument will be automatically filled based on threads assigned to each rule. Note that the entire section in quotes can be replaced with an SGE equivalent (see below).
- `-j 5` will tell snakemake to run a maximum of 5 jobs simultaneously on the cluster. You can adjust this as needed.
- `--jobname "{rule}.{wildcards}.{jobid}"` provides convenient names for your snakemake jobs running on the cluster.
- `--latency-wait 60` this is important to include because there may be some delay in file writing between steps, and this prevents errors if files are not immediately found.

And here is an example using SGE instead:

```
snakemake --snakefile Snakefile-hifimags.smk --configfile configs/Sample-Config.yaml --use-conda --cluster "qsub -q default -pe smp {threads} -V -cwd -S /bin/bash" -j 5 --jobname "{rule}.{wildcards}.{jobid}" --latency-wait 60 
```
- `--cluster "qsub -q default -pe smp {threads} -V -cwd -S /bin/bash"` are the settings for execution with SGE, where 'default' is the name of the machine. The threads argument will be automatically filled based on threads assigned to each rule.

Upon the first execution, conda will download packages and create the correct environment. After, the jobs should begin scheduling and running. You can see the progress on screen in the interactive session, and also be able to monitor snakemake jobs running on the cluster. 


## Cloud Configuration

For information on how to run snakemake with AWS (Amazon Web Services), Google Cloud Life Sciences, or generic cloud computing, please see the snakemake documentation [here](https://snakemake.readthedocs.io/en/stable/executing/cloud.html).

[Back to top](#TOP)

---------------

## **5. Outputs** <a name="OTPS"></a>

Successful runs will result in several new directories:

```
HiFi-MAG-Pipeline
│
├── configs/
├── envs/
├── inputs/
├── scripts/
├── Snakefile-hifimags.smk
├── config.yaml
│
├── benchmarks/
├── logs/
│
├── 1-long-contigs/
├── 2-bam/
├── 3-metabat2/
├── 3-semibin2/
├── 4-DAStool/
├── 5-dereplicated-bins/
├── 6-checkm2/
├── 7-gtdbtk/
└── 8-summary/


```

- `benchmarks/` contains benchmark information on memory usage and I/O for each rule executed.
- `logs/` contains log files for each rule executed.
- `1-long-contigs/` contains the outputs from the long contig completeness evaluation. The contents change depending on whether or not any long, complete contigs are found. If none are found, a `SAMPLE.no_passed_bins.txt` file will be here, but if some are found a `SAMPLE.passed_bins.txt` file will be here instead. Additionally some useful figures will be present: `SAMPLE.completeness_histo.pdf`, `SAMPLE.completeness_vs_size_scatter.pdf`.
- `2-bam/` contains the sorted bam files and depth files needed for binning, and later for depth of coverage calculations per MAG.
- `3-metabat2/` contains the outputs from MetaBat2, per sample, using the "incomplete" contigs set (e.g., the starting contigs minus and long complete contigs).
- `3-semibin2/` contains the outputs from SemiBin2, per sample, using the "incomplete" contigs set (e.g., the starting contigs minus and long complete contigs).
- `4-DAStool/` contains outputs from DAS_Tool for comparing the MetaBat2 and SemiBin2 bin sets of the "incomplete" contigs set (e.g., the starting contigs minus and long complete contigs), per sample.
- `5-dereplicated-bins/` contains the dereplicated bins from DAS_Tool and any long complete contigs from step 1, per sample.
- `6-checkm2/` contains the CheckM2 results for the dereplicated bin set above, per sample.
- `7-gtdbtk/` contains gtdb-tk results for dereplicated bins that passed filtering with CheckM2, per sample.
- `8-summary/` **contains the main output files of interest**.

Within `8-summary/`, there will be a folder for each sample. Within a sample folder there are several items:

+ `MAGs/`: A folder that contains the fasta files for all high-quality MAGs/bins.
+ `SAMPLE.All-DASTool-Bins.pdf`: Figure that shows the dereplicated bins that were created from the set of incomplete contigs (using MetaBat2 and SemiBin2) as well as the long complete contigs.
+ `SAMPLE.Complete.txt`: This is a blank file that is created when the workflow stopping point is reached. 
+ `SAMPLE.Completeness-Contamination-Contigs.pdf`: A plot showing the relationship between completeness and contamination for each high-quality MAG recovered, colored by the number of contigs per MAG.
+ `SAMPLE.GenomeSizes-Depths.pdf`:  A plot showing the relationship between genome size and depth of coverage for each high-quality MAG recovered, colored by % GC content per MAG.
+ `SAMPLE.HiFi_MAG.summary.txt`: A main summary file that brings together information from CheckM2 and GTDB-Tk for all MAGs that pass the filtering step. 


[Back to top](#TOP)

```
