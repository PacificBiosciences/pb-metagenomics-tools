import argparse
import os
import pandas as pd

def get_args():
    """
    Get arguments from command line with argparse.
    """
    parser = argparse.ArgumentParser(
        prog='Perform-bin-comparisons.py',
        description="""Use filtered tsv files from Filter-Checkm2-Bins.py to perform comparison and consolidation.""")
    parser.add_argument("-i1", "--input_tsv1",
                        required=True,
                        help="The filtered checkm2 quality tsv file 1.")
    parser.add_argument("-i2", "--input_tsv2",
                        required=True,
                        help="The filtered checkm2 quality tsv file 2.")
    parser.add_argument("-c", "--consolidation_method",
                        required=True,
                        choices=["unify", "bins1", "bins2"],
                        help="Strategy to select mixed bins. See documentation.")
    parser.add_argument("-o", "--outdir",
                        required=True,
                        help="Path of directory to write output files.")
    parser.add_argument("-t1", "--output_tsv1",
                        required=True,
                        help="Name of bins1 comparison summary tsv to write.")
    parser.add_argument("-t2", "--output_tsv2",
                        required=True,
                        help="Name of bins2 comparison summary tsv to write.")
    parser.add_argument("-t3", "--output_tsv3",
                        required=True,
                        help="Name of unified summary tsv to write.")
    parser.add_argument("-m", "--missing_data_char",
                        required=False,
                        type=str,
                        default="NA",
                        help="Symbol to use for missing data in the output files [NA].")
    return parser.parse_args()

def get_bin_contig_dicts(f):
    """
    Make a bin_dict where k:v = "bin_name":{"contig_names":LIST(STR),
                                            "contig_number":INT,
                                            "completeness":FLOAT,
                                            "contamination":FLOAT,
                                            "contig_lengths":LIST(INT),
                                            "total_length":INT}

    Ex. 'complete.560': {'contig_names': [s1181.ctg001444c, ...],
                         'contig_number': 3,
                         'completeness': 100.0,
                         'contamination': 1.43,
                         'contig_lengths': [1283354, ...]
                         'total_length': 1500340}

    Make a contig_dict where k:v = "contig": {"bin":STR,
                                              "length":INT}

    Ex. 's1181.ctg001444c': {'bin': 'complete.560',
                             'length': 2450426}

    Expected header in tsv files:
        0 Name
        1 Completeness
        2 Contamination
        3 Contig_Number
        4 Contig_Names
        5 Contig_Lengths
        6 Status
        7 Completeness_Model_Used
        8 Translation_Table_Used
        9 Coding_Density
        10 Contig_N50
        11 Average_Gene_Length
        12 Genome_Size
        13 GC_Content
        14 Total_Coding_Sequences
        15 Additional_Notes
    """
    print("\nget_bin_contig_dicts: Making dictionary structures from: {}".format(f))
    bin_dict, contig_dict = {}, {}
    with open(f, 'r') as fh:
        # skip header
        next(fh)
        for line in fh:
            # print(line)
            parts = line.split('\t')
            # need to add in check for Pass/Fail column
            if parts[6] == "Pass":
                contig_names_list = [x for x in parts[4].split(', ')]
                contig_lengths_list = [int(x) for x in parts[5].split(', ')]

                bin_dict[parts[0]] = {"contig_names": contig_names_list, "contig_number": parts[3],
                                      "completeness": parts[1], "contamination": parts[2],
                                      "contig_lengths": contig_lengths_list,
                                      "total_length": sum(contig_lengths_list)}

                for i, contig in enumerate(contig_names_list):
                    contig_dict[contig] = {"bin_name": parts[0], "length": contig_lengths_list[i]}
            else:
                print("\t{} failed filtering".format(parts[0]))

    return bin_dict, contig_dict

def get_identical_category(bin_dict1, bin_dict2, misschar):
    """
    Identify exact matches across bin sets.
    Returns a dictionary with match metadata.
    """
    print("\n\n------------------------------------------------------------------\n"
          "get_identical_category: Identifying exact bin matches."
          "\n------------------------------------------------------------------\n")
    match_count = 0
    matches = []
    match_dict = {}

    for k1, v1 in bin_dict1.items():
        for k2, v2 in bin_dict2.items():
            if set(v1["contig_names"]) == set(v2["contig_names"]):
                match_count += 1
                match_dict["{}_{}".format(k1, k2)] = {"bin1_name": k1,
                                                      "bin2_name": k2,
                                                      "bin1_category": "Identical",
                                                      "bin2_category": "Identical",
                                                      "bin1_contig_number": bin_dict1[k1]["contig_number"],
                                                      "bin2_contig_number": bin_dict2[k2]["contig_number"],
                                                      "bin1_completeness": bin_dict1[k1]["completeness"],
                                                      "bin2_completeness": bin_dict2[k2]["completeness"],
                                                      "bin1_contamination": bin_dict1[k1]["contamination"],
                                                      "bin2_contamination": bin_dict2[k2]["contamination"],
                                                      "bin1_size": bin_dict1[k1]["total_length"],
                                                      "bin2_size": bin_dict2[k2]["total_length"],
                                                      "bin1_perc_bases_shared": 100,
                                                      "bin2_perc_bases_shared": 100,
                                                      "shared_contigs": ", ".join(bin_dict1[k1]["contig_names"]),
                                                      "shared_contig_lengths": ", ".join(
                                                          [str(i) for i in bin_dict1[k1]["contig_lengths"]]),
                                                      "shared_contigs_number": bin_dict1[k1]["contig_number"],
                                                      "shared_contig_total_bases": bin_dict1[k1]["total_length"],
                                                      "bin1_unique_contigs": misschar,
                                                      "bin1_unique_contig_lengths": misschar,
                                                      "bin1_unique_contigs_number": misschar,
                                                      "bin1_unique_contig_total_bases": misschar,
                                                      "bin2_unique_contigs": misschar,
                                                      "bin2_unique_contig_lengths": misschar,
                                                      "bin2_unique_contigs_number": misschar,
                                                      "bin2_unique_contig_total_bases": misschar}

    print("Identical matches = {:,}\n\n".format(match_count))

    return match_dict


def get_unique_category(bin_dict1, bin_dict2, misschar):
    """
    Identify unique bins - these contain a set of contigs, which individually are not found anywhere else.
    Returns a dictionary with match metadata.
    """
    print("------------------------------------------------------------------\n"
          "get_unique_category: Identifying strictly unique bins."
          "\n------------------------------------------------------------------\n")
    unq_cnt1, unq_cnt2 = 0, 0
    match_dict1, match_dict2 = {}, {}

    # scan dict1 first
    for k1, v1 in bin_dict1.items():
        # set boolean flag for unique
        is_unique = True
        for k2, v2 in bin_dict2.items():
            # test if there are any contigs shared between the sets
            # a unique set should produce a length of zero for this intersection operation
            if len(set(v1["contig_names"]) & set(v2["contig_names"])) >= 1:
                is_unique = False
        # only continue if this particular bin1 bin is unique
        if is_unique == True:
            unq_cnt1 += 1
            match_dict1["{}_{}".format(k1, "NA")] = {"bin1_name": k1,
                                                     "bin2_name": misschar,
                                                     "bin1_category": "Unique",
                                                     "bin2_category": misschar,
                                                     "bin1_contig_number": bin_dict1[k1]["contig_number"],
                                                     "bin2_contig_number": misschar,
                                                     "bin1_completeness": bin_dict1[k1]["completeness"],
                                                     "bin2_completeness": misschar,
                                                     "bin1_contamination": bin_dict1[k1]["contamination"],
                                                     "bin2_contamination": misschar,
                                                     "bin1_size": bin_dict1[k1]["total_length"],
                                                     "bin2_size": misschar,
                                                     "bin1_perc_bases_shared": misschar,
                                                     "bin2_perc_bases_shared": misschar,
                                                     "shared_contigs": misschar,
                                                     "shared_contig_lengths": misschar,
                                                     "shared_contigs_number": misschar,
                                                     "shared_contig_total_bases": misschar,
                                                     "bin1_unique_contigs": ", ".join(
                                                         [str(i) for i in bin_dict1[k1]["contig_names"]]),
                                                     "bin1_unique_contig_lengths": ", ".join(
                                                         [str(i) for i in bin_dict1[k1]["contig_lengths"]]),
                                                     "bin1_unique_contigs_number": bin_dict1[k1]["contig_number"],
                                                     "bin1_unique_contig_total_bases": sum(
                                                         bin_dict1[k1]["contig_lengths"]),
                                                     "bin2_unique_contigs": misschar,
                                                     "bin2_unique_contig_lengths": misschar,
                                                     "bin2_unique_contigs_number": misschar,
                                                     "bin2_unique_contig_total_bases": misschar}
    # scan dict2
    for k2, v2 in bin_dict2.items():
        # set boolean flag for unique
        is_unique = True
        for k1, v1 in bin_dict1.items():
            # test if there are any contigs shared between the sets
            # a unique set should produce a length of zero for this intersection operation
            if len(set(v1["contig_names"]) & set(v2["contig_names"])) >= 1:
                is_unique = False
        # only continue if this particular bin1 bin is unique
        if is_unique == True:
            unq_cnt2 += 1
            match_dict2["{}_{}".format("NA", k2)] = {"bin1_name": misschar,
                                                     "bin2_name": k2,
                                                     "bin1_category": misschar,
                                                     "bin2_category": "Unique",
                                                     "bin1_contig_number": misschar,
                                                     "bin2_contig_number": bin_dict2[k2]["contig_number"],
                                                     "bin1_completeness": misschar,
                                                     "bin2_completeness": bin_dict2[k2]["completeness"],
                                                     "bin1_contamination": misschar,
                                                     "bin2_contamination": bin_dict2[k2]["contamination"],
                                                     "bin1_size": misschar,
                                                     "bin2_size": bin_dict2[k2]["total_length"],
                                                     "bin1_perc_bases_shared": misschar,
                                                     "bin2_perc_bases_shared": misschar,
                                                     "shared_contigs": misschar,
                                                     "shared_contig_lengths": misschar,
                                                     "shared_contigs_number": misschar,
                                                     "shared_contig_total_bases": misschar,
                                                     "bin1_unique_contigs": misschar,
                                                     "bin1_unique_contig_lengths": misschar,
                                                     "bin1_unique_contigs_number": misschar,
                                                     "bin1_unique_contig_total_bases": misschar,
                                                     "bin2_unique_contigs": ", ".join(
                                                         [str(i) for i in bin_dict2[k2]["contig_names"]]),
                                                     "bin2_unique_contig_lengths": ", ".join(
                                                         [str(i) for i in bin_dict2[k2]["contig_lengths"]]),
                                                     "bin2_unique_contigs_number": bin_dict2[k2]["contig_number"],
                                                     "bin2_unique_contig_total_bases": sum(
                                                         bin_dict2[k2]["contig_lengths"])}
    print("Unique to bins1  = {:,}".format(unq_cnt1))
    print("Unique to bins2 = {:,}".format(unq_cnt2))
    print("Total unique bins = {:,}\n\n".format(unq_cnt1 + unq_cnt2))

    return match_dict1, match_dict2


def check_contigs_contained_elsewhere(contigs, contig_dict):
    """
    Lookup contig names in the contig_dict to set a boolean.
    """
    contained_elsewhere = False
    for c in contigs:
        if c in contig_dict:
            contained_elsewhere = True
            break

    return contained_elsewhere


def get_superset_subset_category(bin_dict1, bin_dict2, contig_dict1, contig_dict2, misschar):
    """
    Identify superset/subset matches across bin sets.
    Returns a dictionary with match metadata.
    """
    print("------------------------------------------------------------------\n"
          "get_superset_subset_category: Identifying superset/subset bins."
          "\n------------------------------------------------------------------\n")
    spr_cnt1, spr_cnt2 = 0, 0
    match_dict = {}

    # scan dict1 first
    for k1, v1 in bin_dict1.items():
        for k2, v2 in bin_dict2.items():
            if set(v1["contig_names"]).issuperset(set(v2["contig_names"])) \
                    and len(v1["contig_names"]) > len(v2["contig_names"]):
                # get list of contigs exclusive to the superset
                bin1_unique_contigs = list(set(v1["contig_names"]) - set(v2["contig_names"]))
                # check if those contigs can be found in any other bin in bin2 set
                if check_contigs_contained_elsewhere(bin1_unique_contigs, contig_dict2) is False:
                    spr_cnt1 += 1
                    shared_contigs = list(set(v1["contig_names"]) - set(bin1_unique_contigs))
                    match_dict["{}_{}".format(k1, k2)] = {"bin1_name": k1,
                                                          "bin2_name": k2,
                                                          "bin1_category": "Superset",
                                                          "bin2_category": "Subset",
                                                          "bin1_contig_number": bin_dict1[k1]["contig_number"],
                                                          "bin2_contig_number": bin_dict2[k2]["contig_number"],
                                                          "bin1_completeness": bin_dict1[k1]["completeness"],
                                                          "bin2_completeness": bin_dict2[k2]["completeness"],
                                                          "bin1_contamination": bin_dict1[k1]["contamination"],
                                                          "bin2_contamination": bin_dict2[k2]["contamination"],
                                                          "bin1_size": bin_dict1[k1]["total_length"],
                                                          "bin2_size": bin_dict2[k2]["total_length"],
                                                          "bin1_perc_bases_shared": 100,
                                                          "bin2_perc_bases_shared": int(
                                                              bin_dict2[k2]["total_length"] / bin_dict1[k1][
                                                                  "total_length"] * 100),
                                                          "shared_contigs": ", ".join(shared_contigs),
                                                          "shared_contig_lengths": ", ".join(
                                                              [str(contig_dict1[i]["length"]) for i in shared_contigs]),
                                                          "shared_contigs_number": len(shared_contigs),
                                                          "shared_contig_total_bases": sum(
                                                              [contig_dict1[i]["length"] for i in shared_contigs]),
                                                          "bin1_unique_contigs": ", ".join(bin1_unique_contigs),
                                                          "bin1_unique_contig_lengths": ", ".join(
                                                              [str(contig_dict1[x]["length"]) for x in
                                                               bin1_unique_contigs]),
                                                          "bin1_unique_contigs_number": len(bin1_unique_contigs),
                                                          "bin1_unique_contig_total_bases": sum(
                                                              [contig_dict1[x]["length"] for x in bin1_unique_contigs]),
                                                          "bin2_unique_contigs": misschar,
                                                          "bin2_unique_contig_lengths": misschar,
                                                          "bin2_unique_contigs_number": misschar,
                                                          "bin2_unique_contig_total_bases": misschar}
                else:
                    # one or more of the unique contigs in this bin1 bin was found in a different bin2 bin
                    # this is not a superset bin, it is a mixed bin
                    pass

            elif set(v2["contig_names"]).issuperset(set(v1["contig_names"])) and len(v2["contig_names"]) > len(
                    v1["contig_names"]):
                # get list of contigs exclusive to the superset
                bin2_unique_contigs = list(set(v2["contig_names"]) - set(v1["contig_names"]))
                # check if those contigs can be found in any other bin in bin1 set
                if check_contigs_contained_elsewhere(bin2_unique_contigs, contig_dict1) is False:
                    spr_cnt2 += 1
                    shared_contigs = list(set(v2["contig_names"]) - set(bin2_unique_contigs))
                    match_dict["{}_{}".format(k1, k2)] = {"bin1_name": k1,
                                                          "bin2_name": k2,
                                                          "bin1_category": "Subset",
                                                          "bin2_category": "Superset",
                                                          "bin1_contig_number": bin_dict1[k1]["contig_number"],
                                                          "bin2_contig_number": bin_dict2[k2]["contig_number"],
                                                          "bin1_completeness": bin_dict1[k1]["completeness"],
                                                          "bin2_completeness": bin_dict2[k2]["completeness"],
                                                          "bin1_contamination": bin_dict1[k1]["contamination"],
                                                          "bin2_contamination": bin_dict2[k2]["contamination"],
                                                          "bin1_size": bin_dict1[k1]["total_length"],
                                                          "bin2_size": bin_dict2[k2]["total_length"],
                                                          "bin1_perc_bases_shared": int(
                                                              bin_dict1[k1]["total_length"] / bin_dict2[k2][
                                                                  "total_length"] * 100),
                                                          "bin2_perc_bases_shared": 100,
                                                          "shared_contigs": ", ".join(shared_contigs),
                                                          "shared_contig_lengths": ", ".join(
                                                              [str(contig_dict2[i]["length"]) for i in shared_contigs]),
                                                          "shared_contigs_number": len(shared_contigs),
                                                          "shared_contig_total_bases": sum(
                                                              [contig_dict2[i]["length"] for i in shared_contigs]),
                                                          "bin1_unique_contigs": misschar,
                                                          "bin1_unique_contig_lengths": misschar,
                                                          "bin1_unique_contigs_number": misschar,
                                                          "bin1_unique_contig_total_bases": misschar,
                                                          "bin2_unique_contigs": ", ".join(bin2_unique_contigs),
                                                          "bin2_unique_contig_lengths": ", ".join(
                                                              [str(contig_dict2[x]["length"]) for x in
                                                               bin2_unique_contigs]),
                                                          "bin2_unique_contigs_number": len(bin2_unique_contigs),
                                                          "bin2_unique_contig_total_bases": sum(
                                                              [contig_dict2[x]["length"] for x in bin2_unique_contigs])}

                else:
                    # one or more of the unique contigs in this bin2 bin was found in a different bin1 bin
                    # this is not a superset bin, it is a mixed bin
                    pass

    print("Supersets in bins1 = {:,}".format(spr_cnt1))
    print("Supersets in bins2 = {:,}".format(spr_cnt2))
    print("Total superset/subset combinations = {:,}\n\n".format(spr_cnt1 + spr_cnt2))

    return match_dict


def calculate_percent_shared_bases(shared_contigs, bin1_unique_contigs, bin2_unique_contigs, all_contigs_dict):
    """
    Calculate the percent of shared bases between two contig sets.
    """
    shared_bases = sum([all_contigs_dict[i]["length"] for i in shared_contigs])
    bin1_unique_bases = sum([all_contigs_dict[i]["length"] for i in bin1_unique_contigs])
    bin2_unique_bases = sum([all_contigs_dict[i]["length"] for i in bin2_unique_contigs])
    bin1_perc = int((shared_bases / (shared_bases + bin1_unique_bases)) * 100)
    bin2_perc = int((shared_bases / (shared_bases + bin2_unique_bases)) * 100)

    return bin1_perc, bin2_perc

def assign_mixed_status(bin1_perc, bin2_perc):
    """
    Assign a category based on percent shared bases of both bins.
    """
    status = ""
    if bin1_perc >= 80:
        if bin2_perc >= 80:
            status = "Mixed-HS"
        elif bin2_perc < 80 and bin2_perc >= 50:
            status = "Mixed-MS"
        elif bin2_perc < 50:
            status = "Mixed-LS"
    elif bin1_perc < 80 and bin1_perc >= 50:
        if bin2_perc >= 50:
            status = "Mixed-MS"
        elif bin2_perc < 50:
            status = "Mixed-LS"
    elif bin1_perc < 50:
        status = "Mixed-LS"

    return status

def get_mixed_category(combined_dict, bin_dict1, bin_dict2, contig_dict1, contig_dict2, outdir):
    """
    Identify mixed bin matches across bin sets, based on pairwise comparisons.
    Writes a match summary file per bin, and a file with breakdown of categories found per bin set.
    Returns a dictionary with match metadata.
    """
    print("------------------------------------------------------------------\n"
          "get_mixed_category: Pairwise comparisons for mixed bins."
          "\n------------------------------------------------------------------\n")
    per_bin_dir = os.path.join(outdir, "pairwise-bin-results")
    if not os.path.exists(per_bin_dir):
        os.makedirs(per_bin_dir, exist_ok=True)

    # get names of bins that are already identified as identical, superset/subset, or unique
    exclude_bins1 = [v["bin1_name"] for k, v in combined_dict.items()]
    exclude_bins2 = [v["bin2_name"] for k, v in combined_dict.items()]

    # filter dictionaries to exclude these entries
    filtered_bin_dict1 = {k: v for (k, v) in bin_dict1.items() if k not in exclude_bins1}
    filtered_bin_dict2 = {k: v for (k, v) in bin_dict2.items() if k not in exclude_bins2}

    # combine the contig dictionaries
    all_contigs_dict = {**contig_dict1, **contig_dict2}

    match_dict1, match_dict2 = {}, {}
    summary_dict1, summary_dict2 = {}, {}

    # run through bins1 first
    for k1, v1 in filtered_bin_dict1.items():
        temp_match_dict = {}
        for k2, v2 in filtered_bin_dict2.items():
            # get list of contigs shared between bins
            shared_contigs = list(set(v1["contig_names"]) & set(v2["contig_names"]))
            # only create entries if some contigs are shared
            if len(shared_contigs) > 0:
                # get names of contigs unique to each bin
                # calculate percent shared bases for each bin
                bin1_unique_contigs = list(set(v1["contig_names"]) - set(v2["contig_names"]))
                bin2_unique_contigs = list(set(v2["contig_names"]) - set(v1["contig_names"]))
                bin1_perc, bin2_perc = calculate_percent_shared_bases(shared_contigs, bin1_unique_contigs,
                                                                      bin2_unique_contigs, all_contigs_dict)

                # assign a category based on shared bases of each bin
                status = assign_mixed_status(bin1_perc, bin2_perc)

                # write results to temporary dictionary
                temp_match_dict["{}_{}".format(k1, k2)] = {"bin1_name": k1,
                                                           "bin2_name": k2,
                                                           "bin1_category": status,
                                                           "bin2_category": "reference",
                                                           "bin1_contig_number": bin_dict1[k1]["contig_number"],
                                                           "bin2_contig_number": bin_dict2[k2]["contig_number"],
                                                           "bin1_completeness": bin_dict1[k1]["completeness"],
                                                           "bin2_completeness": bin_dict2[k2]["completeness"],
                                                           "bin1_contamination": bin_dict1[k1]["contamination"],
                                                           "bin2_contamination": bin_dict2[k2]["contamination"],
                                                           "bin1_size": bin_dict1[k1]["total_length"],
                                                           "bin2_size": bin_dict2[k2]["total_length"],
                                                           "bin1_perc_bases_shared": bin1_perc,
                                                           "bin2_perc_bases_shared": bin2_perc,
                                                           "shared_contigs": ", ".join(shared_contigs),
                                                           "shared_contig_lengths": ", ".join(
                                                               [str(all_contigs_dict[i]["length"]) for i in
                                                                shared_contigs]),
                                                           "shared_contigs_number": len(shared_contigs),
                                                           "shared_contig_total_bases": sum(
                                                               [all_contigs_dict[i]["length"] for i in shared_contigs]),
                                                           "bin1_unique_contigs": ", ".join(bin1_unique_contigs),
                                                           "bin1_unique_contig_lengths": ", ".join(
                                                               [str(all_contigs_dict[x]["length"]) for x in
                                                                bin1_unique_contigs]),
                                                           "bin1_unique_contigs_number": len(bin1_unique_contigs),
                                                           "bin1_unique_contig_total_bases": sum(
                                                               [all_contigs_dict[x]["length"] for x in
                                                                bin1_unique_contigs]),
                                                           "bin2_unique_contigs": ", ".join(bin2_unique_contigs),
                                                           "bin2_unique_contig_lengths": ", ".join(
                                                               [str(all_contigs_dict[x]["length"]) for x in
                                                                bin2_unique_contigs]),
                                                           "bin2_unique_contigs_number": len(bin2_unique_contigs),
                                                           "bin2_unique_contig_total_bases": sum(
                                                               [all_contigs_dict[x]["length"] for x in
                                                                bin2_unique_contigs])}

        # write the temporary dictionary of results for pairwise comparisons to output file
        outname = os.path.join(per_bin_dir, "bins1.{}.mixed_comparisons.txt".format(k1))
        pd.DataFrame.from_dict(temp_match_dict, orient='index').to_csv(outname, sep='\t', index=False)

        # sort temporary dictionary to get top match (in terms of percent bases shared)
        temp_sort = sorted(temp_match_dict.items(), key=lambda x: x[1]['bin1_perc_bases_shared'], reverse=True)
        # write the top hit to the main bins1 match dictionary
        match_dict1[temp_sort[0][0]] = temp_match_dict[temp_sort[0][0]]

        summary_dict1[k1] = {
            "Mixed-HS": sum([1 for k, v in temp_match_dict.items() if v["bin1_category"] == "Mixed-HS"]),
            "Mixed-MS": sum([1 for k, v in temp_match_dict.items() if v["bin1_category"] == "Mixed-MS"]),
            "Mixed-LS": sum([1 for k, v in temp_match_dict.items() if v["bin1_category"] == "Mixed-LS"]),
            "Total": len(temp_match_dict)}
    sumname = os.path.join(outdir, "Counts.bins1.mixed_comparisons.txt")
    pd.DataFrame.from_dict(summary_dict1, orient='index').to_csv(sumname, sep='\t', index=True)

    print("Bins1 starting bins = {}\nBins1 confirmed mixed bins = {}".format(len(filtered_bin_dict1), len(match_dict1)))
    print("\tMixed-HS bins: {}\n\tMixed-MS bins: {}\n\tMixed-LS bins: {}".format(
        sum([1 for k, v in match_dict1.items() if v["bin1_category"] == "Mixed-HS"]),
        sum([1 for k, v in match_dict1.items() if v["bin1_category"] == "Mixed-MS"]),
        sum([1 for k, v in match_dict1.items() if v["bin1_category"] == "Mixed-LS"])))

    # run through bins2
    for k2, v2 in filtered_bin_dict2.items():
        temp_match_dict = {}
        for k1, v1 in filtered_bin_dict1.items():
            # get list of contigs shared between bins
            shared_contigs = list(set(v1["contig_names"]) & set(v2["contig_names"]))
            # only create entries if some contigs are shared
            if len(shared_contigs) > 0:
                # get names of contigs unique to each bin
                # calculate percent shared bases for each bin
                bin1_unique_contigs = list(set(v1["contig_names"]) - set(v2["contig_names"]))
                bin2_unique_contigs = list(set(v2["contig_names"]) - set(v1["contig_names"]))
                bin1_perc, bin2_perc = calculate_percent_shared_bases(shared_contigs, bin1_unique_contigs,
                                                                      bin2_unique_contigs, all_contigs_dict)

                # assign a category based on shared bases of each bin
                status = assign_mixed_status(bin1_perc, bin2_perc)

                # write results to temporary dictionary
                temp_match_dict["{}_{}".format(k1, k2)] = {"bin1_name": k1,
                                                           "bin2_name": k2,
                                                           "bin1_category": "reference",
                                                           "bin2_category": status,
                                                           "bin1_contig_number": bin_dict1[k1]["contig_number"],
                                                           "bin2_contig_number": bin_dict2[k2]["contig_number"],
                                                           "bin1_completeness": bin_dict1[k1]["completeness"],
                                                           "bin2_completeness": bin_dict2[k2]["completeness"],
                                                           "bin1_contamination": bin_dict1[k1]["contamination"],
                                                           "bin2_contamination": bin_dict2[k2]["contamination"],
                                                           "bin1_size": bin_dict1[k1]["total_length"],
                                                           "bin2_size": bin_dict2[k2]["total_length"],
                                                           "bin1_perc_bases_shared": bin1_perc,
                                                           "bin2_perc_bases_shared": bin2_perc,
                                                           "shared_contigs": ", ".join(shared_contigs),
                                                           "shared_contig_lengths": ", ".join(
                                                               [str(all_contigs_dict[i]["length"]) for i in
                                                                shared_contigs]),
                                                           "shared_contigs_number": len(shared_contigs),
                                                           "shared_contig_total_bases": sum(
                                                               [all_contigs_dict[i]["length"] for i in shared_contigs]),
                                                           "bin1_unique_contigs": ", ".join(bin1_unique_contigs),
                                                           "bin1_unique_contig_lengths": ", ".join(
                                                               [str(all_contigs_dict[x]["length"]) for x in
                                                                bin1_unique_contigs]),
                                                           "bin1_unique_contigs_number": len(bin1_unique_contigs),
                                                           "bin1_unique_contig_total_bases": sum(
                                                               [all_contigs_dict[x]["length"] for x in
                                                                bin1_unique_contigs]),
                                                           "bin2_unique_contigs": ", ".join(bin2_unique_contigs),
                                                           "bin2_unique_contig_lengths": ", ".join(
                                                               [str(all_contigs_dict[x]["length"]) for x in
                                                                bin2_unique_contigs]),
                                                           "bin2_unique_contigs_number": len(bin2_unique_contigs),
                                                           "bin2_unique_contig_total_bases": sum(
                                                               [all_contigs_dict[x]["length"] for x in
                                                                bin2_unique_contigs])}

        # write the temporary dictionary of results for pairwise comparisons to output file
        outname = os.path.join(per_bin_dir, "bins2.{}.mixed_comparisons.txt".format(k2))
        pd.DataFrame.from_dict(temp_match_dict, orient='index').to_csv(outname, sep='\t', index=False)

        # sort temporary dictionary to get top match (in terms of percent bases shared)
        temp_sort = sorted(temp_match_dict.items(), key=lambda x: x[1]['bin2_perc_bases_shared'], reverse=True)
        # write the top hit to the main bins1 match dictionary
        match_dict2[temp_sort[0][0]] = temp_match_dict[temp_sort[0][0]]

        summary_dict2[k2] = {
            "Mixed-HS": sum([1 for k, v in temp_match_dict.items() if v["bin2_category"] == "Mixed-HS"]),
            "Mixed-MS": sum([1 for k, v in temp_match_dict.items() if v["bin2_category"] == "Mixed-MS"]),
            "Mixed-LS": sum([1 for k, v in temp_match_dict.items() if v["bin2_category"] == "Mixed-LS"]),
            "Total": len(temp_match_dict)}
    sumname = os.path.join(outdir, "Counts.bins2.mixed_comparisons.txt")
    pd.DataFrame.from_dict(summary_dict2, orient='index').to_csv(sumname, sep='\t', index=True)

    print("Bins2 starting bins = {}\nBins2 confirmed mixed bins = {}".format(len(filtered_bin_dict2), len(match_dict2)))
    print("\tMixed-HS bins: {}\n\tMixed-MS bins: {}\n\tMixed-LS bins: {}\n\n".format(
        sum([1 for k, v in match_dict2.items() if v["bin2_category"] == "Mixed-HS"]),
        sum([1 for k, v in match_dict2.items() if v["bin2_category"] == "Mixed-MS"]),
        sum([1 for k, v in match_dict2.items() if v["bin2_category"] == "Mixed-LS"])))

    # df_match_dict1 = pd.DataFrame.from_dict(match_dict1, orient='index')
    # print("Mixed bins1 categories:\n", df_match_dict1["bin1_category"].value_counts(), "\n\n\n")
    # df_match_dict2 = pd.DataFrame.from_dict(match_dict2, orient='index')
    # print("Mixed bins2 categories:\n", df_match_dict2["bin2_category"].value_counts(), "\n\n\n")

    return match_dict1, match_dict2

def unify_match_dicts(mixed_dict1, mixed_dict2):
    print("------------------------------------------------------------------\n"
          "unify_match_dicts: Unifying mixed bins."
          "\n------------------------------------------------------------------\n")
    # find keys that are identical across dicts
    # this indicates that match was best found across all pairwise comparisons in both directions
    unified_dict = {}
    for k1, v1 in mixed_dict1.items():
        for k2, v2 in mixed_dict2.items():
            if k1 == k2:
                v1["bin2_category"] = v1["bin1_category"]
                unified_dict[k1] = v1
    print("Unified bins = {}\n".format(len(unified_dict)))

    # quantify bin loss using this method
    unmatched_keys = [k for k in list(mixed_dict1.keys()) + list(mixed_dict2.keys()) if k not in unified_dict]
    bins1_unmatched = [[v["bin1_name"], v["bin1_category"]] for k, v in mixed_dict1.items() if k not in unified_dict]
    bins2_unmatched = [[v["bin2_name"], v["bin2_category"]]for k, v in mixed_dict2.items() if k not in unified_dict]
    print("Excluded {} bin(s) from bins1:".format(len(bins1_unmatched)))
    for x in bins1_unmatched:
        print("\t{} = {}".format(x[0], x[1]))
    print("\nExcluded {} bin(s) from bins2:".format(len(bins1_unmatched)))
    for x in bins2_unmatched:
        print("\t{} = {}".format(x[0], x[1]))

    return unified_dict

def sanity_check_bin_numbers(bin_dict1, bin_dict2, bins1_combined_dict, bins2_combined_dict):
    print("------------------------------------------------------------------\n"
          "sanity_check_bin_numbers: Just for fun."
          "\n------------------------------------------------------------------\n")
    if len(bin_dict1) == len(bins1_combined_dict):
        print("bins1: all {} bins assigned to categories.".format(len(bin_dict1)))
    else:
        print("bins1: issue, only {} of {} bins assigned to categories.".format(len(bins1_combined_dict), len(bin_dict1)))
    if len(bin_dict2) == len(bins2_combined_dict):
        print("bins2: all {} bins assigned to categories.\n\n".format(len(bin_dict2)))
    else:
        print("bins2: issue, only {} of {} bins assigned to categories.\n\n".format(len(bins2_combined_dict), len(bin_dict2)))

def summary_counts(bin_dict1, bin_dict2, consolidated_dict, identical_dict, superset_dict, mixed_dict, unique_dict1, unique_dict2):
    print("\n\n------------------------------------------------------------------\nSummary "
          "counts\n------------------------------------------------------------------\n\nBins1 "
          "filtered bins: {}".format(len(bin_dict1)))
    print("Bins2 filtered bins: {}\n".format(len(bin_dict2)))
    print("Consolidated bins: {}".format(len(consolidated_dict)))
    print("    Identical: {}".format(len(identical_dict)))
    print("    Superset/subset: {}".format(len(superset_dict)))
    print("    Mixed: {}".format(len(mixed_dict)))
    print("    Bins1 unique: {}".format(len(unique_dict1)))
    print("    Bins2 unique: {}\n\n".format(len(unique_dict2)))

def write_dict_to_tsv(dictionary, outname):
    """
    Create pandas dataframe from dictionary and write to tsv file.
    """
    pd.DataFrame.from_dict(dictionary, orient='index').to_csv(outname, sep='\t', index=False)

def main():
    args = get_args()
    bin_dict1, contig_dict1 = get_bin_contig_dicts(args.input_tsv1)
    bin_dict2, contig_dict2 = get_bin_contig_dicts(args.input_tsv2)

    identical_dict = get_identical_category(bin_dict1, bin_dict2, args.missing_data_char)
    unique_dict1, unique_dict2 = get_unique_category(bin_dict1, bin_dict2, args.missing_data_char)
    superset_dict = get_superset_subset_category(bin_dict1, bin_dict2, contig_dict1, contig_dict2, args.missing_data_char)
    mixed_dict1, mixed_dict2 = get_mixed_category({**identical_dict, **unique_dict1, **unique_dict2, **superset_dict},
                                                  bin_dict1, bin_dict2, contig_dict1, contig_dict2, args.outdir)

    bins1_combined_dict = {**identical_dict, **superset_dict, **mixed_dict1, **unique_dict1}
    bins2_combined_dict = {**identical_dict, **superset_dict, **mixed_dict2, **unique_dict2}

    sanity_check_bin_numbers(bin_dict1, bin_dict2, bins1_combined_dict, bins2_combined_dict)

    if args.consolidation_method == "unify":
        mixed_dict = unify_match_dicts(mixed_dict1, mixed_dict2)
    elif args.consolidation_method == "bins1":
        mixed_dict = mixed_dict1
    elif args.consolidation_method == "bins2":
        mixed_dict = mixed_dict2

    consolidated_dict = {**identical_dict, **superset_dict, **mixed_dict, **unique_dict1, **unique_dict2}
    summary_counts(bin_dict1, bin_dict2, consolidated_dict, identical_dict, superset_dict, mixed_dict,
                   unique_dict1, unique_dict2)

    write_dict_to_tsv(identical_dict, os.path.join(args.outdir, "Results.Identical.tsv"))
    write_dict_to_tsv(unique_dict1, os.path.join(args.outdir, "Results.Unique_Bins1.tsv"))
    write_dict_to_tsv(unique_dict2, os.path.join(args.outdir, "Results.Unique_Bins2.tsv"))
    write_dict_to_tsv(superset_dict, os.path.join(args.outdir, "Results.Superset_Subset.tsv"))
    write_dict_to_tsv(mixed_dict1, os.path.join(args.outdir, "Results.Mixed_Bins1.tsv"))
    write_dict_to_tsv(mixed_dict2, os.path.join(args.outdir, "Results.Mixed_Bins2.tsv"))
    write_dict_to_tsv(bins1_combined_dict, args.output_tsv1)
    write_dict_to_tsv(bins2_combined_dict, args.output_tsv2)
    write_dict_to_tsv(consolidated_dict, args.output_tsv3)

if __name__ == '__main__':
    main()


