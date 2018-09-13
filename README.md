# pystrike

Python wrapper for [Acinq's Strike lightning network payment service](https://strike.acinq.co).

## Use

Initialize the `Charge` class:

```
Charge = charge_class_maker(api_key="YOURAPIKEY", api_base="https://api.dev.strike.acinq.co/api/v1/")
```

Create a new `charge`:

```
charge = Charge(
        currency=Charge.CURRENCY_BTC,
        amount=42000,                   # Amount in Satoshi
        description="1%20Blockaccino",
    )
```

Retrieve a payment request:
```
payment_request = charge.payment_request

# Now `payment_request` might be something like "lntb420u1pdsdxfepp58hgsk3qeggjfx66hxjv3tkk2fmq9k4srkq6z4h69a33euns3rzwsdq4xysyymr0vd4kzcmrd9hx7cqp2fs6hglhgfax7depekep53kmlgkswhcvxlmju3e4k0cdex6ml4xpygcxzt93julus09hj30fruzw9l65n5uktqe9khmlk8uh8pvl3f7sp3026hz"
```

At this point, you would present the `payment_request` to your customer. You can then reference `charge.paid` to determine whether the charge has been paid.

The `charge.paid` is a boolean `@property` method which opperates according to the following pseudocode:
```
class Charge():
    # ...

    def __init__(...):
        # ...
        self.paid = False
        # ...

    # ...

    @property
    def paid(self):
        # If self.paid is False:
            # Ask the server if the charge is paid and update self.paid

        # return self.paid
```



