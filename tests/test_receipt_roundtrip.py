import pytest
import os
import json
from src.receipt_generator import ReceiptChain

def test_append_single_receipt():
    chain = ReceiptChain()
    r = chain.append("OP001", {"action": "create"})
    assert r.index == 0
    assert chain.verify() == True

def test_append_multiple_receipts():
    chain = ReceiptChain()
    for i in range(10):
        chain.append(f"OP{i:03d}", {"val": i})
    assert len(chain.receipts) == 10
    assert chain.verify() == True

def test_chain_tamper_detection():
    chain = ReceiptChain()
    for i in range(5):
        chain.append(f"OP{i:03d}", {"val": i})
    
    assert chain.verify() == True
    
    # Tamper
    chain.receipts[3].changeset_hash = "tampered"
    assert chain.verify() == False

def test_hash_determinism():
    chain1 = ReceiptChain()
    chain2 = ReceiptChain()
    
    hash1 = chain1._compute_changeset_hash({"a": 1, "b": 2})
    hash2 = chain2._compute_changeset_hash({"b": 2, "a": 1})
    assert hash1 == hash2

def test_export_manifest_format(tmp_path):
    chain = ReceiptChain()
    chain.append("OP001", {"action": "create"})
    
    manifest_path = tmp_path / "BATES_MANIFEST.json"
    chain.export_manifest(str(manifest_path))
    
    with open(manifest_path) as f:
        data = json.load(f)
        assert "receipts" in data
        assert "root_hash" in data
        assert "generated_at" in data
        assert len(data["receipts"]) == 1

def test_empty_chain_verification():
    chain = ReceiptChain()
    assert chain.verify() == True
