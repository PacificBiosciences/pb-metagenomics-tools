# Tutorial for Taxonomic-Profiling-Diamond-Megan <a name="TOP"></a>

## **Table of Contents**

+ [Taxonomic-Profiling-Diamond-Megan Overview](#PO)
+ [Quick Start](#QS)
+ [1. Snakemake Contents](#SMC)
+ [2. Requirements for Running](#RFR)
+ [3. Configuring the Analysis](#CTA)
+ [4. Executing Snakemake](#EXS)
+ [5. Outputs](#OTPS)
+ [6. Usage Details for Main Programs](#UDMP)


---------------

# **Taxonomic-Profiling-Diamond-Megan Overview** <a name="PO"></a>

The purpose of this snakemake workflow is to perform translation alignment of HiFi reads to a protein database, and summarize the resulting alignments using MEGAN-LR. This allows interactive taxonomic and functional analyses to be performed across samples. 

This workflow will output absolute read counts and read-based classifications of the EC, EGGNOG, INTERPRO2GO, and SEED functional classes across all samples, along with read counts and read-based classifications of the NCBI and GTDB taxonomy classes. The NCBI taxonomic counts are now also provided in kraken report (kreport) and metaphlan (mpa) output formats. The KEGG annotations can be obtained by using MEGAN-UE. 

The general steps of the Taxonomic-Profiling-Diamond-Megan pipeline are shown below:

![GBSteps](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/Image-Taxonomic-Profiling-Diamond-Megan.png)

This pipeline performed favorably in a recent benchmarking study evaluating several methods for taxonomic classification with long reads ([Portik et al. 2022](https://bmcbioinformatics.biomedcentral.com/articles/10.1186/s12859-022-05103-0)), which used mock communities as the ground truth. A summary figure of performance is shown below, with Taxonomic-Profiling-Diamond-Megan labeled below as MEGAN-LR-Prot:

![benchy](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/docs/Image-Profiling-Benchmarks-HiFi.png)



[Back to top](#TOP)

---------------

# **Quick Start** <a name="QS"></a>

This workflow requires [Anaconda](https://docs.anaconda.com/anaconda/)/[Conda](https://docs.conda.io/projects/conda/en/latest/index.html) and [Snakemake](https://snakemake.readthedocs.io/en/stable/) to be installed, and will require ~60GB memory and 40-200GB disk space per sample (see [Requirements section](#RFR)). All dependencies in the workflow are installed using conda and the environments are activated by snakemake for relevant steps. Snakemake v8+ is required, and the workflows have been tested using v8.25.

- Clone the Taxonomic-Profiling-Diamond-Megan directory.
- Download MEGAN6 community edition (or ultimate edition) from the [MEGAN download page](https://software-ab.informatik.uni-tuebingen.de/download/megan6/welcome.html) to obtain `sam2rma`and `rma2info`. **Ensure you have at least version 6.19.+**
- Download and unpack the newest MEGAN mapping file for NCBI-nr accessions from the [MEGAN download page](https://software-ab.informatik.uni-tuebingen.de/download/megan6/welcome.html). This should be the community edition or ultimate edition, depending on which MEGAN you've downloaded.
- Download the NCBI-nr database from: ftp://ftp.ncbi.nlm.nih.gov/blast/db/FASTA/nr.gz*
- Index the NCBI-nr database with DIAMOND using `diamond makedb --in nr.gz --db diamond_nr_db --threads 24`. This will result in a `diamond_nr_db.dmnd` file that is ~150GB.
- Include all input HiFi fasta files (`SAMPLE.fasta`) in the `inputs/` folder. These can be files or symlinks. 
- Edit sample names in `Sample-Config.yaml` the configuration file in `configs/` for your project. 
- Specify the full path to `sam2rma`, full path to `rma2info`, full path to the MEGAN database file , and full path to the indexed NCBI-nr database in `config.yaml`. Ensure the `hit_limit` argument (under `diamond`), `readassignmentmode` (under `sam2rma`), and `minSupportPercent` (under `sam2rma`) arguments are set correctly for your analysis.
- Execute snakemake using the general commands below: 
```
snakemake --snakefile Snakefile-diamond-megan.smk --configfile configs/Sample-Config.yaml --software-deployment-method conda [additional arguments for local/HPC execution]
```
The choice of additional arguments to include depends on where and how you choose to run snakemake. Please refer to the [Executing Snakemake](#EXS) section for more details.

[Back to top](#TOP)

---------------

# **1. Snakemake Contents** <a name="SMC"></a>

To run the workflow, you will need to obtain all contents within the [Taxonomic-Profiling-Diamond-Megan folder](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/Taxonomic-Profiling-Diamond-Megan). The default contents should look like this:

```
Taxonomic-Profiling-Diamond-Megan
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
│	├── Convert_MEGAN_RMA_NCBI_c2c-snake.py
│	├── Run_ete3_NCBI_update.py
│	└── sam-merger-screen-cigar.py
│
├── Snakefile-diamond-megan.smk
├── Snakefile-diamond-megan-ue.smk
│
└── config.yaml
```
The `Snakefile-diamond-megan.smk` and `Snakefile-diamond-megan-ue.smk` files are the Snakefiles for this snakemake workflow. They contains all of the rules of the workflow. One is for MEGAN community edition, and the other for MEGAN ultimate edition. 

The `config.yaml` file is the main configuration file used in the snakemake workflow. It contains the main settings that will be used for various programs. 

The `configs/` directory contains an example configuration file for specifying which samples are to be run. It must be referenced in the command line call for snakemake for any samples to be run.

The `inputs/` directory should contain all of the required input files for each sample. In this workflow there must be a `SAMPLE.fasta` file of HiFi reads per sample. These can be the actual files, or symbolic links to the files (for example using `ln -s source_file symbolic_name`). 

The `scripts/` directory contains a Python script required for the workflow. It is used to filter and merge the protein-SAM files.

Finally, the `envs/` directory contains the `general.yml` file which is needed to install all dependencies through conda. This environment is activated for each step of the workflow. The dependencies are installed from bioconda and conda-forge and include `exonerate 2.4.0`, `diamond 2.0.4`, and several packages for Python3.

[Back to top](#TOP)

---------------

# **2. Requirements for Running** <a name="RFR"></a>


## Memory and disk space requirements

Running this pipeline using the default settings should require <60GB of memory. Approximately 150GB disk space is required for the DIAMOND-indexed NCBI-nr database. Additionally, depending on the size of the HiFi reads fasta file, 40-200GB disk space may be required per sample (using the default setting for `hit_limit`:`--top 5`): 
- Very large HiFi reads fasta files (>2 million reads @ 10kb) can produce protein-SAM outputs 100-180GB in size, which can result in RMA files 20-35GB in size (**150-215GB total**).
- Smaller HiFi reads fasta files (<1 million reads @ 8kb) can produce protein-SAM outputs 40-80GB in size, which can result in RMA files 6-11GB in size (**40-90GB total**).

After completion, the large protein-SAM files can be deleted. The protein-SAM files are not removed automatically in case different formats of RMA files need to be produced by the user.** The run time and the size of output protein-SAM files can be greatly reduced by changing the `hit_limit` setting to `-k 5` instead (see [Configuring the Analysis](#CTA) section below)** .

## Dependencies

In order to run a snakemake workflow, you will need to have an anaconda or conda installation. Conda is essential because it will be used to install the dependencies within the workflow and setup the correct environments. 

Snakemake will also need to be installed. Snakemake v8+ is now required, and the workflows have been tested using v8.25.

You can install the snakemake environment file in the main directory [snakemake-environment.yaml](https://github.com/PacificBiosciences/pb-metagenomics-tools/blob/master/snakemake-environment.yml) to obtain snakemake v8.25 and the packages required for cluster execution. 
> You can optionally install snakemake 8.25+ via the provided conda environment file via `conda env create -f environment.yml`, and then activate this environment via `conda activate pb-metagenomics-tools` to run the workflows.

Alternatively, instructions for installing snakemake using conda can be found [here](https://snakemake.readthedocs.io/en/stable/getting_started/installation.html). 

## Download MEGAN6 and MEGAN database file

MEGAN6 community edition or ultimate edition should be downloaded from the [MEGAN download page](https://software-ab.informatik.uni-tuebingen.de/download/megan6/welcome.html). The `sam2rma` and `rma2info` binaries are required for this pipeline. Both binaries should be present in the `tools` bin distributed with MEGAN. **The full path to `sam2rma` and `rma2info` must be specified in `config.yaml`.** The binaries will be slightly different between the community and ultimate editions. If you want to access KEGG annotations, use the ultimate edition.

The newest MEGAN mapping file for NCBI-nr accessions should also be downloaded from the [MEGAN download page](https://software-ab.informatik.uni-tuebingen.de/download/megan6/welcome.html). It must be unpacked to use it. The current unpacked file is ~7GB. **The full path to the unpacked database file (ending with `.db`) must be specified in `config.yaml`.** Note that there is one file for the community edition, and one for the ultimate edition. If you want access to KEGG annotations, use the ultimate edition.

## Download and index the NCBI-nr database

The NCBI-nr protein database is available at: ftp://ftp.ncbi.nlm.nih.gov/blast/db/FASTA/nr.gz*

The gzipped database (`nr.gz`) is ~80GB in size.

The database must be indexed with DIAMOND prior to running the pipeline. This can be accomplished using the following command:
`diamond makedb --in nr.gz --db diamond_nr_db --threads 24`. 

This command will result in a `diamond_nr_db.dmnd` file that is ~150GB. **The full path to the `diamond_nr_db.dmnd` file must be specified in `config.yaml`.**

You can always use a customized protein database, for example a subset of the NCBI nr database. 

[Back to top](#TOP)

---------------

# **3. Configuring the Analysis** <a name="CTA"></a>

To configure the analysis, the main configuration file (`config.yaml`) and sample configuration file (`configs/Sample-Config.yaml`) should be edited. 

#### Main configuration file (`config.yaml`)
The main configuration file contains several parameters, each of which is described in the configuration file. 

**NEW:** You can now change the number of fasta chunks to run with DIAMOND. Previous versions hard-coded this to 4 chunks, which is optimal for a HiFi fasta of 2.5 million reads. Smaller files will benefit from fewer chunks (such as 2 or 1). You can also increase the number of chunks for larger files, but the upper limit is 9. Increasing the number of chunks may also slow down the workflow, and the recommended value for DIAMOND is 4.

Depending on your system resources, you may choose to change the number of threads used in the diamond and sam2rma settings. Additionally, the `block_size` parameter of diamond will affect the speed of the analysis and memory requirements. 

The `hit_limit` argument allows you to specify the type of hit limit method and corresponding value. You can choose between the `--top` method or `-k` method, which are used with the range-culling mode (see [DIAMOND documentation](http://www.diamondsearch.org/index.php?pages/command_line_options/)). The default is `--top 5`, meaning a hit will only be deleted if its score is more than 5% lower than that of a higher scoring hit over at least 50% of its query range. Using `-k 5` instead means that a hit will only be deleted if at least 50% of its query range is spanned by at least 5 higher or equal scoring hits. In general, the `-k` method will keep far fewer hits, and specifying `-k 1` will keep a single hit per query range. This can be useful for 1) very simple metagenomic communities, or 2) reducing the output file size. If you choose to modify the `hit_limit` argument, you will want to supply the complete DIAMOND flag (e.g., `-k 3` or `--top 10`).

Finally, consider the `minSupportPercent` argument, which is the minimum support as percent of assigned reads required to report a taxon. The default in MEGAN is 0.05, but with HiFi the best value appears to be 0.01. This provides an optimal trade-off between precision and recall, with near perfect detection of species down to ~0.04% abundance. To avoid any filtering based on this threshold, use a value of 0 instead. This will report ALL assigned reads, which will potentially include thousands of false positives at ultra-low abundances (<0.01%), similar to results from short-read methods (e.g., Kraken2, Centrifuge, etc). Make sure you filter such files after the analysis to reduce false positives! **Note:** This parameter will only affect the filtered RMA file; a second unfiltered RMA file is also produced by default.

**You must also specify the full paths to `sam2rma`, `rma2info`, the MEGAN mapping database file, and the indexed NCBI-nr database (`diamond_nr_db.dmnd`)**. 

#### Sample configuration file (`configs/Sample-Config.yaml`)
The example sample configuration file is called `Sample-Config.yaml` and is located in the `configs/` directory. Here you should specify the sample names that you wish to include in the analysis. 

All samples specified in the sample configuration file must have a fasta file of HiFi reads (`SAMPLE.fasta`) in the `inputs/` folder. The pipeline can be run for any number of samples (though be aware of disk space requirements). You can also configure the file to only run for a subset of the samples present in the `inputs/` folder. Please note that if the input files do not follow the naming convention (`SAMPLE.fasta`), they will not be recognized by the workflow. You can use the actual files or symlinks to those files, both are compatible with snakemake.

[Back to top](#TOP)

---------------

# **4. Executing Snakemake** <a name="EXS"></a>

Before attempting to run this snakemake analysis, please ensure that the pre-analysis requirements have been satisfied, the analysis has been configured properly (using the general and sample configuration files), and the input files are available in the `inputs/` folder. 

There are several ways to execute the workflow. The easiest way is to run snakemake on HPC using an interactive session. The most efficient way is to use cluster or cloud configuration so that snakemake can schedule and run jobs on HPC or cloud environments. 

## Local execution

Snakemake can be run "locally" (e.g., without cluster configuration). Snakemake will automatically determine how many jobs can be run simultaneously based on the resources specified. This type of snakemake analysis can be run on a local system, but ideally it should be executed using an interactive HPC session (for example, `qrsh` with SGE or the SLURM equivalent).

The workflow must be executed from within the directory containing all the snakemake contents for the Taxonomic-Functional-Profiling-Protein pipeline. 

### Test workflow
It is a good idea to test the workflow for errors before running it. This can be done with the following command:
```
snakemake -np --snakefile Snakefile-diamond-megan.smk --configfile configs/Sample-Config.yaml
```

Let's unpack this command:
- `snakemake` calls snakemake.
- `-np` performs a 'dry-run' where the rule compatibilities are tested but they are not executed.
- `--snakefile Snakefile-diamond-megan.smk` tells snakemake to run this particular snakefile.
- `--configfile configs/Sample-Config.yaml` tells snakemake to include the samples listed in the sample configuration file.

The dry run command should result in a sequence of jobs being displayed on screen. 


### Execute workflow locally
Finally, you can execute the workflow using:
```
snakemake --snakefile Snakefile-diamond-megan.smk --configfile configs/Sample-Config.yaml -j 48 --software-deployment-method conda
```

There are a couple important arguments that were added here:

- `-j 48` specifies that there are 48 threads available to use. You should change this to match the resources available. If more threads are specified in the configuration file than are available here, snakemake automatically scales them down to this number.
-  `--software-deployment-method conda` allows conda to install the programs and environments required for each step. This is essential.

Upon execution, the first step will be conda downloading packages and creating the correct environment. After, the jobs should begin running. You will see the progress on screen.


## Cluster Configuration

Executing snakemake on HPC with cluster configuration allows it schedule jobs and run  steps in parallel. This is the most efficient way to run snakemake.

There are several ways to run snakemake on HPC using the executor modules introduced in v8+. Instructions on cluster execution is available for the [slurm executor](https://snakemake.github.io/snakemake-plugin-catalog/plugins/executor/slurm.html) and the [cluster generic executor](https://snakemake.github.io/snakemake-plugin-catalog/plugins/executor/cluster-generic.html). The `cluster generic` syntax is described below, as it is most similar to previous instructions. 

One easy way to run snakemake is to start an interactive session, and execute snakemake with the relevant cluster settings as described in the documentation. In this case, only a few threads are required for the interactive session, since most jobs will be run elsewhere. Snakemake will act as a job scheduler and also run local jobs from this location, until all jobs are complete. This can take a while, so it is best to use a detachable screen with the interactive session. 

 Below is an example of cluster configuration using SLURM:

```
snakemake --snakefile Snakefile-diamond-megan.smk --configfile configs/Sample-Config.yaml --software-deployment-method conda --executor cluster-generic --cluster-generic-submit-cmd "mkdir -p HPC_logs/{rule} && sbatch --partition=compute9 --nodes=1 --cpus-per-task={threads} --output=HPC_logs/{rule}/{wildcards}.{jobid}.txt" -j 30 --jobname "{rule}.{wildcards}.{jobid}" --latency-wait 60
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
Taxonomic-Profiling-Diamond-Megan
│
├── configs/
├── envs/
├── inputs/
├── scripts/
├── Snakefile-diamond-megan.smk
├── Snakefile-diamond-megan-ue.smk
├── config.yaml
│
├── benchmarks/
├── logs/
│
├── 3-merged/
│
├── 4-rma/
│
├── 5-r2c/
│
├── 6-c2c/
│
└── 7-kraken-mpa-reports/
```

- `benchmarks/` contains benchmark information on memory usage and I/O for each rule executed.
- `logs/` contains log files for each rule executed. 
- `3-merged/` contains the filtered and merged protein-SAM files for each sample. *These can be deleted if no other RMA files will be created.*
- `4-rma/` contains final RMA files for MEGAN. **These are the main files of interest.** This includes `{sample}_filtered.protein.{mode}.rma` and `{sample}_unfiltered.protein.{mode}.rma`, which are the optimal filtered and unfiltered RMA files, respectively.
- `5-r2c/` holds the per-sample read assignment files for each database. For protein RMA, this includes EC, EGGNOG, GTDB, INTERPRO2GO, NCBI (full and bacteria-only), and SEED. For nucleotide RMA, this will only include NCBI reads. These files are temporary and will be deleted before completion if no errors occur.
- `6-c2c/` holds the per-sample class count files for each database. For protein RMA, this includes EC, EGGNOG, GTDB, INTERPRO2GO, NCBI (full and bacteria-only), and SEED class counts. For nucleotide RMA, this will only include NCBI class counts.
- `7-kraken-mpa-reports/` contains the taxonomic class counts in kraken report (kreport) and metaphlan (mpa) format. **These two taxonomic count files allow comparisons to other taxonomic profiling programs.**

If no additional RMA files are to be generated, you should remove all the large protein-SAM files from the `3-merged/` folder. 

[Back to top](#TOP)

---------------

## **6. Usage Details for Main Programs** <a name="UDMP"></a>

In this section, additional details are provided for the main programs used in the workflow. The commands to call these programs are provided here for quick reference. Curly braces are sections filled automatically by snakemake. For additional details on other steps, please refer to the Snakefile-taxprot file.


### exonerate

Exonerate is used to split the fasta file into chunks, specifically using the `fastasplit` module:

```
fastasplit -c 4 -f {input} -o 1-chunks/
```

Chunks are named as `SAMPLE.fasta_chunk_0000000`, `SAMPLE.fasta_chunk_0000001`, `SAMPLE.fasta_chunk_0000002`, and `SAMPLE.fasta_chunk_0000004`.   

### DIAMOND

DIAMOND is used to perform translation alignment of HiFi reads to the NCBI-nr database, using long-read settings. In particular, the `--range-culling` and `--top 5` options are used. Here is an explanation of the `--range-culling` feature from the [DIAMOND website](http://www.diamondsearch.org/index.php?pages/command_line_options/):

> --range-culling 

> This feature is designed for long query DNA sequences that may span several genes. In these cases, reporting the overall top N hits can cause hits to a lower-scoring gene to be superseded by a higher-scoring gene. Using this option, hit culling will be performed locally with respect to a hit’s query range, thus reporting the locally top N hits while allowing more hits that span a different region of the query.

Using this feature along with `--top 5`, a hit will only be deleted if its score is more than 5% lower than that of a higher scoring hit over at least 50% of its query range. This allows more hits to be reported along the full length of the HiFi reads, and is more representative of our data.

Unfortunately, in the current version of DIAMOND (2.0.4) the `--range-culling` is only available if frameshifts (`-F` flag) are allowed. The frameshift characters are what create serious problems during the conversion to RMA format. The frameshift feature was intended for long, noisy reads (such as ONT), and not for HiFi reads. HiFi reads are 99% accurate, and although indels do occur, enabling frameshifts is not particularly beneficial (most hits will be reported anyways). So, the current workaround is to set an extraordinarily high frameshift penalty (`-F 5000` vs. default of `-F 15`) to prevent them. This allows the `--range-culling` feature to be used, while mostly preventing frameshift inferences. However, a small amount of frameshifts are still inferred and these hits must be filtered out prior to conversion to RMA.  

During the filter and merge step using `sam-merger-screen-cigar.py`, the CIGAR strings of all hits are checked for the illegal frameshift characters. If they are found, the hit is removed. This is generally <0.01% of hits with the current settings.

NOTE - `sam2rma` may accept silently accept illegal protein CIGAR strings in a future release. However, these frameshift CIGAR strings will still prevent alignment features and many calculations from being performed in MEGAN. Thus, allowing frameshifts in DIAMOND for HiFi data is still not recommended. For more information, see discussion [here](http://megan.informatik.uni-tuebingen.de/t/does-sam2rma-work-for-converting-sam-protein-alignments/1595/11).

Here is the DIAMOND call used in the pipeline:
 
```
diamond blastx -d {params.db} -q {input} -o {output} -f 101 -F 5000 --range-culling --top 5 -b {params.block} -p {threads} 2> {log}
```

### sam2rma

Run the sam2rma tool with long read settings (`-alg longReads`). The default readAssignmentMode (`-ram`) for long reads is `alignedBases`, and `readCount` for all else. This controls whether or not the abundance counts rely on the total number of bases, or the number of reads. I prefer the number of reads, but this option can be changed in the `config.yaml` file to use `alignedBases` instead. The `--minSupportPercent` argument controls the minimum percent of assigned reads required to report a taxon. The default for this pipeline is `0.01` (best tradeoff between precision and recall). Note that a second unfiltered RMA file is produced using a value of `0` (enabling all read-hits to be reported).

```
sam2rma -i {input.sam} -r {input.reads} -o {output} -lg -alg longReads -t {threads} -mdb {params.db} -ram {params.ram} --minSupportPercent {params.ms} -v 2> {log}
```

In this case, we are using a MEGAN database that maps NCBI-nr accessions to taxonomic and functional classes (NCBI, GTDB, eggNOG, InterPro2GO, SEED).

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

### MEGAN c2c format to kraken and metaphlan formats

The conversion from c2c format to kreport and mpa format is done using a modified version of the `Convert_MEGAN-NCBI-c2c_to_kreport-mpa.py` script available in the [pb-metagenomics-scripts](https://github.com/PacificBiosciences/pb-metagenomics-tools/tree/master/pb-metagenomics-scripts) folder. The version used here was modified to make inputs and outputs more explicit for snakemake.

[Back to top](#TOP)

---------------
