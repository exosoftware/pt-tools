import re

from odoo import _, api, models
from odoo.exceptions import ValidationError

from ..webservice import WebserviceZipCtt


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.onchange("zip")
    def _onchange_zip(self):

        access_key = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("l10n_pt_zip_ctt.access_key")
        )

        if not self.zip or not access_key:
            return

        # TODO check if address is already in
        # self.verify_existing_address()

        self.correct_syntax_zip()
        data = self._get_details_from_zip()

        if not data:
            return

        data = data[0]
        address = data.get("morada")
        port = data.get("porta")
        city = data.get("concelho")
        state = data.get("distrito-codigo")

        values = {
            "street": "{address}".format(address=address)
            if not port
            else "{address}, {port}".format(address=address, port=port),
            "city": city if city else False,
            "state_id": self.env.ref("base.state_pt_pt-{}".format("0{}".format(state)))
            if len(str(state)) == 1
            else self.env.ref("base.state_pt_pt-{}".format(state)),
        }

        self.update(values)

    def correct_syntax_zip(self):
        """
        Verify if zip code has the correct syntax
        for Portuguese Partners
        """
        if len(self.zip) == 8:
            zip_regex = re.compile(r"^\d{4}(-\d{3})?$")
            for partner in self:
                if partner.country_id and partner.country_id.code == "PT":
                    if partner.zip and not re.match(zip_regex, partner.zip):
                        raise ValidationError(
                            _(
                                "Invalid zip code %s \nCorrect ZIP format for Portugal:"
                                " 4100-100"
                            )
                            % partner.zip
                        )

    def _get_details_from_zip(self):
        """Handle the webservice request"""
        webservice = WebserviceZipCtt(self.env, self.env.company)
        return webservice.get_address(self).json()
