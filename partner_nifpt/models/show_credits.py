import json
import logging

import requests

from odoo import models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


def check_credits_nif(API_KEY):
    if API_KEY:
        while True:
            api_request = "http://www.nif.pt/?json=1&credits=1&key=" + API_KEY
            error_msg = ""
            try:
                r = requests.get(api_request)
                r.raise_for_status()
                data_credits_status = r.json()

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
            _logger.info(data_credits_status)
            try:
                if data_credits_status["credits"]:
                    # credits_month = data_credits_status['credits']['month']
                    # credits_day = data_credits_status['credits']['day']
                    # credits_hour = data_credits_status['credits']['hour']
                    # credits_minute = data_credits_status['credits']['minute']
                    credits_paid = data_credits_status["credits"]["paid"]

                    return credits_paid
            except Exception:
                credits_paid = 0
                return credits_paid

    else:
        credits_paid = 0
        return credits_paid


class ShowCreditsTemplate(models.TransientModel):
    _name = "show.credits"

    def content_credits_info(self):
        API_KEY = self.env["iap.account"].get("nif.pt").partner_nifpt_token
        data_credits = check_credits_nif(API_KEY)
        return data_credits
