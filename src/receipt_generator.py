import hashlib
import json
import time
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any

@dataclass
class Receipt:
    index: int
    prev_hash: str
    operation_id: str
    timestamp: float
    changeset_hash: str
    chain_hash: str

class ReceiptChain:
    def __init__(self):
        self.receipts: List[Receipt] = []

    def _compute_changeset_hash(self, data: dict) -> str:
        canonical = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical.encode('utf-8')).hexdigest()

    def _compute_chain_hash(self, prev_hash: str, operation_id: str, timestamp: float, changeset_hash: str) -> str:
        payload = f"{prev_hash}{operation_id}{timestamp}{changeset_hash}"
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()

    def append(self, operation_id: str, changeset_dict: dict) -> Receipt:
        index = len(self.receipts)
        prev_hash = self.receipts[-1].chain_hash if self.receipts else "0" * 64
        timestamp = time.time()
        changeset_hash = self._compute_changeset_hash(changeset_dict)
        chain_hash = self._compute_chain_hash(prev_hash, operation_id, timestamp, changeset_hash)
        
        receipt = Receipt(
            index=index,
            prev_hash=prev_hash,
            operation_id=operation_id,
            timestamp=timestamp,
            changeset_hash=changeset_hash,
            chain_hash=chain_hash
        )
        self.receipts.append(receipt)
        return receipt

    def verify(self) -> bool:
        if not self.receipts:
            return True
        for i, receipt in enumerate(self.receipts):
            if i > 0:
                expected_prev = self.receipts[i-1].chain_hash
                if receipt.prev_hash != expected_prev:
                    return False
            expected_chain = self._compute_chain_hash(
                receipt.prev_hash,
                receipt.operation_id,
                receipt.timestamp,
                receipt.changeset_hash
            )
            if receipt.chain_hash != expected_chain:
                return False
        return True

    def export_manifest(self, path: str) -> None:
        root_hash = self.receipts[-1].chain_hash if self.receipts else "0" * 64
        import datetime
        manifest = {
            "receipts": [asdict(r) for r in self.receipts],
            "root_hash": root_hash,
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        with open(path, "w") as f:
            json.dump(manifest, f, indent=2)
            
    def load_state(self, path: str):
        try:
            with open(path, "r") as f:
                data = json.load(f)
                self.receipts = [Receipt(**r) for r in data.get("receipts", [])]
        except FileNotFoundError:
            self.receipts = []

    def save_state(self, path: str):
        import os
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        manifest = {
            "receipts": [asdict(r) for r in self.receipts],
        }
        with open(path, "w") as f:
            json.dump(manifest, f, indent=2)

    def verify_manifest(self, path: str) -> bool:
        """Fail closed on a on-disk Bates-style manifest.

        Recomputes every chain_hash from stored fields and checks root_hash.
        A mutated JSON that still `verify()`s in memory must not pass here.
        """
        try:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, json.JSONDecodeError):
            return False
        receipts = data.get("receipts")
        if not isinstance(receipts, list):
            return False
        prev = "0" * 64
        last_hash = prev
        for i, raw in enumerate(receipts):
            if not isinstance(raw, dict):
                return False
            try:
                index = int(raw["index"])
                prev_hash = str(raw["prev_hash"])
                operation_id = str(raw["operation_id"])
                timestamp = float(raw["timestamp"])
                changeset_hash = str(raw["changeset_hash"])
                chain_hash = str(raw["chain_hash"])
            except (KeyError, TypeError, ValueError):
                return False
            if index != i:
                return False
            if prev_hash != prev:
                return False
            expected = self._compute_chain_hash(prev_hash, operation_id, timestamp, changeset_hash)
            if expected != chain_hash:
                return False
            prev = chain_hash
            last_hash = chain_hash
        declared_root = data.get("root_hash")
        if declared_root is None:
            return True
        return declared_root == last_hash
