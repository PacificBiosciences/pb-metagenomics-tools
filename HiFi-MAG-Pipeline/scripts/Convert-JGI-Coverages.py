import argparse
import pandas as pd

def get_args():
    """
    Get arguments from command line with argparse.
    """
    parser = argparse.ArgumentParser(
        prog='Convert-JGI-Coverages.py',
        description="""Convert JGI depth files.""")
    parser.add_argument("-i", "--in_jgi",
                        required=True,
                        help="The input JGI depth file (sample.JGI.depth.txt).")
    parser.add_argument("-p", "--passed_bins",
                        required=True,
                        help="Name of output file with list of passed bins.")
    parser.add_argument("-o1", "--out_jgi",
                        required=True,
                        help="Name of output filtered JGI depth file.")
    parser.add_argument("-o2", "--out_maxbin",
                        required=False,
                        default=None,
                        help="Name of output depth file.")

    return parser.parse_args()

def get_avoid_bins(f):
    """
    Format of passed bins file is:

    s4.ctg000005c	complete.1
    s8.ctg000009c	complete.3
    s9.ctg000010c	complete.4
    s14.ctg000015c	complete.6
    s15.ctg000016c	complete.7
    """
    with open(f, 'r') as fh:
        avoid_bins = [line.split('\t')[0] for line in fh]
    print("Found {:,} bins to avoid.".format(len(avoid_bins)))
    return avoid_bins

def make_df(f):
    """
    Get initial pandas dataframe (from JGI depth file)
    """
    print("Making df from JGI depth file.")
    return pd.read_csv(f, sep='\t')

def filter_df(df, avoid_bins):
    """
    Filter out bins that passed completeness test from dataframe.
    """
    print("Filtering JGI depth file.")
    if avoid_bins:
        return df[(~df['contigName'].str.contains("|".join(avoid_bins), regex=True))]
    else:
        return df

def subset_filtered_df(df):
    """
    Create bare bones df for maxbin2.
    """
    print("Creating maxbin df.")
    return df[['contigName', 'totalAvgDepth']]

def write_df_to_csv(df, outname, header=True):
    """
    Write df to output. Toggle header option.
    """
    print("Writing output file: {}.".format(outname))
    df.to_csv(outname, sep='\t', header=header, index=False, float_format="%.4f")

def main():
    args = get_args()
    avoid_bins = get_avoid_bins(args.passed_bins)
    df = make_df(args.in_jgi)
    df_filtered = filter_df(df, avoid_bins)
    write_df_to_csv(df_filtered, args.out_jgi, header=True)
    if args.out_maxbin is not None:
        df_maxbin = subset_filtered_df(df_filtered)
        write_df_to_csv(df_maxbin, args.out_maxbin, header=False)

if __name__ == '__main__':
    main()


