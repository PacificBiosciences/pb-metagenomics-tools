import argparse
import os
import shutil

def get_args():
    """
    Get arguments from command line with argparse.
    """
    parser = argparse.ArgumentParser(
        prog='Maxbin2-organize-outputs.py',
        description="""Organize output files from maxbin2.""")
    parser.add_argument("-s", "--sample",
                        required=True,
                        help="The sample name.")
    parser.add_argument("-o", "--outdir",
                        required=True,
                        help="Name of output directory.")
    return parser.parse_args()

def make_outdir(outdir):
    fulldir = os.path.join(os.getcwd(), outdir)
    if not os.path.exists(fulldir):
        os.mkdir(fulldir)
    print("Created directory: {}".format(fulldir))
    return fulldir

def move_outputs(sample, fulldir):
    target_files = [f for f in os.listdir('.') if f.startswith(sample)
                    and f.endswith(('.seed', '.log', '.marker', '.tar.gz', '.noclass', '.summary', '.tooshort'))]
    for f in target_files:
        print("\tMoving file: {}".format(f))
        shutil.move(f, fulldir)

    fasta_files = [f for f in os.listdir('.') if f.startswith(sample)
                    and f.endswith('.fasta')]
    for f in fasta_files:
        outname = "maxbin.{}.{}".format(f.split('.')[1], f.split('.')[-1])
        print("Relabeling file: {}".format(f))
        print("\t{}".format(outname))
        shutil.move(f, os.path.join(fulldir, outname))

def main():
    args = get_args()
    fulldir = make_outdir(args.outdir)
    move_outputs(args.sample, fulldir)
    print("Finished.")
        
if __name__ == '__main__':
    main()
