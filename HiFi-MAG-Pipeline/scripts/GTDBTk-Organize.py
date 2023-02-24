import argparse
import os
import numpy as np
import pandas as pd

def get_args():
    """
    Get arguments from command line with argparse.
    """
    parser = argparse.ArgumentParser(
        prog='GTDBTk-Organize.py',
        description="""Grab all summary files from GTDB-Tk and merge.""")
    parser.add_argument("-i", "--input_dir",
                        required=True,
                        help="The full path to the classify directory.")
    parser.add_argument("-o", "--outfile",
                        required=True,
                        help="Name of merged GTDB-Tk summary file to write.")

    return parser.parse_args()

def make_dfs_and_merge(input_dir):
    print("make_dfs_and_merge: Merging tsv files.")
    tsv_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith("summary.tsv")]
    if len(tsv_files) > 1:
        dfs = [pd.read_csv(f, sep='\t', na_filter=False) for f in tsv_files]
        return pd.concat(dfs, axis=0)
    else:
        return pd.read_csv(tsv_files[0], sep='\t', na_filter=False)

def write_merged_df(df, outfile):
    print("write_merged_df: Writing updated tsv file.")
    df.to_csv(outfile, sep='\t', index=False)

def main():
    args = get_args()
    df = make_dfs_and_merge(args.input_dir)
    write_merged_df(df, args.outfile)

if __name__ == '__main__':
    main()


