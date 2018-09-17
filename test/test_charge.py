import unittest
import os

from pystrike.charge import make_charge_class
from pystrike.exceptions import ConnectionException, \
        ClientRequestException, ChargeNotFoundException

strike_api_key = os.environ.get('STRIKE_TESTNET_API_KEY')
strike_api_host = os.environ.get('STRIKE_TESTNET_HOST', 'api.dev.strike.acinq.co')
strike_api_base = os.environ.get('STRIKE_TESTNET_API_BASE', '/api/v1/')

retrieve_charge_id = os.environ.get('RETRIEVE_CHARGE_ID')

class ChargeTestCase(unittest.TestCase):

    def setUp(self):
        self.ChargeClass = make_charge_class(
                strike_api_key,
                strike_api_host,
                strike_api_base,
            )

    def test_charge_creation(self):

        # Initialize a charge and create it on the Strike server.
        charge = self.ChargeClass(
                100,
                self.ChargeClass.CURRENCY_BTC,
                'Charge creation note',
            )

        # The charge should have retrieved a charge.id during the
        # process of syncing to the server. This id should be a string
        # and it should be fairly long.
        self.assertGreater(len(charge.id), 10)

    def test_retrieve(self):

        # Retrieve a charge from Strike with a given charge id.
        charge = self.ChargeClass.from_charge_id(retrieve_charge_id)

        # The retrieved charge should have a charge.payment_request.
        # This payment request should be a string, and it should be
        # fairly long.
        self.assertGreater(len(charge.payment_request), 10)

    def test_charge_not_found_exception(self):

        with self.assertRaises(ChargeNotFoundException):

            # Retrieve a charge from Strike with a non-existant charge
            # id.
            charge = self.ChargeClass.from_charge_id('ch_madeupchargeid')

    def test_client_request_exception(self):

        with self.assertRaises(ClientRequestException):

            # Attempt to create a charge with a non-existant currency.
            charge = self.ChargeClass(
                    100,
                    'non-existant-currency',
                    'Charge creation note',
                )

