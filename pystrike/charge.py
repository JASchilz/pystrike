"""
Python library for interacting with ACINQ's Strike API for lightning
network payments.
"""

import json
import base64
import http.client
import urllib.parse
import ssl
import abc
import socket

from .exceptions import ConnectionException, ClientRequestException, \
        ChargeNotFoundException, UnexpectedResponseException, \
        ServerErrorException


class Charge(abc.ABC):
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

    :ivar amount:           The amount of the invoice, in self.currency.
    :ivar currency:         The currency of the request.
    :ivar description:      Narrative description of the invoice.
    :ivar customer_id:      An optional customer identifier.
    :ivar id:               The id of the charge on Strike's server.
    :ivar amount_satoshi:   The amount of the request, in satoshi.
    :ivar payment_request:  The payment request string for the charge.
    :ivar payment_hash:     The hash of the payment for this charge.
    :ivar paid:             Whether the request has been satisfied.
    :ivar created:          When the charge was created, in epoch time.
    :ivar updated:          When the charge was updated, in epoch time.

    """

    CURRENCY_BTC = "btc"

    @property
    @abc.abstractmethod
    def api_key(self):
        """Concrete subclasses must define an api_key."""

        pass

    @property
    @abc.abstractmethod
    def api_host(self):
        """Concrete subclasses must define an api_host."""

        pass

    @property
    @abc.abstractmethod
    def api_base(self):
        """Concrete subclasses must define an api_base."""

        pass

    def __init__(
            self,
            amount,
            currency,
            description="",
            customer_id="",
            create=True,
    ):
        """
        Initialize an instance of `Charge`. See the Strike API
        documentation for details on each of the arguments.

        Args:
            - amount (int): The amount of the charge, in Satoshi.
            - currenency (str): Must be `Charge.CURRENCY_BTC`.

        Kwargs:
            - description (str): Optional invoice description.
            - customer_id (str): Optional customer identifier.
            - create (bool): Whether to automatically create a
                             corresponding charge on the Strike
                             service.


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

        if create:
            self.update()

    def _make_request(self, method, path, body, headers):

        try:
            self.api_connection.request(
                method,
                path,
                body=body,
                headers=headers,
            )
        except socket.gaierror:
            raise ConnectionException("Unable to communicate with host.")

        try:
            try:
                response = self.api_connection.getresponse()
            except http.client.RemoteDisconnected:
                """
                I found that the Strike server will prematurely close
                the connection the _first_ time I make a GET request
                after the invoice has been paid.

                This `except` clause represents a retry on that close
                condition.
                """

                if method == 'GET':
                    self.api_connection.request(
                        method,
                        path,
                        body=body,
                        headers=headers,
                    )
                    response = self.api_connection.getresponse()
        except:
            raise ConnectionException("Unable to communicate with host.")

        return json.loads(response.read())

    def _fill_from_data_dict(self, data):
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

 
    def update(self):
        """
        Update the charge from the server.

        If this charge has an `id`, then the method will _retrieve_ the
        charge from the server. If this charge does not have an `id`,
        then this method will _create_ the charge on the server and
        then fill the local charge from the attributes created and
        returned by the Strike server.
        """

        auth = base64.b64encode(self.api_key.encode() + b':').decode('ascii')
        must_create = super().__getattribute__('id') is None

        if must_create:
            method = 'POST'
            path = self.api_base + 'charges'
            body = urllib.parse.urlencode({
                'amount': self.amount,
                'currency': self.currency,
                'description': self.description,
                'customer_id': self.customer_id,
            })
            headers = {
                'Authorization': 'Basic ' + auth,
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': '*/*',
                'User-Agent': 'pystrikev0.5.1',
            }

        else:
            method = 'GET'
            path = self.api_base + 'charges/' + self.id
            body = None
            headers = {
                'Authorization': 'Basic ' + auth,
                'Accept': '*/*',
                'User-Agent': 'pystrikev0.5.1',
            }

        data = self._make_request(method, path, body, headers)
        
        try:
            self._fill_from_data_dict(data)
        except KeyError:
            if 'code' in data:
                if data['code'] == 404:
                    raise ChargeNotFoundException(data['message'])
                elif data['code'] >= 400 and data['code'] <= 499:
                    raise ClientRequestException(data['message'])
                elif data['code'] >= 500 and data['code'] <= 599:
                    raise ServerErrorException(data['message'])

            raise UnexpectedResponseException(
                "The strike server returned an unexpected response: " +
                json.dumps(data)
            )


    @classmethod
    def from_charge_id(cls, charge_id):
        """
        Class method to create and an instance of `Charge` and fill it
        from the Strike server.

        Args:
            - charge_id (str): The id of a charge on Strike's server.

        Returns:
            - An instance of `Charge`, filled from the attributes of
              the charge with the given `charge_id`.

        """

        charge = cls(0, cls.CURRENCY_BTC, create=False)

        charge.id = charge_id
        charge.update()

        return charge


def make_charge_class(api_key, api_host, api_base):
    """
    Generates a Charge class with the given parameters

    Args:
        - api_key (str): An API key associated with your Strike account.
        - api_host (str): The host name of the Strike server you'd like
                        to connect to. Probably one of:
                        - "api.strike.acinq.co"
                        - "api.dev.strike.acinq.co"
        - api_base (str): The base path of the Strike API on the host
                        server. Probably: "/api/v1/"

    Returns:
        A parameterized Charge class object.
    """

    parameters = {
        'api_key': api_key,
        'api_host': api_host,
        'api_base': api_base,
    }

    class MyCharge(Charge):
        """
        This concrete subclass of `Charge` is defined and returned by
        the `make_charge_class` function.
        """

        api_key = parameters['api_key']
        api_host = parameters['api_host']
        api_base = parameters['api_base']

    return MyCharge
