# apex-zk-receipt-chain
ZK-STARK verifiable audit trail system.

## ZK receipt architecture
Pedersen hash chain diagram:
[R0] <- [R1] <- [R2] ...

## Lean4 theorem list
- ChainMonotonicity
- ReceiptUniqueness

## Cairo contract API
- append_receipt
- get_receipt
- verify_chain

## Python CLI usage
```
python3 src/prover.py append --op-id OP001 --changeset '{"action": "create", "target": "agent-42"}'
```

## Evidence state
- Python: tested
- Cairo: toolchain-gated
- Lean4: toolchain-gated
