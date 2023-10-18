from odoo import fields, models


class IapAccount(models.Model):
    _inherit = "iap.account"

    provider = fields.Selection(
        selection_add=[("partner_nifpt", "Partner NIF.PT")],
        ondelete={"partner_nifpt": "cascade"},
    )
    partner_nifpt_token = fields.Char(string="Access Key")

    def _get_service_from_provider(self):
        if self.provider == "partner_nifpt":
            return "nif.pt"
        return super()._get_service_from_provider()

    @property
    def _server_env_fields(self):
        res = super()._server_env_fields
        res.update(
            {
                "partner_nifpt_token": {},
            }
        )
        return res
