"""Explicit offline freeze or authorized live execution; never runs on import."""
import argparse
import json
from pathlib import Path
import study

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='Freeze original cases or run 102 bounded Jev POSTs.')
    sub=parser.add_subparsers(dest='action',required=True)
    freeze=sub.add_parser('freeze',help='Offline: freeze original fixtures, configuration, seed, source hashes.')
    freeze.add_argument('--plan-dir',type=Path,default=study.ROOT)
    run=sub.add_parser('run',help='LIVE: 102 planned POSTs; TYPESAFE_API_KEY environment only.')
    run.add_argument('--plan-dir',type=Path,default=study.ROOT)
    run.add_argument('--private-dir',type=Path,required=True)
    args=parser.parse_args()
    if args.action=='freeze':
        print(json.dumps(study.freeze(args.plan_dir),indent=2))
    else:
        result=study.execute(args.plan_dir,args.private_dir)
        print(json.dumps({k:v for k,v in result.items() if k!='conditions'},indent=2))
