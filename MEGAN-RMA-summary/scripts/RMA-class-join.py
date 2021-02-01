import argparse
import pandas as pd
from functools import reduce

def get_args():
    """
    Get arguments from command line with argparse.
    """
    parser = argparse.ArgumentParser(
        prog='RMA-class-join.py',
        description="""Summarize database results obtained from MEGAN RMA files.""")

    parser.add_argument("-c", "--counts",
                        required=True,
                        nargs='+',
                        help="The complete set of count files.")
    parser.add_argument("-o", "--output",
                        required=True,
                        help="Name of output file.")
    return parser.parse_args()

def make_df(f):
    """
    Read in dataframe using Class and Sample as column headers, return dataframe.
    """
    temp_df = pd.read_csv(f, sep='\t', names=['Class', '{}'.format(f.split('/')[-1].split('.')[0])], header=None)
    return temp_df

def get_df_list(counts):
    """
    Create a list of the dataframes from the list of file paths supplied.
    """
    df_list = []
    for f in counts:
        df_list.append(make_df(f))
    return df_list

def merge_dfs(df_list):
    """
    Merge the list of dataframes, performing outer joins using the Class column.
    """
    df_merged = reduce(lambda left, right: pd.merge(left, right, on='Class', how='outer'), df_list).fillna(0)
    df_sorted = df_merged.sort_values(['Class'])
    # remove unassigned counts
    filter_unassigned = ((df_sorted['Class'] != "EC;Not assigned;") &
                         (df_sorted['Class'] != "eggNOG;Not assigned;") &
                         (df_sorted['Class'] != "InterPro2GO;Not assigned;") &
                         (df_sorted['Class'] != "SEED;Not assigned;"))
    df_filtered = df_sorted[filter_unassigned]
    return df_filtered

def write_df(df, output):
    """
    Write the dataframe to tab-delimited text file.
    """
    df.to_csv(output, index=False, sep='\t')

def main():
    args = get_args()
    if len(args.counts) >= 2:
        df_list = get_df_list(args.counts)
        df_sorted = merge_dfs(df_list)
    else:
        df = make_df(args.counts[0])
        filter_unassigned = ((df['Class'] != "EC;Not assigned;") &
                         (df['Class'] != "eggNOG;Not assigned;") &
                         (df['Class'] != "InterPro2GO;Not assigned;") &
                         (df['Class'] != "SEED;Not assigned;"))
        df_filtered = df[filter_unassigned]
        df_sorted = df_filtered.sort_values(['Class'])
        

    write_df(df_sorted, args.output)

if __name__ == '__main__':
    main()


