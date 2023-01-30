import argparse
import os
import shutil

def get_args():
    """
    Get arguments from command line with argparse.
    """
    parser = argparse.ArgumentParser(
        prog='Concoct-organize-outputs.py',
        description="""Relabel bin files from concoct.""")
    parser.add_argument("-i", "--indir",
                        required=True,
                        help="Name of output directory.")
    return parser.parse_args()

def relabel_outputs(indir):
    os.chdir(indir)
    fasta_files = [f for f in os.listdir('.') if f.endswith('.fa')]
    for f in fasta_files:
        outname = "concoct.{}.{}".format(f.split('.')[0], f.split('.')[-1])
        print("Relabeling file: {}".format(f))
        print("\t{}".format(outname))
        shutil.move(f, os.path.join(indir, outname))

def main():
    args = get_args()
    relabel_outputs(args.indir)
    print("Finished.")
        
if __name__ == '__main__':
    main()
