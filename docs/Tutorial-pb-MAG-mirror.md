# Tutorial for pb-MAG-mirror <a name="TOP"></a>

## **Table of Contents**

+ [pb-MAG-mirror Overview](#PO)
+ [Quick Start](#QS)
+ [1. Snakemake Contents](#SMC)
+ [2. Requirements for Running](#RFR)
+ [3. Configuring the Analysis](#CTA)
+ [4. Executing Snakemake](#EXS)
+ [5. Outputs](#OTPS)


---------------

# **pb-MAG-mirror Overview** <a name="PO"></a>

pb-MAG-mirror can be used to compare the contig contents of MAGs across two binning methods, identify MAG matches across different categories, and consolidate the MAGs into a non-redundant set. The two binning methods must use the same starting set of contigs. 

The ideal use-case is to compare filtered MAGs obtained using different binning approaches. However, there if the bin sets have not been filtered yet, this workflow allows you to set thresholds for filtering (completeness, contamination, max number of contigs). 

The analysis identifies four main comparison categories (shown below): a) identical bins, b) superset/subset bins, c) unique bins, and d) mixed bins. 

![Categories](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/Image-pb-MAG-mirror-categories.png) 

Identical bins occur when a bin from each method contains the exact same contig set. A subset bin occurs when the contig set of a bin is fully contained in a bin of the alternate method (i.e., the superset bin). We further require that any additional contigs in the superset bin do not occur in any other bin (e.g., any additional contigs present in the superset bin were unique to the superset bin). Lastly, a unique bin occurs when it contains a set of contigs that does not occur in any bin of the alternative method. If a single contig of the set can be found in a bin of the alternative method, the bin cannot be classified as unique. All bins not falling into these categories (identical, subset/superset, unique) are considered mixed, as they contain two or more contigs that occur in two or more bins of the alternative method. For these mixed bins, we perform cross-method pairwise comparisons. We examine the shared contig content of each comparison to identify the best match, which is selected based on the percentage of total shared bases. We consider high-similarity (HS) matches as those with ≥80% shared bases in each bin, medium-similarity (MS) as those with ≥50% shared bases in each bin, and low-similarity (LS) as those with <50% shared bases in each bin. 


Based on the category results, pb-MAG-mirror can be used to consolidate the two bin sets. The default behavior is to include one representative bin for each of the identical bins, all superset bins and unique bins from both sets, and for cross-set mixed matches the bin with the highest completeness score is selected. However, for cross-set mixed matches the bins from one set can be preferentially selected instead.


Outputs include tables with matches, category, and quality information, along with several figures (examples below). 


Figure showing assignment of MAGs to different comparison categories, and MAG quality metrics across comparison categories:

![CatResults](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/Image-pb-MAG-mirror-outputfigs.png)

For explanations of these figures, please see the [5. Outputs](#OTPS) section below.

[Back to top](#TOP)

---------------

# **Quick Start** <a name="QS"></a>

This workflow requires [Anaconda](https://docs.anaconda.com/anaconda/)/[Conda](https://docs.conda.io/projects/conda/en/latest/index.html) and [Snakemake](https://snakemake.readthedocs.io/en/stable/) to be installed, and will require <15GB memory and <1GB temporary disk space (see [Requirements section](#RFR)). All dependencies in the workflow are installed using conda and the environments are activated by snakemake for relevant steps.

- Clone the pb-MAG-mirror directory.
- Download the CheckM2 database and put path in the configuration file. The database file can be downloaded directly from this [link](https://zenodo.org/records/5571251/files/checkm2_database.tar.gz). Alternate instructions can be found [here](https://github.com/chklovski/CheckM2?tab=readme-ov-file#database). 
- Include two directories in the `inputs/` folder. Use the following the naming scheme: `SAMPLE.bins1/`, `SAMPLE.bins2`. The directories must contain all bins/MAGs to be used in the analysis, for which each bin/MAG is represented by an individual fasta file. The fasta files must have the extensions `.fa`, `.fna`, or `.fasta`.
- Edit sample names in `Sample-Config.yaml` configuration file in `configs/` for your project. 
- Check settings in `config.yaml`, and ensure the `tmpdir` argument is set correctly in `config.yaml`. The default is `/scratch`.
- Execute snakemake using the general commands below: 
```
snakemake --snakefile Snakefile-pb-mag-mirror.smk --configfile configs/Sample-Config.yaml --use-conda [additional arguments for local/HPC execution]
```
The choice of additional arguments to include depends on where and how you choose to run snakemake. Please refer to the [4. Executing Snakemake](#EXS) section for more details.

[Back to top](#TOP)

---------------

# **1. Snakemake Contents** <a name="SMC"></a>

To run the workflow, you will need to obtain all contents within the [HiFi-MAG-Pipeline folder](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/HiFi-MAG-Pipeline). The default contents should look like this:

```
pb-MAG-mirror
│
├── configs/
│	└── Sample-Config.yaml
│
├── envs/
│	├── checkm2.yml
│	└── python.yml
│
├── inputs/
│	└── README.md (this is just a placeholder file, and not required)
│
├── scripts/
│	├── Copy-consolidated-bins.py
│	├── Filter-Checkm2-Bins.py
│	├── Perform-bin-comparisons.py
│	├── Plot-Main.py
│	└── Plot-Qualities.py
│
├── Snakefile-pb-mag-mirror.smk
│
└── config.yaml
```
The `Snakefile-pb-mag-mirror.smk` file is the Snakefile for this snakemake workflow. It contains all of the rules of the workflow. 

The `config.yaml` file is the main configuration file used in the snakemake workflow. It contains the main settings that will be used for various programs. 

The `configs/` directory contains an example configuration file for specifying which samples are to be run. The configuration file can be renamed. It must be specified in the command line call for snakemake for any samples to be run.

The `inputs/` directory should contain all of the required input files for each sample. In this workflow there must be two directories in the `inputs/` folder. Use the following the naming scheme: `SAMPLE.bins1/`, `SAMPLE.bins2`. The directories must contain all bins/MAGs to be used in the analysis, for which each bin/MAG is represented by an individual fasta file. The fasta files must have the extensions `.fa`, `.fna`, or `.fasta`.
These can be the actual files, or symbolic links to the files (for example using `ln -s source_file symbolic_name`). An example of this is shown below:

```
pb-MAG-mirror
│
├── inputs/
│	├── SAMPLE.bins1/
│	│		├──	bin23.fa
│	│		├──	bin43.fa
│	│		├──	bin67.fa
│	│		└──	bin96.fa
│	│		
│	└── SAMPLE.bins2/
│			├──	metabat_23.fna
│			├──	metabat_43.fna
│			├──	metabat_67.fna
│			├──	metabat_67.fna
│			├──	metabat_67.fna
│			└──	metabat_96.fna
```

The `scripts/` directory contains a few Python scripts required for the workflow. These are involved with formatting, filtering, plotting, and summarizing. They are called in different steps of the workflow.

Finally, the `envs/` directory contains the several files which are needed to install all dependencies through conda. These environments are activated for each step of the workflow.

[Back to top](#TOP)

---------------

# **2. Requirements for Running** <a name="RFR"></a>

## Memory and disk space requirements

Running certain steps in this pipeline will potentially require ~15GB of memory, and the amount of disk space required is equivalent to the size of the starting bins sets. 

## Dependencies

In order to run a snakemake workflow, you will need to have an anaconda or conda installation. Conda is essential because it will be used to install the dependencies within the workflow and setup the correct environments. 

Snakemake will also need to be installed. Instructions for installing snakemake using conda can be found [here](https://snakemake.readthedocs.io/en/stable/getting_started/installation.html). 

If you intend to generate a graphic for the snakemake workflow graph, you will also need graphviz installed.

## Download required database

Download the CheckM2 database and put path in the configuration file. 

The database file can be downloaded directly from this [link](https://zenodo.org/records/5571251/files/checkm2_database.tar.gz). 

Alternate instructions can be found [here](https://github.com/chklovski/CheckM2?tab=readme-ov-file#database). 

[Back to top](#TOP)

---------------

# **3. Configuring the Analysis** <a name="CTA"></a>

To configure the analysis, the main configuration file (`config.yaml`) and sample configuration file (`configs/Sample-Config.yaml`) should be edited. 

#### Main configuration file (`config.yaml`)
The main configuration file contains several parameters, each of which is described in the configuration file. 

**CheckM2**

Please check that the `tmpdir` argument is set correctly. The default is `/scratch`, which may be available to most users on HPC. This can be changed if `/scratch` is not available, or if you are running snakemake locally. Change it to a valid output directory that can be used to write many large files. This is used in conjunction with the `--tmpdir` flag in CheckM2. 

Please also check that the fasta file extensions for each bin directory are set correctly. Accepted extensions include: `.fa`, `.fna`, or `.fasta`.

**Filtering**

You may wish to change the thresholds for filtering MAGs (if they have not yet been pre-filtered),as the defaults are set to: 
+ `min_completeness`: 50
+ `max_contamination`: 10
+ `max_contigs`: 200

**Consolidation**

Finally, you should check the method for consolidating mixed bins. There are three options available for merging:
+ `unify` - Only select mixed bins which have a consistent match in both pairwise directions, then select the MAG with highest completion score.
+ `bins1` - Select only the mixed bins from the bins1 set.
+ `bins2` - Select only the mixed bins from the bins2 set.


#### Sample configuration file (`configs/Sample-Config.yaml`)
The example sample configuration file is called `Sample-Config.yaml` and is located in the `configs/` directory. Here you should specify the sample names that you wish to include in the analysis. 

All samples specified in the sample configuration file must have two corresponding directories in the `inputs/` folder. These include `SAMPLE.bins1/` and `SAMPLE.bins2`. Here, the `SAMPLE` component is a name included in the sample configuration file. The pipeline can be run for any number of samples. You can also configure the file to only run for a subset of the samples present in the `inputs/` folder. Please note that if the input directories do not follow these naming conventions they will not be recognized by the workflow. You can use the actual files or symlinks to the directories.

[Back to top](#TOP)

---------------

# **4. Executing Snakemake** <a name="EXS"></a>

Before attempting to run this snakemake analysis, please ensure that the pre-analysis requirements have been satisfied, the analysis has been configured properly (using the general and sample configuration files), and the input directories are available in the `inputs/` folder. 

There are several ways to execute the workflow. The easiest way is to run snakemake on HPC using an interactive session. The most efficient way is to use cluster or cloud configuration so that snakemake can schedule and run jobs on HPC or cloud environments. 

## Local execution

**Given the large memory requirements for some programs used in the workflow, execution of this mode is only recommended with interactive HPC sessions.**

Snakemake can be run "locally" (e.g., without cluster configuration). Snakemake will automatically determine how many jobs can be run simultaneously based on the resources specified. This type of snakemake analysis can be run on a local system, but ideally it should be executed using an interactive HPC session (for example, `qrsh` with SGE or the SLURM equivalent).

The workflow must be executed from within the directory containing all the snakemake contents for the HiFi-MAG-Pipeline. 

### Test workflow
It is a good idea to test the workflow for errors before running it. This can be done with the following command:
```
snakemake -np --snakefile Snakefile-pb-mag-mirror.smk --configfile configs/Sample-Config.yaml
```

Let's unpack this command:
- `snakemake` calls snakemake.
- `-np` performs a 'dry-run' where the rule compatibilities are tested but they are not executed.
- `--snakefile Snakefile-pb-mag-mirror.smk` tells snakemake to run this particular snakefile.
- `--configfile configs/Sample-Config.yaml` tells snakemake to include the samples listed in the sample configuration file.

The dry run command should result in the jobs being displayed on screen. 

### Create workflow figure
If there are no errors, you may wish to generate a figure of the directed acyclic graph (the workflow steps). You can do this using the following command:
```
snakemake --dag --snakefile Snakefile-pb-mag-mirror.smk --configfile configs/Sample-Config.yaml | dot -Tsvg > hifimags_analysis.svg
```
Here the `--dag` flag creates an output that is piped to `dot`, and an svg file is created. This will show the workflow visually.

### Execute workflow
Finally, you can execute the workflow using:
```
snakemake --snakefile Snakefile-pb-mag-mirror.smk --configfile configs/Sample-Config.yaml -j 36 --use-conda
```

There are a couple important arguments that were added here:

- `-j 36` specifies that there are 36 threads available to use. You should change this to match the resources available. If more threads are specified in the configuration file than are available here, snakemake automatically scales them down to this number.
-  `--use-conda` allows conda to install the programs and environments required for each step. This is essential.

Upon execution, the first step will be conda downloading packages and creating the correct environment. After, the jobs should begin running. You will see the progress on screen.


## Cluster Configuration

Executing snakemake on HPC with cluster configuration allows it schedule jobs and run  steps in parallel. This is the most efficient way to run snakemake.

There are several ways to run snakemake on HPC. There are limited instructions on cluster execution in the snakemake documentation [here](https://snakemake.readthedocs.io/en/stable/executing/cluster.html).

One easy way to run snakemake is to start an interactive session, and execute snakemake with the relevant cluster settings as described in the documentation. In this case, only a few threads are required for the interactive session, since most jobs will be run elsewhere. Snakemake will act as a job scheduler and also run local jobs from this location, until all jobs are complete. This can take a while, so it is best to use a detachable screen with the interactive session. 

The same general commands are used as with "local" execution, but with some additional arguments to support cluster configuration. Below is an example of cluster configuration using SLURM:

```
snakemake --snakefile Snakefile-pb-mag-mirror.smk --configfile configs/Sample-Config.yaml --use-conda --cluster "sbatch --partition=compute --cpus-per-task={threads}" -j 5 --jobname "{rule}.{wildcards}.{jobid}" --latency-wait 60 
```

Let's unpack this command:
- `snakemake` calls snakemake.
- `--snakefile Snakefile-pb-mag-mirror.smk` tells snakemake to run this particular snakefile.
- `--configfile configs/Sample-Config.yaml` tells snakemake to use this sample configuration file in the `configs/` directory. This file can have any name, as long as that name is provided here.
-  `--use-conda` this allows conda to install the programs and environments required for each step. It is essential.
- `--cluster "sbatch --partition=compute --cpus-per-task={threads}"` are the settings for execution with SLURM, where 'compute' is the name of the machine. The threads argument will be automatically filled based on threads assigned to each rule. Note that the entire section in quotes can be replaced with an SGE equivalent (see below).
- `-j 5` will tell snakemake to run a maximum of 5 jobs simultaneously on the cluster. You can adjust this as needed.
- `--jobname "{rule}.{wildcards}.{jobid}"` provides convenient names for your snakemake jobs running on the cluster.
- `--latency-wait 60` this is important to include because there may be some delay in file writing between steps, and this prevents errors if files are not immediately found.

And here is an example using SGE instead:

```
snakemake --snakefile Snakefile-pb-mag-mirror.smk --configfile configs/Sample-Config.yaml --use-conda --cluster "qsub -q default -pe smp {threads} -V -cwd -S /bin/bash" -j 5 --jobname "{rule}.{wildcards}.{jobid}" --latency-wait 60 
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
├── Snakefile-pb-mag-mirror.smk
├── config.yaml
│
├── benchmarks/
├── logs/
│
├── 1-checkm2/
├── 2-comparisons/
└── 3-summary/
```

- `benchmarks/` contains benchmark information on memory usage and I/O for each rule executed.
- `logs/` contains log files for each rule executed.
- `1-checkm2/` contains the outputs from CheckM2 for each input directory per sample.
- `2-comparisons/` contains the detailed results for each specific category, a summary across categories (per bin directory), and outputs for all pairwise-comparisons of mixed bins.
- `3-summary/` contains summary tables from the analysis (detailed metadata and simple counts) along with multiple figures.

Within `3-summary/`, there will be a folder for each sample. Within a sample folder there are several items:

+ `SAMPLE.consolidated.comparisons.txt`: detailed table with metadata summarizing matches.

![DetailedTable](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/Image-pb-MAG-mirror-table-detailed.png) 

+ `SAMPLE.comparison_categories.table.txt`: Simple table with counts per category.

![DetailedTable](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/Image-pb-MAG-mirror-table-counts.png)


+ `SAMPLE.comparison_categories.completeness.pdf`: Percent completeness scores across comparison categories, per binning method. 

![Fig1](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/Image-pb-MAG-mirror-fig-completeness.png)

+ `SAMPLE.comparison_categories.contamination.pdf`: Percent contamination scores across comparison categories, per binning method. 

![Fig2](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/Image-pb-MAG-mirror-fig-contamination.png.png)

+ `SAMPLE.comparison_categories.contigs.pdf`: Number of contigs per MAG across comparison categories, per binning method. 

![Fig3](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/Image-pb-MAG-mirror-fig-contigs.png)

+ `SAMPLE.comparison_categories.sizes.pdf`: Genome sizes across comparison categories, per binning method. 

![Fig4](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/Image-pb-MAG-mirror-fig-sizes.png)

+ `SAMPLE.comparison_categories.summary.pdf`: Stacked barplot showing assignments of MAGs to different categories. 

![Fig5](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/Image-pb-MAG-mirror-fig-summary.png)

[Back to top](#TOP)

```
