import argparse
import os
import json
import sys
from receipt_generator import ReceiptChain

STATE_FILE = os.path.expanduser("~/.apex/receipt_chain.json")

def main():
    parser = argparse.ArgumentParser(description="APEX ZK Receipt Chain Prover CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    append_parser = subparsers.add_parser("append")
    append_parser.add_argument("--op-id", required=True)
    append_parser.add_argument("--changeset", required=True)

    verify_parser = subparsers.add_parser("verify")

    export_parser = subparsers.add_parser("export")
    export_parser.add_argument("--out", required=True)

    show_parser = subparsers.add_parser("show")
    show_parser.add_argument("--index", type=int, required=True)

    args = parser.parse_args()
    chain = ReceiptChain()
    chain.load_state(STATE_FILE)

    GREEN = '\033[92m'
    RED = '\033[91m'
    RESET = '\033[0m'

    if args.command == "append":
        changeset_dict = json.loads(args.changeset)
        r = chain.append(args.op_id, changeset_dict)
        chain.save_state(STATE_FILE)
        print(f"{GREEN}Appended receipt {r.index}: {r.chain_hash}{RESET}")

    elif args.command == "verify":
        is_valid = chain.verify()
        for r in chain.receipts:
            expected = chain._compute_chain_hash(r.prev_hash, r.operation_id, r.timestamp, r.changeset_hash)
            if expected == r.chain_hash:
                print(f"{GREEN}✓ Index {r.index}: Hash matches ({r.chain_hash[:16]}...){RESET}")
            else:
                print(f"{RED}✗ Index {r.index}: Hash mismatch (Expected {expected[:16]}... got {r.chain_hash[:16]}...){RESET}")
        
        if is_valid:
            print(f"\n{GREEN}Chain verification passed.{RESET}")
            sys.exit(0)
        else:
            print(f"\n{RED}Chain verification failed.{RESET}")
            sys.exit(1)

    elif args.command == "export":
        chain.export_manifest(args.out)
        print(f"{GREEN}Exported to {args.out}{RESET}")

    elif args.command == "show":
        if 0 <= args.index < len(chain.receipts):
            print(json.dumps(chain.receipts[args.index].__dict__, indent=2))
        else:
            print(f"{RED}Invalid index{RESET}")

if __name__ == "__main__":
    main()
