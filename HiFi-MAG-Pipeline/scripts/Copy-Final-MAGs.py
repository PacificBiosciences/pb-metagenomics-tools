import argparse
import os
import shutil
import pandas as pd

def get_args():
    """
    Get arguments from command line with argparse.
    """
    parser = argparse.ArgumentParser(
        prog='Copy-Final-MAGs.py',
        description="""Copy MAGs passing filters to final directory.""")
    parser.add_argument("-i", "--mag_summary",
                        required=True,
                        help="The MAG summary file.")
    parser.add_argument("-m", "--magdir",
                        required=True,
                        help="Name of directory containing all MAGs.")
    parser.add_argument("-o", "--outdir",
                        required=True,
                        help="Name of output directory to copy filtered MAGs.")
    return parser.parse_args()

def make_outdir(outdir):
    if not os.path.exists(outdir):
        os.makedirs(outdir, exist_ok=True)

def make_df_get_bins(mag_summary):
    """
    Convert mag_summary file into pandas dataframe, pass bin names to a list
    """
    print("make_df_get_bins: Making dataframe.")
    df = pd.read_csv(mag_summary, sep='\t')
    return df['Name'].tolist()

def write_mags(mags, magdir, outdir):
    """
    Write MAGs passing filters to output directory.
    """
    print("write_mags: Writing final MAG files.")
    mag_count = 0
    if mags:
        for mag in mags:
            shutil.copy(os.path.join(magdir, "{}.fa".format(mag)), outdir)
            mag_count += 1
        print("write_mags: Wrote {:,} MAG files.".format(mag_count))
    else:
        print("write_mags: No MAG files passed filters, skipping copy.".format(mag_count))

def main():
    args = get_args()
    make_outdir(args.outdir)
    mags = make_df_get_bins(args.mag_summary)
    write_mags(mags, args.magdir, args.outdir)

if __name__ == '__main__':
    main()


