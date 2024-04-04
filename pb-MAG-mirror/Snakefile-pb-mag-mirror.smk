import os
localrules: 
    AssessCheckm2Bins, CloseCheckm2Fork, SkipComparisons, MakeComparisons, MakeMainPlot, MakeQualityPlots, CopyConsolidatedBins, all
configfile: "config.yaml"

SAMPLES = config['samplenames']
CWD = os.getcwd()

rule all:
    input:
        expand(os.path.join(CWD, "1-checkm2", "{sample}_bins1", "{sample}_bins1.quality_report.tsv"), sample = SAMPLES),
        expand(os.path.join(CWD, "1-checkm2", "{sample}_bins2", "{sample}_bins2.quality_report.tsv"), sample = SAMPLES),
        expand(os.path.join(CWD, "3-summary", "{sample}", "{sample}.Complete.txt"), sample = SAMPLES)

##################################################################################################
# CheckM2

rule Checkm2BinAnalysis1:
    input:
        indir = os.path.join(CWD, "inputs", "{sample}_bins1", "")
    output:
        qv = os.path.join(CWD, "1-checkm2", "{sample}_bins1", "checkm2", "quality_report.tsv")
    conda:
        "envs/checkm2.yml"
    threads:
        config["checkm2"]["threads"]
    params:
        outdir = os.path.join(CWD, "1-checkm2", "{sample}_bins1", "checkm2", ""),
        tmp = config["checkm2"]["tmpdir"],
        db = config["checkm2"]["db_path"],
        ext = config["checkm2"]["fasta_ext1"]
    log:
        os.path.join(CWD, "logs", "{sample}_bins1.Checkm2BinAnalysis.log")
    shell:
        "checkm2 predict -i {input.indir} -o {params.outdir} -x {params.ext} -t {threads} --force "
        "--remove_intermediates --database_path {params.db} --tmpdir {params.tmp} &> {log}"

rule Checkm2BinAnalysis2:
    input:
        indir = os.path.join(CWD, "inputs", "{sample}_bins2", "")
    output:
        qv = os.path.join(CWD, "1-checkm2", "{sample}_bins2", "checkm2", "quality_report.tsv")
    conda:
        "envs/checkm2.yml"
    threads:
        config["checkm2"]["threads"]
    params:
        outdir = os.path.join(CWD, "1-checkm2", "{sample}_bins2", "checkm2", ""),
        tmp = config["checkm2"]["tmpdir"],
        db = config["checkm2"]["db_path"],
        ext = config["checkm2"]["fasta_ext2"]
    log:
        os.path.join(CWD, "logs", "{sample}_bins2.Checkm2BinAnalysis.log")
    shell:
        "checkm2 predict -i {input.indir} -o {params.outdir} -x {params.ext} -t {threads} --force "
        "--remove_intermediates --database_path {params.db} --tmpdir {params.tmp} &> {log}"

# Checkpoint 1
checkpoint AssessCheckm2Bins:
    input:
        qv1 = os.path.join(CWD, "1-checkm2", "{sample}_bins1", "checkm2", "quality_report.tsv"),
        qv2 = os.path.join(CWD, "1-checkm2", "{sample}_bins2", "checkm2", "quality_report.tsv")
    output:
        target = os.path.join(CWD, "1-checkm2", "{sample}.BinCounts.txt"),
        output_tsv1 = os.path.join(CWD, "1-checkm2", "{sample}_bins1", "{sample}_bins1.quality_report.tsv"),
        output_tsv2 = os.path.join(CWD, "1-checkm2", "{sample}_bins2", "{sample}_bins2.quality_report.tsv")
    conda:
        "envs/python.yml"
    threads:
        1
    params:
        bin_dir1 = os.path.join(CWD, "inputs", "{sample}_bins1", ""),
        bin_dir2 = os.path.join(CWD, "inputs", "{sample}_bins2", ""),
        completeness = config['filters']['min_completeness'],
        contamination = config['filters']['max_contamination'],
        contigs = config['filters']['max_contigs']
    log:
        os.path.join(CWD, "logs", "{sample}.AssessCheckm2Bins.log")
    shell:
        "python scripts/Filter-Checkm2-Bins.py -i1 {input.qv1} -i2 {input.qv2} -b1 {params.bin_dir1} "
        "-b2 {params.bin_dir2} -c1 {params.completeness} -c2 {params.contamination} -c3 {params.contigs} "
        "-t {output.target} -u1 {output.output_tsv1} -u2 {output.output_tsv2} &> {log}"

# Function to get targets of forked checkpoint 1 workflow
def get_post_checkm2_inputs(wildcards):
    # decision is based on whether bin count file is > 0 (bins passed checkm2 filters) or not (no bins passed filtering)
    with checkpoints.AssessCheckm2Bins.get(sample=wildcards.sample).output[0].open() as fh:
        lines = fh.readlines()
        if int(lines[0].strip()) == 0 or int(lines[1].strip()) == 0:
            return os.path.join(CWD, "3-summary", "{sample}", "{sample}.No_filtered_bins.txt")
        else:
            return os.path.join(CWD, "3-summary", "{sample}", "{sample}.copied_bins.txt")

# Checkpoint 1 aggregator; close the fork; outputs '/8-summary/SAMPLE/SAMPLE.Complete.txt'
rule CloseCheckm2Fork:
    input:
        get_post_checkm2_inputs
    output:
        os.path.join(CWD, "3-summary", "{sample}", "{sample}.Complete.txt")
    shell:
        "touch {output}"

##############################
# Checkpoint 1: Fork 1 - No bins in at least one method passed the filtering criteria.
rule SkipComparisons:
    input:
        target = os.path.join(CWD, "1-checkm2", "{sample}.BinCounts.txt"),
        qv1 = os.path.join(CWD, "1-checkm2", "{sample}_bins1", "{sample}_bins1.quality_report.tsv"),
        qv2 = os.path.join(CWD, "1-checkm2", "{sample}_bins2", "{sample}_bins2.quality_report.tsv")
    output:
        os.path.join(CWD, "2-comparisons", "{sample}", "{sample}.No_filtered_bins.txt")
    threads:
        1
    params:
        outdir = os.path.join(CWD, "2-comparisons", "{sample}", "")
    log:
        os.path.join(CWD, "logs", "{sample}.SkipComparisons.log")
    shell:
        "mkdir -p {params.outdir} && echo No bins passed filtering in CheckM2, "
        "see {input.qv1} and {input.qv2} for more information > {output}"

##############################
# Checkpoint 1: Fork 2 - Some bins in both methods passed the filtering criteria.
rule MakeComparisons:
    input:
        target = os.path.join(CWD, "1-checkm2", "{sample}.BinCounts.txt"),
        qv1 = os.path.join(CWD, "1-checkm2", "{sample}_bins1", "{sample}_bins1.quality_report.tsv"),
        qv2 = os.path.join(CWD, "1-checkm2", "{sample}_bins2", "{sample}_bins2.quality_report.tsv")
    output:
        o1 = os.path.join(CWD, "2-comparisons", "{sample}", "{sample}.bins1.comparisons.txt"),
        o2 = os.path.join(CWD, "2-comparisons", "{sample}", "{sample}.bins2.comparisons.txt"),
        o3 = os.path.join(CWD, "3-summary", "{sample}", "{sample}.consolidated.comparisons.txt")
    conda:
        "envs/python.yml"
    threads:
        1
    params:
        outdir = os.path.join(CWD, "2-comparisons", "{sample}", ""),
        method = config['consolidation']['mixed_method'],
        missing_char = config['consolidation']['missing_char']
    log:
        os.path.join(CWD, "logs", "{sample}.MakeComparisons.log")
    shell:
        "python scripts/Perform-bin-comparisons.py -i1 {input.qv1} -i2 {input.qv2} -c {params.method} "
        "-o {params.outdir} -t1 {output.o1} -t2 {output.o2} -t3 {output.o3} -m {params.missing_char} &> {log}"

rule MakeMainPlot:
    input:
        tsv1 = os.path.join(CWD, "2-comparisons", "{sample}", "{sample}.bins1.comparisons.txt"),
        tsv2 = os.path.join(CWD, "2-comparisons", "{sample}", "{sample}.bins2.comparisons.txt")
    output:
        o1 = os.path.join(CWD, "3-summary", "{sample}", "{sample}.comparison_categories.table.txt"),
        o2 = os.path.join(CWD, "3-summary", "{sample}", "{sample}.comparison_categories.summary.pdf")
    conda:
        "envs/python.yml"
    threads:
        1
    params:
        label1 = config['consolidation']['label1'],
        label2 = config['consolidation']['label2']
    log:
        os.path.join(CWD, "logs", "{sample}.MakeMainPlot.log")
    shell:
        "python scripts/Plot-Main.py -i1 {input.tsv1} -i2 {input.tsv2} -o1 {output.o1} -o2 {output.o2} "
        "-l1 {params.label1} -l2 {params.label2} &> {log}"

rule MakeQualityPlots:
    input:
        tsv1 = os.path.join(CWD, "2-comparisons", "{sample}", "{sample}.bins1.comparisons.txt"),
        tsv2 = os.path.join(CWD, "2-comparisons", "{sample}", "{sample}.bins2.comparisons.txt")
    output:
        o1 = os.path.join(CWD, "3-summary", "{sample}", "{sample}.comparison_categories.completeness.pdf"),
        o2 = os.path.join(CWD, "3-summary", "{sample}", "{sample}.comparison_categories.contamination.pdf"),
        o3 = os.path.join(CWD, "3-summary", "{sample}", "{sample}.comparison_categories.contigs.pdf"),
        o4 = os.path.join(CWD, "3-summary", "{sample}", "{sample}.comparison_categories.sizes.pdf")
    conda:
        "envs/python.yml"
    threads:
        1
    params:
        label1 = config['consolidation']['label1'],
        label2 = config['consolidation']['label2']
    log:
        os.path.join(CWD, "logs", "{sample}.MakeQualityPlots.log")
    shell:
        "python scripts/Plot-Qualities.py -i1 {input.tsv1} -i2 {input.tsv2} -o1 {output.o1} -o2 {output.o2} "
        "-o3 {output.o3} -o4 {output.o4} -l1 {params.label1} -l2 {params.label2} &> {log}"

rule CopyConsolidatedBins:
    input:
        table = os.path.join(CWD, "3-summary", "{sample}", "{sample}.comparison_categories.table.txt"),
        plot = os.path.join(CWD, "3-summary", "{sample}", "{sample}.comparison_categories.summary.pdf"),
        tsv = os.path.join(CWD,"3-summary","{sample}","{sample}.consolidated.comparisons.txt"),
        indir1 = os.path.join(CWD, "inputs", "{sample}_bins1", ""),
        indir2 = os.path.join(CWD, "inputs", "{sample}_bins2", ""),
        o4 = os.path.join(CWD,"3-summary","{sample}","{sample}.comparison_categories.sizes.pdf")
    output:
        os.path.join(CWD, "3-summary", "{sample}", "{sample}.copied_bins.txt")
    conda:
        "envs/python.yml"
    threads:
        1
    params:
        outdir = os.path.join(CWD, "3-summary", "{sample}", "Consolidated_bins", ""),
        method = config['consolidation']['mixed_method'],
        ext = config['consolidation']['file_extension'],
        label1 = config['consolidation']['label1'],
        label2 = config['consolidation']['label2']
    log:
        os.path.join(CWD, "logs", "{sample}.CopyConsolidatedBins.log")
    shell:
        "python scripts/Copy-consolidated-bins.py -t {input.tsv} -i1 {input.indir1} -i2 {input.indir2} "
        "-c {params.method} -e {params.ext} -l1 {params.label1} -l2 {params.label2} -o {params.outdir} "
        "&> {log} && touch {output}"
