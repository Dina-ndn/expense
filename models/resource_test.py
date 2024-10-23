# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ast import Store
import string
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import format_datetime

class WaaneizaResourceAdvance(models.Model):
    _name = "waaneiza.resource.advance"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Waaneiza Resource Advance"
    _rec_name = 'vr_name'

    process_name = fields.Many2one('hr.employee', string="Process Name", required=True, tracking=True)
    department_id = fields.Many2one('hr.department',string='Department Name',related="process_name.department_id", store=True)
    company_id = fields.Many2one("res.company",string="Company")
    vr_name = fields.Char(string="Voucher No", readonly=True,default=lambda self: _('New'))
    
    datetime = fields.Datetime(string="Receive Date/Time (24 hr format)",required=True,store=True)

    resource_details_lines = fields.One2many('waaneiza.resource.info','info_id',string="Resource Info Lines", index=True,store=True, required=True)
    total_amount = fields.Float(string="Total Amount", compute="_compute_amount",index=True,store=True, readonly=False)
    currency = fields.Many2one('res.currency',string="Currency", store=True, readonly=False)
    
    prepared_by_process = fields.Many2one('hr.employee', string="Prepared By Process", required=True, tracking=True)
    prepared_by_name = fields.Many2one('hr.employee.information',string="Name",related="prepared_by_process.emp_info_ids",required=True)
    prepared_job_id = fields.Many2one('hr.job',string="Rank", related="prepared_by_process.job_id")
    
    check_by_process = fields.Many2one('hr.employee', string="Checked By Process", required=True, tracking=True)
    check_by_name = fields.Many2one('hr.employee.information',string="Name",related="check_by_process.emp_info_ids",required=True)
    check_job_id = fields.Many2one('hr.job',string="Rank", related="check_by_process.job_id")
    
    approve_by_process = fields.Many2one('hr.employee', string="Approved By Process", required=True, tracking=True)
    approve_by_name = fields.Many2one('hr.employee.information',related="approve_by_process.emp_info_ids",string="Name", required=True)
    approve_job_id = fields.Many2one('hr.job',string="Rank", related="approve_by_process.job_id")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, index=True,default='draft', tracking=True)

    #state
    def action_confirm(self):
        self.state = "confirm"


    def action_draft(self):
        self.state = "draft"

    def action_done(self):
        self.state = "done"

    def action_cancel(self):
        self.state = "draft"

    @api.model
    def create(self, vals):
        if vals.get('vr_name', _('New')) == _('New'):
            vals['vr_name'] = self.env['ir.sequence'].next_by_code(
                'waaneiza.resource.seq') or _('New')
            vals['vr_name'] =  str(vals['vr_name']) 
        result = super(WaaneizaResourceAdvance, self).create(vals)
        return result


     #compute amount
    @api.depends('resource_details_lines')
    def _compute_amount(self):
        for rec in self:
            total = 0.0
            for exp in rec.resource_details_lines:
                total += exp.amount
            rec.total_amount= total


class WaaneizaResourceInfo(models.Model):
    _name = 'waaneiza.resource.info'
    _description = 'Waaneiza Resource Info'
    
    info_id = fields.Many2one('waaneiza.resource.advance',string="info_id",ondelete='cascade')
    account_code_sub = fields.Many2one('waaneiza.exp.acc.code.sub',string="Account sub Code",store=True)
    account_description = fields.Char("Account Description",related="account_code_sub.description",store=True)
    vendor_id = fields.Many2one('res.company',string="Vendor Name")
    description= fields.Char(string="Description")
    amount = fields.Float(string='Amount')
    currency = fields.Many2one('res.currency',string="Currency",store=True, readonly=False)