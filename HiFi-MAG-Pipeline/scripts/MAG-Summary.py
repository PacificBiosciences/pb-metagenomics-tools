import argparse
import os
import numpy as np
import pandas as pd

def get_args():
    """
    Get arguments from command line with argparse.
    """
    parser = argparse.ArgumentParser(
        prog='MAG-Summary.py',
        description="""Grab all summary files from GTDB-Tk and merge.""")
    parser.add_argument("-g", "--gtdb_summary",
                        required=True,
                        help="Full path to merged GTDB-Tk summary file.")
    parser.add_argument("-c", "--checmk2_summary",
                        required=True,
                        help="Full path to CheckM2 summary file.")
    parser.add_argument("-o", "--outfile",
                        required=True,
                        help="Name of combined summary file to write.")

    return parser.parse_args()

def make_gtdb_df(f):
    print("make_gtdb_df: Making GTDB-TK df.")
    return pd.read_csv(f, sep='\t', na_filter=False)

def make_checkm2_df(f):
    print("make_checkm2_df: Making CheckM2 df.")
    df = pd.read_csv(f, sep='\t')
    return df[(df['Status'] == "Pass")]

def merge_dfs(df_checkm2, df_gtdb):
    print("merge_dfs: Merging dataframes.")
    df_merged = pd.merge(df_checkm2, df_gtdb, left_on='Name', right_on='user_genome')
    df_trim = df_merged[['Name', 'Completeness', 'Contamination', 'Contig_Number', 'Contig_Names', 'Contig_Lengths',
                         'Contig_Depths', 'Avg_Depth', 'Coding_Density','Average_Gene_Length', 'Genome_Size', 'GC_Content',
                         'Total_Coding_Sequences', 'classification', 'fastani_reference', 'closest_placement_ani',
                         'closest_placement_af', 'classification_method', 'note',
                         'other_related_references(genome_id,species_name,radius,ANI,AF)','warnings']].copy()
    print("merge_dfs: Sorting dataframe.")
    df_trim.sort_values(by=['Contig_Number', 'Completeness'], ascending=[True,False], inplace=True)
    return df_trim

def write_df(df, outfile):
    print("write_df: Writing output file.")
    df.to_csv(outfile, sep='\t', index=False)

def main():
    args = get_args()
    df_checkm2 = make_checkm2_df(args.checmk2_summary)
    df_gtdb = make_gtdb_df(args.gtdb_summary)
    df_merged = merge_dfs(df_checkm2, df_gtdb)
    write_df(df_merged, args.outfile)

if __name__ == '__main__':
    main()


