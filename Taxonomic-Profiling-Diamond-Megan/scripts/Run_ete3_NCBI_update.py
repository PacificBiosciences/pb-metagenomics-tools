import argparse
import os
import ete3
import pandas as pd
from ete3 import NCBITaxa

def get_args():
    """
    Get arguments from command line with argparse.
    """
    parser = argparse.ArgumentParser(
        prog='Run_ete3_NCBI_update.py',
        description="""More or less make sure ete3 NCBI taxonomy will work with snakemake.""")

    parser.add_argument("-i", "--input",
                        required=True,
                        nargs='+',
                        help="This is a dummy argument.")
    parser.add_argument("-o", "--outname",
                        required=True,
                        help="The name of intermediate file to write after script runs.")

    return parser.parse_args()

def activate_ncbi(update=True):
    print("\nActivating NCBI taxonomy database...")
    ncbi = NCBITaxa()
    if update is True:
        print("\tUpdating database...")
        ncbi.update_taxonomy_database()
    return ncbi

def main():
    args = get_args()
    ncbi = activate_ncbi()
    with open(args.outname, 'a') as fh:
        fh.write("NCBI-taxonomy done updating.")
    print("\nDone!\n")

if __name__ == '__main__':
    main()
