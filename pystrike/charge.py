"""
Python library for interacting with ACINQ's Strike API for lightning
network payments.
"""

import json
import base64
import http.client
import urllib.parse
import ssl


def make_charge_class(api_key, api_host, api_base):
    """
    Generates a Charge class with the given parameters

    Args:
        api_key (str): An API key associated with your Strike account.
        api_host (str): The host name of the Strike server you'd like
                        to connect to. Probably one of:
                        - "api.strike.acinq.co"
                        - "api.dev.strike.acinq.co"
        api_base (str): The base path of the Strike API on the host
                        server. Probably: "/api/v1/"

    Returns:
        A parameterized Charge class object.
    """

    parameters = {
        'api_key': api_key,
        'api_host': api_host,
        'api_base': api_base,
    }

    class Charge():
        """
        The Charge class is your interface to the Strike web service.
        Use it to create, retrieve, and update lighting network
        charges.

        Each instance is a lazy mirror, reflecting a single charge on
        the Strike servers. The instance is lazy in that it will
        communicate with Strike implicitly, but only as needed.

        When you initialize a charge with an amount and description,
        the instance does not create an instance on Strike until the
        moment that you request an attribute such as `payment_request`.
        If you request the charge's `paid` attribute, then the charge
        will update itself from the Strike server if it has not yet
        seen its payment clear; but if `paid` is already set to `True`
        then the charge will simply report `True` without reaching out
        to the server.
        """

        CURRENCY_BTC = "btc"

        api_key = parameters['api_key']
        api_host = parameters['api_host']
        api_base = parameters['api_base']


        def __init__(
                self,
                amount,
                currency,
                description="",
                customer_id="",
        ):
            """
            Initialize an instance of `Charge`. See the Strike API
            documentation for details on each of the arguments.

            Args:
                amount (int): The amount of the charge, in Satoshi.
                currenency (str): Must be `Charge.CURRENCY_BTC`.
 
            Kwargs:
                description (str): Optional invoice description.
                customer_id (str): Optional customer identifier.

            """


            self.api_connection = http.client.HTTPSConnection(
                self.api_host,
                context=ssl.create_default_context(),
            )

            self.amount = amount
            self.currency = currency
            self.description = description
            self.customer_id = customer_id

            self.id = None
            self.amount_satoshi = None
            self.payment_request = None
            self.payment_hash = None
            self.paid = False
            self.created = None
            self.updated = None

        def __getattribute__(self, name):
            """
            The dunder method `__getattribute__` takes responsibility
            for updating instance attributes from the Strike server as
            needed.

            Specifically, if the client code requests an attribute that
            has not yet been retrieved from the server, then this
            method will retrieve it. And if the client code requests
            the instance's `paid` attribute and the instance has not
            yet seen its payment clear, this method will poll the
            Strike server to detect if payment has cleared.

            Args:
                name (str): The name of the attribute to retrieve

            Returns:
                value: The value of the requested instance attribute

            """
            value = super().__getattribute__(name)

            if value is None and name in [
                    'id', 'amount_satoshi', 'payment_request', 'created', 'updated'
            ]:
                self._update()
                value = super().__getattribute__(name)

            elif name == 'paid' and value is False:
                self._update()
                value = super().__getattribute__(name)

            return value

        @classmethod
        def from_charge_id(cls, charge_id):
            """
            Class method to fill an instance of `Charge` from the
            Strike server.

            Args:
                charge_id (str): The id of a charge on Strike's server.

            Returns:
                An instance of `Charge`, filled from the attributes of
                the charge with the given `charge_id`.
            """

            charge = cls(0, cls.CURRENCY_BTC)

            charge.id = charge_id
            charge._update()

            return charge


        def _update(self):
            auth = base64.b64encode(self.api_key.encode() + b':').decode('ascii')
            am_on_server = super().__getattribute__('id') is not None

            if not am_on_server:
                method = 'POST'
                path = self.api_base + 'charges'
                body = urllib.parse.urlencode({
                    'amount': self.amount,
                    'currency': self.currency,
                    'description': self.description,
                    'customer_id': self.customer_id,
                })
                headers = {
                    'Authorization' : 'Basic ' + auth,
                    'Content-Type' : 'application/x-www-form-urlencoded',
                    'Accept' : '*/*',
                    'User-Agent' : 'pystrike',
                }

            else:
                method = 'GET'
                path = self.api_base + 'charges/' + self.id
                body = None
                headers = {
                    'Authorization' : 'Basic ' + auth,
                    'Accept' : '*/*',
                    'User-Agent' : 'pystrike',
                }

                # print(method, path, body, headers)

            self.api_connection.request(
                method,
                path,
                body=body,
                headers=headers,
            )

            try:
                response = self.api_connection.getresponse()
            except http.client.RemoteDisconnected:
                if method == 'GET':
                    self.api_connection.request(
                        method,
                        path,
                        body=body,
                        headers=headers,
                    )
                    response = self.api_connection.getresponse()


            data = json.loads(response.read())

            self.id = data['id']
            self.amount = data['amount']
            self.currency = data['currency']
            self.amount_satoshi = data['amount_satoshi']
            self.payment_hash = data['payment_hash']
            self.payment_request = data['payment_request']
            self.description = data['description']
            self.paid = data['paid']
            self.created = data['created']
            self.updated = data['updated']

    return Charge
