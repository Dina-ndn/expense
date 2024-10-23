# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import format_datetime

class WaaneizaExpAccCode(models.Model):
    _name = "waaneiza.exp.acc.code"
    _description = "Waaneiza Exp Account Code"
    _rec_name = "name"


    name = fields.Char(string="Account Code",index=True, copy=False, store=True, readonly=False, tracking=True)
    description = fields.Char(string="Description",required=True,store=True)


class WaaneizaExpAccCodeSub(models.Model):
    _name = "waaneiza.exp.acc.code.sub"
    _description = "Waaneiza Exp Account Code Sub"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "name"


    name = fields.Char(string="Sub Account Code",required=True)
    description = fields.Char(string="Description",required=True,store=True)
    account_code = fields.Many2one('waaneiza.exp.acc.code',string="Main Account Code",required=True)
    acc_des = fields.Char(string="Main Heading",related='account_code.description',required=True)
