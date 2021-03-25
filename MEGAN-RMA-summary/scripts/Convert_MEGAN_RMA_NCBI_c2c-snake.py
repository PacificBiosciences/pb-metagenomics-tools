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
        prog='Convert_RMA_NCBI_c2c.py',
        description="""Convert a NCBI c2c file obtained from a read-count MEGAN6 RMA file 
        into an mpa (metaphlan) and kreport (kraken) output format.""")

    parser.add_argument("-i", "--input",
                        required=True,
                        help="An NCBI 'c2c' text file obtained from a read-count MEGAN6 "
                             "RMA file using the rma2info program "
                             "(rma2info -i input.RMA -o NCBI.c2c.txt -c2c Taxonomy -n -r)")
    parser.add_argument("-o1", "--outname1",
                        required=True,
                        help="The name of intermediate output file 1, which contains taxon names "
                             "(e.g., SAMPLE.names.txt).")
    parser.add_argument("-o2", "--outname2",
                        required=True,
                        help="The name of intermediate output file 2, which contains taxon id codes "
                             "(e.g., SAMPLE.codes.txt).")
    parser.add_argument("-m", "--mpa",
                        required=True,
                        help="The name of the mpa formatted output file (e.g., SAMPLE.mpa.txt).")
    parser.add_argument("-k", "--kreport",
                        required=True,
                        help="The name of the kreport formatted output file (e.g., SAMPLE.kreport.txt).")
    parser.add_argument("-r", "--readsfile",
                        required=True,
                        help="The sample:read count txt file.")
    parser.add_argument("--update",
                        required=False,
                        action='store_true',
                        help="Including this flag will cause NCBITaxa to update the taxonomy database.")

    return parser.parse_args()

def activate_ncbi(update=False):
    print("\nactivate_ncbi: Activating NCBI taxonomy database...")
    ncbi = NCBITaxa()
    if update is True:
        print("\tUpdating database...")
        ncbi.update_taxonomy_database()
    return ncbi

def get_taxon_dict(ncbi, df):
    print("get_taxon_dict: Translating taxon names into numerical IDs...")
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
    print("write_intermediate_output: Writing intermediate output using {}s...".format(label))
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
    print("\nmake_lineage_dict: Reading intermediate ranks file...")
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
                lineage_dict[lineage] = {'level_count': int(parts[1]), 'cumulative_count': int(0)}
    return lineage_dict

def fill_out_lineages(lineage_dict):
    print("fill_out_lineages: Filling out lineage gaps...")
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
    print("write_mpa: Writing mpa output file...")
    # mpa is 2 columns: full_lineage + cumulative_count
    with open(outname, 'a') as fh:
        for k, v in sorted(expanded_dict.items()):
            fh.write("{}\t{}\n".format(k.replace(" ","_"), v['cumulative_count']))

def get_readcount(c2c, rcfile):
    # c2c is labeled as: 2-c2c/{sample}.NCBI.counts.prot.txt
    sample = c2c.split('/')[-1].split('.')[0]
    print("get_readcount: Identified sample {}".format(sample))
    rc_dict = {}
    with open(rcfile, 'r') as fh:
        for line in fh:
            rc_dict[line.strip().split()[0]] = int(line.strip().split()[1])
            print("get_readcount: parsed line - {}, {}".format(line.strip().split()[0], line.strip().split()[1]))
    return rc_dict[sample]


def write_kreport(expanded_dict, outname, reads, ncbi):
    print("write_kreport: Writing kreport output file...")
    # headers for kreport
    # proportion + cumulative_count + level_count + rank + taxid + name
    with open(outname, 'a') as fh:
        for k, v in sorted(expanded_dict.items()):
            indent_rules = {"K":"", "P":"  ", "C":"    ",
                            "O":"      ", "F":"        ",
                            "G":"          ", "S":"          ",
                            "SS":"            "}
            if '|' in k:
                rank = k.split('|')[-1].split('_')[0].upper()
                name = k.split('|')[-1].split('_')[-1]
            else:
                rank = k.split('_')[0].upper()
                name = k.split('_')[-1]
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
    print("\npandas: Reading in c2c file...")
    df = pd.read_csv(args.input, sep='\t', names=['Level', 'Name', 'Count'], header=None)
    taxon_dict = get_taxon_dict(ncbi, df)
    print("add_ranks: Getting lineage information for all taxa...")
    for k, v in taxon_dict.items():
        # add lineage ranks and names
        v.update(add_ranks(ncbi, k, v))
        # add read counts
        v['Count'] = int((df.loc[df['Name'] == k])['Count'])
    write_intermediate_output(taxon_dict, args.outname1, 'name')
    write_intermediate_output(taxon_dict, args.outname2, 'taxid')
    lineage_dict = make_lineage_dict(args.outname1)
    expanded_dict = fill_out_lineages(lineage_dict)
    write_mpa(expanded_dict, args.mpa)
    readcount = get_readcount(args.input, args.readsfile)
    write_kreport(expanded_dict, args.kreport, readcount, ncbi)
    print("\nDone!\n")

if __name__ == '__main__':
    main()
