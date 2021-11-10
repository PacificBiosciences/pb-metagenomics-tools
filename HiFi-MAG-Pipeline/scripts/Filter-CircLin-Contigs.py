import argparse
import os
import pandas as pd
from Bio import SeqIO

def get_args():
    """
    Get arguments from command line with argparse.
    """
    parser = argparse.ArgumentParser(
        prog='Filter-CircLin-Contigs.py',
        description="""Separate linear and circular contigs into distinct fasta files.""")

    parser.add_argument("-f", "--fasta",
                        required=True,
                        help="Full path to the input fasta file.")
    parser.add_argument("-a", "--assembler",
                        required=True,
                        choices=["hifiasm-meta", "hicanu", "metaflye"],
                        help="Assembler used.")
    parser.add_argument("--metaflye_info",
                        required=False,
                        help="Name of metaflye asembly info file.")
    parser.add_argument("-o1", "--fastalinear",
                        required=True,
                        help="Name of output fasta file (linear).")
    parser.add_argument("-o2", "--fastacircular",
                        required=True,
                        help="Name of output fasta file (circular).")
    parser.add_argument("-o3", "--loglinear",
                        required=True,
                        help="Name of output fasta file (linear).")
    parser.add_argument("-o4", "--logcircular",
                        required=True,
                        help="Name of output fasta file (circular).")

    return parser.parse_args()

def write_headers(f):
    with open(f, 'a') as fh:
        fh.write('Contig\tLength\n')

def parse_hifiasm(fasta, fastalinear, fastacircular, loglinear, logcircular):
    """
    hifiasm-meta contig names will have an "l" or "c" suffix.
    """
    circ_count, lin_count = int(0), int(0)

    with open(fastalinear, 'a') as fhfl, open(fastacircular, 'a') as fhfc:
        with open(loglinear, 'a') as fhll, open(logcircular, 'a') as fhlc:
            for rec in SeqIO.parse(fasta, "fasta"):
                if rec.id.endswith('l'):
                    lin_count += 1
                    fhfl.write(rec.format("fasta"))
                    fhll.write("{}\t{}\n".format(rec.id, len(rec.seq)))
                elif rec.id.endswith('c'):
                    print("circular: {}\n\tlength: {}\n".format(rec.id, len(rec.seq) ))
                    circ_count += 1
                    fhfc.write(rec.format("fasta"))
                    fhlc.write("{}\t{}\n".format(rec.id, len(rec.seq)))

    #catch no-circulars by adding one dummy seq
    if os.stat(fastacircular).st_size == 0:
        with open(fastacircular, 'a') as fh:
            fh.write(">dummyseq\nATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG\n")
        with open(logcircular, 'a') as fh:
            fh.write("{}\t{}\n".format("NA", "0"))

    print("Circular contigs: {:,}".format(circ_count))
    print("Linear contigs: {:,}".format(lin_count))

def parse_hicanu(fasta, fastalinear, fastacircular, loglinear, logcircular):
    """
    hicanu contig descriptions will have an "suggestCircular=yes" or "suggestCircular=no".
    """
    circ_count, lin_count = int(0), int(0)

    with open(fastalinear, 'a') as fhfl, open(fastacircular, 'a') as fhfc:
        with open(loglinear, 'a') as fhll, open(logcircular, 'a') as fhlc:
            for rec in SeqIO.parse(fasta, "fasta"):
                if "suggestCircular=yes" in rec.description:
                    circ_count += 1
                    fhfc.write(rec.format("fasta"))
                    fhlc.write("{}\t{}\n".format(rec.id, len(rec.seq)))
                elif "suggestCircular=no" in rec.description:
                    lin_count += 1
                    fhfl.write(rec.format("fasta"))
                    fhll.write("{}\t{}\n".format(rec.id, len(rec.seq)))

    #catch no-circulars by adding one dummy seq
    if os.stat(fastacircular).st_size == 0:
        with open(fastacircular, 'a') as fh:
            fh.write(">dummyseq\nATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG\n")
        with open(logcircular, 'a') as fh:
            fh.write("{}\t{}\n".format("NA", "0"))

    print("Circular contigs: {:,}".format(circ_count))
    print("Linear contigs: {:,}".format(lin_count))

def parse_metaflye(fasta, metaflye_info, fastalinear, fastacircular, loglinear, logcircular):
    """
    metaflye fasta contains no information.
    This is contained in the SAMPLE-assembly_info.txt file.
    """
    df = pd.read_csv(metaflye_info, sep='\t')
    # this file may have changed symbols for yes, possibilities include a Y or +
    circular_contigs = list(df[df['circ.'].isin(['Y', '+'])]["#seq_name"])

    circ_count, lin_count = int(0), int(0)

    with open(fastalinear, 'a') as fhfl, open(fastacircular, 'a') as fhfc:
        with open(loglinear, 'a') as fhll, open(logcircular, 'a') as fhlc:
            for rec in SeqIO.parse(fasta, "fasta"):
                if rec.id in circular_contigs:
                    circ_count += 1
                    fhfc.write(rec.format("fasta"))
                    fhlc.write("{}\t{}\n".format(rec.id, len(rec.seq)))
                else:
                    lin_count += 1
                    fhfl.write(rec.format("fasta"))
                    fhll.write("{}\t{}\n".format(rec.id, len(rec.seq)))

    #catch no-circulars by adding one dummy seq
    if os.stat(fastacircular).st_size == 0:
        with open(fastacircular, 'a') as fh:
            fh.write(">dummyseq\nATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG\n")
        with open(logcircular, 'a') as fh:
            fh.write("{}\t{}\n".format("NA", "0"))
            
    print("Circular contigs: {:,}".format(circ_count))
    print("Linear contigs: {:,}".format(lin_count))

def main():
    args = get_args()
    write_headers(args.loglinear)
    write_headers(args.logcircular)
    print("Selected assembler: {}\n".format(args.assembler))
    if args.assembler == "hifiasm-meta":
        parse_hifiasm(args.fasta, args.fastalinear, args.fastacircular, args.loglinear, args.logcircular)
    elif args.assembler == "hicanu":
        parse_hicanu(args.fasta, args.fastalinear, args.fastacircular, args.loglinear, args.logcircular)
    elif args.assembler == "metaflye":
        if not os.path.isfile(args.metaflye_info):
            raise IOError("Could not locate assembly info file: {}".format(args.metaflye_info))
        else:
            parse_metaflye(args.fasta, args.metaflye_info, args.fastalinear, args.fastacircular, args.loglinear, args.logcircular)

if __name__ == '__main__':
    main()

"""
Finding circular contigs...

hifiasm-meta:
>s4.ctg000732l
>s11.ctg000015c

hicanu:
>tig00000001 len=5293670 reads=39793 class=contig suggestRepeat=no suggestBubble=no suggestCircular=no
>tig00000481 len=17533 reads=9 class=contig suggestRepeat=no suggestBubble=no suggestCircular=yes

metaFlye:
only available in SAMPLE-assembly_info.txt:

#seq_name	length	cov.	circ.	repeat	mult.	alt_group	graph_path
contig_11909	3733704	14	Y	N	1	*	11909
contig_11404	3650108	58	N	N	2	*	-11400,11404,-11400
"""