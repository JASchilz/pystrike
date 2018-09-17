.. image:: https://travis-ci.org/JASchilz/pystrike.svg?branch=master
    :target: https://travis-ci.org/JASchilz/pystrike
.. image:: https://api.codeclimate.com/v1/badges/3b5d31b0331c41501416/maintainability
   :target: https://codeclimate.com/github/JASchilz/pystrike/maintainability
   :alt: Maintainability
.. image:: https://img.shields.io/pypi/v/pystrike.svg
   :target: https://pypi.org/project/pystrike/
   :alt: PyPI
.. image:: https://readthedocs.org/projects/pystrike/badge/?version=latest
   :target: https://pystrike.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status


pystrike
========

Python wrapper for `Acinq’s Strike lightning network payment service`_.

The lightning network allows near-fee, near-instant transactions atop the Bitcoin chain layer. Acinq operates the Strike service, which allows you to create lightning invoices, receive lightning payments into your Strike account, and then receive consolidated payouts on-chain. This Python library allows you to invoice customers and check the payment-status of those invoices in just a few lines of code.

This library does not require any third-party dependencies.

Example
-------

Initialize the ``Charge`` class:

::

   from pystrike.charge import make_charge_class

   Charge = make_charge_class(
       api_key="YOURSTRIKETESTNETAPIKEY",
       api_host="api.dev.strike.acinq.co",
       api_base="/api/v1/",
   )

Create a new ``charge``:

::

   charge = Charge(
           currency=Charge.CURRENCY_BTC,
           amount=4200,                    # Amount in Satoshi
           description="services rendered",
       )

Retrieve a payment request:

::

   payment_request = charge.payment_request

   # Now `payment_request` might be something like "lnbtb420u1pfoobarbaz..."
   
At this point, you would present the ``payment_request`` to your
customer. You can call ``charge.update()`` to poll the Strike server
for the current status of the charge, and then retrieve whether or not
the charge has been paid from the ``charge.paid`` attribute.

The example above uses Strike's testnet web service at ``api.dev.strike.acinq.co``. When you're ready to issue mainnet lightning invoices, you'll need to use your Strike mainnet API key and make your requests to host ``api.strike.acinq.co``.

Use
---

Install pystrike
^^^^^^^^^^^^^^^^

::

   $ pip install pystrike

Creating an API Key
^^^^^^^^^^^^^^^^^^^

Begin by creating an account on `Acinq’s Strike lightning network payment service`_. Note that there is also a `testnet version of the service`_ that you may wish to use for your initial development. The two versions of this service are distinct, with separate accounts, separate API keys, and separate API hosts.

Once you have created an account and logged into the dashboard, you can retrieve an API key from your dashboard settings. You will need this key to configure your connection to Strike.

Configuring a Charge Class
^^^^^^^^^^^^^^^^^^^^^^^^^^

You'll begin by creating a Charge class from the provided ``make_charge_class`` function.
    
::

   from pystrike.charge import make_charge_class

   Charge = make_charge_class(
       api_key="YOURSTRIKETESTNETAPIKEY",
       api_host="api.dev.strike.acinq.co",
       api_base="/api/v1/",
   )

The host will probably be one of:

  - api.strike.acinq.co: the mainnet version of Strike
  - api.dev.strike.acinq.co: the testnet version of Strike

If you're pointing your charge class to the mainnet version then be sure to use the API key from your mainnet Strike dashboard.

Creating a Charge
^^^^^^^^^^^^^^^^^

You can create a new charge with the following code:

::

   charge = Charge(
           currency=Charge.CURRENCY_BTC,
           amount=4200,                     # Amount in Satoshi
           description="services rendered",
       )

This initialization will automatically reach out to the Strike web service and create a new charge on their servers. Once this call has returned, you can immediately access the details of that charge through ``charge.id``, ``charge.payment_request``, and so on.

At this point, you might present the ``charge.payment_request`` to your customer for payment.

Retrieving a Charge
^^^^^^^^^^^^^^^^^^^

Rather than creating a new charge, if you know the Strike id of an existing charge you can retrieve it with the following code:

::

   charge = Charge.from_charge_id('ch_LWafoobarbazjFFv8eurFJkerhgDA')

Updating a Charge
^^^^^^^^^^^^^^^^^

You can poll the Strike server to update your local charge object:

::

   charge.update()

For example, if you are waiting on payment for a charge, you might run ``charge.update()`` and then access ``charge.paid`` to see if a payment has been recorded for the charge on the Strike server.

If you're developing a web application, you could use web hooks instead of polling the server. See Strike's documentation on web hooks for more information.

Testing
-------

Running the library tests requires two environment variables:

  - ``STRIKE_TESTNET_API_KEY``: Your API key for the ``api.dev.strike.acinq.co``
    web service.
  - ``RETRIEVE_CHARGE_ID``:  The Strike id of a charge in your
    ``api.dev.strike.acinq.co``. For example: ``ch_LWafoobarbazjFFv8eufoobarbaz``

.. _Acinq’s Strike lightning network payment service: https://strike.acinq.co
.. _testnet version of the service: https://dev.strike.acinq.co
