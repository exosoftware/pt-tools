import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    nif_pt = fields.Boolean(
        string="Partner NIF Autocomplete",
        config_parameter="partner_nifpt.default_state",
    )
    new_credits = fields.Integer(readonly="True")

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        data_details_credits = self.env["show.credits"].content_credits_info()
        self.env["ir.config_parameter"].sudo().set_param(
            "partner_nifpt.new_credits", data_details_credits
        )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        credits_updated = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("partner_nifpt.new_credits")
        )
        if credits_updated:
            res.update(new_credits=credits_updated)
        return res
