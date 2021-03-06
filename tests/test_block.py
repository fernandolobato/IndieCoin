# -*- coding: utf-8 -*-
import unittest
import os

from context import indiecoin
from context import GENESIS_BLOCK_HASH, PUBLIC_KEY_GENESIS, PRIVATE_KEY_GENESIS
from indiecoin.blockchain import block
from indiecoin.util import default_data_directory


class BlockTestCase(unittest.TestCase):
    """ Test the functionality for blocks

        @TODO TESTS:

    """
    def setUp(self):
        """ Create database object with different file_name. Open connection to database.
            Creates data dictionaries with transactions and blocks.
        """
        self.file_name = 'test_database'
        self.path = os.path.join(default_data_directory(), self.file_name)
        self.database = block.Database(file_name=self.file_name)
        self.transaction_database = indiecoin.blockchain.transaction.Database(
            file_name=self.file_name)
        self.block = indiecoin.blockchain.BlockChain(database=self.database).get_block(
            GENESIS_BLOCK_HASH)

        self.transaction = self.block.transactions[0]
        self.address = indiecoin.wallet.address.Address(private_key=PRIVATE_KEY_GENESIS)

        signature = self.address.sign(self.transaction.hash)

        self.tx_input_data = {
            'signature': signature,
            'hash_transaction': self.transaction.hash,
            'prev_out_index': '0',
            'database': self.transaction_database
        }

        self.transaction_outputs = [
            {
                'amount': 25,
                'public_key_owner': PUBLIC_KEY_GENESIS,
                'unspent': 1
            },
            {
                'amount': 25,
                'public_key_owner': PUBLIC_KEY_GENESIS,
                'unspent': 1
            }
        ]

        self.transaction_data = {
            'hash': '',
            'block_hash': '',
            'num_inputs': 1,
            'num_outputs': '2',
            'timestamp': '1490477410',
            'is_coinbase': 0,
            'is_orphan': 0,
            'tx_inputs': [self.tx_input_data],
            'tx_outputs': self.transaction_outputs,
            'database': self.transaction_database
        }

        self.coin_base_output = {
            'amount': 5,
            'public_key_owner': PUBLIC_KEY_GENESIS,
            'unspent': 1,
        }

        self.coin_base_transaction_data = {
            'hash': '',
            'block_hash': '',
            'num_inputs': 0,
            'num_outputs': 1,
            'timestamp': '1490477419',
            'is_coinbase': 1,
            'is_orphan': 0,
            'tx_inputs': [],
            'tx_outputs': [self.coin_base_output],
            'database': self.transaction_database
        }

        self.block_data = {
            'hash': '',
            'timestamp': '',
            'nonce': '',
            'num_transactions': 2,
            'is_orphan': 0,
            'previous_block_hash': GENESIS_BLOCK_HASH,
            'height': 2,
            'transactions': [self.transaction_data, self.coin_base_transaction_data],
            'database': self.database,
        }

    def tearDown(self):
            """ Destroy database.
            """
            os.system('rm {}'.format(self.path))

    def test_create_block_object(self):
        """ Test creating a block from dictionary data.
        """
        new_block = block.Block(**self.block_data)

        self.assertEqual(type(new_block.serialize()), dict)
        self.assertEqual(type(new_block.to_json()), str)
        self.assertEqual(len(new_block.hash), 64)
        self.assertTrue(new_block.is_valid())

    def test_block_invalid_transaction(self):
        """ Test trying to create a block with invalid transaction.
        """
        change = self.block_data['transactions'][0]['tx_inputs'][0]['signature'].replace('1', '2')
        self.block_data['transactions'][0]['tx_inputs'][0]['signature'] = change

        try:
            block.Block(**self.block_data)
        except AssertionError as e:
            self.assertEqual(e[0], 'Transaction not valid')

    def test_block_two_coinbase_transactions(self):
        """ Test trying to create a block with two coinbase transactions.
        """
        coinbase = {
            'hash': '',
            'block_hash': '',
            'num_inputs': 0,
            'num_outputs': 1,
            'timestamp': '1490477419',
            'is_coinbase': 1,
            'is_orphan': 0,
            'tx_inputs': [],
            'tx_outputs': [self.coin_base_output],
            'database': self.transaction_database
        }

        self.block_data['transactions'].append(coinbase)
        self.block_data['num_transactions'] += 1
        try:
            block.Block(**self.block_data)
        except AssertionError as e:
            self.assertEqual(e[0], 'Block is not valid')

    def test_incorrect_height(self):
        """ Test trying to create a block with incorrect height
        """
        self.block_data['height'] += 10
        try:
            block.Block(**self.block_data)
        except AssertionError as e:
            self.assertEqual(e[0], 'Block is not valid')

    def test_save_to_database(self):
        """ Test saving a block to database.
        """
        new_block = block.Block(**self.block_data)
        block_id = new_block.save()

        self.assertNotEqual(block_id, None)
        saved_block = indiecoin.blockchain.BlockChain(database=self.database).get_block(
            new_block.hash)
        self.assertEqual(new_block.hash, saved_block.hash)
        self.assertEqual(len(new_block.transactions), len(saved_block.transactions))


if __name__ == '__main__':
    unittest.main()
