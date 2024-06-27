import argparse
import os
import numpy as np
import pandas as pd
from Bio import SeqIO

def get_args():
    """
    Get arguments from command line with argparse.
    """
    parser = argparse.ArgumentParser(
        prog='Filter-Checkm2-Bins.py',
        description="""Identify good bins from checkm2 scores.""")
    parser.add_argument("-i", "--input_tsv",
                        required=True,
                        help="The checkm2 quality tsv file.")
    parser.add_argument("-b", "--bin_dir",
                        required=True,
                        help="Full path to directory containing bins.")
    parser.add_argument("-d", "--depth_file",
                        required=True,
                        help="The JGI depth file.")
    parser.add_argument("-c1", "--min_completeness",
                        required=False,
                        type=int,
                        default=70,
                        help="The minimum threshold for completeness (integer; a percent).")
    parser.add_argument("-c2", "--max_contamination",
                        required=False,
                        type=int,
                        default=10,
                        help="The maximum threshold for contamination (integer; a percent).")
    parser.add_argument("-c3", "--max_contigs",
                        required=False,
                        type=int,
                        default=20,
                        help="The maximum number of contigs allowed in a genome bin (integer).")
    parser.add_argument("-o", "--gtdb_outfile",
                        required=True,
                        help="Name of GTDB-Tk batch file to write.")
    parser.add_argument("-t", "--target_outfile",
                        required=True,
                        help="Name of target file to write.")
    parser.add_argument("-u", "--updated_tsv",
                        required=True,
                        help="Name of updated tsv file to write.")

    return parser.parse_args()

def make_checkm_df(checkm):
    """
    Convert checkm2 quality_report.tsv file into pandas dataframe.
    """
    print("make_checkm_df: Making checkm2 dataframe.")
    return pd.read_csv(checkm, sep='\t')

def make_depth_dict(depth_file):
    """
    Convert checkm2 quality_report.tsv file into pandas dataframe.
    """
    print("make_depth_dict: Making depth dictionary.")
    depth_dict = {}
    with open(depth_file, 'r') as fh:
        # skip header
        next(fh)
        for line in fh:
            depth_dict[line.split('\t')[0]] = str(int(float(line.split('\t')[2])))
    return depth_dict

def add_contig_numbers_and_status(df, depth_dict, bin_dir, min_completeness, max_contamination, max_contigs):
    """
    Make a list of the contig counts for all bins.
    Turn this list into a new column.
    """
    print("add_contig_numbers_and_status: Adding contig numbers and assessing Pass/Fail filtering status.")
    # count contigs per bin
    # open each fasta and scan to get numbers, append to list
    counts, contigs, lengths, depths, avgdepths = [], [], [], [], []
    for b in df['Name'].tolist():
        filename = os.path.join(bin_dir, "{}.fa".format(b))
        counts.append(sum([1 for rec in SeqIO.parse(filename, 'fasta')]))
        contigs.append(", ".join([rec.id for rec in SeqIO.parse(filename, 'fasta')]))
        lengths.append(", ".join([str(len(rec)) for rec in SeqIO.parse(filename, 'fasta')]))
        depths.append(", ".join([depth_dict[rec.id] for rec in SeqIO.parse(filename, 'fasta')]))
        int_depths = [int(depth_dict[rec.id]) for rec in SeqIO.parse(filename, 'fasta')]
        avgdepths.append(sum(int_depths) // len(int_depths))

    # add contig counts as a column
    df.insert(loc=3, column='Contig_Number', value=pd.Series(counts))
    df.insert(loc=4, column='Contig_Names', value=pd.Series(contigs))
    df.insert(loc=5, column='Contig_Lengths', value=pd.Series(lengths))
    df.insert(loc=6, column='Contig_Depths', value=pd.Series(depths))
    df.insert(loc=7, column='Avg_Depth', value=pd.Series(avgdepths))
    # add a new column for Pass/Fail based on filtering conditions
    search = np.where((df['Completeness'] >= min_completeness)
                       & (df['Contamination'] <= max_contamination)
                       & (df['Contig_Number'] <= max_contigs), "Pass", "Fail")
    df.insert(loc=8, column='Status', value=search)
    df.sort_values(by=['Status'], ascending=False, inplace=True)
    print("add_contig_numbers_and_status: Done.")

def get_passing_bins(df):
    """
    Filter checkm2 dataframe to obtain a list of names of all bins with > minimum completeness value.
    Why is the default completeness 93? In binny they have it set it to 92.5, so some precendent.
    """
    print("get_passing_bins: Identifying bins passing filters.")
    return df[(df['Status'] == "Pass")]['Name'].tolist()

def write_gtdb_batch_file(passing_bins, bin_dir, gtdb_outfile):
    """
    Write the GTDB-Tk batch file.

    Format of batch file:
    /PATH/TO/4-DAStool/Drain_Revio/Drain_Revio_DASTool_bins/circular.2.fa	circular.2
    /PATH/TO/4-DAStool/Drain_Revio/Drain_Revio_DASTool_bins/circular.3.fa	circular.3
    /PATH/TO/4-DAStool/Drain_Revio/Drain_Revio_DASTool_bins/circular.4.fa	circular.4
    """
    print("write_gtdb_batch_file: Writing GTDB batch file.")
    print("write_gtdb_batch_file: {:,} bins passed filtering.".format(len(passing_bins)))
    if passing_bins:
        with open(gtdb_outfile, 'a') as fh:
            for bin in passing_bins:
                filepath = os.path.join(bin_dir, "{}.fa".format(bin))
                fh.write("{}\t{}\n".format(filepath, bin))
    else:
        with open(gtdb_outfile, 'a') as fh:
            fh.write("No bins passed filtering!")

def write_fork_target_file(passing_bins, target_outfile):
    """
    Write the target file. This just has the number of bins passing filtering.
    """
    print("write_fork_target_file: Writing fork target file.")
    with open(target_outfile, 'a') as fh:
        fh.write("{}".format(len(passing_bins)))

def write_updated_tsv_file(df, updated_tsv):
    """
    Write the target file. This just has the number of bins passing filtering.
    """
    print("write_updated_tsv_file: Writing updated tsv file.")
    df.to_csv(updated_tsv, sep='\t', index=False)

def main():
    args = get_args()
    df = make_checkm_df(args.input_tsv)
    depth_dict = make_depth_dict(args.depth_file)
    add_contig_numbers_and_status(df, depth_dict, args.bin_dir, args.min_completeness, args.max_contamination, args.max_contigs)
    passing_bins = get_passing_bins(df)
    write_gtdb_batch_file(passing_bins, args.bin_dir, args.gtdb_outfile)
    write_fork_target_file(passing_bins, args.target_outfile)
    write_updated_tsv_file(df, args.updated_tsv)

if __name__ == '__main__':
    main()


