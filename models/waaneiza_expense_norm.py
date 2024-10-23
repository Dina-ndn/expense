from ast import Store
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import format_datetime

class WaaneizaExpenseNorm(models.Model):
    _name = "waaneiza.expense.norm"
    _description = "Waaneiza Expense Norm"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "name"

    name = fields.Char(string="Norm Description",required=True)
    amount = fields.Float(string="Norm Amount",track_visibility='onchange',required=True,store=True)
    account_code = fields.Many2one('waaneiza.exp.acc.code',string="Account Code",required=True,store=True)
    norm_category = fields.Many2one('hr.job', string="Postion Category",required=True,store=True)