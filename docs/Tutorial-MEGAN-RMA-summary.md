# Tutorial for MEGAN-RMA-summary <a name="TOP"></a>

## **Table of Contents**

+ [MEGAN-RMA-summary Overview](#PO)
+ [Quick Start](#QS)
+ [1. Snakemake Contents](#SMC)
+ [2. Requirements for Running](#RFR)
+ [3. Configuring the Analysis](#CTA)
+ [4. Executing Snakemake](#EXS)
+ [5. Outputs](#OTPS)
+ [6. Usage Details for Main Programs](#UDMP)


---------------

# **MEGAN-RMA-summary Overview** <a name="PO"></a>

The purpose of this snakemake workflow is to summarize the information contained in long-read RMA format files for MEGAN6. These RMA files were previously created from alignments of HiFi data to nucleotide or protein databases. 

This workflow is intended to be used after running the [Taxonomic-Functional-Profiling-Protein](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/Taxonomic-Functional-Profiling-Protein) pipeline or the [Taxonomic-Profiling-Nucleotide](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/Taxonomic-Profiling-Nucleotide) pipeline. To work properly, these RMA files must should be created using the following settings in `sam2rma`: `-lg -alg longReads -ram readCount`. These are the default settings for both of the above pipelines. 

For protein RMA files, this workflow will output absolute and normalized read counts of the EC, EGGNOG, INTERPRO2GO, and SEED functional classes across all samples, along with read counts of the NCBI (full database and bacteria-only) and GTDB taxonomy classes across samples. A summary file and several plots will be created showing the number and percentage of reads assigned to functional and taxonomic databases, the total classes represented per database, and average annotations per read. A visual depiction of the protein-RMA workflow is shown below:

![rmaprotein](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/MEGAN-RMA-summary-protein.png)


For nucleotide RMA files, this workflow will output absolute and normalized read counts of the NCBI taxonomy classes across samples. A summary file and plots will be created showing the number of reads assigned to the NCBI taxonomic database and the total NCBI classes represented. A visual depiction of the nucleotide-RMA workflow is shown below:

![rmanucleotide](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/MEGAN-RMA-summary-nucleotide-fix.png)


[Back to top](#TOP)

---------------

# **Quick Start** <a name="QS"></a>

This workflow requires [Anaconda](https://docs.anaconda.com/anaconda/)/[Conda](https://docs.conda.io/projects/conda/en/latest/index.html) and [Snakemake](https://snakemake.readthedocs.io/en/stable/) to be installed, and will require <5GB memory and <100MB disk space (see [Requirements section](#RFR)). All dependencies in the workflow are installed using conda and the environments are activated by snakemake for relevant steps. Snakemake v5+ is required, and the workflows have been tested using v5.19+.

- Clone the MEGAN-RMA-summary directory.
- Download MEGAN6 community edition from the [MEGAN download page](https://software-ab.informatik.uni-tuebingen.de/download/megan6/welcome.html) to obtain `rma2info`. **Ensure you have at least version 6.19.+**
- Include all input RMA files (`SAMPLE.protein.readCount.rma` or `SAMPLE.nucleotide.readCount.rma`) in the `inputs/` folder. These can be files or symlinks. 
- Edit the required `Sample-Read-Counts.txt` text file in the `inputs/` folder. This is a two column space-delimited text file, with the sample name in column one and the number of HiFi reads of that sample in column two. 
- Edit sample names in either the `Sample-Config-protein.yaml` or `Sample-Config-nucleotide.yaml` configuration file in `configs/` for your project. 
- Specify the full path to `rma2info` in `config.yaml`.
- Execute snakemake using the general commands below.

For protein RMA files: 
```
snakemake --snakefile Snakefile-summarizeProteinRMA --configfile configs/Sample-Config-protein.yaml --use-conda [additional arguments for local/HPC execution]
```

For nucleotide RMA files: 
```
snakemake --snakefile Snakefile-summarizeNucleotideRMA --configfile configs/Sample-Config-nucleotide.yaml --use-conda [additional arguments for local/HPC execution]
```

The choice of additional arguments to include depends on where and how you choose to run snakemake. Please refer to the [Executing Snakemake](#EXS) section for more details.

[Back to top](#TOP)

---------------

# **1. Snakemake Contents** <a name="SMC"></a>

To run the workflow, you will need to obtain all contents within the [MEGAN-RMA-summary folder](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/MEGAN-RMA-summary). The default contents should look like this:

```
MEGAN-RMA-summary
│
├── configs/
│   ├── Sample-Config-nucleotide.yaml
│	└── Sample-Config-protein.yaml
│
├── envs/
│	└── general.yml
│
├── inputs/
│	└── Sample-Read-Counts.txt
│
├── scripts/
│   ├── RMA-class-join.py
│   ├── RMA-Summarizer-nuc.py
│   ├── RMA-Summarizer-prot.py
│	└── RMA-taxonomy-join.py
│
├── Snakefile-summarizeNucleotideRMA
├── Snakefile-summarizeProteinRMA
│
└── config.yaml
```
The `Snakefile-summarizeNucleotideRMA` file is the Snakefile for the nucleotide RMA version of this snakemake workflow, and the `Snakefile-summarizeProteinRMA` file is the Snakefile for the protein RMA version. Each contains all of the rules of the respective workflow. 

The `config.yaml` file is the main configuration file used for both snakemake workflows. It contains the main settings that will be used. 

The `configs/` directory contains two example configuration files for specifying which samples are to be run. It must be referenced in the command line call for snakemake for any samples to be run.

The `inputs/` directory should contain all of the required input files for each sample. In this workflow there must be an RMA file per sample. There must also be a `Sample-Reads-Counts.txt` file present. These can be the actual files, or symbolic links to the files (for example using `ln -s source_file symbolic_name`). 

The `scripts/` directory contains several Python scripts required to run the workflows.

Finally, the `envs/` directory contains the `general.yml` file which is needed to install all dependencies through conda. This environment is activated for the steps of the workflow. The dependencies are installed from bioconda and conda-forge and include several packages for Python3.

[Back to top](#TOP)

---------------

# **2. Requirements for Running** <a name="RFR"></a>


## Memory and disk space requirements

Running this pipeline using the default settings should require <5GB of memory, and less than 100MB disk space. 

## Dependencies

In order to run a snakemake workflow, you will need to have an anaconda or conda installation. Conda is essential because it will be used to install the dependencies within the workflow and setup the correct environments. 

Snakemake will also need to be installed. Instructions for installing snakemake using conda can be found [here](https://snakemake.readthedocs.io/en/stable/getting_started/installation.html). Snakemake v5+ is required, and the workflows have been tested using v5.19+.

If you intend to generate a graphic for the snakemake workflow graph, you will also need graphviz installed.

## Download MEGAN6

MEGAN6 community edition should be downloaded from the [MEGAN download page](https://software-ab.informatik.uni-tuebingen.de/download/megan6/welcome.html). The `rma2info` binary is required for this pipeline. The `rma2info` binary should be present in the `tools` bin distributed with MEGAN. **The full path to `rma2info` must be specified in `config.yaml`.**


[Back to top](#TOP)

---------------

# **3. Configuring the Analysis** <a name="CTA"></a>

To configure the analysis, the main configuration file (`config.yaml`) and sample configuration file (`configs/Sample-Config-nucleotide.yaml` or `configs/Sample-Config-protein.yaml`) should be edited. 

#### Main configuration file (`config.yaml`)
The main configuration file allows you to specify the full path to the `rma2info` binary, the number of threads to use for `rma2info`, and the number of threads for the final summary script. **The path to `rma2info` must be provided.** 

#### Sample configuration files
The example sample configuration files are called `Sample-Config-nucleotide.yaml` and `Sample-Config-protein.yaml`. They are located in the `configs/` directory. Here you should specify the sample names that you wish to include in the analysis. 

The `samplenames` argument is where to provide the names of samples. The `rma: fill: ` argument is used to specify the text between the sample name and the `.rma` file extension. For example, the default naming scheme from the [Taxonomic-Functional-Profiling-Protein](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/Taxonomic-Functional-Profiling-Protein) pipeline is `SAMPLE.protein.readCount.rma`. If the name of the rma file to include is `FP103.protein.readCount.rma`, then entering `"FP103"` under the `samplenames` argument is sufficient. If the rma file is called `FP103.custom.rma`, this will also require changing `rma: fill: ` from `".protein.readCount"` to `"custom"`. If the rma is called `FP103.rma`, then this will require changing `rma: fill: ` from `".protein.readCount"` to `""`.

Finally, the `Sample-Read-Counts.txt` file must be edited to include information for the samples to be run. This two column file contains a sample name in column one and the number of HiFi reads in column two. The sample names here should be identical to what is provided under `samplenames` in the sample config file. Using the above example of an rma file called `FP103.protein.readCount.rma`, this is an acceptable read counts file:
```
FP103 2181367
```


[Back to top](#TOP)

---------------

# **4. Executing Snakemake** <a name="EXS"></a>

Before attempting to run this snakemake analysis, please ensure that the pre-analysis requirements have been satisfied, the analysis has been configured properly (using the general and sample configuration files), and the input files (rma files and read-count file) are available in the `inputs/` folder. 

There are several ways to execute the workflow. The easiest way is to run snakemake on HPC using an interactive session. The most efficient way is to use cluster or cloud configuration so that snakemake can schedule and run jobs on HPC or cloud environments. 

## Local execution

Snakemake can be run "locally" (e.g., without cluster configuration). Snakemake will automatically determine how many jobs can be run simultaneously based on the resources specified. This type of snakemake analysis can be run on a local system, but ideally it should be executed using an interactive HPC session (for example, `qrsh` with SGE or the SLURM equivalent).

The workflow must be executed from within the directory containing all the snakemake contents for the Taxonomic-Functional-Profiling-Protein pipeline. 

### Test workflow
It is a good idea to test the workflow for errors before running it. This can be done with the following commands.

Nucleotide RMA version:
```
snakemake -np --snakefile Snakefile-summarizeNucleotideRMA --configfile configs/Sample-Config-nucleotide.yaml
```

Protein RMA version:
```
snakemake -np --snakefile Snakefile-summarizeProteinRMA --configfile configs/Sample-Config-protein.yaml
```

Let's unpack this command:
- `snakemake` calls snakemake.
- `-np` performs a 'dry-run' where the rule compatibilities are tested but they are not executed.
- `--snakefile Snakefile-summarizeNucleotideRMA` or `--snakefile Snakefile-summarizeProteinRMA` tells snakemake to run the particular snakefile.
- `--configfile configs/Sample-Config-nucleotide.yaml` or `--configfile configs/Sample-Config-protein.yaml` tells snakemake to include the samples listed in the sample configuration file.

The dry run command should result in a sequence of jobs being displayed on screen. 

### Create workflow figure
If there are no errors, you may wish to generate a figure of the directed acyclic graph (the workflow steps). You can do this using the following commands.

Nucleotide rma version:
```
snakemake --dag --snakefile Snakefile-summarizeNucleotideRMA --configfile configs/Sample-Config-nucleotide.yaml | dot -Tsvg > nuc-RMA-Summary.svg
```

Protein rma version:
```
snakemake --dag --snakefile Snakefile-summarizeProteinRMA --configfile configs/Sample-Config-protein.yaml | dot -Tsvg > prot-RMA-Summary.svg
```

Here the `--dag` flag creates an output that is piped to `dot`, and an svg file called `genome-binning_analysis.svg` is created. This will show the workflow visually.

### Execute workflow
Finally, you can execute the workflow using the following commands.

Nucleotide RMA version:
```
snakemake --snakefile Snakefile-summarizeNucleotideRMA --configfile configs/Sample-Config-nucleotide.yaml -j 48 --use-conda
```

Protein RMA version:
```
snakemake --snakefile Snakefile-summarizeProteinRMA --configfile configs/Sample-Config-protein.yaml -j 48 --use-conda
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


Nucleotide RMA version:
```
snakemake --snakefile Snakefile-summarizeNucleotideRMA --configfile configs/Sample-Config-nucleotide.yaml --use-conda --cluster "qsub -q default -pe smp {threads} -V -cwd -S /bin/bash" -j 5 --jobname "{rule}.{wildcards}.{jobid}" --latency-wait 60 
```

Protein RMA version:
```
snakemake --snakefile Snakefile-summarizeProteinRMA --configfile configs/Sample-Config-protein.yaml --use-conda --cluster "qsub -q default -pe smp {threads} -V -cwd -S /bin/bash" -j 5 --jobname "{rule}.{wildcards}.{jobid}" --latency-wait 60 
```

Let's unpack this command:
- `snakemake` calls snakemake.
- `--snakefile Snakefile-summarizeNucleotideRMA` or `--snakefile Snakefile-summarizeProteinRMA` tells snakemake to run this particular snakefile.
- `--configfile configs/Sample-Config-nucleotide.yaml` or `--configfile configs/Sample-Config-protein.yaml` tells snakemake to use this sample configuration file in the `configs/` directory. This file can have any name, as long as that name is provided here.
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
MEGAN-RMA-summary
│
├── configs/
├── envs/
├── inputs/
├── scripts/
├── Snakefile-summarizeNucleotideRMA
├── Snakefile-summarizeProteinRMA
├── config.yaml
│
├── benchmarks/
├── logs/
│
├── 1-r2c/
│
├── 2-c2c/
│
└── 3-summaries/
```

- `benchmarks/` contains benchmark information on memory usage and I/O for each rule executed.
- `logs/` contains log files for each rule executed. 
- `1-r2c/` holds the per-sample read assignment files for each database. For protein RMA, this includes EC, EGGNOG, GTDB, INTERPRO2GO, NCBI (full and bacteria-only), and SEED. For nucleotide RMA, this will only include NCBI reads. These files are temporary and will be deleted before completion if no errors occur.
- `2-c2c/` holds the per-sample class count files for each database. For protein RMA, this includes EC, EGGNOG, GTDB, INTERPRO2GO, NCBI (full and bacteria-only), and SEED class counts. For nucleotide RMA, this will only include NCBI class counts.
- `3-summaries/` contains combined counts files for each database which include all samples. These are present as absolute counts, and normalized counts (determined by the sample with the least number of HiFi reads). **These are the main files of interest.**


### Outputs from the Protein RMA version:

Upon successful completion, the following main output files will be available in the `3-summaries/` folder:

```
3-summaries/
│
├── Absolute.EC.counts.prot.txt
├── Absolute.EGGNOG.counts.prot.txt
├── Absolute.GTDB.counts.prot.txt
├── Absolute.INTERPRO2GO.counts.prot.txt
├── Absolute.NCBI.counts.prot.txt
├── Absolute.NCBIbac.counts.prot.txt
├── Absolute.SEED.counts.prot.txt
├── Normalized.EC.counts.prot.txt
├── Normalized.EGGNOG.counts.prot.txt
├── Normalized.GTDB.counts.prot.txt
├── Normalized.INTERPRO2GO.counts.prot.txt
├── Normalized.NCBI.counts.prot.txt
├── Normalized.NCBIbac.counts.prot.txt
├── Normalized.SEED.counts.prot.txt
├── Plots-Samples/
├── Plots-Summaries/
│   ├── SummaryPlot-Functional_Classes_Assigned.prot.pdf
│   ├── SummaryPlot-Functional_Percent_Reads_Assigned.prot.pdf
│   ├── SummaryPlot-Functional_Total_Reads_Assigned.prot.pdf
│   ├── SummaryPlot-Taxonomic_Classes_Assigned.prot.pdf
│   ├── SummaryPlot-Taxonomic_Percent_Reads_Assigned.prot.pdf
│	└── SummaryPlot-Taxonomic_Total_Reads_Assigned.prot.pdf
└── RMA-Full-Summary.prot.txt
```

The absolute read counts and normalized read counts are summarized for each functional database (EC, EGGNOG, INTERPRO2GO, and SEED) and taxonomic database (GTDB, NCBI, NCBI bacteria only). For normalization, counts are normalized to the smallest number of reads found in the sample set. The count file for NCBI classes contains an additional column containing an abbreviation that indicates the taxonomic rank of the class (Kingdom = K, Genus = G, etc.).

Within the `Plots-Samples/` folder, there are histograms showing the number of annotations per read per functional database per sample. 

Within the `Plots-Summaries/` folder are figures showing the number of classes found, the percent of reads assigned, and total reads assigned to the functional and taxonomic databases.

Finally, the `RMA-Full-Summary.prot.txt` contains a detailed summary of all of this information. Here is an example of the contents of this file:
```
Category	Database	FP103	HL103	TD324
Total reads assigned	Combined_Functional	964,533	656,271	1,327,626
Total reads assigned	EC	496,449	304,421	490,897
Total reads assigned	EGGNOG	693,518	468,010	857,796
Total reads assigned	INTERPRO2GO	736,706	491,967	847,996
Total reads assigned	SEED	715,636	486,654	1,030,114
Total reads assigned	Combined_Taxonomic	1,063,364	733,291	1,590,226
Total reads assigned	GTDB	1,048,622	723,418	1,565,263
Total reads assigned	NCBI	1,060,129	731,385	1,576,219
Total reads assigned	NCBIbac	1,058,176	728,429	1,564,859
Percent reads assigned	Combined_Functional	90.5	89.2	82.9
Percent reads assigned	EC	46.6	41.4	30.6
Percent reads assigned	EGGNOG	65.1	63.6	53.5
Percent reads assigned	INTERPRO2GO	69.1	66.9	52.9
Percent reads assigned	SEED	67.1	66.1	64.3
Percent reads assigned	Combined_Taxonomic	99.8	99.7	99.3
Percent reads assigned	GTDB	98.4	98.3	97.7
Percent reads assigned	NCBI	99.5	99.4	98.4
Percent reads assigned	NCBIbac	98.9	99.1	97.6
Number of unique classes	EC	1,676	1,652	1,499
Number of unique classes	EGGNOG	4,087	4,081	3,939
Number of unique classes	INTERPRO2GO	13,184	12,836	12,949
Number of unique classes	SEED	596	583	572
Number of unique classes	GTDB	188	190	235
Number of unique classes	NCBI	117	159	147
Number of unique classes	NCBIbac	110	153	141
Total assignments to classes	EC	776,380	466,575	732,219
Total assignments to classes	EGGNOG	1,244,316	833,497	1,479,322
Total assignments to classes	INTERPRO2GO	2,941,071	1,904,750	3,304,754
Total assignments to classes	SEED	1,190,914	805,433	1,697,989
Total assignments to classes	GTDB	1,048,622	723,418	1,565,263
Total assignments to classes	NCBI	1,060,129	731,385	1,576,219
Total assignments to classes	NCBIbac	1,058,176	728,429	1,564,859
Average annotations per read	EC	2.1	2	1.9
Average annotations per read	EGGNOG	3	3	2.8
Average annotations per read	INTERPRO2GO	3.9	4	3.8
Average annotations per read	SEED	2.2	2.1	2.1
```


### Outputs from the Nucleotide RMA version:

Upon successful completion, the following main output files will be available in the `3-summaries/` folder:

```
3-summaries/
│
├── Absolute.NCBI.counts.nuc.txt
├── Normalized.NCBI.counts.nuc.txt
├── Plots-Summaries/
│   ├── SummaryPlot-Taxonomic_Classes_Assigned.nuc.pdf
│   ├── SummaryPlot-Taxonomic_Percent_Reads_Assigned.nuc.pdf
│	└── SummaryPlot-Taxonomic_Total_Reads_Assigned.nuc.pdf
└── RMA-Full-Summary.nuc.txt
```

The absolute read counts and normalized read counts are summarized for the NCBI taxonomic database. For normalization, counts are normalized to the smallest number of reads found in the sample set. The count file for NCBI classes contains an additional column containing an abbreviation that indicates the taxonomic rank of the class (Kingdom = K, Genus = G, etc.).

Within the `Plots-Summaries/` folder are figures showing the number of classes found, the percent of reads assigned, and total reads assigned to the NCBI taxonomic database.

Finally, the `RMA-Full-Summary.prot.txt` contains a detailed summary of all of this information. Here is an example of the contents of this file:
```
Category	Database	FP103	HL103	TD324
Total reads assigned	NCBI	967,057	651,956	1,331,839
Percent reads assigned	NCBI	90.7	88.6	83.1
Number of classes	NCBI	167	184	175
```

[Back to top](#TOP)

---------------

## **6. Usage Details for Main Programs** <a name="UDMP"></a>

In this section, additional details are provided for the main programs used in the workflow. The commands to call these programs are provided here for quick reference. Curly braces are sections filled automatically by snakemake. For additional details on other steps, please refer to the relevant Snakefile.

### rma2info

The `rma2info` program is run in two different ways: 1) to obtain all reads assigned to each class per database, and 2) to obtain all class counts per database. 

To obtain the lists of all classes and corresponding read names assigned to those classes, the following command is used:

```
rma2info -i {input.rma} -o {output.name} -r2c {database} &> {log}
```

The database argument can include: `EC`, `EGGNOG`, `INTERPRO2GO`, `SEED`, `Taxonomy` (for NCBI), and `GTDB`. The `-n` flag can also be included for `Taxonomy` and `GTDB` to include taxon names rather than a numerical code for the class. 


To obtain all class counts per database, the following command is used:

```
rma2info -i {input.rma} -o {output.name} -c2c {database} &> {log}
```

The database argument can include: `EC`, `EGGNOG`, `INTERPRO2GO`, `SEED`, `Taxonomy` (for NCBI), and `GTDB`. The `-p` flag is used with `EC`, `EGGNOG`, `INTERPRO2GO`, and `SEED` to include the full name of the functional classes, rather than numeric codes. The `-n` flag is used with `Taxonomy` and `GTDB` to include taxon names rather than a numerical code for the class. 

To include the taxonomic rank of the class for NCBI as an additional column, the following can be used:
```
rma2info -i {input.rma} -o {output.name} -c2c Taxonomy -n -r &> {log}
```


[Back to top](#TOP)

---------------
