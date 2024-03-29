import os

localrules: 
    ReadCounts, SplitFasta, MergeSam, UpdateNCBI, TaxonomyFiltered, TaxonomyUnfiltered
 
configfile: "config.yaml"

SAMPLES = config['samplenames']
CHUNKS = [str(i) for i in list(range(0,config['diamond']['chunks']))]
CWD = os.getcwd()

rule all:
    input:
        expand(os.path.join(CWD, "5-r2c", "{sample}.{type}.reads.txt"), sample = SAMPLES, 
                type = ["EC", "EGGNOG", "INTERPRO2GO", "SEED"]),
                
        expand(os.path.join(CWD, "6-c2c", "{sample}.{type}.counts.txt"), sample = SAMPLES, 
                type = ["EC", "EGGNOG", "INTERPRO2GO", "SEED"]),
                
        expand(os.path.join(CWD, "5-r2c", "{sample}.{type}.reads.{filt}.txt"), sample = SAMPLES, 
                type = ["NCBI", "GTDB"], filt = ["unfiltered", "filtered"]),
                
        expand(os.path.join(CWD, "6-c2c", "{sample}.{type}.counts.{filt}.txt"), sample = SAMPLES, 
                type = ["NCBI", "GTDB"], filt = ["unfiltered", "filtered"]),

        expand(os.path.join(CWD, "7-kraken-mpa-reports", "{sample}.diamond_megan.kreport.filtered.txt"), sample = SAMPLES),
        expand(os.path.join(CWD, "7-kraken-mpa-reports", "{sample}.diamond_megan.mpa.filtered.txt"), sample = SAMPLES),
        expand(os.path.join(CWD, "7-kraken-mpa-reports", "{sample}.diamond_megan.kreport.unfiltered.txt"), sample = SAMPLES),
        expand(os.path.join(CWD, "7-kraken-mpa-reports", "{sample}.diamond_megan.mpa.unfiltered.txt"), sample = SAMPLES)


rule ReadCounts:
    input: 
        os.path.join(CWD, "inputs", "{sample}.fasta")
    output: 
        os.path.join(CWD, "4-rma", "{sample}.readcounts.txt")
    threads: 2
    benchmark: 
        os.path.join(CWD, "benchmarks", "{sample}.ReadCounts.tsv")
    shell:
        "grep -c '>' {input} > {output}"


##################################################
# Diamond prep and run

rule SplitFasta:
    input: 
        os.path.join(CWD, "inputs", "{sample}.fasta")
    output: 
        temp(expand(os.path.join(CWD, "1-chunks", "{{sample}}.fasta_chunk_000000{piece}"), piece = CHUNKS))
    conda:
        "envs/exonerate.yml"
    threads: 2
    benchmark: 
        os.path.join(CWD, "benchmarks", "{sample}.SplitFasta.tsv")
    params:
        chunks = config['diamond']['chunks'],
        outdir = os.path.join(CWD, "1-chunks", "")
    shell:
        "fastasplit -c {params.chunks} -f {input} -o {params.outdir}"

rule RunDiamond:
    input:
        os.path.join(CWD, "1-chunks", "{sample}.fasta_chunk_000000{piece}")
    output:
        temp(os.path.join(CWD, "2-diamond", "{sample}.{piece}.sam"))
    conda:
        "envs/diamond.yml"
    threads: 
        config['diamond']['threads']
    params:
        db = config['diamond']['db'],
        block = config['diamond']['block_size'],
        hits = config['diamond']['hit_limit']
    log: 
        os.path.join(CWD, "logs", "{sample}.{piece}.RunDiamond.log")
    benchmark: 
        os.path.join(CWD, "benchmarks", "{sample}.{piece}.RunDiamond.tsv")
    shell:
        "diamond blastx -d {params.db} -q {input} -o {output} -f 101 -F 5000 "
        "--range-culling {params.hits} -b {params.block} -p {threads} 2> {log}"

##################################################
# MEGAN RMA prep and run

rule MergeSam:
    input:
        expand(os.path.join(CWD, "2-diamond", "{{sample}}.{piece}.sam"), piece = CHUNKS)
    output:
        os.path.join(CWD, "3-merged", "{sample}.merged.sam")
    conda:
        "envs/python.yml"
    threads: 1
    log: 
        os.path.join(CWD, "logs", "{sample}.MergeSam.log")
    benchmark: 
        os.path.join(CWD, "benchmarks", "{sample}.MergeSam.tsv")
    shell:
        "python scripts/sam-merger-screen-cigar.py -i {input} -o {output} -l {log}"
        
rule MakeRMAfiltered:
    input:
        sam = os.path.join(CWD, "3-merged", "{sample}.merged.sam"),
        reads = os.path.join(CWD, "inputs", "{sample}.fasta")
    output:
        expand(os.path.join(CWD, "4-rma", "{{sample}}_filtered.protein.{mode}.rma"), mode = config['sam2rma']['readassignmentmode'])
    threads: 
        config['sam2rma']['threads']
    params:
        sam2rma = config['sam2rma']['path'],
        db = config['sam2rma']['db'],
        ram = config['sam2rma']['readassignmentmode'],
        ms = config['sam2rma']['minSupportPercent']
    log: 
        os.path.join(CWD, "logs", f"{{sample}}.MakeRMA.filtered.{config['sam2rma']['readassignmentmode']}.log")
    benchmark: 
        os.path.join(CWD, "benchmarks", f"{{sample}}.MakeRMA.filtered.{config['sam2rma']['readassignmentmode']}.tsv")
    shell:
        "{params.sam2rma} -i {input.sam} -r {input.reads} -o {output} -lg -alg longReads "
        "-t {threads} -mdb {params.db} -ram {params.ram} --minSupportPercent {params.ms} "
        "-v 2> {log}"

rule MakeRMAunfiltered:
    input:
        sam =  os.path.join(CWD, "3-merged", "{sample}.merged.sam"),
        reads =  os.path.join(CWD, "inputs", "{sample}.fasta")
    output:
        expand(os.path.join(CWD, "4-rma", "{{sample}}_unfiltered.protein.{mode}.rma"), mode = config['sam2rma']['readassignmentmode'])
    threads: 
        config['sam2rma']['threads']
    params:
        sam2rma = config['sam2rma']['path'],
        db = config['sam2rma']['db'],
        ram = config['sam2rma']['readassignmentmode']
    log: 
         os.path.join(CWD, "logs", f"{{sample}}.MakeRMA.unfiltered.{config['sam2rma']['readassignmentmode']}.log")
    benchmark: 
         os.path.join(CWD, "benchmarks", f"{{sample}}.MakeRMA.unfiltered.{config['sam2rma']['readassignmentmode']}.tsv")
    shell:
        "{params.sam2rma} -i {input.sam} -r {input.reads} -o {output} -lg -alg longReads "
        "-t {threads} -mdb {params.db} -ram {params.ram} --minSupportPercent 0 "
        "-v 2> {log}"

##################################################
# MEGAN RMA summaries - Read classification

rule RunR2CforEC:
    input:
        expand(os.path.join(CWD, "4-rma", "{{sample}}_unfiltered.protein.{mode}.rma"), mode = config['sam2rma']['readassignmentmode'])
    output:
        os.path.join(CWD, "5-r2c", "{sample}.EC.reads.txt")
    threads: 
        config['rma2info']['threads']
    params:
        rma2info = config['rma2info']['path']
    log: 
        os.path.join(CWD, "logs", "{sample}.RunR2CforEC.log")
    benchmark: 
        os.path.join(CWD, "benchmarks", "{sample}.RunR2CforEC.tsv")
    shell:
        "{params.rma2info} -i {input} -o {output} -r2c EC &> {log}"
        
rule RunR2CforEGGNOG:
    input:
        expand(os.path.join(CWD, "4-rma", "{{sample}}_unfiltered.protein.{mode}.rma"), mode = config['sam2rma']['readassignmentmode'])
    output:
        os.path.join(CWD, "5-r2c", "{sample}.EGGNOG.reads.txt")
    threads: 
        config['rma2info']['threads']
    params:
        rma2info = config['rma2info']['path']
    log: 
        os.path.join(CWD, "logs", "{sample}.RunR2CforEGGNOG.log")
    benchmark: 
        os.path.join(CWD, "benchmarks", "{sample}.RunR2CforEGGNOG.tsv")
    shell:
        "{params.rma2info} -i {input} -o {output} -r2c EGGNOG &> {log}"

rule RunR2CforINTERPRO2GO:
    input:
        expand(os.path.join(CWD, "4-rma", "{{sample}}_unfiltered.protein.{mode}.rma"), mode = config['sam2rma']['readassignmentmode'])
    output:
        os.path.join(CWD, "5-r2c", "{sample}.INTERPRO2GO.reads.txt")
    threads: 
        config['rma2info']['threads']
    params:
        rma2info = config['rma2info']['path']
    log: 
        os.path.join(CWD, "logs", "{sample}.RunR2CforINTERPRO2GO.log")
    benchmark: 
        os.path.join(CWD, "benchmarks", "{sample}.RunR2CforINTERPRO2GO.tsv")
    shell:
        "{params.rma2info} -i {input} -o {output} -r2c INTERPRO2GO &> {log}"

rule RunR2CforSEED:
    input:
        expand(os.path.join(CWD, "4-rma", "{{sample}}_unfiltered.protein.{mode}.rma"), mode = config['sam2rma']['readassignmentmode'])
    output:
        os.path.join(CWD, "5-r2c", "{sample}.SEED.reads.txt")
    threads: 
        config['rma2info']['threads']
    params:
        rma2info = config['rma2info']['path']
    log: 
        os.path.join(CWD, "logs", "{sample}.RunR2CforSEED.log")
    benchmark: 
        os.path.join(CWD, "benchmarks", "{sample}.RunR2CforSEED.tsv")
    shell:
        "{params.rma2info} -i {input} -o {output} -r2c SEED &> {log}"     

rule RunR2CforKEGG:
    input:
        expand(os.path.join(CWD, "4-rma", "{{sample}}_unfiltered.protein.{mode}.rma"), mode = config['sam2rma']['readassignmentmode'])
    output:
        os.path.join(CWD, "5-r2c", "{sample}.KEGG.reads.txt")
    threads: 
        config['rma2info']['threads']
    params:
        rma2info = config['rma2info']['path']
    log: 
        os.path.join(CWD, "logs", "{sample}.RunR2CforKEGG.log")
    benchmark: 
        os.path.join(CWD, "benchmarks", "{sample}.RunR2CforKEGG.tsv")
    shell:
        "{params.rma2info} -i {input} -o {output} -r2c KEGG &> {log}"     

rule RunR2CforNCBIfiltered:
    input:
        expand(os.path.join(CWD, "4-rma", "{{sample}}_filtered.protein.{mode}.rma"), mode = config['sam2rma']['readassignmentmode'])
    output:
        os.path.join(CWD, "5-r2c", "{sample}.NCBI.reads.filtered.txt")
    threads: 
        config['rma2info']['threads']
    params:
        rma2info = config['rma2info']['path']
    log: 
        os.path.join(CWD, "logs", "{sample}.RunR2CforNCBIfiltered.log")
    benchmark: 
        os.path.join(CWD, "benchmarks", "{sample}.RunR2CforNCBIfiltered.tsv")
    shell:
        "{params.rma2info} -i {input} -o {output} -r2c Taxonomy -n &> {log}"

rule RunR2CforNCBIunfiltered:
    input:
        expand(os.path.join(CWD, "4-rma", "{{sample}}_unfiltered.protein.{mode}.rma"), mode = config['sam2rma']['readassignmentmode'])
    output:
        os.path.join(CWD, "5-r2c", "{sample}.NCBI.reads.unfiltered.txt")
    threads: 
        config['rma2info']['threads']
    params:
        rma2info = config['rma2info']['path']
    log: 
        os.path.join(CWD, "logs", "{sample}.RunR2CforNCBIunfiltered.log")
    benchmark: 
        os.path.join(CWD, "benchmarks", "{sample}.RunR2CforNCBIunfiltered.tsv")
    shell:
        "{params.rma2info} -i {input} -o {output} -r2c Taxonomy -n &> {log}"

rule RunR2CforGTDBfiltered:
    input:
        expand(os.path.join(CWD, "4-rma", "{{sample}}_filtered.protein.{mode}.rma"), mode = config['sam2rma']['readassignmentmode'])
    output:
        os.path.join(CWD, "5-r2c", "{sample}.GTDB.reads.filtered.txt")
    threads: 
        config['rma2info']['threads']
    params:
        rma2info = config['rma2info']['path']
    log: 
        os.path.join(CWD, "logs", "{sample}.RunR2CforGTDBfiltered.log")
    benchmark: 
        os.path.join(CWD, "benchmarks", "{sample}.RunR2CforGTDBfiltered.tsv")
    shell:
        "{params.rma2info} -i {input} -o {output} -r2c GTDB -n &> {log}"

rule RunR2CforGTDBunfiltered:
    input:
        expand(os.path.join(CWD, "4-rma", "{{sample}}_unfiltered.protein.{mode}.rma"), mode = config['sam2rma']['readassignmentmode'])
    output:
        os.path.join(CWD, "5-r2c", "{sample}.GTDB.reads.unfiltered.txt")
    threads: 
        config['rma2info']['threads']
    params:
        rma2info = config['rma2info']['path']
    log: 
        os.path.join(CWD, "logs", "{sample}.RunR2CforGTDBunfiltered.log")
    benchmark: 
        os.path.join(CWD, "benchmarks", "{sample}.RunR2CforGTDBunfiltered.tsv")
    shell:
        "{params.rma2info} -i {input} -o {output} -r2c GTDB -n &> {log}"



##################################################
# MEGAN RMA summaries - Class counts

rule RunC2CforEC:
    input:
        expand(os.path.join(CWD, "4-rma", "{{sample}}_unfiltered.protein.{mode}.rma"), mode = config['sam2rma']['readassignmentmode'])
    output:
        os.path.join(CWD, "6-c2c", "{sample}.EC.counts.txt")
    threads: 
        config['rma2info']['threads']
    params:
        rma2info = config['rma2info']['path']
    log: 
        os.path.join(CWD, "logs", "{sample}.RunC2CforEC.log")
    benchmark: 
        os.path.join(CWD, "benchmarks", "{sample}.RunC2CforEC.tsv")
    shell:
        "{params.rma2info} -i {input} -o {output} -c2c EC -p &> {log}"

rule RunC2CforEGGNOG:
    input:
        expand(os.path.join(CWD, "4-rma", "{{sample}}_unfiltered.protein.{mode}.rma"), mode = config['sam2rma']['readassignmentmode'])
    output:
        os.path.join(CWD, "6-c2c", "{sample}.EGGNOG.counts.txt")
    threads: 
        config['rma2info']['threads']
    params:
        rma2info = config['rma2info']['path']
    log: 
        os.path.join(CWD, "logs", "{sample}.RunC2CforEGGNOG.log")
    benchmark: 
        os.path.join(CWD, "benchmarks", "{sample}.RunC2CforEGGNOG.tsv")
    shell:
        "{params.rma2info} -i {input} -o {output} -c2c EGGNOG -p &> {log}"

rule RunC2CforINTERPRO2GO:
    input:
        expand(os.path.join(CWD, "4-rma", "{{sample}}_unfiltered.protein.{mode}.rma"), mode = config['sam2rma']['readassignmentmode'])
    output:
        os.path.join(CWD, "6-c2c", "{sample}.INTERPRO2GO.counts.txt")
    threads: 
        config['rma2info']['threads']
    params:
        rma2info = config['rma2info']['path']
    log: 
        os.path.join(CWD, "logs", "{sample}.RunC2CforINTERPRO2GO.log")
    benchmark: 
        os.path.join(CWD, "benchmarks", "{sample}.RunC2CforINTERPRO2GO.tsv")
    shell:
        "{params.rma2info} -i {input} -o {output} -c2c INTERPRO2GO -p &> {log}"

rule RunC2CforSEED:
    input:
        expand(os.path.join(CWD, "4-rma", "{{sample}}_unfiltered.protein.{mode}.rma"), mode = config['sam2rma']['readassignmentmode'])
    output:
        os.path.join(CWD, "6-c2c", "{sample}.SEED.counts.txt")
    threads: 
        config['rma2info']['threads']
    params:
        rma2info = config['rma2info']['path']
    log: 
        os.path.join(CWD, "logs", "{sample}.RunC2CforSEED.log")
    benchmark: 
        os.path.join(CWD, "benchmarks", "{sample}.RunC2CforSEED.tsv")
    shell:
        "{params.rma2info} -i {input} -o {output} -c2c SEED -p &> {log}"

rule RunC2CforKEGG:
    input:
        expand(os.path.join(CWD, "4-rma", "{{sample}}_unfiltered.protein.{mode}.rma"), mode = config['sam2rma']['readassignmentmode'])
    output:
        os.path.join(CWD, "6-c2c", "{sample}.KEGG.counts.txt")
    threads: 
        config['rma2info']['threads']
    params:
        rma2info = config['rma2info']['path']
    log: 
        os.path.join(CWD, "logs", "{sample}.RunC2CforKEGG.log")
    benchmark: 
        os.path.join(CWD, "benchmarks", "{sample}.RunC2CforKEGG.tsv")
    shell:
        "{params.rma2info} -i {input} -o {output} -c2c KEGG -p &> {log}"     

rule RunC2CforGTDBfiltered:
    input:
        expand(os.path.join(CWD, "4-rma", "{{sample}}_filtered.protein.{mode}.rma"), mode = config['sam2rma']['readassignmentmode'])
    output:
        os.path.join(CWD, "6-c2c", "{sample}.GTDB.counts.filtered.txt")
    threads: 
        config['rma2info']['threads']
    params:
        rma2info = config['rma2info']['path']
    log: 
        os.path.join(CWD, "logs", "{sample}.RunC2CforGTDBfiltered.log")
    benchmark: 
        os.path.join(CWD, "benchmarks", "{sample}.RunC2CforGTDBfiltered.tsv")
    shell:
        "{params.rma2info} -i {input} -o {output} -c2c GTDB -n &> {log}"

rule RunC2CforGTDBunfiltered:
    input:
        expand(os.path.join(CWD, "4-rma", "{{sample}}_unfiltered.protein.{mode}.rma"), mode = config['sam2rma']['readassignmentmode'])
    output:
        os.path.join(CWD, "6-c2c", "{sample}.GTDB.counts.unfiltered.txt")
    threads: 
        config['rma2info']['threads']
    params:
        rma2info = config['rma2info']['path']
    log: 
        os.path.join(CWD, "logs", "{sample}.RunC2CforGTDBunfiltered.log")
    benchmark: 
        os.path.join(CWD, "benchmarks", "{sample}.RunC2CforGTDBunfiltered.tsv")
    shell:
        "{params.rma2info} -i {input} -o {output} -c2c GTDB -n &> {log}"

rule RunC2CforNCBIfiltered:
    input:
        expand(os.path.join(CWD, "4-rma", "{{sample}}_filtered.protein.{mode}.rma"), mode = config['sam2rma']['readassignmentmode'])
    output:
        os.path.join(CWD, "6-c2c", "{sample}.NCBI.counts.filtered.txt")
    threads: 
        config['rma2info']['threads']
    params:
        rma2info = config['rma2info']['path']
    log: 
        os.path.join(CWD, "logs", "{sample}.RunC2CforNCBIfiltered.log")
    benchmark: 
        os.path.join(CWD, "benchmarks", "{sample}.RunC2CforNCBIfiltered.tsv")
    shell:
        "{params.rma2info} -i {input} -o {output} -c2c Taxonomy -n -r &> {log}"
        
rule RunC2CforNCBIunfiltered:
    input:
        expand(os.path.join(CWD, "4-rma", "{{sample}}_unfiltered.protein.{mode}.rma"), mode = config['sam2rma']['readassignmentmode'])
    output:
        os.path.join(CWD, "6-c2c", "{sample}.NCBI.counts.unfiltered.txt")
    threads: 
        config['rma2info']['threads']
    params:
        rma2info = config['rma2info']['path']
    log: 
        os.path.join(CWD, "logs", "{sample}.RunC2CforNCBIunfiltered.log")
    benchmark: 
        os.path.join(CWD, "benchmarks", "{sample}.RunC2CforNCBIunfiltered.tsv")
    shell:
        "{params.rma2info} -i {input} -o {output} -c2c Taxonomy -n -r &> {log}"

##################################################
# Make taxonomic reports

rule UpdateNCBI:
    input:
        expand(os.path.join(CWD, "6-c2c", "{sample}.NCBI.counts.unfiltered.txt"), sample = SAMPLES)
    output:
        dummy = os.path.join(CWD, "7-kraken-mpa-reports", "NCBI-updated.txt"),
        taxdump = temp(os.path.join(CWD, "taxdump.tar.gz"))
    conda:
        "envs/python.yml"
    threads: 
        1
    log: 
        os.path.join(CWD, "logs", "UpdateNCBI.prot.log")
    benchmark: 
        os.path.join(CWD, "benchmarks", "UpdateNCBI.prot.tsv")
    shell:
        "python scripts/Run_ete3_NCBI_update.py -i {input} -o {output.dummy} &> {log}"

rule TaxonomyUnfiltered:
    input:
        c2c = os.path.join(CWD, "6-c2c", "{sample}.NCBI.counts.unfiltered.txt"),
        ncbiready = os.path.join(CWD, "7-kraken-mpa-reports", "NCBI-updated.txt"),
        taxdump = os.path.join(CWD, "taxdump.tar.gz"),
        readcount = os.path.join(CWD, "4-rma", "{sample}.readcounts.txt")
    output:
        inter1 = temp(os.path.join(CWD, "7-kraken-mpa-reports", "{sample}.diamond_megan.unfiltered.taxnames.txt")),
        inter2 = temp(os.path.join(CWD, "7-kraken-mpa-reports", "{sample}.diamond_megan.unfiltered.taxids.txt")),
        kreport = os.path.join(CWD, "7-kraken-mpa-reports", "{sample}.diamond_megan.kreport.unfiltered.txt"),
        mpa = os.path.join(CWD, "7-kraken-mpa-reports", "{sample}.diamond_megan.mpa.unfiltered.txt")
    conda:
        "envs/python.yml"
    threads: 
        1
    log: 
        os.path.join(CWD, "logs", "{sample}.TaxonomyUnfilteredlog")
    benchmark: 
        os.path.join(CWD, "benchmarks", "{sample}.TaxonomyUnfiltered.tsv")
    shell:
        "python scripts/Convert_MEGAN_RMA_NCBI_c2c-snake.py -i {input.c2c} -o1 {output.inter1} "
        "-o2 {output.inter2} -m {output.mpa} -k {output.kreport} -r {input.readcount} &> {log}"

rule TaxonomyFiltered:
    input:
        c2c = os.path.join(CWD, "6-c2c", "{sample}.NCBI.counts.filtered.txt"),
        ncbiready = os.path.join(CWD, "7-kraken-mpa-reports", "NCBI-updated.txt"),
        taxdump = os.path.join(CWD, "taxdump.tar.gz"),
        readcount = os.path.join(CWD, "4-rma", "{sample}.readcounts.txt")
    output:
        inter1 = temp(os.path.join(CWD, "7-kraken-mpa-reports", "{sample}.diamond_megan.filtered.taxnames.txt")),
        inter2 = temp(os.path.join(CWD, "7-kraken-mpa-reports", "{sample}.diamond_megan.filtered.taxids.txt")),
        kreport = os.path.join(CWD, "7-kraken-mpa-reports", "{sample}.diamond_megan.kreport.filtered.txt"),
        mpa = os.path.join(CWD, "7-kraken-mpa-reports", "{sample}.diamond_megan.mpa.filtered.txt")
    conda:
        "envs/python.yml"
    threads: 
        1
    log: 
        os.path.join(CWD, "logs", "{sample}.TaxonomyFilteredlog")
    benchmark: 
        os.path.join(CWD, "benchmarks", "{sample}.TaxonomyFiltered.tsv")
    shell:
        "python scripts/Convert_MEGAN_RMA_NCBI_c2c-snake.py -i {input.c2c} -o1 {output.inter1} "
        "-o2 {output.inter2} -m {output.mpa} -k {output.kreport} -r {input.readcount} &> {log}"
