import hashlib
import json
import random
from typing import Dict


def hash_me(msg: str = "") -> str:
    if not isinstance(type(msg), str):
        msg = json.dumps(msg, sort_keys=True)

    return hashlib.sha256(str(msg).encode('utf-8')).hexdigest()


def is_valid_txn(txn: Dict, state: Dict) -> bool:
    if sum(txn.values()) is not 0:
        return False

    for key in txn.keys():
        account_balance = 0
        if key in state.keys():
            account_balance = state[key]

        if (account_balance + txn[key]) < 0:
            return False

    return True


def make_transaction(max_value: int = 3) -> Dict:
    sign = int(random.getrandbits(1)) * 2 - 1
    amount = random.randint(1, max_value)
    alicePays = sign * amount
    bobPays = -1 * alicePays

    return {'Alice': alicePays, 'Bob': bobPays}


def update_state(txn: Dict, state: Dict) -> Dict:
    state = state.copy()

    for key in txn:
        if key in state.keys():
            state[key] += txn[key]
        else:
            state[key] = txn[key]
    return state


if __name__ == '__main__':
    txn_buffer = [make_transaction() for i in range(30)]

    state = {'Alice': 5, 'Bob': 5}

    # Basic transaction- this works great!
    print(is_valid_txn({'Alice': -3, 'Bob': 3}, state))  # True
    # But we can't create or destroy tokens
    print(is_valid_txn({'Alice': -4, 'Bob': 3}, state))  # False
    # We also can't overdraft our account.
    print(is_valid_txn({'Alice': -6, 'Bob': 6}, state))  # False
    # Creating new users is valid
    print(is_valid_txn({'Alice': -4, 'Bob': 2, 'Lisa': 2}, state))  # True
    # But the same rules still apply!
    print(is_valid_txn({'Alice': -4, 'Bob': 3, 'Lisa': 2}, state))  # False

            
