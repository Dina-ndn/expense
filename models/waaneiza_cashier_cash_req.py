# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ast import Store
import string
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import format_datetime

class WaaneizaCashierCashReq(models.Model):
    _name = "waaneiza.cashier.cash.req"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Waaneiza Cash Requisition"

    name = fields.Char(string="Sr.No:", readonly=True, required=True, copy=False, index=True, default=lambda self: _('New'))
    date = fields.Date(string="Date")
    company_id = fields.Many2one("res.company",string="Company")

    requisition_details_lines = fields.One2many('waaneiza.cashier.req.details','requisition_id',string="Requisition Details Lines", index=True, copy=False, store=True, readonly=False, required=True)

    total_amount = fields.Float(string="Total Amount", compute="_compute_total_amount",index=True, copy=False, store=True, readonly=False, tracking=True)
    currency_id = fields.Many2one('res.currency',string="Currency",related='requisition_details_lines.currency',store=True)

    requested_by_process = fields.Many2one('hr.employee', string="Requested By Process", required=True,tracking=True,store=True)
    requested_by_name = fields.Many2one('hr.employee.information',string="Requested By Name",related="requested_by_process.emp_info_ids")
    requested_job_id = fields.Many2one('hr.job',string="Rank", related="requested_by_process.job_id")
    requested_department_id = fields.Many2one('hr.department',string="Department",related="requested_by_process.department_id")

    # approved_by_name = fields.Many2one('res.users',string="Approved By Name",required=True)
    approved_by_user = fields.Many2one('res.users', related="approved_by_process.user_id",string="Approved By User")
    approved_by_process = fields.Many2one('hr.employee', string="Approved By Process", tracking=True,required=True)
    approved_by_name = fields.Many2one('hr.employee.information', related="approved_by_process.emp_info_ids",string="Approved By Name")
    approved_job_id = fields.Many2one('hr.job',string="Rank", related="approved_by_process.job_id")
    approved_department_id = fields.Many2one('hr.department',string="Department", related="approved_by_process.department_id")

    # Second Approver 
    approved_by_user_second = fields.Many2one('res.users', related="approved_by_process_second.user_id",string="Second Approved By User")
    approved_by_process_second = fields.Many2one('hr.employee', string="Second Approved By Process", tracking=True,required=True)
    approved_by_name_second = fields.Many2one('hr.employee.information', related="approved_by_process_second.emp_info_ids",string="Second Approved By Name")
    approved_job_id_second = fields.Many2one('hr.job',string="Rank", related="approved_by_process_second.job_id")
    approved_department_id_second = fields.Many2one('hr.department',string="Department", related="approved_by_process_second.department_id")
    # Submit Approver
    approved_submit = fields.Char(string='Real Approved By Process',store=True)
    approved_name = fields.Char(string="Approved By Name",store=True)
    approved_job = fields.Char(string="Rank",store=True)
    approved_department = fields.Char(string="Department",store=True)

    checked_by_user = fields.Many2one('res.users', related="checked_by_process.user_id",string="Checked By Employee User")
    checked_by_process = fields.Many2one('hr.employee', string="Checked By Process", required=True, tracking=True)
    checked_by_name = fields.Many2one('hr.employee.information', related="checked_by_process.emp_info_ids",string="Checked By Employee Name")
    checked_job_id = fields.Many2one('hr.job',string="Rank", related="checked_by_process.job_id")
    checked_department_id = fields.Many2one('hr.department',string="Department", related="checked_by_process.department_id")
    duplicate_expense_ids = fields.Many2many('waaneiza.cashier.cash.req', compute='_compute_duplicate_expense_ids')

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
    is_refused = fields.Boolean("Explicitly Refused by manager or accountant", readonly=True, copy=False, tracking=True)
    reason = fields.Char(string="Reason Refuse", tracking=True)
    show_validate = fields.Boolean(
        compute='_compute_show_validate',
        help='Technical field used to decide whether the button "Validate" should be displayed.')
    
    expense_cashdrawing_lines = fields.One2many('waaneiza.cashier.cashdrawing','requisition_id',string="Expense Cashdrawing Lines", index=True, copy=False, store=True, readonly=False)
    cashdrawing_count = fields.Integer(compute="_compute_cashdrawing_count", string='Cashdrawing Counts', copy=False, default=0, store=True)
    cashdrawing_ids = fields.Many2many('waaneiza.cashier.cashdrawing', compute="_compute_cashdrawing_count", string='Cashdrawing', copy=False, store=True)
    #connect cashdrawing
    is_draw = fields.Char(string="Is Drawing?",store=True,default='No',
        help='Technical field used to decide whether the field "Cash Out Code" should be displayed.')
    #line number auto generate
    def set_line_number(self):
        sl_no = 0
        for line in self.requisition_details_lines:
            sl_no += 1
            line.sr_number = sl_no
        return


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'waaneiza.cashier.cash.requisition.srn') or _('New')
            vals['name'] =  str(vals['name']) 
        result = super(WaaneizaCashierCashReq, self).create(vals)
        result.set_line_number()
        return result
        
    def unlink(self):
        for rec in self:
            if rec.state =='done':
                raise ValidationError(_("You cannot delete record with 'Done' State"))
        rtn = super(WaaneizaCashierCashReq,self).unlink()
        return rtn  
    
    #line number auto generate
    def write(self, vals):
        res = super(WaaneizaCashierCashReq, self).write(vals)

        #Line number auto generate
        self.set_line_number()
        # sl_no = 0
        # for line in self.requisition_details_lines:
        #     sl_no += 1
        #     line.sr_number = sl_no
        return res

    ############### Start Get Real Approver of Data ###############
    # @api.depends('approved_submit')
    # def _get_data_realapprover(self):
    #     for rec in self:
    #         approve_one_string = str(rec.approved_by_process)
    #         approve_two_string = str(rec.approved_by_process_second)
    #         if rec.approved_submit == approve_one_string:
    #             rec.approved_name = 'Approver One'
    #             # rec.approved_submit_job = str(rec.approved_job_id)
    #             # rec.approved_submit_department = str(rec.approved_department_id)
    #         elif rec.approved_submit == approve_two_string:
    #             rec.approved_name = 'Approver Two'
    #             # rec.approved_submit_job = str(rec.approved_job_id_second)
    #             # rec.approved_submit_department = str(rec.approved_department_id_secondsss)
    #         else:
    #             rec.approved_name = 'else state'


    ############### Start Count Cashdrawing ###############
    @api.depends('expense_cashdrawing_lines')
    def _compute_cashdrawing_count(self):
        for count in self:
            counts = count.mapped('expense_cashdrawing_lines')
            count.cashdrawing_ids = counts
            count.cashdrawing_count = len(counts)
    
    def action_view_cashdrawing(self, counts=False, context=None):
        if not counts:
            counts = self.cashdrawing_ids
        if len(counts) > 1:
            result = self.env['ir.actions.act_window']._for_xml_id('waaneiza_expense_cashier.action_waaneiza_cashier_cashdrawing')
            result['domain'] = [('id', 'in', counts.ids)]
            return result

        elif len(counts) <= 1:
            return {
            'res_model': 'waaneiza.cashier.cashdrawing',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref("waaneiza_expense_cashier.waaneiza_cashier_cashdrawing_form_view").id,
            'target': 'self.',
            'res_id': counts.id
        }

    ############### End Count Cashdrawing ###############

    # Compute Total Amount
    @api.depends('requisition_details_lines')
    def _compute_total_amount(self):
        for rec in self:
            total = 0.0
            for req in rec.requisition_details_lines:
                total += req.amount
            rec.total_amount = total
    
    def action_cashdrawing_amount(self):
        return {
            'res_model': 'waaneiza.cashier.cashdrawing',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref("waaneiza_expense_cashier.waaneiza_cashier_cashdrawing_form_view").id,
            'target': 'self.'
        }

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

    def action_cancel(self):
        self.state = "draft"

    # def action_tosubmit(self):
    #     self.state = "tosubmit"
    
    def action_refuse(self):
        self.state = "refuse"

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
                'waaneiza_expense_cashier.mail_act_requisition_approval',
                user_id=expense_report.sudo()._get_responsible_for_check().id or self.env.user.id)
        self.filtered(lambda hol: hol.state == 'checked').activity_feedback(['waaneiza_expense_cashier.mail_act_requisition_approval'])
        self.filtered(lambda hol: hol.state in ('draft', 'cancel')).activity_unlink(['waaneiza_expense_cashier.mail_act_requisition_approval'])

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
            sheet.write({'state': 'approve', 'approved_by_user': sheet.approved_by_user.id or self.env.user.id,  'approved_by_user_second': sheet.approved_by_user_second.id or self.env.user.id})
        notification['params'].update({
            'title': _('The expense reports were successfully approved.'),
            'type': 'success',
            'next': {'type': 'ir.actions.act_window_close'},
        })
        self.approved_submit = self.env.user.name
        for rec in self:
            approve_one_string = str(rec.approved_by_process.name)
            approve_two_string = str(rec.approved_by_process_second.name)
            if rec.approved_submit == approve_one_string:
                rec.approved_name = str(rec.approved_by_name.name)
                rec.approved_job = str(rec.approved_job_id.name)
                rec.approved_department = str(rec.approved_department_id.name)
            elif rec.approved_submit == approve_two_string:
                rec.approved_name = str(rec.approved_by_name_second.name)
                rec.approved_job = str(rec.approved_job_id_second.name)
                rec.approved_department = str(rec.approved_department_id_second.name)
        self.activity_update()
        return notification

    def _get_responsible_for_approval(self):
        if self.approved_by_user:
            return self.approved_by_user

    def _get_responsible_for_second_approval(self):
        if self.approved_by_user_second:
            return self.approved_by_user_second

    def activity_update(self):
        for expense_report in self.filtered(lambda hol: hol.state == 'confirm'):
            self.activity_schedule(
                'waaneiza_expense_cashier.mail_act_requisition_approval',
                user_id = expense_report.sudo()._get_responsible_for_approval().id)
            self.activity_schedule(
                'waaneiza_expense_cashier.mail_act_requisition_approval',
                user_id = expense_report.sudo()._get_responsible_for_second_approval().id)
        self.filtered(lambda hol: hol.state == 'approve').activity_feedback(['waaneiza_expense_cashier.mail_act_requisition_approval'])
        self.filtered(lambda hol: hol.state in ('draft', 'cancel')).activity_unlink(['waaneiza_expense_cashier.mail_act_requisition_approval'])

    ################ End For Approval Function ###############


    def refuse_expense(self, reason):
        self._do_approve()
        self.write({'is_refused': True})
        self.write({'state': 'refuse'})
        self.write({'reason': reason})
        self.message_post_with_view('waaneiza_expense_cashier."waaneiza_expense_template_refuse_reason',
                                             values={'reason': reason,'name': self.name})
    
    @api.depends('state')
    def _compute_show_validate(self):
        for picking in self:
            if picking.state == 'done':
                picking.show_validate = True
            else:
                picking.show_validate = False
        

class WaaneizaCashierReqDetails(models.Model):
    _name = 'waaneiza.cashier.req.details'
    _description = 'Cash Requisition Details'
    
    requisition_id = fields.Many2one('waaneiza.cashier.cash.req', string="Requisition ID",ondelete='cascade')
    sr_number = fields.Integer(string="Sr")
    particular = fields.Char(string="Particular")
    amount = fields.Float(string="Amount")
    currency = fields.Many2one('res.currency',string="Currency")
    remarks = fields.Char(string="Remarks")
    