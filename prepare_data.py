"""Export original MATLAB observation blocks to the shared input CSV format.

Usage:
 python prepare_data.py --fder path/to/Data_pFdeR_final_experimental_blocks_*.mat
                        --plux path/to/Data_struct_pLux.mat --output observations.csv
"""
import argparse
from pathlib import Path
import pandas as pd
from biosensor_studio.loaders import load_fder_mat, load_plux_mat, inventory


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--fder',type=Path,default=None)
    p.add_argument('--plux',type=Path,default=None)
    p.add_argument('--output',type=Path,default=Path('observations.csv'))
    args=p.parse_args()
    if args.fder is None and args.plux is None:
        p.error('Specify at least one of --fder or --plux')
    parts=[]
    if args.fder:
        parts.append(load_fder_mat(args.fder))
    if args.plux:
        parts.append(load_plux_mat(args.plux))
    df=pd.concat(parts,ignore_index=True)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    df.to_csv(args.output,index=False)
    print(f'Wrote {len(df)} replicate-dose rows to {args.output}')
    print(inventory(df).to_string(index=False))


if __name__=='__main__':main()
