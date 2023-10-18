import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_l10n_pt_zip_ctt = fields.Boolean(string="ZIP CTT")
    ctt_access_key = fields.Char(
        string="ZIP CTT Access Key", config_parameter="l10n_pt_zip_ctt.access_key"
    )
