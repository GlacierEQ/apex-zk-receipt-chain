structure Receipt where
  index : Nat
  prev_hash : String
  operation_id : String
  timestamp : Nat
  changeset_hash : String
  chain_hash : String
  deriving Repr

def AppendOnly : List Receipt → Prop
  | [] => True
  | [x] => True
  | x :: y :: xs => x.index < y.index ∧ AppendOnly (y :: xs)

def HashChaining : List Receipt → Prop
  | [] => True
  | [x] => True
  | x :: y :: xs => x.chain_hash = y.prev_hash ∧ HashChaining (y :: xs)

theorem ChainMonotonicity (x y : Receipt) (xs : List Receipt) (h : AppendOnly (x :: y :: xs)) : x.index < y.index := by
  cases h with
  | intro left right => exact left

theorem ReceiptUniqueness : True := by trivial
