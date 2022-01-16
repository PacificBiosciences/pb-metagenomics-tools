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
        prog='Adjust-kreport-taxonomy',
        description="""Update a kraken-style report using the most current NCBI Taxonomy.""")

    parser.add_argument("-i", "--input",
                        required=True,
                        help="A kreport file to update.")
    parser.add_argument("-l", "--label",
                        required=True,
                        help="A prefix that will help name the output files.")
    parser.add_argument("-r", "--readcount",
                        required=True,
                        type=int,
                        help="The total number of reads that were screened to produce the kreport file.")
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

def create_df(infile):
    df = pd.read_csv(infile, sep='\t', names=['Proportion', 'Cumulative_Count', 'Count', 'Rank', 'ID', 'Name'],
                     header=None, skipinitialspace = True)
    print("Number taxa in report: {:,}".format(df.shape[0]))
    filt = df[df['Count'] >= 1]
    print("Number taxa with level count >= 1 in report: {:,}\n".format(filt.shape[0]))
    return filt

def get_taxon_dict(ncbi, df):
    print("Translating taxon names into numerical IDs...")
    #print([i.strip() for i in list(df['Name'].unique())])
    name2taxid = ncbi.get_name_translator(list(df['Name'].unique()))
    taxon_dict = {}
    for k, v in name2taxid.items():
        taxon_dict[k] = {'taxid': v[0]}
    return taxon_dict

def add_ranks(ncbi, k, v):
    lineage = ncbi.get_lineage(v['taxid'])
    taxid_to_rank_dict = ncbi.get_rank(lineage)
    taxid_to_names_dict = ncbi.get_taxid_translator(lineage)
    ranks = ['superkingdom', 'kingdom', 'clade', 'phylum', 'class', 'order', 'family', 'genus', 'species', 'strain']
    temp_dict = {}
    for taxid in lineage:
        if taxid_to_rank_dict[taxid] in ranks:
            temp_dict[taxid_to_rank_dict[taxid]] = {'taxid': taxid, 'name': taxid_to_names_dict[taxid]}
    for r in ranks:
        if r not in temp_dict:
            temp_dict[r] = {'taxid': 'NA', 'name': 'NA'}
    return temp_dict

def write_intermediate_output(taxon_dict, output, label):
    print("Writing intermediate output using {}s...".format(label))
    with open(output, 'a') as fh:
        fh.write("{0}\t{1}\t{2}\t{3}\t{4}\t{5}"
                 "\t{6}\t{7}\t{8}\t{9}\t{10}\t{11}\n".format('Taxon', 'Count', 'superkingdom',
                                                     'kingdom', 'clade', 'phylum', 'class',
                                                     'order', 'family', 'genus', 'species', 'strain'))
        for k, v in taxon_dict.items():
            fh.write("{0}\t{1}\t{2}\t{3}\t{4}\t{5}"
                     "\t{6}\t{7}\t{8}\t{9}\t{10}\t{11}\n".format(k, v['Count'], v['superkingdom'][label],
                                                           v['kingdom'][label], v['clade'][label],
                                                           v['phylum'][label], v['class'][label],
                                                           v['order'][label], v['family'][label],
                                                           v['genus'][label], v['species'][label],
                                                           v['strain'][label]))

def make_lineage_dict(infile):
    print("\nReading intermediate ranks file...")
    lineage_dict = {}
    with open(infile, 'r') as fh:
        next(fh)
        for line in fh:
            parts = line.strip().split('\t')
            badnames = ["k__NA", "p__NA", "c__NA", "o__NA", "f__NA", "g__NA", "s__NA", "ss__NA"]
            relabeled = ["k__{}".format(parts[2]), "p__{}".format(parts[5]),
                         "c__{}".format(parts[6]), "o__{}".format(parts[7]),
                         "f__{}".format(parts[8]), "g__{}".format(parts[9]),
                         "s__{}".format(parts[10]), "ss__{}".format(parts[11])]
            lineage = "|".join([l for l in relabeled if l not in badnames])
            if lineage:
                if lineage in lineage_dict:
                    lineage_dict[lineage]['level_count'] += int(parts[1])
                else:
                    lineage_dict[lineage] = {'level_count': int(parts[1]), 'cumulative_count': int(0)}
    return lineage_dict

def fill_out_lineages(lineage_dict):
    print("Filling out lineage gaps...")
    expanded_dict = {k: v for (k, v) in lineage_dict.items()}
    for k, v in lineage_dict.items():
        expanded_dict[k] = v
        label = ""
        for i in k.split('|'):
            label += i
            if label not in expanded_dict:
                expanded_dict[label] = {'level_count': int(0), 'cumulative_count': int(0)}
            label += "|"
    print("Calculating cumulative counts...")
    for key in expanded_dict.keys():
        expanded_dict[key]['cumulative_count'] = sum([expanded_dict[k]['level_count'] for k in expanded_dict.keys() if k.startswith(key)])
    return expanded_dict

def write_mpa(expanded_dict, outname):
    print("Writing mpa output file...")
    # mpa is 2 columns: full_lineage + cumulative_count
    with open(outname, 'a') as fh:
        for k, v in sorted(expanded_dict.items()):
            fh.write("{}\t{}\n".format(k.replace(" ","_"), v['cumulative_count']))

def write_kreport(expanded_dict, outname, reads, ncbi):
    print("Writing kreport output file...")
    # headers for kreport
    # proportion + cumulative_count + level_count + rank + taxid + name
    with open(outname, 'a') as fh:
        for k, v in sorted(expanded_dict.items()):
            indent_rules = {"K":"", "P":"  ", "C":"    ",
                            "O":"      ", "F":"        ",
                            "G":"          ", "S":"            ",
                            "SS":"              "}
            if '|' in k:
                rank = k.split('|')[-1].split('__')[0].upper()
                name = k.split('|')[-1].split('__')[-1]
            else:
                rank = k.split('__')[0].upper()
                name = k.split('__')[-1]
            taxid = ncbi.get_name_translator([name])[name][0]
            name = indent_rules[rank] + name
            if rank == "SS":
                rank = "S1"
            row_data = [round((float(v['cumulative_count'])/float(reads))*100, 2), v['cumulative_count'], v['level_count'], rank, taxid, name]
            row_string = "\t".join([str(i) for i in row_data])
            fh.write("{}\n".format(row_string))

def main():
    args = get_args()
    ncbi = activate_ncbi(args.update)
    print("\nReading in kreport file...")
    df = create_df(args.input)
    taxon_dict = get_taxon_dict(ncbi, df)
    print("Getting lineage information for all taxa...")
    for k, v in taxon_dict.items():
        # add lineage ranks and names
        v.update(add_ranks(ncbi, k, v))
        # add read counts
        v['Count'] = int( (df.loc[df['Name'] == k])['Count'] )
    write_intermediate_output(taxon_dict, "{}.intermediate.names.txt".format(args.label), 'name')
    write_intermediate_output(taxon_dict, "{}.intermediate.taxid.txt".format(args.label), 'taxid')
    lineage_dict = make_lineage_dict("{}.intermediate.names.txt".format(args.label))
    expanded_dict = fill_out_lineages(lineage_dict)
    write_mpa(expanded_dict, "{}.taxonomy-updated.mpa.txt".format(args.label))
    write_kreport(expanded_dict, "{}.taxonomy-updated.kreport.txt".format(args.label), args.readcount, ncbi)
    os.remove("{}.intermediate.names.txt".format(args.label))
    os.remove("{}.intermediate.taxid.txt".format(args.label))
    print("\nDone!\n")

if __name__ == '__main__':
    main()
