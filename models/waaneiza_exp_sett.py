# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from collections import defaultdict
from datetime import datetime, timedelta
from operator import itemgetter

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime, time
from odoo.tools import format_datetime

class WaaneizaExpSett(models.Model):
    _name = "waaneiza.exp.sett"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Waaneiza Exp Advance Settlement"
    _rec_name="vr_name"

    def _default_employee(self):
        return self.env.user.employee_id
    # current_user = fields.Many2one('res.users','Current User', default=lambda self: self.env.user)
    employee = fields.Many2one('hr.employee', string="Employee", default=_default_employee, required=True, ondelete='cascade', index=True)
    vr_name = fields.Char(string="Expense Code", readonly=True, required=True, copy=False, index=True, default=lambda self: _('New'))
    cash_drawing_srn = fields.Many2one('waaneiza.cashier.cashdrawing',string='Cah Drawing Vr No',domain="[('is_advance','!=', 'Yes'),('process_id','=',employee)]")
    cash_out_code = fields.Char(string="Cash Out Code", related='cash_drawing_srn.cash_out_code',store=True)
    # # cash_out_code_id = fields.Integer(string='Cash Out Code Integer',related='cash_drawing_srn.cash_out_code',store=True)
    cash_drawing_id = fields.Integer(string='Cash Out Code Integer',related='cash_drawing_srn.id',store=True)
    cash_out_code_test = fields.Char(string="Cash Out Code", compute='_get_cash_code',index=True, copy=False, store=True, readonly=False)
    drawing_date = fields.Datetime(string="Cashdrawing Date",related='cash_drawing_srn.datetime',store=True)
    drawing_date_string = fields.Date(string="Cashdrawing Date",compute='get_drawing_date',store=True)
    sett_date = fields.Datetime(string="Settment Date", required=True,store=True)
    date = fields.Date(string="Date")
    date_to_string2 = fields.Char(string="Date Vrn Code",compute='_compute_date_vrn_code')
    date_to_string = fields.Char(string="Date Vrn Code",compute='_compute_date_vrn_code')
    process_id = fields.Many2one('hr.employee', 'Process Name', related='cash_drawing_srn.process_id',store=True)
    employee_id = fields.Many2one('hr.employee.information', 'Employee Name', related='process_id.emp_info_ids',store=True)
    process_code_employee = fields.Char(string='Process Code',related='cash_drawing_srn.process_code_employee')
    company_id = fields.Many2one('res.company','Company Name', compute='_get_processinfo',index=True, copy=False, store=True, readonly=False)
    currency = fields.Many2one('res.currency',string="Currency",related='cash_drawing_srn.currency',store=True,readonly=True)
    department_id = fields.Many2one('hr.department', related='cash_drawing_srn.department_id',string="Department",store=True)
    type_of_cashdrawing = fields.Selection([
        ('eco', 'ECO'),
     ], string='Type of Cashdrawing', readonly=True, index=True, copy=False, default='eco', tracking=True,related='cash_drawing_srn.type_of_cashdrawing_select')
    reason_for_cashdrawing = fields.Char(string="Reason for Cashdrawing")
    amount = fields.Float(string="Cash Drawing Amount", related='cash_drawing_srn.amount',store=True)
    total_receipt = fields.Float(string="Total Receipt",related='cash_drawing_srn.amount',store=True)
    state = fields.Selection([
         ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    show_validate = fields.Boolean(
         compute='_compute_show_validate',
         help='Technical field used to decide whether the button "Validate" should be displayed.')
    expense_info_lines = fields.One2many('waaneiza.exp.info','expense_id',string="Expense Info Lines", index=True, copy=False, store=True, readonly=False)
    total_expense_amount = fields.Float(string="Total Expense", compute="_compute_amount",index=True, copy=False, store=True, readonly=False)
    before_return = fields.Float(string="Before Return",compute="_compute_before",store=True)
    net_surplus = fields.Float(string="Net Surplus/Net (deflicit)",compute="_compute_net_surplus_amount",index=True, copy=False, store=True, readonly=False,tracking=True)
    requisition_id = fields.Many2one('waaneiza.cashier.cash.req',related="cash_drawing_srn.requisition_id")
    requested_by_process = fields.Many2one('hr.employee', string="Prepared By Process", related="requisition_id.requested_by_process", required=True, tracking=True)
    requested_by_name = fields.Many2one('hr.employee.information',string="Prepared By Name",related="requested_by_process.emp_info_ids")
    requested_job_id = fields.Many2one('hr.job',string="Rank", related="requested_by_process.job_id")
    requested_department_id = fields.Many2one('hr.department',string="Department",related="requested_by_process.department_id")

    approved_by_user = fields.Many2one('res.users', related="approved_by_process.user_id",string="Approved By User")
    approved_by_process = fields.Many2one('hr.employee', string="Approved By Process", related="requisition_id.approved_by_process",required=True, tracking=True)
    approved_by_name = fields.Many2one('hr.employee.information', related="approved_by_process.emp_info_ids",string="Approved By Name")
    approved_job_id = fields.Many2one('hr.job',string="Rank", related="approved_by_process.job_id")
    approved_department_id = fields.Many2one('hr.department',string="Department", related="approved_by_process.department_id")

    checked_by_user = fields.Many2one('res.users', related="checked_by_process.user_id",string="Checked By Employee User")
    checked_by_process = fields.Many2one('hr.employee', string="Checked By Process", related="requisition_id.checked_by_process",required=True, tracking=True)
    checked_by_name = fields.Many2one('hr.employee.information', related="checked_by_process.emp_info_ids",string="Checked By Employee Name")
    checked_job_id = fields.Many2one('hr.job',string="Rank", related="checked_by_process.job_id")
    checked_department_id = fields.Many2one('hr.department',string="Department", related="checked_by_process.department_id")

    code_year = fields.Integer(string="Year", default=datetime.now().year)
    return_count = fields.Integer(compute="_compute_return", string='Return Count', copy=False, default=0, store=True)
    invoice_ids = fields.Many2many('waaneiza.expense.return', compute="_compute_return", string='Bills', copy=False, store=True)
    expense_return_lines = fields.One2many('waaneiza.expense.return','sett_id',string="Expense Return Lines", index=True, copy=False, store=True, readonly=False)

    # Deficit
    expense_deficit_lines = fields.One2many('waaneiza.cashier.cashdrawing','expense_settlement',string="Expense Deficit Lines", index=True, copy=False, store=True, readonly=False)
    is_deficit = fields.Boolean(default=False,string="Visible",compute='_compute_show_deficit_visible',
        help='Technical field used to decide whether the button should be displayed.')
    
    is_visible = fields.Boolean(default=False,string="Visible",compute='_compute_show_visible',
        help='Technical field used to decide whether the button should be displayed.')

    #For Advance
    total_sett_amount = fields.Float(string="Total Settlement", compute="_compute_amount",index=True, copy=False, store=True, readonly=False)
    real_amount = fields.Float(string="Amount")
    # SrNo Sequence
    @api.model
    def create(self, vals):
        if vals.get('vr_name', _('New')) == _('New'):
            vals['vr_name'] = self.env['ir.sequence'].next_by_code(
                 'waaneiza.exp.settlement.vr') or _('New')
        result = super(WaaneizaExpSett, self).create(vals)
        return result

    @api.model
    def _get_employee_id(self):
        employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        return employee_rec.id

    def action_exp_return(self):
         return {
            'res_model': 'waaneiza.expense.return',
            'type': 'ir.actions.act_window',
            'tag': 'reload',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref("waaneiza_expense_cashier.waaneiza_return_form_view").id,
            'target': 'self.'
         }

    # Deficit
    def action_exp_deficit(self):
        return {
            'res_model': 'waaneiza.cashier.cashdrawing',
            'type': 'ir.actions.act_window',
            'tag': 'reload',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref("waaneiza_expense_cashier.waaneiza_cashier_cashdrawing_form_view").id,
            'target': 'self.'
        }
    
    @api.depends('state')
    def _compute_show_validate(self):
       for picking in self:
            if picking.state == 'done':
                picking.show_validate = True
            else:
                picking.show_validate = False

    @api.depends('net_surplus')
    def _compute_show_visible(self):
         for rec in self:
            if (rec.net_surplus > 0.0 or rec.net_surplus > 0) and rec.state == 'done':
                rec.is_visible = True
            else:
                 rec.is_visible = False
    # Deficit
    @api.depends('net_surplus','state')
    def _compute_show_deficit_visible(self):
        for rec in self:
            if rec.net_surplus < 0 and rec.state == 'done':
                rec.is_deficit = True
            else:
                rec.is_deficit = False

    def action_confirm(self):
        self.state = "confirm"

    def action_draft(self):
        self.state = "draft"

    def action_done(self):
        self.state = "done"
        self.cash_drawing_srn.is_advance_amount= self.cash_drawing_srn.is_advance_amount+self.total_expense_amount
        self.cash_drawing_srn.is_advance = 'Yes'


    @api.depends('expense_return_lines')
    def _compute_return(self):
        for order in self:
            invoices = order.mapped('expense_return_lines')
            order.invoice_ids = invoices
            order.return_count = len(invoices)


    def action_view_return(self, invoices=False, context=None):
        if not invoices:
            # Invoice_ids may be filtered depending on the user. To ensure we get all
            # invoices related to the purchase order, we read them in sudo to fill the
            # cache.
            # self.sudo()._read(['invoice_ids'])
            invoices = self.invoice_ids
            #view_id_tree = self.env['ir.ui.view'].search([('name','=','waaneiza_settlement.tree')])
            # 'domain'] = [('id', 'in', invoices.ids)]
        if len(invoices) > 1:
            result = self.env['ir.actions.act_window']._for_xml_id('waaneiza_expense_cashier.action_waaneiza_exp_return')
            result['domain'] = [('id', 'in', invoices.ids)]
            return result

        elif len(invoices) <= 1:
            return {
            'res_model': 'waaneiza.expense.return',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref("waaneiza_expense_cashier.waaneiza_return_form_view").id,
            'target': 'self.',
            'res_id': invoices.id
        }
        
    def action_cancel(self):
        self.state = "cancel" 


    @api.depends('cash_out_code')
    def _get_cash_code(self):
        for order in self:
            new_string = str(order.cash_out_code)
            order.cash_out_code_test = new_string[-5:]

    @api.depends('drawing_date')
    def get_drawing_date(self):
        for rec in self:
            rec.drawing_date_string=rec.drawing_date.date()

    def unlink(self):
        for rec in self:
            if rec.state =='done':
                raise ValidationError(_("You cannot delete cashdrawing with 'Done' State"))
        rtn = super(WaaneizaExpSett,self).unlink()
        return rtn
        
    # Compute Expense Total Amount
    @api.depends('expense_info_lines')
    def _compute_amount(self):
        for rec in self:
            total = 0.0
            for exp in rec.expense_info_lines:
                total += exp.amount
            rec.total_expense_amount = total
    @api.depends('expense_info_lines')
    def _compute_before(self):
        for rec in self:
            total = 0.0
            for exp in rec.expense_info_lines:
                total += exp.amount
            rec.before_return = total

    # Compute Net Surplus Amount
    @api.depends('amount','total_expense_amount')
    def _compute_net_surplus_amount(self):
        for rec in self:
            rec.net_surplus = rec.amount - rec.total_expense_amount
    # Get Process/Employee Information

    @api.depends('process_id')
    def _get_processinfo(self):
        for rec in self:
            rec.company_id = rec.process_id.company_id

    @api.constrains(' drawing_dat', 'sett_date')
    def _check_dates(self):
        if any(self.filtered(lambda overtime: overtime.drawing_date > overtime.sett_date)):
            raise ValidationError(_("Settlement 'Date' must not be earlier than 'Drawing Date'."))

    @api.depends('sett_date')
    def _compute_date_vrn_code(self):
        for rec in self:
            if rec.sett_date:
                rec.date_to_string = rec.sett_date.strftime('%y%m%d')
                rec.date_to_string2 = rec.sett_date.strftime('%y/%m/%d')

    # @api.onchange('state','net_surplus')
    # def _compute_show_visible(self):
    #     for rec in self:
    #         if rec.state not in ('draft','confirm','cancel'):
    #             if rec.total_receipt != rec.total_expense_amount:
    #                 rec.is_visible= True
    #             else:
    #                 rec.is_visible= False  
    #         else:
    #             rec.is_visible= False  

class WaaneizaExpInfo(models.Model):
    _name = 'waaneiza.exp.info'
    _description = 'Expense Info'
    
    expense_id = fields.Many2one('waaneiza.exp.sett', string="Expense ID",ondelete='cascade')
    line_date = fields.Datetime(string="Date", related="expense_id.sett_date",store=True)
    currency = fields.Many2one('res.currency',string="Currency",related='expense_id.currency',store=True,readonly=True)
    expense_code = fields.Char(string="Expense Code",default=lambda self: _('New'))

    account_code_sub = fields.Many2one("waaneiza.exp.acc.code.sub",string="Account sub Code")
    code_description_sub = fields.Char(string="Sub Account Description", related='account_code_sub.description',store=True)

    account_code = fields.Many2one("waaneiza.exp.acc.code",string="Account Code",related="account_code_sub.account_code",store=True)
    code_description = fields.Char(string="Account Description",related='account_code.description',store=True)
    vendor_name = fields.Char(string="Vendor Name")
    description = fields.Char(string="Description")
    amount = fields.Float(string="Amount")
    standard_amount = fields.Float(string="Standard Amount")
    name = fields.Char(string="Expense Vr No", readonly=True, required=True, copy=False, index=True, default=lambda self: _('New'))
    employee_id = fields.Many2one('hr.employee','Process ID', related="expense_id.process_id",index=True, copy=False, store=True, readonly=False)    
    company_id = fields.Many2one('res.company','Company Name', related="expense_id.company_id",index=True, copy=False, store=True, readonly=False)
    process_id = fields.Many2one('hr.employee', 'Process Name', index=True,related="expense_id.process_id", copy=False, store=True, readonly=True)
    job_id = fields.Many2one('hr.job', 'Rank', related="expense_id.requested_job_id",index=True, copy=False, store=True, readonly=False)
    voucher_code = fields.Integer(string="Voucher Code",index=True, copy=False, store=True, readonly=False)
    voucher_number_string = fields.Char(string="Voucher Number String",index=True, copy=False, store=True, readonly=False) 
    test_name = fields.Char(string="Expense Vr No", compute="_compute_vrn_code", index=True, copy=False, store=True, readonly=False)
    voucher_number_string2 = fields.Char(string="Voucher Code",compute="_compute_code",index=True, copy=False, store=True, readonly=False)   
    date_to_string = fields.Char(related="expense_id.date_to_string",store=True,string="Date Vrn Code")
    
    norm_id = fields.Many2one('waaneiza.expense.norm',string="Norm",store=True)
    norm_amount = fields.Float(related="norm_id.amount",string="NormAmount")
    norm_exp_amount = fields.Float(string="Norm Exp Amount",store=True)
    norm_job_amount = fields.Float(string="Norm Job Exp Amount",store=True)
    
    @api.onchange("voucher_code")
    def change_code(self):
        for rec in self:
            rec.voucher_number_string = rec.name + str(rec.voucher_code)
    
    @api.onchange("norm_id")
    def get_norm_amount(self):
        for rec in self:
            rec.norm_exp_amount = rec.norm_id.amount
    
    #Account Code links Norm Expense
    @api.onchange('account_code')
    def _onchange_accountcode_by_norm(self):
        for rec in self:
            rec.norm_id = self.env['waaneiza.expense.norm'].search([('account_code','=',rec.account_code.id),('norm_category','=',rec.job_id.id)])
            rec.norm_job_amount = rec.norm_id.amount
    
    @api.model
    def create(self, vals):
        if vals.get('expense_cod', _('New')) == _('New'):
            vals['expense_code'] = self.env['ir.sequence'].next_by_code(
                 'waaneiza.exp.settlement.info') or _('New')
            company = self.env['res.company'].browse(vals.get('company_id'))
            company_name = self.env.company.name
            vals['expense_code'] = str(company_name) + str(vals['expense_code'])
            process = self.env['hr.employee'].browse(vals.get('process_id'))
            vrn = self.env['waaneiza.exp.sett'].browse(vals.get('expense_id'))
            vals['name'] = str(process.process_code) + str(vrn.date_to_string)
            vals['voucher_number_string'] =  vals['name'] + str(vals['voucher_code'])
        result = super(WaaneizaExpInfo, self).create(vals)
        return result

    @api.depends('process_id','expense_id','date_to_string')
    def _compute_vrn_code(self):
        for rec in self:
            if rec.expense_id.sett_date != False:
                process = rec.process_id.process_code
                vrn_date = rec.date_to_string
                rec.test_name = str(process) + str(vrn_date)
            # else:
            #     raise UserError(_("You cannonot add a voucher code before choosing date"))

    @api.depends('test_name','voucher_code')
    def _compute_code(self):
        for rec in self:
            rec.voucher_number_string2 = str(rec.test_name) + str(rec.voucher_code)
            
    @api.depends('expense_id')
    def _get_processinfo(self):
        for rec in self:
            rec.process_id = rec.expense_id.process_id
            rec.job_id = rec.expense_id.requested_job_id