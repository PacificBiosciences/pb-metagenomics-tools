# Tutorial for Taxonomic-Profiling-Sourmash <a name="TOP"></a>

## **Table of Contents**

+ [Taxonomic-Profiling-Sourmash Overview](#PO)
+ [Quick Start](#QS)
+ [1. Snakemake Contents](#SMC)
+ [2. Requirements for Running](#RFR)
+ [3. Configuring the Analysis](#CTA)
+ [4. Executing Snakemake](#EXS)
+ [5. Outputs](#OTPS)
+ [6. Benchmarks](#BENCH)
---------------

# **Taxonomic-Profiling-Sourmash Overview** <a name="PO"></a>

The purpose of this snakemake workflow is to generate a taxonomic profile for metagenome reads.

Each fasta file is decomposed into k-mers and then searched against the provided database(s). Sourmash will find the minimum set of reference genomes that cover the information in the reads, and then use the lineage information from those genomes to build a taxonomic profile.

This pipeline performed favorably in a recent benchmarking study evaluating several methods for taxonomic classification with long reads ([Portik et al. 2022](https://bmcbioinformatics.biomedcentral.com/articles/10.1186/s12859-022-05103-0)), which used mock communities as the ground truth. For HiFi datasets, sourmash outperformed other available long-read classifiers. In mock communities, it detected species down to 0.001% relative abundance, displayed the best recall, and had high precision:

![benchy](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/Image-Profiling-Benchmarks-HiFi.png)


[Back to top](#TOP)

---------------

# **Quick Start** <a name="QS"></a>

This workflow requires [Anaconda](https://docs.anaconda.com/anaconda/)/[Conda](https://docs.conda.io/projects/conda/en/latest/index.html) and [Snakemake](https://snakemake.readthedocs.io/en/stable/) to be installed, and will require ~40-100GB memory and minimal additional disk space per sample (see [Requirements section](#RFR)). All dependencies in the workflow are installed using conda and the environments are activated by snakemake for relevant steps. Snakemake v8+ is required, and the workflows have been tested using v8.25.

- Clone the Taxonomic-Profiling-Sourmash directory.
- Download prepared databases from: [https://sourmash.readthedocs.io/en/latest/databases.html](https://sourmash.readthedocs.io/en/latest/databases.html])
- Specify the full path to each database and corresponding lineages file in `config.yaml`.
- Include all input HiFi fasta files (`SAMPLE.fasta`) in the `inputs/` folder. These can be files or symlinks. 
- Edit sample names in `Sample-Config.yaml` configuration file in `configs/` for your project. 
- Execute snakemake using the general commands below: 
```
snakemake --snakefile Snakefile-sourmash --configfile configs/Sample-Config.yaml --software-deployment-method conda [additional arguments for local/HPC execution]
```
The choice of additional arguments to include depends on where and how you choose to run snakemake. Please refer to the [Executing Snakemake](#EXS) section for more details.

[Back to top](#TOP)

---------------

# **1. Snakemake Contents** <a name="SMC"></a>

To run the workflow, you will need to obtain all contents within the [Taxonomic-Profiling-Sourmash folder](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/Taxonomic-Profiling-Sourmash). The default contents should look like this:

```
Taxonomic-Profiling-Sourmash
│
├── configs/
│	└── Sample-Config.yaml
│
├── envs/
│	└── sourmash.yml
│
├── inputs/
│	└── README.md (this is just a placeholder file, and not required)
│
├── Snakefile-sourmash
│
└── config.yaml
```
The `Snakefile-sourmash` file is the Snakefile for this snakemake workflow. It contains all of the rules of the workflow. 

The `config.yaml` file is the main configuration file used in the snakemake workflow. It contains the main settings that will be used for various programs. 

The `configs/` directory contains an example configuration file for specifying which samples are to be run. It must be referenced in the command line call for snakemake for any samples to be run.

The `inputs/` directory should contain all of the required input files for each sample. In this workflow there must be a `SAMPLE.fasta` file of HiFi reads per sample. These can be the actual files, or symbolic links to the files (for example using `ln -s source_file symbolic_name`). 

Finally, the `envs/` directory contains the `sourmash.yml` file which is needed to install all dependencies through conda. This environment is activated for each step of the workflow. The dependencies are installed from bioconda and conda-forge and include Python3.10 and `sourmash >= 4.5`.

[Back to top](#TOP)

---------------

# **2. Requirements for Running** <a name="RFR"></a>


## Memory and disk space requirements

Running this pipeline using the default settings should require 10-100GB of memory, depending on your reads file size and chosen database. GenBank databases take approximately 40G of disk space and require 40G of memory and minimal additional space is used by intermediate or output files.

## Dependencies

In order to run a snakemake workflow, you will need to have an anaconda or conda installation. Conda is essential because it will be used to install the dependencies within the workflow and setup the correct environments. 

Snakemake will also need to be installed. Snakemake v8+ is now required, and the workflows have been tested using v8.25.

You can install the snakemake environment file in the main directory [snakemake-environment.yaml](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/snakemake-environment.yml) to obtain snakemake v8.25 and the packages required for cluster execution. 
> You can optionally install snakemake 8.25+ via the provided conda environment file via `conda env create -f environment.yml`, and then activate this environment via `conda activate pb-metagenomics-tools` to run the workflows.

Alternatively, instructions for installing snakemake using conda can be found [here](https://snakemake.readthedocs.io/en/stable/getting_started/installation.html). 

## Download sourmash database file(s)

Download prepared databases from [here](https://sourmash.readthedocs.io/en/latest/databases.html]). These databases range from 2G (GTDB representative genomes) to 40G (genbank genomes as of March 2022). Make sure to download the corresponding lineages file (`*csv.gz`) for each database you download.  **The path to these files must be specified in `config.yaml`.** You can alternatively build your own database of sourmash signatures for each.

[Back to top](#TOP)

---------------


# **3. Configuring the Analysis** <a name="CTA"></a>

To configure the analysis, the main configuration file (`config.yaml`) and sample configuration file (`configs/Sample-Config.yaml`) should be edited. 

#### Main configuration file (`config.yaml`)
The main configuration file contains several parameters, each of which is described in the configuration file. 

By default, this workflow runs profiling with k-mer lengths of 31 and 51, but you can modify to choose one or both.

#### Sample configuration file (`configs/Sample-Config.yaml`)
The example sample configuration file is called `Sample-Config.yaml` and is located in the `configs/` directory. Here you should specify the sample names that you wish to include in the analysis. 

For the Taxonomic-Profiling-Sourmash pipeline, all samples specified in the sample configuration file must have a fasta file of HiFi reads (`SAMPLE.fasta`) in the `inputs/` folder. The pipeline can be run for any number of samples. You can also configure the file to only run for a subset of the samples present in the `inputs/` folder. Please note that if the input files do not follow the naming convention (`SAMPLE.fasta`), they will not be recognized by the workflow. You can use the actual files or symlinks to those files, both are compatible with snakemake.

[Back to top](#TOP)

---------------

# **4. Executing Snakemake** <a name="EXS"></a>

Before attempting to run this snakemake analysis, please ensure that the pre-analysis requirements have been satisfied, the analysis has been configured properly (using the general and sample configuration files), and the input files are available in the `inputs/` folder. 

There are several ways to execute the workflow. The easiest way is to run snakemake on HPC using an interactive session. The most efficient way is to use cluster or cloud configuration so that snakemake can schedule and run jobs on HPC or cloud environments. 

## Local execution

Snakemake can be run "locally" (e.g., without cluster configuration). Snakemake will automatically determine how many jobs can be run simultaneously based on the resources specified. This type of snakemake analysis can be run on a local system, but ideally it should be executed using an interactive HPC session (for example, `qrsh` with SGE or the SLURM equivalent).

The workflow must be executed from within the directory containing all the snakemake contents for the Taxonomic-Profiling-Sourmash pipeline. 

### Test workflow
It is a good idea to test the workflow for errors before running it. This can be done with the following command:
```
snakemake -np --snakefile Snakefile-sourmash --configfile configs/Sample-Config.yaml
```

Let's unpack this command:
- `snakemake` calls snakemake.
- `-np` performs a 'dry-run' where the rule compatibilities are tested but they are not executed.
- `--snakefile Snakefile-sourmash` tells snakemake to run this particular snakefile.
- `--configfile configs/Sample-Config.yaml` tells snakemake to include the samples listed in the sample configuration file.

The dry run command should result in a sequence of jobs being displayed on screen. 

### Execute workflow locally
Finally, you can execute the workflow using:
```
snakemake --snakefile Snakefile-sourmash --configfile configs/Sample-Config.yaml -j 48 --software-deployment-method conda
```

There are a couple important arguments that were added here:

- `-j 48` specifies that there are 48 threads available to use. You should change this to match the resources available. If more threads are specified in the configuration file than are available here, snakemake automatically scales them down to this number. Note that since sourmash is single-theaded, this will simply change the number of individual jobs that can be run at a single time. Do be aware of memory requirements (~40-100G for `sourmash gather` step when searching GenBank database).
-  `--software-deployment-method conda` allows conda to install the programs and environments required for each step. This is essential.

Upon execution, the first step will be conda downloading packages and creating the correct environment. After, the jobs should begin running. You will see the progress on screen.


## Cluster Configuration

Executing snakemake on HPC with cluster configuration allows it schedule jobs and run  steps in parallel. This is the most efficient way to run snakemake.

There are several ways to run snakemake on HPC using the executor modules introduced in v8+. Instructions on cluster execution is available for the [slurm executor](https://snakemake.github.io/snakemake-plugin-catalog/plugins/executor/slurm.html) and the [cluster generic executor](https://snakemake.github.io/snakemake-plugin-catalog/plugins/executor/cluster-generic.html). The `cluster generic` syntax is described below, as it is most similar to previous instructions. 

One easy way to run snakemake is to start an interactive session, and execute snakemake with the relevant cluster settings as described in the documentation. In this case, only a few threads are required for the interactive session, since most jobs will be run elsewhere. Snakemake will act as a job scheduler and also run local jobs from this location, until all jobs are complete. This can take a while, so it is best to use a detachable screen with the interactive session. 

 Below is an example of cluster configuration using SLURM:

```
snakemake --snakefile Snakefile-sourmash --configfile configs/Sample-Config.yaml --software-deployment-method conda --executor cluster-generic --cluster-generic-submit-cmd "mkdir -p HPC_logs/{rule} && sbatch --partition=compute9 --nodes=1 --cpus-per-task={threads} --output=HPC_logs/{rule}/{wildcards}.{jobid}.txt" -j 30 --jobname "{rule}.{wildcards}.{jobid}" --latency-wait 60
```

Let's unpack this command:
- `snakemake` calls snakemake.
- `--snakefile Snakefile-hifimags.smk` tells snakemake to run this particular snakefile.
- `--configfile configs/Sample-Config.yaml` tells snakemake to use this sample configuration file in the `configs/` directory. This file can have any name, as long as that name is provided here.
-  `--software-deployment-method conda` this allows conda to install the programs and environments required for each step. It is essential.
- `--executor cluster-generic` indicates which HPC module we are using.
- `--cluster-generic-submit-cmd "mkdir -p HPC_logs/{rule} && sbatch --partition=compute9 --nodes=1 --cpus-per-task={threads} --output=HPC_logs/{rule}/{wildcards}.{jobid}.txt"` are the settings for execution with SLURM. This will make a directory called HPC_logs and populate it with SLURM logs per job. The remaining arguments are pretty typical for sbatch execution, and only the `--pratition` name likely needs to be changed. 
- `-j 30` will tell snakemake to run a maximum of 30 jobs simultaneously on the cluster. You can adjust this as needed.
- `--jobname "{rule}.{wildcards}.{jobid}"` provides convenient names for your snakemake jobs running on the cluster.
- `--latency-wait 60` this is important to include because there may be some delay in file writing between steps, and this prevents errors if files are not immediately found.

Upon the first execution, conda will download packages and create the correct environment. After, the jobs should begin scheduling and running. You can see the progress on screen in the interactive session, and also be able to monitor snakemake jobs running on the cluster. 

**Potential issues with snakemake v8.25**

Note that it might be helpful to include the following flags for HPC execution:

```
--cores=72 --max-threads=72 --resources mem_mb=500000
```

This prevents a known issue where submitted jobs are downscaled to the resources on the head node. 


## Cloud Configuration

For information on how to run snakemake with AWS (Amazon Web Services), Google Cloud Life Sciences, or generic cloud computing, please see the other executor modules available on the snakemake documentation [here](https://snakemake.github.io/snakemake-plugin-catalog/index.html).

[Back to top](#TOP)

---------------

## **5. Outputs** <a name="OTPS"></a>

Successful runs will result in several new directories:

```
Taxonomic-Profiling-sourmash
│
├── configs/
├── envs/
├── inputs/
├── scripts/
├── Snakefile-sourmash
├── config.yaml
│
├── benchmarks/
├── logs/
│
├── output.sourmash-profiling/
│   └── 1-sketch
│   └── 2-gather
│   └── 3-taxprofile
```

- `benchmarks/` contains benchmark information on memory usage and I/O for each rule executed.
- `logs/` contains log files for each rule executed. 
- `1-sketch/` contains the k-mer sketches for each sample. 
- `2-gather/` contains the genome-resolved taxonomic matches 
- `3-taxprofile/` contains the LCA taxonomic profiles built from the genome match information

[Back to top](#TOP)

---------------

# **6. Benchmarks** <a name="BENCH"></a>

![benchy](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/Image-sourmash-benchmark.png)
