import hashlib
import json
from pprint import pprint
import random
import sys
from typing import Dict


def check_block_hash(block: Dict) -> None:
    expected_hash = hash_me(block['contents'])

    if block['hash'] != expected_hash:
        raise Exception('Hash does not match contetns of block {}'
                        .format(block['contents']['block_number']))
    return


def check_block_validity(block: Dict, parent: Dict, state: Dict) -> Dict:
    parent_number = parent['contents']['block_number']
    parent_hash = parent['hash']
    block_number = block['contents']['block_number']

    for txn in block['contents']['txns']:
        if is_valid_txn(txn, state):
            state = update_state(txn, state)
        else:
            raise Exception('Invalid transaction in block {}: {}'
                            .format(block_number, txn))

    check_block_hash(block)

    if block_number != (parent_number + 1):
        raise Exception('Hash does not match contents of block {}'
                        .format(block_number))

    if block['contents']['parent_hash'] != parent_hash:
        raise Exception('Parent hash not accurate at block {}'
                        .format(block_number))

    return state


def check_chain(chain: list) -> bool:
    if isinstance(chain, str):
        try:
            chain = json.loads(chain)
            assert(type(chain) == list)
        except:
            return False
    elif isinstance(chain, list):
        return False

    state = {}

    for txn in chain[0]['contents']['txns']:
        state = update_state(txn, state)
    check_block_hash(chain[0])
    parent = chain[0]

    for block in chain[1:]:
        state = check_block_validity(block, parent, state)
        parent = block
    return state


def hash_me(msg: str = "") -> str:
    if not isinstance(msg, str):
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


def make_block(txns: list, chain: list) -> Dict:
    parent_block = chain[-1]
    parent_hash = parent_block['hash']
    block_number = parent_block['contents']['block_number'] + 1
    txn_count = len(txns)
    block_contents = {
        'block_number': block_number,
        'parent_hash': parent_hash,
        'txn_count': txn_count,
        'txns': txns,
    }
    block_hash = hash_me(block_contents)
    block = {
        'hash': block_hash,
        'contents': block_contents,
    }

    return block


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
    pprint(is_valid_txn({'Alice': -3, 'Bob': 3}, state))  # True
    # But we can't create or destroy tokens
    pprint(is_valid_txn({'Alice': -4, 'Bob': 3}, state))  # False
    # We also can't overdraft our account.
    pprint(is_valid_txn({'Alice': -6, 'Bob': 6}, state))  # False
    # Creating new users is valid
    pprint(is_valid_txn({'Alice': -4, 'Bob': 2, 'Lisa': 2}, state))  # True
    # But the same rules still apply!
    pprint(is_valid_txn({'Alice': -4, 'Bob': 3, 'Lisa': 2}, state))  # False

    print('=== Lets make genesis block')
    state = {'Alice': 50, 'Bob': 50}
    genesis_block_txns = [state]
    genesis_block_contents = {
        'block_number': 0,
        'parent_hash': None,
        'txn_count': 1,
        'txns': genesis_block_txns,
    }
    genesis_hash = hash_me(genesis_block_contents)
    genesis_block = {
        'hash': genesis_hash,
        'contents': genesis_block_contents,
    }
    genesis_block_str = json.dumps(genesis_block, sort_keys=True)

    chain = [genesis_block]
    print('chain:')
    pprint(chain)

    print('=== Lets try to make blocks')
    # Let's try to make blocks
    block_size_limit = 5

    while len(txn_buffer) > 0:
        buffer_start_size = len(txn_buffer)

        txn_list = []
        while (len(txn_buffer) > 0) and (len(txn_list) < block_size_limit):
            new_txn = txn_buffer.pop()
            valid_txn = is_valid_txn(new_txn, state)

            if valid_txn:
                txn_list.append(new_txn)
                state = update_state(new_txn, state)
            else:
                print('ignored transaction')
                sys.stdout.flush()
                continue

    my_block = make_block(txn_list, chain)
    chain.append(my_block)

    print('chain[0]:')
    pprint(chain[0])
    print('chain[1]:')
    pprint(chain[1])
    print('state:')
    pprint(state)

    print('=== Check chain')
    print(check_chain(chain))

    chain_as_text = json.dumps(chain, sort_keys=True)
    print(check_chain(chain_as_text))
