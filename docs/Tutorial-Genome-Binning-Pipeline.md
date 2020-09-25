# Genome-Binning-Pipeline <a name="TOP"></a>

## **Table of Contents**

+ [1. Genome-Binning-Pipeline Overview](#PO)
+ [2. Snakemake Contents](#SMC)
+ [3. Requirements for Running](#RFR)
+ [4. Configuring the Analysis](#CTA)
+ [5. Executing Snakemake](#EXS)
+ [6. Usage for Main Programs](#MPU)


---------------

# **1. Genome-Binning-Pipeline Overview** <a name="PO"></a>

The purpose of this snakemake workflow is to obtain high-quality metagenome-assembled genomes (MAGs) from previously generated assemblies. The general steps of the Genome-Binning-Pipeline are shown below:

![GBSteps](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/Genome-Binning-Steps.png)

HiFi reads are mapped to contigs using minimap2 to generate BAM files. The BAM files are used to obtain coverage estimates for the contigs. The coverages and contigs are used as inputs to MetaBAT2, which constructs the genome bins. CheckM is used to assess the quality of the resulting genome bins. It provides measures of genome completeness, contamination, and other useful metrics. A custom filtering step is used to eliminate genome bins with <70% genome completeness, >10% genome contamination, and >10 contigs per bin. These are default values, and they can be changed. The genome bins which pass the default thresholds can be considered high-quality MAGs. Finally, the Genome Taxonomy Database Toolkit (GTDB-Tk) is used to identify the closest reference match to each high-quality MAG. It will report the taxonomy of the closest reference. This does not guarantee the identity of the MAG, but serves as a starting point for understanding which genus, species, or strain it is most closely related to.

[Back to top](#TOP)

---------------

# **2. Snakemake Contents** <a name="SMC"></a>

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

# **3. Requirements for Running** <a name="RFR"></a>

There are a few steps that must be completed prior to running the snakemake workflow.

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

# **4. Configuring the Analysis** <a name="CTA"></a>

To configure the analysis, the main configuration file (`config.yaml`) and sample configuration file (must be in the `configs/` directory) can be edited. 

The main configuration file contains several parameters, each of which is described in the configuration file. Depending on your system resources, you may choose to change the number of threads used in the minimap, metabat, checkm, or gtdbtk settings. However, **you must specify the full paths to the databases that were downloaded for checkm and gtdbtk**. In the configuration file, this is the `datapath` parameter in the checkm settings, and the `gtdbtk_data` parameter in the gtdbtk settings. See above section for where to obtain these databases.

The example sample configuration file is called `Sample-Config-Example.yaml` and is located in the `configs/` directory. You can rename this file if desired. Here you should specify the sample names that you wish to include in the analysis. 

For the Genome-Binning-Pipeline, all samples specified in the sample configuration file must have two corresponding files in the `inputs/` folder. These include the fasta file of HiFi reads (`SAMPLE.fasta`) and the assembled contigs (`SAMPLE.contig.fasta`). Here, the `SAMPLE` component is a name included in the sample configuration file. The pipeline can be run for any number of samples. You can also configure the file to only run some of the samples present in the `inputs/` folder. Please note that if the input files do not follow these naming conventions (`SAMPLE.fasta`, `SAMPLE.contig.fasta`), they will not be recognized by the workflow. 

[Back to top](#TOP)

---------------

# **5. Executing Snakemake** <a name="EXS"></a>

Before attempting to run this snakemake analysis, please ensure that the pre-analysis requirements have been satisfied, the analysis has been configured properly (using the general and sample configuration files), and the input files are available in the `inputs/` folder. 

There are several ways to execute the workflow.

## Local execution

Snakemake can be run locally (e.g., without cluster configuration). Snakemake will automatically determine how many jobs can be run simultaneously based on the resources specified. 

The workflow should be executed from within the directory containing all the snakemake contents for the genome-binning-pipeline. 

### Test workflow
It is a good idea to test the workflow for errors before running it. This can be done with the following command:
```
snakemake -np --snakefile Snakefile-genomebinning -j 48 --use-conda
```

Let's unpack this command:
- `snakemake` calls snakemake.
- `-np` performs a 'dry-run' where the rule compatibilities are tested but they are not executed.
- `--snakefile Snakefile-genomebinning` tells snakemake to run this particular snakefile.
- `-j 48` specifies that there are 48 threads available to use. If more threads are specified in the configuration file than are available here, snakemake automatically scales them down.
-  `--use-conda` allows conda to install the programs and environments required for each step. It is essential.

The dry run command should result in the jobs being displayed on screen. 

### Create workflow figure
If there are no errors, you may wish to generate a figure of the directed acyclic graph (the workflow steps). You can do this using the following command:
```
snakemake --dag --snakefile Snakefile-genomebinning -j 48 --use-conda | dot -Tsvg > genome-binning_analysis.svg
```
Here the `--dag` flag creates an output that is piped to `dot`, and an svg file called `genome-binning_analysis.svg` is created. This will show the workflow visually.

### Execute workflow
Finally, you can execute the workflow using:
```
snakemake --snakefile Snakefile-genomebinning -j 48 --use-conda
```

The jobs should begin scheduling and running. You can see the progress on screen.

This type of snakemake analysis can be run on a local system, or it can be executed the same way using an HPC interactive session. For example, `qrsh -q default -pe smp 48` can be used to start an interactive session with 48 threads (replacing `default` with the name of your machine). If the snakemake directory and databases are set up on the cluster, snakemake can be executed the same way. Navigate to the directory and use the same commands as above. You may need to load anaconda, snakemake, and graphviz before running the workflow, depending on your system setup. You may also want to use a detachable screen so the analysis is not interrupted.


## HPC execution

Executing snakemake on HPC allows it schedule jobs and run steps in parallel. This is the preferred method.

There are several ways to run snakemake on HPC. There are limited instructions on cluster execution in the snakemake documentation [here](https://snakemake.readthedocs.io/en/stable/executing/cluster.html), so an example of execution are shown below.

### Executing with an interactive session

One easy way to run snakemake is to start an interactive session, and execute snakemake with the relevant cluster settings. Snakemake will act as a job scheduler and also run local jobs from this location, until all jobs are complete. This can take a while, so it is best to use a detachable screen with the interactive session. 

Here is an example (based on SGE configuration) of starting an interactive session and preparing to run snakemake. This assumes you are already logged in:

```
# use a detachable screen
screen -S gbp

# start the interactive session
# use four slots for running the local jobs
# instead of 'default', use the name of your machine
qrsh -q default -pe smp 4

# navigate to the snakemake directory
cd SOME/PATH/TO/GENOMEBINNING

# you may need to load anaconda, snakemake, and graphviz depending on your setup
module load anaconda
module load snakemake
module load graphviz
```
Now we are in the genome-binning snakemake directory, with everything ready.

## Test workflow
It is best to test for any issues in the workflow before executing it. We can do this using the `-np` flag.
```
snakemake -np --snakefile Snakefile-genomebinning --cluster "qsub -q default -pe smp {threads} -V -cwd -S /bin/bash -o HPC_logs/ -e HPC_logs/" -j 5 --jobname "{rule}.{wildcards}.{jobid}" --configfile configs/Twoplex.yaml --latency-wait 60 --use-conda 
```

Let's unpack this command:
- `snakemake` calls snakemake.
- `-np` performs a 'dry-run' where the rule compatibilities are tested but they are not executed.
- `--snakefile Snakefile-genomebinning` tells snakemake to run this particular snakefile.
- `--cluster "qsub -q default -pe smp {threads} -V -cwd -S /bin/bash"` are the settings for cluster execution. Replace 'default' with the name of your machine.
- `-j 5` will tell snakemake to run a maximum of 5 jobs simultaneously on the cluster. You can adjust this as needed.
- `--jobname "{rule}.{wildcards}.{jobid}"` provides convenient names for your snakemake jobs running on the cluster.
- `--configfile configs/Sample-Config.yaml` tells snakemake to use this sample configuration file in the `configs/` directory. This file can have any name, as long as that name is provided here.
- `--latency-wait 60` this is important to include because there may be some delay in file writing between steps, this prevents errors if files are not immediately found.
-  `--use-conda` this allows conda to install the programs and environments required for each step. It is essential.

The dry run command should result in the jobs being displayed on screen. 

### Create workflow figure
If there are no errors, you may wish to generate a figure of the directed acyclic graph (the workflow steps). You can do this using the following command:
```
snakemake --dag --snakefile Snakefile-genomebinning --cluster "qsub -q default -pe smp {threads} -V -cwd -S /bin/bash -o HPC_logs/ -e HPC_logs/" -j 5 --jobname "{rule}.{wildcards}.{jobid}" --configfile configs/Twoplex.yaml --latency-wait 60 --use-conda | dot -Tsvg > genome-binning_analysis.svg
```
Here the `--dag` flag creates an output that is piped to `dot`, and an svg file called `genome-binning_analysis.svg` is created. This will show the workflow visually.

### Execute workflow
Finally, you can execute the workflow using:
```
snakemake --snakefile Snakefile-genomebinning --cluster "qsub -q default -pe smp {threads} -V -cwd -S /bin/bash -o HPC_logs/ -e HPC_logs/" -j 5 --jobname "{rule}.{wildcards}.{jobid}" --configfile configs/Twoplex.yaml --latency-wait 60 --use-conda
```
Again, you will want to replace 'default' in the cluster options with the name of your machine.

The jobs should begin scheduling and running. You can see the progress on screen in the interactive session, and also see the snakemake jobs running on the cluster using `qstat`.


[Back to top](#TOP)

---------------


## **6. Usage for Main Programs** <a name="MPU"></a>

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
