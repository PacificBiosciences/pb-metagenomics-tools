import os

localrules: 
    Checkm2Database, LongContigsToBins, CloseLongbinFork, StopLongBinCheckm2, FilterCompleteContigs,
    ConvertJGIBamDepth, DASinputMetabat2, DASinputSemiBin2, CopyDAStoolBins, AssessCheckm2Bins,
    CloseCheckm2Fork, SkipGTDBAnalysis, GTDBTkCleanup, MAGSummary, MAGPlots, all

configfile: "config.yaml"

SAMPLES = config['samplenames']
CWD = os.getcwd()

rule all:
    input:
        expand(os.path.join(CWD, "1-long-contigs", "{sample}", "{sample}.LongBinCompleted.txt"), sample = SAMPLES),
        expand(os.path.join(CWD, "2-bam", "{sample}.JGI.filtered.depth.txt"), sample = SAMPLES),
        expand(os.path.join(CWD,"5-dereplicated-bins","{sample}.bins_copied.txt"), sample = SAMPLES),
        expand(os.path.join(CWD,"6-checkm2","{sample}","checkm2","quality_report.tsv"), sample = SAMPLES),
        expand(os.path.join(CWD,"6-checkm2","{sample}","{sample}.BinCount.txt"), sample = SAMPLES),
        expand(os.path.join(CWD,"8-summary","{sample}","{sample}.Complete.txt"), sample = SAMPLES)

##################################################################################################
# Setup CheckM2

rule Checkm2Database:
    input:
        contigs = expand(os.path.join(CWD, "inputs", "{sample}.contigs.fasta"), sample = SAMPLES)
    output:
        key = os.path.join(CWD, "CheckM2_database", "uniref100.KO.1.dmnd"),
        complete = os.path.join(CWD, "CheckM2_database", "CheckM2.complete.txt")
    conda:
        "envs/checkm2.yml"
    threads:
        1
    params:
        installdir = CWD
    log:
        os.path.join(CWD, "logs", "Checkm2Database.log")
    benchmark:
        os.path.join(CWD, "benchmarks", "Checkm2Database.tsv")
    shell:
        "checkm2 database --download --path {params.installdir} &> {log} && touch {output.complete}"

##################################################################################################
# Completeness-aware binning steps

# Checkpoint 1: Fork samples into two groups: those with long contigs (> min length), and those with no contigs.
checkpoint LongContigsToBins:
    input:
        contigs = os.path.join(CWD, "inputs", "{sample}.contigs.fasta")
    output:
        key = os.path.join(CWD, "1-long-contigs", "{sample}", "{sample}.bin_key.txt")
    conda:
        "envs/python.yml"
    threads: 
        1
    params: 
        length = config["completeness_aware"]["min_length"],
        outdir = os.path.join(CWD, "1-long-contigs", "{sample}", "bins", "")
    log: 
        os.path.join(CWD, "logs", "{sample}.LongContigsToBins.log")
    shell:
        "python scripts/Fasta-Make-Long-Seq-Bins.py -i {input.contigs} -o {params.outdir} "
        "-b {output.key} -l {params.length} &> {log}"

# Function to get targets of forked workflow
def get_long_binning_targets(wildcards):
    # decision is based on whether long bin key file is empty (no bins) or not (long bins created)
    with checkpoints.LongContigsToBins.get(sample=wildcards.sample).output[0].open() as fh:
        if fh.read().strip().startswith("complete"):
            return os.path.join(CWD, "1-long-contigs", "{sample}", "{sample}.passed_bins.txt")
        else:
            return os.path.join(CWD, "1-long-contigs", "{sample}", "{sample}.no_passed_bins.txt")

# Checkpoint 1 aggregator; close the fork; outputs '/1-long-contigs/SAMPLE/SAMPLE.incomplete_contigs.fasta'
rule CloseLongbinFork:
    input:
        get_long_binning_targets
    output:
        incomplete_contigs = os.path.join(CWD,"1-long-contigs","{sample}","{sample}.incomplete_contigs.fasta"),
        complete = os.path.join(CWD, "1-long-contigs", "{sample}", "{sample}.LongBinCompleted.txt"),
        outdir = directory(os.path.join(CWD,"5-dereplicated-bins","{sample}",""))
    conda:
        "envs/python.yml"
    threads:
        1
    params:
        contigs = os.path.join(CWD,"inputs","{sample}.contigs.fasta"),
        fastadir = os.path.join(CWD, "1-long-contigs", "{sample}", "bins", "")
    log:
        os.path.join(CWD, "logs", "{sample}.CloseLongbinFork.log")
    shell:
        "python scripts/Make-Incomplete-Contigs.py -i {params.contigs} -f {output.incomplete_contigs} "
        "-p {input} -d {params.fastadir} -o {output.outdir} &> {log} && cp {input} {output.complete}"

##############################
# Checkpoint 1: Fork 1 - No contigs > min length were found.
rule StopLongBinCheckm2:
    input:
        key = os.path.join(CWD, "1-long-contigs", "{sample}", "{sample}.bin_key.txt")
    output:
        os.path.join(CWD, "1-long-contigs", "{sample}", "{sample}.no_passed_bins.txt")
    threads:
        1
    params:
        outdir= os.path.join(CWD,"5-dereplicated-bins","{sample}","")
    shell:
        "touch {output} && mkdir -p {params.outdir}"

##############################
# Checkpoint 1: Fork 2 - Long contigs found, sample moves through Checkm2ContigAnalysis -> FilterCompleteContigs
rule Checkm2ContigAnalysis:
    input:
        db = os.path.join(CWD, "CheckM2_database", "uniref100.KO.1.dmnd"),
        key = os.path.join(CWD, "1-long-contigs", "{sample}", "{sample}.bin_key.txt")
    output:
        os.path.join(CWD, "1-long-contigs", "{sample}", "checkm2", "quality_report.tsv")
    conda:
        "envs/checkm2.yml"
    threads: 
        config["checkm2"]["threads"]
    params:
        indir = os.path.join(CWD, "1-long-contigs", "{sample}", "bins", ""),
        outdir = os.path.join(CWD, "1-long-contigs", "{sample}", "checkm2", ""),
        tmp = config["tmpdir"]
    log:
        os.path.join(CWD, "logs", "{sample}.Checkm2ContigAnalysis.log")
    benchmark: 
        os.path.join(CWD, "benchmarks", "{sample}.Checkm2ContigAnalysis.tsv")
    shell:
        "checkm2 predict -i {params.indir} -o {params.outdir} -x fa -t {threads} --force "
        "--database_path {input.db} --remove_intermediates --tmpdir {params.tmp} &> {log}"

# Checkpoint 1: Fork 2 - Long contigs found, sample moves through Checkm2ContigAnalysis -> FilterCompleteContigs
rule FilterCompleteContigs:
    input:
        contigs = os.path.join(CWD, "inputs", "{sample}.contigs.fasta"),
        report = os.path.join(CWD, "1-long-contigs", "{sample}", "checkm2", "quality_report.tsv"),
        key = os.path.join(CWD, "1-long-contigs", "{sample}", "{sample}.bin_key.txt")
    output:
        passed = os.path.join(CWD, "1-long-contigs", "{sample}", "{sample}.passed_bins.txt"),
        p1 = os.path.join(CWD, "1-long-contigs", "{sample}", "{sample}.completeness_vs_size_scatter.pdf"),
        p2 = os.path.join(CWD, "1-long-contigs", "{sample}", "{sample}.completeness_histo.pdf")
    conda:
        "envs/python.yml"
    threads: 
        1
    params:
        length = config["completeness_aware"]["min_length"],
        completeness = config["completeness_aware"]["min_completeness"]
    log:
        os.path.join(CWD, "logs", "{sample}.FilterCompleteContigs.log")
    shell:
        "python scripts/Filter-Complete-Contigs.py -i {input.contigs} -c {input.report} -b {input.key} "
        "-l {params.length} -m {params.completeness} -p {output.passed} -p1 {output.p1} "
        "-p2 {output.p2} &> {log} "

##################################################################################################
# Get various coverage files (performed after completeness-aware binning steps)

rule MinimapToBam:
    input:
        reads = os.path.join(CWD, "inputs", "{sample}.fasta"),
        contigs = os.path.join(CWD, "inputs", "{sample}.contigs.fasta")
    output:
        os.path.join(CWD, "2-bam", "{sample}.bam")
    conda:
        "envs/samtools.yml"
    threads: 
        config['minimap']['threads']
    log: 
        os.path.join(CWD, "logs", "{sample}.MinimapToBam.log")
    benchmark: 
        os.path.join(CWD, "benchmarks", "{sample}.MinimapToBam.tsv")
    shell:
        "minimap2 -a -k 19 -w 10 -I 10G -g 5000 -r 2000 --lj-min-ratio 0.5 "
        "-A 2 -B 5 -O 5,56 -E 4,1 -z 400,50 --sam-hit-only -t {threads} " 
        "{input.contigs} {input.reads} 2> {log} | samtools sort -@ {threads} -o {output}"
        
rule IndexBam:
    input:
        os.path.join(CWD, "2-bam", "{sample}.bam")
    output:
        index = os.path.join(CWD, "2-bam", "{sample}.bam.bai"),
        complete = os.path.join(CWD, "2-bam", "{sample}.index.completed.txt")
    conda:
        "envs/samtools.yml"
    threads: 
        config['minimap']['threads']
    log: 
        os.path.join(CWD, "logs", "{sample}.IndexBam.log")
    benchmark: 
        os.path.join(CWD, "benchmarks", "{sample}.IndexBam.tsv")
    shell:
        "samtools index -@ {threads} {input} &> {log} && touch {output.complete}"

rule JGIBamDepth:
    input:
        complete = os.path.join(CWD, "2-bam", "{sample}.index.completed.txt"),
        bam = os.path.join(CWD, "2-bam", "{sample}.bam"),
        index = os.path.join(CWD, "2-bam", "{sample}.bam.bai")
    output:
        os.path.join(CWD, "2-bam", "{sample}.JGI.depth.txt")
    conda:
        "envs/metabat.yml"
    log:
        os.path.join(CWD, "logs", "{sample}.JGIBamDepth.log")
    benchmark: 
        os.path.join(CWD, "benchmarks", "{sample}.JGIBamDepth.tsv")
    shell:
        "jgi_summarize_bam_contig_depths --outputDepth {output} {input.bam} 2> {log}"

rule ConvertJGIBamDepth:
    input:
        depth = os.path.join(CWD, "2-bam", "{sample}.JGI.depth.txt"),
        passed = os.path.join(CWD, "1-long-contigs", "{sample}", "{sample}.LongBinCompleted.txt")
    output:
        os.path.join(CWD, "2-bam", "{sample}.JGI.filtered.depth.txt")
    conda:
        "envs/python.yml"
    threads:
        1
    log:
        os.path.join(CWD, "logs", "{sample}.ConvertJGIBamDepth.log")
    shell:
        "python scripts/Convert-JGI-Coverages.py -i {input.depth} -p {input.passed} -o1 {output} "
        "&> {log}"

##################################################################################################
# Run MetaBat2, make DAS_Tool input

rule Metabat2Analysis:
    input:
        contigs = os.path.join(CWD, "1-long-contigs", "{sample}", "{sample}.incomplete_contigs.fasta"),
        depths = os.path.join(CWD, "2-bam", "{sample}.JGI.filtered.depth.txt")
    output:
        complete = os.path.join(CWD, "3-metabat2", "{sample}.completed.txt"),
        outdir = directory(os.path.join(CWD, "3-metabat2", "{sample}", ""))
    conda:
        "envs/metabat.yml"
    threads:
        config['metabat']['threads']
    params:
        prefix = os.path.join(CWD, "3-metabat2", "{sample}", "metabat2"),
        min_contig_size = config['metabat']['min_contig_size']
    log:
        os.path.join(CWD, "logs", "{sample}.Metabat2Analysis.log")
    benchmark:
        os.path.join(CWD, "benchmarks", "{sample}.Metabat2Analysis.tsv")
    shell:
        "metabat2 -i {input.contigs} -a {input.depths} -o {params.prefix} -t {threads} "
        "-m {params.min_contig_size} -v &> {log} && touch {output.complete}"

rule DASinputMetabat2:
    input:
        os.path.join(CWD, "3-metabat2", "{sample}", "")
    output:
        os.path.join(CWD, "4-DAStool", "{sample}.metabat2.tsv")
    conda:
        "envs/dastool.yml"
    log:
        os.path.join(CWD, "logs", "{sample}.DASinputMetabat2.log")
    shell:
        "Fasta_to_Scaffolds2Bin.sh -i {input} -e fa 1> {output} 2> {log}"


##################################################################################################
# Run SemiBin2

rule SemiBin2Analysis:
    input:
        contigs = os.path.join(CWD, "1-long-contigs", "{sample}", "{sample}.incomplete_contigs.fasta"),
        bam = os.path.join(CWD, "2-bam", "{sample}.bam")
    output:
        bins = os.path.join(CWD, "3-semibin2", "{sample}", "bins_info.tsv"),
        outdir = directory(os.path.join(CWD,"3-semibin2","{sample}",""))
    conda:
        "envs/semibin.yml"
    threads:
        config['semibin']['threads']
    params:
        tmp = config["tmpdir"],
        modelflag = config['semibin']['model']
    log:
        os.path.join(CWD, "logs", "{sample}.SemiBin2Analysis.log")
    benchmark:
        os.path.join(CWD, "benchmarks", "{sample}.SemiBin2Analysis.tsv")
    shell:
        "SemiBin single_easy_bin -i {input.contigs} -b {input.bam} -o {output.outdir} --self-supervised "
        "--sequencing-type=long_reads --compression=none -t {threads} --tag-output semibin2 {params.modelflag} "
        "--verbose --tmpdir={params.tmp} &> {log}"
#--environment=global

rule DASinputSemiBin2:
    input:
        os.path.join(CWD,"3-semibin2","{sample}","")
    output:
        os.path.join(CWD, "4-DAStool", "{sample}.semibin2.tsv")
    conda:
        "envs/dastool.yml"
    params:
        indir = os.path.join(CWD, "3-semibin2", "{sample}", "output_bins", "")
    log:
        os.path.join(CWD, "logs", "{sample}.DASinputSemiBin2.log")
    shell:
        "Fasta_to_Scaffolds2Bin.sh -i {params.indir} -e fa 1> {output} 2> {log}"

##################################################################################################
# Run DAS_Tool

rule DAStoolAnalysis:
    input:
        metabat = os.path.join(CWD, "4-DAStool", "{sample}.metabat2.tsv"),
        semibin = os.path.join(CWD,"4-DAStool","{sample}.semibin2.tsv"),
        contigs = os.path.join(CWD, "1-long-contigs", "{sample}", "{sample}.incomplete_contigs.fasta")
    output:
        binsdir = directory(os.path.join(CWD, "4-DAStool", "{sample}", "{sample}_DASTool_bins", "")),
        complete = os.path.join(CWD, "4-DAStool", "{sample}.Complete.txt")
    conda:
        "envs/dastool.yml"
    threads:
        config['dastool']['threads']
    params:
        outlabel = os.path.join(CWD, "4-DAStool", "{sample}", "{sample}"),
        search = config['dastool']['search'],
        thresh = config['dastool']['score_threshold']
    log:
        os.path.join(CWD, "logs", "{sample}.DAStoolAnalysis.log")
    benchmark:
        os.path.join(CWD, "benchmarks", "{sample}.DAStoolAnalysis.tsv")
    shell:
        "DAS_Tool -i {input.metabat},{input.semibin} -c {input.contigs} "
        "-l metabat2,semibin2 -o {params.outlabel} --search_engine {params.search} "
        "--write_bins 1 -t {threads} --score_threshold {params.thresh} --debug "
        "&> {log} && touch {output.complete}"

rule CopyDAStoolBins:
    input:
        binsdir = os.path.join(CWD, "4-DAStool", "{sample}", "{sample}_DASTool_bins", ""),
        complete = os.path.join(CWD, "4-DAStool", "{sample}.Complete.txt"),
        copydir = os.path.join(CWD,"5-dereplicated-bins","{sample}","")
    output:
        os.path.join(CWD,"5-dereplicated-bins","{sample}.bins_copied.txt")
    conda:
        "envs/dastool.yml"
    threads:
        1
    log:
        os.path.join(CWD, "logs", "{sample}.CopyDAStoolBins.log")
    shell:
        "cp {input.binsdir}/*.fa {input.copydir} 2> {log} && touch {output}"

##################################################################################################
# CheckM2 analysis and checkpoint, fork to GTDB-Tk & summary (if bins found) or end analysis (no bins found)

rule Checkm2BinAnalysis:
    input:
        db = os.path.join(CWD, "CheckM2_database", "uniref100.KO.1.dmnd"),
        derep_bins = os.path.join(CWD,"5-dereplicated-bins","{sample}.bins_copied.txt")
    output:
        qv = os.path.join(CWD, "6-checkm2", "{sample}", "checkm2", "quality_report.tsv")
    conda:
        "envs/checkm2.yml"
    threads:
        config["checkm2"]["threads"]
    params:
        indir = os.path.join(CWD, "5-dereplicated-bins", "{sample}", ""),
        outdir = os.path.join(CWD, "6-checkm2", "{sample}", "checkm2", ""),
        tmp = config["tmpdir"]
    log:
        os.path.join(CWD, "logs", "{sample}.Checkm2BinAnalysis.log")
    benchmark:
        os.path.join(CWD, "benchmarks", "{sample}.Checkm2BinAnalysis.tsv")
    shell:
        "checkm2 predict -i {params.indir} -o {params.outdir} -x fa -t {threads} --force "
        "--remove_intermediates --database_path {input.db} --tmpdir {params.tmp} &> {log}"

# Checkpoint 2 - Ensure there are bins after CheckM2, before running GTDB-Tk and the summary
checkpoint AssessCheckm2Bins:
    input:
        qv = os.path.join(CWD, "6-checkm2", "{sample}", "checkm2", "quality_report.tsv"),
        depth = os.path.join(CWD, "2-bam", "{sample}.JGI.depth.txt")
    output:
        gtdb = os.path.join(CWD, "6-checkm2", "{sample}", "{sample}.GTDBTk_batch_file.txt"),
        target = os.path.join(CWD,"6-checkm2","{sample}","{sample}.BinCount.txt"),
        output_tsv = os.path.join(CWD, "6-checkm2", "{sample}", "{sample}.quality_report.tsv")
    conda:
        "envs/python.yml"
    threads:
        1
    params:
        bin_dir = os.path.join(CWD, "5-dereplicated-bins", "{sample}", ""),
        completeness = config['filters']['min_completeness'],
        contamination = config['filters']['max_contamination'],
        contigs = config['filters']['max_contigs']
    log:
        os.path.join(CWD, "logs", "{sample}.AssessCheckm2Bins.log")
    shell:
        "python scripts/Filter-Checkm2-Bins.py -i {input.qv} -b {params.bin_dir} -d {input.depth} "
        "-c1 {params.completeness} -c2 {params.contamination} -c3 {params.contigs} -o {output.gtdb} "
        "-t {output.target} -u {output.output_tsv} &> {log}"

# Function to get targets of forked workflow
def get_post_checkm2_inputs(wildcards):
    # decision is based on whether bin count file is > 0 (bins passed checkm2 filters) or not (no bins passed filtering)
    with checkpoints.AssessCheckm2Bins.get(sample=wildcards.sample).output[1].open() as fh:
        if int(fh.read().strip()) > 0:
            return os.path.join(CWD, "8-summary", "{sample}", "{sample}.Completeness-Contamination-Contigs.pdf")
        else:
            return os.path.join(CWD,"8-summary","{sample}","{sample}.No_MAGs.summary.txt")

# Checkpoint 2 aggregator; close the fork; outputs '/8-summary/SAMPLE/SAMPLE.Complete.txt'
rule CloseCheckm2Fork:
    input:
        get_post_checkm2_inputs
    output:
        os.path.join(CWD,"8-summary","{sample}","{sample}.Complete.txt")
    shell:
        "touch {output}"

##############################
# Checkpoint 2: Fork 1 - No bins passed the filtering criteria.
rule SkipGTDBAnalysis:
    input:
        gtdb = os.path.join(CWD, "6-checkm2", "{sample}", "{sample}.GTDBTk_batch_file.txt"),
        target = os.path.join(CWD,"6-checkm2","{sample}","{sample}.BinCount.txt"),
        output_tsv = os.path.join(CWD,"6-checkm2","{sample}","{sample}.quality_report.tsv")
    output:
        os.path.join(CWD,"8-summary","{sample}","{sample}.No_MAGs.summary.txt")
    threads:
        1
    params:
        outdir = os.path.join(CWD, "8-summary", "{sample}", "")
    shell:
        "mkdir -p {params.outdir} && echo No bins passed filtering in CheckM2, "
        "see {input.output_tsv} for more information > {output}"

##############################
# Checkpoint 2: Fork 2 - Bins passed filters; GTDBTkAnalysis -> GTDBTkCleanup -> MAGSummary -> MAGCopy -> MAGPlots
rule GTDBTkAnalysis:
    input:
        gtdb = os.path.join(CWD, "6-checkm2", "{sample}", "{sample}.GTDBTk_batch_file.txt"),
        target = os.path.join(CWD,"6-checkm2","{sample}","{sample}.BinCount.txt")
    output:
        dir_align = directory(os.path.join(CWD, "7-gtdbtk", "{sample}", "align", "")),
        dir_classify = directory(os.path.join(CWD, "7-gtdbtk", "{sample}", "classify", "")),
        dir_identify = directory(os.path.join(CWD, "7-gtdbtk", "{sample}", "identify", "")),
        complete = os.path.join(CWD,"7-gtdbtk","{sample}","{sample}.Complete.txt")
    conda:
        "envs/gtdbtk.yml"
    threads:
        config['gtdbtk']['threads']
    params:
        gtdbtk_data = config['gtdbtk']['gtdbtk_data'],
        outdir = os.path.join(CWD, "7-gtdbtk", "{sample}", "")
    log:
        os.path.join(CWD, "logs", "{sample}.GTDBTkAnalysis.log")
    benchmark:
        os.path.join(CWD, "benchmarks", "{sample}.GTDBTkAnalysis.tsv")
    shell:
        "GTDBTK_DATA_PATH={params.gtdbtk_data:q} gtdbtk classify_wf --batchfile {input.gtdb} "
        "--out_dir {params.outdir} -x fa --prefix {wildcards.sample} --cpus {threads} "
        " &> {log} && touch {output.complete}"

# Checkpoint 2: Fork 2 - Bins passed filters; GTDBTkAnalysis -> GTDBTkCleanup -> MAGSummary -> MAGCopy -> MAGPlots
rule GTDBTkCleanup:
    input:
        dir_classify = os.path.join(CWD, "7-gtdbtk", "{sample}", "classify", ""),
        complete = os.path.join(CWD,"7-gtdbtk","{sample}","{sample}.Complete.txt")
    output:
        os.path.join(CWD,"7-gtdbtk","{sample}","{sample}.GTDBTk_Summary.txt")
    conda:
        "envs/python.yml"
    threads:
        1
    log:
        os.path.join(CWD, "logs", "{sample}.GTDBTkCleanup.log")
    shell:
        "python scripts/GTDBTk-Organize.py -i {input.dir_classify} -o {output} &> {log}"

# Checkpoint 2: Fork 2 - Bins passed filters; GTDBTkAnalysis -> GTDBTkCleanup -> MAGSummary -> MAGCopy -> MAGPlots
rule MAGSummary:
    input:
        gtdbtk = os.path.join(CWD,"7-gtdbtk","{sample}","{sample}.GTDBTk_Summary.txt"),
        checkm2 = os.path.join(CWD, "6-checkm2", "{sample}", "{sample}.quality_report.tsv")
    output:
        os.path.join(CWD,"8-summary","{sample}","{sample}.HiFi_MAG.summary.txt")
    conda:
        "envs/python.yml"
    threads:
        1
    log:
        os.path.join(CWD, "logs", "{sample}.MAGSummary.log")
    shell:
        "python scripts/MAG-Summary.py -g {input.gtdbtk} -c {input.checkm2} -o {output} &> {log}"

# Checkpoint 2: Fork 2 - Bins passed filters; GTDBTkAnalysis -> GTDBTkCleanup -> MAGSummary -> MAGCopy -> MAGPlots
rule MAGCopy:
    input:
        mag_sum = os.path.join(CWD,"8-summary","{sample}","{sample}.HiFi_MAG.summary.txt"),
        mag_dir = os.path.join(CWD, "5-dereplicated-bins", "{sample}", "")
    output:
        directory(os.path.join(CWD,"8-summary","{sample}", "MAGs", ""))
    conda:
        "envs/python.yml"
    threads:
        1
    log:
        os.path.join(CWD, "logs", "{sample}.MAGCopy.log")
    shell:
        "python scripts/Copy-Final-MAGs.py -i {input.mag_sum} -m {input.mag_dir} -o {output} &> {log}"

# Checkpoint 2: Fork 2 - Bins passed filters; GTDBTkAnalysis -> GTDBTkCleanup -> MAGSummary -> MAGCopy -> MAGPlots
rule MAGPlots:
    input:
        checkm2_tsv = os.path.join(CWD, "6-checkm2", "{sample}", "{sample}.quality_report.tsv"),
        mag_dir = os.path.join(CWD,"8-summary","{sample}", "MAGs", ""),
        mag_eval = os.path.join(CWD,"8-summary","{sample}","{sample}.HiFi_MAG.summary.txt")
    output:
        o1 = os.path.join(CWD, "8-summary", "{sample}", "{sample}.All-DASTool-Bins.pdf"),
        o2 = os.path.join(CWD, "8-summary", "{sample}", "{sample}.Completeness-Contamination-Contigs.pdf"),
        o3 = os.path.join(CWD, "8-summary", "{sample}", "{sample}.GenomeSizes-Depths.pdf")
    conda:
        "envs/python.yml"
    threads:
        1
    params:
        completeness = config['filters']['min_completeness'],
        contamination = config['filters']['max_contamination']
    log:
        os.path.join(CWD, "logs", "{sample}.MAGPlots.log")
    shell:
        "python scripts/Plot-Figures.py -i1 {input.checkm2_tsv} -i2 {input.mag_eval} -l {wildcards.sample} "
        "-c1 {params.completeness} -c2 {params.contamination} -o1 {output.o1} -o2 {output.o2} -o3 {output.o3}"
        "&> {log}"
