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
        prog='Convert_kreport_to_mpa.py',
        description="""Convert a kraken report file into mpa (metaphlan) output format.""")

    parser.add_argument("-i", "--input",
                        required=True,
                        help="A kraken report text file.")
    parser.add_argument("-f", "--format",
                        required=True,
                        choices=['kraken', 'mmseqs'],
                        help="Style of ranks in the kreport, either kraken (K, P, C, etc.) "
                             "or mmseqs (kingdom, phylum, class, etc.).")
    parser.add_argument("-l", "--label",
                        required=True,
                        help="A prefix that will help name the output file (LABEL.mpa.txt).")
    parser.add_argument("--update",
                        required=False,
                        action='store_true',
                        help="Including this flag will cause NCBITaxa to update the taxonomy database.")

    return parser.parse_args()

def activate_ncbi(update=False):
    print("\nActivating NCBI taxonomy database...")
    ncbi = NCBITaxa()
    if update is True:
        print("\tUpdating database...")
        ncbi.update_taxonomy_database()
    return ncbi

def make_filtered_df(infile, rank_style):
    print("Reading in kreport file...")
    df = pd.read_csv(infile, sep = '\t',
                     names = ['proportion', 'cumulative_count', 'level_count', 'rank', 'taxid', 'name'],
                     header=None, comment='#')

    if rank_style == "mmseqs":
        ranks = ['superkingdom', 'phylum', 'class', 'order', 'family', 'genus', 'species', 'strain']
    elif rank_style == "kraken":
        ranks = ['D', 'P', 'C', 'O', 'F', 'G', 'S', 'S1']
    filt_df = df[df['rank'].isin(ranks)]
    return filt_df

def make_lineage_dict(df, ncbi):
    print("Creating lineages...")
    lineage_dict = {}
    for t in list(df['taxid'].unique()):
        lineage = ncbi.get_lineage(t)
        taxid_to_rank_dict = ncbi.get_rank(lineage)
        taxid_to_names_dict = ncbi.get_taxid_translator(lineage)
        relabel_dict = {'superkingdom': 'k__', 'phylum': 'p__', 'class': 'c__',
                        'order': 'o__', 'family': 'f__', 'genus': 'g__',
                        'species': 's__', 'strain': 'ss__'}
        name_list = []
        for taxid in lineage:
            if taxid_to_rank_dict[taxid] in relabel_dict:
                name_list.append("{}{}".format(relabel_dict[taxid_to_rank_dict[taxid]],
                                               taxid_to_names_dict[taxid].replace(" ", "_")))
        name = "|".join(name_list)
        lineage_dict[t] = name
    return lineage_dict

def write_mpa(df, lineage_dict, outname):
    print("Writing kreport file...")
    with open(outname, 'a') as fh:
        for k, v in lineage_dict.items():
            fh.write("{}\t{}\n".format(v, int((df.loc[df['taxid'] == k])['cumulative_count'])))

def main():
    args = get_args()
    ncbi = activate_ncbi(args.update)
    df = make_filtered_df(args.input, args.format)
    lineage_dict = make_lineage_dict(df, ncbi)
    write_mpa(df, lineage_dict, "{}.mpa.txt".format(args.label))
    print("\nDone!\n")

if __name__ == '__main__':
    main()
