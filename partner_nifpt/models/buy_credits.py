import json
import logging

import requests

from odoo import models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


def buy_credits_nif(API_KEY, num_credits_buy):
    if API_KEY:
        if 1000 <= num_credits_buy <= 1000000:
            while True:

                api_request = (
                    "http://www.nif.pt/?json=1&buy="
                    + str(num_credits_buy)
                    + "&key="
                    + API_KEY
                )
                error_msg = ""
                try:
                    r = requests.get(api_request)
                    r.raise_for_status()

                except requests.exceptions.Timeout:
                    error_msg = _("Timeout")
                except requests.exceptions.TooManyRedirects:
                    error_msg = _("Too many redirects")
                except requests.exceptions.HTTPError as e:
                    error_msg = str(e)
                except requests.exceptions.RequestException as e:
                    error_msg = str(e)
                except json.decoder.JSONDecodeError as e:
                    error_msg = str(e)

                if error_msg:
                    _logger.info(error_msg)

                data_credits = r.json()

                if "credits" in data_credits:
                    amount_credits = data_credits["credits"]
                    mb_entity = data_credits["mb"]["entity"]
                    mb_reference = data_credits["mb"]["reference"]
                    mb_amount = data_credits["mb"]["amount"] + "€"

                    return amount_credits, mb_entity, mb_reference, mb_amount

                elif data_credits["message"] == "Key not valid":
                    raise ValidationError(_("Please enter a valid access key!"))

                elif (
                    data_credits["result"] == "error"
                    and data_credits["message"] != "Key not valid"
                ):
                    raise ValidationError(_("Please enter a valid number!"))
        else:
            raise ValidationError(
                _("Target a number greater than 1000 and must be lower than 1000000!")
            )
    else:
        raise ValidationError(_("Enter an Access key in IAP Account!"))


class BuyCreditsTemplate(models.TransientModel):
    _name = "buy.credits"

    def content_credits_buy(self, num_credits_buy):
        API_KEY = self.env["iap.account"].get("nif.pt").partner_nifpt_token
        _logger.info(API_KEY)
        data_buy_credits = buy_credits_nif(API_KEY, num_credits_buy)
        return (
            data_buy_credits[0],
            data_buy_credits[1],
            data_buy_credits[2],
            data_buy_credits[3],
        )
