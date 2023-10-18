import json
import logging

import requests

from odoo.exceptions import UserError
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)  # pylint: disable=C0103


class WebserviceZipCtt:
    company_id = False
    base_url = ""

    def __init__(self, env, company_id):
        self.company_id = company_id
        self.base_url = "https://www.cttcodigopostal.pt/api/v1/"
        self.API_KEY = (
            env["ir.config_parameter"].sudo().get_param("l10n_pt_zip_ctt.access_key")
        )

    def _request(self, method, service_path, data=None, headers=None):
        """Webservice requester for CTT platform. Makes the call and
        handles exceptions"""

        error_msg = ""
        try:

            # Make the service request
            _logger.debug("%s data: %s" % (service_path, data))
            response = requests.request(
                method,
                self.base_url + self.API_KEY + service_path,
                data=data,
                headers=headers,
            )

            _logger.debug("%s response: %s" % (service_path, response.text))
            response.raise_for_status()
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
        except Exception as e:
            error_msg = str(e)

        if error_msg:
            _logger.info(error_msg)
            error_msg = _("ZIP CTT API Error on service %s:\n\n%s") % (
                service_path,
                error_msg,
            )
            _logger.info(error_msg)
            raise UserError(error_msg)

        return response

    def _request_handler(self, method, service_path, data=None, headers=None):
        """An intermediate level method that makes sure that we have all set
        before performing the actual request if necessary"""

        # headers = {"Content-Type": "application/json"}
        # Go, go, go
        return self._request(method, service_path, data=data, headers=headers)

    #############################
    # Public High Level methods #
    #############################

    def get_address(self, record):

        service_path = "/{zip}".format(zip=record.zip)

        return self._request_handler("GET", service_path)
