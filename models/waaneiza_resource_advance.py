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

    uti_name = fields.Many2one('waaneiza.utilization',string='Utilzation Vr No.',domain="[('is_advance','!=', 'Yes')]", store=True)
    description = fields.Char(string="Description",related="uti_name.description",store=True)
    process_name = fields.Many2one('hr.employee', string="Process Name",related="uti_name.process_name",store=True)
    process_id = fields.Integer(string="Process ID")
    department_id = fields.Many2one('hr.department',string='Department Name',related="uti_name.department_id", index=True, copy=False, store=True, readonly=False)
    company_id = fields.Many2one("res.company",string="Company",related="uti_name.company_id",store=True)
    vr_name = fields.Char(string="Sr No", readonly=True,copy=False, index=True, default=lambda self: _('New'))
    
    datetime = fields.Datetime(string="Receive Date/Time (24 hr format)",required=True,store=True)

    resource_details_lines = fields.One2many('waaneiza.resource.info','info_id',string="Resource Info Lines", index=True, copy=False, store=True, readonly=False, required=True)
    total_amount = fields.Float(string="Total Amount", compute="_compute_amount",index=True, copy=False, store=True, readonly=False)
    total = fields.Float(string="Total Amount", related="uti_name.total_amount",index=True, copy=False, store=True, readonly=False)
    currency_id = fields.Many2one('res.currency',string="Currency",related="uti_name.currency_id", store=True, readonly=False)
    
    prepared_by_process = fields.Many2one('hr.employee', string="Prepared By Process", required=True, tracking=True)
    prepared_by_name = fields.Many2one('hr.employee.information',string="Name",related="prepared_by_process.emp_info_ids")
    prepared_job_id = fields.Many2one('hr.job',string="Rank", related="prepared_by_process.job_id")
    
    checked_by_user = fields.Many2one('res.users', related="checked_by_process.user_id",string="Checked By Employee User")
    checked_by_process = fields.Many2one('hr.employee', string="Checked By Process", required=True, tracking=True)
    checked_by_name = fields.Many2one('hr.employee.information',string="Name",related="checked_by_process.emp_info_ids",required=True)
    checked_job_id = fields.Many2one('hr.job',string="Rank", related="checked_by_process.job_id")
    
    approved_by_user = fields.Many2one('res.users', related="approved_by_process.user_id",string="Approved By User")
    approved_by_process = fields.Many2one('hr.employee', string="Approved By Process", required=True, tracking=True)
    approved_by_name = fields.Many2one('hr.employee.information',related="approved_by_process.emp_info_ids",string="Name")
    approved_job_id = fields.Many2one('hr.job',string="Rank", related="approved_by_process.job_id")
    
    state = fields.Selection([
        ('draft', 'draft'),
        ('tocheck', 'To Check'),
        ('checked', 'Checked'),
        # ('tosubmit', 'To Approve'),
        ('confirm', 'To Approve'),
        ('approve', 'Approved'),
        ('refuse', 'Refuse'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    #state
    def action_confirm(self):
        self.state = 'confirm'
        self.activity_update()
    
    def action_draft(self):
        self.state = "draft"
    
    def action_submit_to_check(self):
        self.state = "tocheck"
        self.check_activity_update()

    def action_done(self):
        self.state = "done"
        self.uti_name.is_advance = 'Yes'

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

    def unlink(self):
        for rec in self:
            if rec.state =='done':
                raise ValidationError(_("You cannot delete record with 'Done' State"))
        rtn = super(WaaneizaResourceAdvance,self).unlink()
        return rtn  


     #compute amount
    @api.depends('resource_details_lines')
    def _compute_amount(self):
        for rec in self:
            total = 0.0
            for exp in rec.resource_details_lines:
                total += exp.amount
            rec.total_amount= total
    ############### Start For Checker Approval Function ###############
    is_visible_check = fields.Boolean(default=False,string="Visible",compute='_compute_show_visible_check',
        help='Technical field used to decide whether the button should be displayed.')

    @api.onchange('state')
    def _compute_show_visible_check(self):
        for rec in self:
            if rec.state in ('tocheck'):
                if self.checked_by_process.user_id == self.env.user:
                    rec.is_visible_check= True
                else:
                    rec.is_visible_check= False  
            else:
                rec.is_visible_check= False  

    def action_check_requisition(self):
        self._do_check()

    def _do_check(self):
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('There are no expense reports to approve.'),
                'type': 'warning',
                'sticky': False,  #True/False will display for few seconds if false
            },
        }
        filtered_sheet = self.filtered(lambda s: s.state in ['tocheck'])
        if not filtered_sheet:
            return notification
        for sheet in filtered_sheet:
            sheet.write({'state': 'checked', 'checked_by_user': sheet.checked_by_user.id or self.env.user.id})
        notification['params'].update({
            'title': _('The expense reports were successfully checked.'),
            'type': 'success',
            'next': {'type': 'ir.actions.act_window_close'},
        })
        self.check_activity_update()
        return notification

    def _get_responsible_for_check(self):
        if self.checked_by_user:
            return self.checked_by_user

    def check_activity_update(self):
        for expense_report in self.filtered(lambda hol: hol.state == 'tocheck'):
            self.activity_schedule(
                'waaneiza_expense_cashier.mail_act_resource_check',
                user_id=expense_report.sudo()._get_responsible_for_check().id or self.env.user.id)
        self.filtered(lambda hol: hol.state == 'checked').activity_feedback(['waaneiza_expense_cashier.mail_act_resource_check'])
        self.filtered(lambda hol: hol.state in ('draft', 'cancel')).activity_unlink(['waaneiza_expense_cashier.mail_act_resource_check'])

    ################ End For Checker Approval Function ###############

    ############### Start For Approval Function ###############
    test_user_id = fields.Char(string="Test User ID",compute="_testing_user")
    test_user = fields.Char(string="Test User",compute="_testing_user")
    is_visible = fields.Boolean(default=False,string="Visible",compute='_compute_show_visible',
        help='Technical field used to decide whether the button should be displayed.')

    @api.onchange('state','test_user_id','test_user')
    def _compute_show_visible(self):
        for rec in self:
            if rec.state in ('confirm'):
                if self.approved_by_process.user_id == self.env.user or self.approved_by_process_second.user_id == self.env.user:
                    rec.is_visible= True
                else:
                    rec.is_visible= False  
            else:
                rec.is_visible= False  

    def _testing_user(self):
        for rec in self:
            rec.test_user_id = rec.approved_by_process.user_id.name
            rec.test_user = self.env.user.name

    is_visible_cashdrawing = fields.Boolean(default=False,string="Visible",compute='_compute_show_visible_cashdrawing',
        help='Technical field used to decide whether the button should be displayed.')
    
    @api.onchange('state')
    def _compute_show_visible_cashdrawing(self):
        for rec in self:
            if rec.state not in ('draft','confirm','cancel','tosubmit','tocheck','approve','refuse','checked'):
                if self.env.user != self.approved_by_process.user_id and self.env.user != self.checked_by_process.user_id:
                    rec.is_visible_cashdrawing= True
                else:
                    rec.is_visible_cashdrawing= False  
            else:
                rec.is_visible_cashdrawing= False    

    def action_approve_requisition(self):
        self._do_approve()

    def _do_approve(self):
        
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('There are no expense reports to approve.'),
                'type': 'warning',
                'sticky': False,  #True/False will display for few seconds if false
            },
        }
        filtered_sheet = self.filtered(lambda s: s.state in ['confirm', 'draft'])
        if not filtered_sheet:
            return notification
        for sheet in filtered_sheet:
            sheet.write({'state': 'approve', 'approved_by_user': sheet.approved_by_user.id or self.env.user.id})
        notification['params'].update({
            'title': _('The expense reports were successfully approved.'),
            'type': 'success',
            'next': {'type': 'ir.actions.act_window_close'},
        })
        self.activity_update()
        return notification

    def _get_responsible_for_approval(self):
        if self.approved_by_user:
            return self.approved_by_user

    def activity_update(self):
        for expense_report in self.filtered(lambda hol: hol.state == 'confirm'):
            self.activity_schedule(
                'waaneiza_expense_cashier.mail_act_resource_approval',
                user_id = expense_report.sudo()._get_responsible_for_approval().id)
        self.filtered(lambda hol: hol.state == 'approve').activity_feedback(['waaneiza_expense_cashier.mail_act_resource_approval'])
        self.filtered(lambda hol: hol.state in ('draft', 'cancel')).activity_unlink(['waaneiza_expense_cashier.mail_act_resource_approval'])

    ################ End For Approval Function ###############


class WaaneizaResourceInfo(models.Model):
    _name = 'waaneiza.resource.info'
    _description = 'Waaneiza Resource Info'
    
    info_id = fields.Many2one('waaneiza.resource.advance',string="info_id",ondelete='cascade')
    account_code_sub = fields.Many2one('waaneiza.exp.acc.code.sub',string="Account sub Code",store=True)
    account_description = fields.Char("Account Description",related="account_code_sub.description",store=True)
    vendor_id = fields.Char(string="Vendor Name")
    description = fields.Char(string="Description")
    amount = fields.Float(string='Amount')
    currency = fields.Many2one('res.currency',string="Currency",store=True, readonly=False)