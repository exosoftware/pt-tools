import json
import logging

import requests

from odoo import api, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


def check_api_nif(API_KEY, nif_numeric):
    if API_KEY:
        while True:
            api_request = (
                "http://www.nif.pt/?json=1&q=" + nif_numeric + "&key=" + API_KEY
            )
            error_msg = ""
            data = ""
            try:
                r = requests.get(api_request)
                r.raise_for_status()
                data = r.json()

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
                error_msg = _(" Error - {}").format(error_msg)
                _logger.info(error_msg)
                raise ValidationError(error_msg)

            if data["nif_validation"] and data["result"] != "error":
                # Save important content from webservice
                user_data = data["records"][str(nif_numeric)]
                name = user_data["title"]
                address = user_data["address"]
                city = user_data["place"]["city"]
                state = user_data["geo"]["region"]
                if user_data["place"]["pc4"] and user_data["place"]["pc3"]:
                    zip_code = "-".join(
                        [user_data["place"]["pc4"], user_data["place"]["pc3"]]
                    )
                else:
                    zip_code = None

                phone = user_data["contacts"]["phone"]
                email = user_data["contacts"]["email"]
                website = user_data["contacts"]["website"]

                # _logger.info(name, address, city, state, zip_code, tax, phone, email, website)
                return name, address, city, state, zip_code, phone, email, website

            elif data["nif_validation"] and data["result"] != "error":
                raise ValidationError(
                    _("Valid NIF, but impossible to present personal information!")
                )
            elif (
                data["message"]
                == "Limit per minute reached. Please, try again later or buy credits."
            ):
                raise ValidationError(
                    _(
                        "Reached the credit limit, to enjoy the service, purchase more credits!"
                    )
                )

            elif data["message"] == "Key not valid":
                raise ValidationError(_("Please enter a valid access key!"))
            else:
                raise ValidationError(_("Enter a valid NIF!"))
    else:
        raise ValidationError(_("Enter an Access key in IAP Account!"))


class ContactsTemplate(models.Model):
    _inherit = "res.partner"

    @api.onchange("vat")
    def _onchange_vat(self):
        if self.vat:
            nif = self.vat
            if nif[:2].upper() == "PT" and nif[2:11].isnumeric() and len(nif) == 11:
                if (
                    self.env["ir.config_parameter"]
                    .sudo()
                    .get_param("partner_nifpt.new_credits")
                    and self.env["iap.account"].get("nif.pt").partner_nifpt_token
                ):
                    nif_numeric = nif[2:11]
                    API_KEY = self.env["iap.account"].get("nif.pt").partner_nifpt_token
                    content = check_api_nif(API_KEY, nif_numeric)

                    self.name = content[0]
                    self.street = content[1]
                    self.city = content[2]
                    state = self.env["res.country.state"].search(
                        [("name", "=", content[3])]
                    )
                    if state:
                        self.state_id = state
                    self.zip = content[4]
                    self.email = content[6]
                    self.website = content[7]
                else:
                    raise ValidationError(_("You need to configure IAP Account"))
