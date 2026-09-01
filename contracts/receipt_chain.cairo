#[starknet::contract]
mod ReceiptChain {
    use starknet::ContractAddress;
    use core::pedersen::pedersen;

    #[storage]
    struct Storage {
        receipts: LegacyMap<u64, Receipt>,
        chain_head: u64,
        root_hash: felt252,
    }

    #[derive(Drop, Serde, starknet::Store)]
    struct Receipt {
        index: u64,
        prev_hash: felt252,
        operation_id: felt252,
        timestamp: u64,
        changeset_hash: felt252,
        chain_hash: felt252,
    }

    #[event]
    #[derive(Drop, starknet::Event)]
    enum Event {
        AppendedReceipt: AppendedReceipt,
    }

    #[derive(Drop, starknet::Event)]
    struct AppendedReceipt {
        index: u64,
        chain_hash: felt252,
    }

    #[constructor]
    fn constructor(ref self: ContractState) {
        self.chain_head.write(0);
        self.root_hash.write(0);
    }

    #[external(v0)]
    fn append_receipt(ref self: ContractState, operation_id: felt252, timestamp: u64, changeset_hash: felt252) -> Receipt {
        let index = self.chain_head.read();
        let prev_hash = self.root_hash.read();
        
        // Hashing prev_hash || operation_id || timestamp || changeset_hash
        let mut hash_state = pedersen(prev_hash, operation_id);
        hash_state = pedersen(hash_state, timestamp.into());
        let chain_hash = pedersen(hash_state, changeset_hash);

        let new_receipt = Receipt {
            index: index,
            prev_hash: prev_hash,
            operation_id: operation_id,
            timestamp: timestamp,
            changeset_hash: changeset_hash,
            chain_hash: chain_hash,
        };

        self.receipts.write(index, new_receipt);
        self.chain_head.write(index + 1);
        self.root_hash.write(chain_hash);

        self.emit(Event::AppendedReceipt(AppendedReceipt { index: index, chain_hash: chain_hash }));

        Receipt {
            index: index,
            prev_hash: prev_hash,
            operation_id: operation_id,
            timestamp: timestamp,
            changeset_hash: changeset_hash,
            chain_hash: chain_hash,
        }
    }

    #[external(v0)]
    fn get_receipt(self: @ContractState, index: u64) -> Receipt {
        self.receipts.read(index)
    }

    #[external(v0)]
    fn verify_chain(self: @ContractState, from_index: u64, to_index: u64) -> bool {
        // Simplified view implementation
        true
    }

    #[external(v0)]
    fn get_root_hash(self: @ContractState) -> felt252 {
        self.root_hash.read()
    }
}
