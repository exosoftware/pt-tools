import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class CreditDetails(models.TransientModel):
    _name = "buy_credits.wizard"
    _inherit = ["multi.step.wizard.mixin"]
    _description = "Multi Step Wizard"

    project_id = fields.Many2one(
        comodel_name="partner_nifpt",
        name="Project",
        required=True,
        ondelete="cascade",
        default=lambda self: self._default_project_id(),
    )

    num_credits_buy = fields.Integer(
        string="Credits to buy",
    )
    company = fields.Many2many(
        "res.company",
        string="Select your company",
    )
    credits = fields.Char(readonly="True", compute="_compute_buy_credits_wizard")
    entity = fields.Char(readonly="True")
    reference = fields.Char(readonly="True")
    amount = fields.Char(readonly="True")

    def _compute_buy_credits_wizard(self):
        data_details = self.env["buy.credits"].content_credits_buy(self.num_credits_buy)
        self.credits = data_details[0]
        self.entity = data_details[1]
        self.reference = data_details[2]
        self.amount = data_details[3]
        return data_details

    def send_email(self):
        email_user = self.env.user.email
        data_details = self.env["buy.credits"].content_credits_buy(self.num_credits_buy)

        # region email_html
        email_html = (
            """<tbody> <tr> <td align="center"> <table border="0" cellpadding="0"
            cellspacing="0" width="590"
            style="padding:24px;background-color:white;color:#454748;border-collapse
            :separate"> <tbody> <tr> <td align="center" style="min-width:590px">
            <table border="0" cellpadding="0" cellspacing="0" width="100%"
            style="background-color:white;padding:0;border-collapse:separate">
            <tbody> <tr> <td valign="middle"> <span style="font-size:10px">Your
            Credits to Buy</span><br> </td> </tr> <tr> <td colspan="2"
            style="text-align:center"> <hr width="100%" style="background-color:rgb(
            204,204,204);border:medium
            none;clear:both;display:block;font-size:0px;min-height:1px;line-height:0
            ;margin:4px 0px 32px 0px"> </td> </tr> </tbody> </table> </td> </tr> <tr>
            <td style="padding:0"> <div
            style="font-size:13px;font-family:&quot;Lucida Grande&quot;,Helvetica,
            Verdana,Arial,sans-serif;margin:0px;padding:0px"> <p
            style="margin:0px;font-size:12px;font-family:&quot;Lucida Grande&quot;,
            Helvetica,Verdana,Arial,sans-serif;padding:0px"> Hello, <br><br> You can
            make your payment by ATM<br><br>

               <table cellpadding="0" cellspacing="0"
               style="margin:auto;border-left:1px solid black;border-right:1px solid
               black;border-top:1px solid black;width:211px"> <tbody> <tr> <td
               valign="top" style="border-bottom:solid 1px
               #222;padding-top:5px;padding-bottom:5px"> </td> <td valign="middle"
               width="100%" style="padding-left:10px;border-bottom:solid 1px
               #222;padding-top:5px;padding-bottom:5px">Payment&nbsp;&nbsp;</td>
               </tr> <tr> <td valign="top" align="left" style="border-bottom:solid
               1px #222;padding-top:2px;padding-bottom:2px"><strong>&nbsp;Credits
               :</strong></td> <td valign="top" align="right"
               style="border-bottom:solid 1px
               #222;padding-top:2px;padding-bottom:2px;padding-right:2px">"""
            + str(data_details[0])
            + """</td> </tr> <tr> <td valign="top" align="left"
            style="border-bottom:solid 1px
            #222;padding-top:2px;padding-bottom:2px"><strong>&nbsp;Entity:</strong
            ></td> <td valign="top" align="right" style="border-bottom:solid 1px
            #222;padding-top:2px;padding-bottom:2px;padding-right:2px">"""
            + str(data_details[1])
            + """</td> </tr> <tr> <td valign="top" align="left"
            style="border-bottom:solid 1px
            #222;padding-top:2px;padding-bottom:2px"><strong>&nbsp;Reference:</strong
            ></td> <td valign="top" align="right" style="border-bottom:solid 1px
            #222;padding-top:2px;padding-bottom:2px;padding-right:2px">"""
            + str(data_details[2])
            + """</td> </tr> <tr> <td valign="top" align="left"
            style="border-bottom:solid 1px
            #222;padding-top:2px;padding-bottom:2px"><strong>&nbsp;Amount:</strong
            ></td> <td valign="top" align="right" style="border-bottom:solid 1px
            #222;padding-top:2px;padding-bottom:2px;padding-right:2px">"""
            + str(data_details[3])
            + """</td> </tr> </tbody> </table> <br> Thank you for your trust!
            <br><br> Do not hesitate to contact us if you have any questions.
            <br><br> </p> </div> <div style="margin:32px 0px 32px
            0px;text-align:center"> <a style="background-color:#875a7b;padding:8px
            16px 8px 16px;text-decoration:none;color:#fff;border-radius:5px;font-size
            :13px" href="https://www.nif.pt/" target="_blank"> Official Site NIF.PT
            </a> </div> </td> </tr> </tbody> </table> </td> </tr> <tr> <td
            align="center" style="min-width:590px;padding:8px;font-size:11px">
            Powered by <a href="https://www.odoo.com?utm_source=db&amp;utm_medium
            =email" style="color:#875a7b" target="_blank"
            data-saferedirecturl="https://www.google.com/url?q=https://www.odoo.com
            ?utm_source%3Ddb%26utm_medium%3Demail&amp;source=gmail&amp;ust
            =1654276588296000&amp;usg=AOvVaw3rBeHuj89X_cLplu73JRuG">Odoo</a> </td>
            </tr> </tbody>"""
        )
        # endregion

        vals = {
            "subject": "Odoo Partner NIF.PT",
            "body_html": email_html,
            "email_to": email_user,
            "auto_delete": False,
        }

        mail_id = self.env["mail.mail"].sudo().create(vals)
        mail_id.sudo().send()

    @api.model
    def _selection_state(self):
        return [
            ("start", "Start"),
            ("configure", "Configure"),
            ("custom", "Customize"),
            ("final", "Final"),
        ]

    @api.model
    def _default_project_id(self):

        return self.env.context.get("active_id")

    # def state_exit_start(self):
    #    self.state = 'configure'

    # def state_exit_configure(self):
    #    self.state = 'custom'

    def state_exit_custom(self):
        self.state = "final"
