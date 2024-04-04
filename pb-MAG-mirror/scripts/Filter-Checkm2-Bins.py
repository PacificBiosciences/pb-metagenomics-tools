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
        description="""Identify good bins from checkm2 scores, add some additional info to the tsv.""")
    parser.add_argument("-i1", "--input_tsv1",
                        required=True,
                        help="The checkm2 quality tsv file 1.")
    parser.add_argument("-i2", "--input_tsv2",
                        required=True,
                        help="The checkm2 quality tsv file 2.")
    parser.add_argument("-b1", "--bin_dir1",
                        required=True,
                        help="Full path to directory containing bins1.")
    parser.add_argument("-b2", "--bin_dir2",
                        required=True,
                        help="Full path to directory containing bins2.")
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
    parser.add_argument("-t", "--target_outfile",
                        required=True,
                        help="Name of target file to write.")
    parser.add_argument("-u1", "--updated_tsv1",
                        required=True,
                        help="Name of updated tsv file1 to write.")
    parser.add_argument("-u2", "--updated_tsv2",
                        required=True,
                        help="Name of updated tsv file2 to write.")

    return parser.parse_args()

def make_checkm_df(checkm):
    """
    Convert checkm2 quality_report.tsv file into pandas dataframe.
    """
    print("make_checkm_df: Making checkm2 dataframe.")
    return pd.read_csv(checkm, sep='\t')

def add_contig_numbers_and_status(df, bin_dir, min_completeness, max_contamination, max_contigs):
    """
    Make a list of the contig counts for all bins.
    Turn this list into a new column.
    """
    print("add_contig_numbers_and_status: Adding contig numbers and assessing Pass/Fail filtering status.")
    # count contigs per bin
    # open each fasta and scan to get numbers, append to list
    counts, contigs, lengths = [], [], []

    if os.path.exists(os.path.join(bin_dir, "{}.fa".format(df['Name'].tolist()[0]))):
        ext = "fa"
    elif os.path.exists(os.path.join(bin_dir, "{}.fasta".format(df['Name'].tolist()[0]))):
        ext = "fasta"
    elif os.path.exists(os.path.join(bin_dir, "{}.fna".format(df['Name'].tolist()[0]))):
        ext = "fna"
    else:
        raise ValueError("Unrecognized file extension - only .fa, .fna, and .fasta are accepted.")

    for b in df['Name'].tolist():
        filename = os.path.join(bin_dir, "{}.{}".format(b, ext))
        counts.append(sum([1 for rec in SeqIO.parse(filename, 'fasta')]))
        contigs.append(", ".join([rec.id for rec in SeqIO.parse(filename, 'fasta')]))
        lengths.append(", ".join([str(len(rec)) for rec in SeqIO.parse(filename, 'fasta')]))

    # add contig counts as a column
    df.insert(loc=3, column='Contig_Number', value=pd.Series(counts))
    df.insert(loc=4, column='Contig_Names', value=pd.Series(contigs))
    df.insert(loc=5, column='Contig_Lengths', value=pd.Series(lengths))
    # add a new column for Pass/Fail based on filtering conditions
    search = np.where((df['Completeness'] >= min_completeness)
                       & (df['Contamination'] <= max_contamination)
                       & (df['Contig_Number'] <= max_contigs), "Pass", "Fail")
    df.insert(loc=6, column='Status', value=search)
    df.sort_values(by=['Status', 'Contig_Number', 'Completeness'], ascending=[False, True,False], inplace=True)
    print("add_contig_numbers_and_status: Done.")

def get_passing_bins(df):
    """
    Filter checkm2 dataframe to obtain a list of names of all bins with > minimum completeness value.
    Why is the default completeness 93? In binny they have it set it to 92.5, so some precendent.
    """
    print("get_passing_bins: Identifying bins passing filters.")
    return df[(df['Status'] == "Pass")]['Name'].tolist()

def write_fork_target_file(passing_bins1, passing_bins2, target_outfile):
    """
    Write the target file. This just has the number of bins passing filtering.
    """
    print("write_fork_target_file: Writing fork target file.")
    with open(target_outfile, 'a') as fh:
        fh.write("{}\n{}".format(len(passing_bins1), len(passing_bins2)))

def write_updated_tsv_file(df, updated_tsv):
    """
    Write updated tsv file with the additional information (e.g., contig contents stuff).
    """
    print("write_updated_tsv_file: Writing updated tsv file.")
    df.to_csv(updated_tsv, sep='\t', index=False)

def main():
    args = get_args()
    df1 = make_checkm_df(args.input_tsv1)
    df2 = make_checkm_df(args.input_tsv2)
    add_contig_numbers_and_status(df1, args.bin_dir1, args.min_completeness, args.max_contamination, args.max_contigs)
    add_contig_numbers_and_status(df2, args.bin_dir2, args.min_completeness, args.max_contamination, args.max_contigs)
    passing_bins1 = get_passing_bins(df1)
    passing_bins2 = get_passing_bins(df2)
    write_fork_target_file(passing_bins1, passing_bins2, args.target_outfile)
    write_updated_tsv_file(df1, args.updated_tsv1)
    write_updated_tsv_file(df2, args.updated_tsv2)

if __name__ == '__main__':
    main()


