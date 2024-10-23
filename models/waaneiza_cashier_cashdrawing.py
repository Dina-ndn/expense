# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ast import Store
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import format_datetime
from datetime import datetime, time

class WaaneizaCashierCashdrawing(models.Model):
    _name = "waaneiza.cashier.cashdrawing"
    _description = "Waaneiza Cashier Cashdrawing"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "name"
   
    name = fields.Char(string="Sr No", readonly=True, required=True, copy=False, index=True, default=lambda self: _('New'))
    datetime = fields.Datetime(string="Date / Time (24 hr format)",store=True)
    cash_out_code = fields.Char(string="Cash Out Code", readonly=True, required=True, copy=False, index=True, default=lambda self: _('New'))
    type_of_drawing = fields.Selection([
        ('cash', 'Cash'),
        ('bank', 'Bank'),
    ], string='Type of Drawing', index=True, default='cash')
    is_visible = fields.Boolean(default=False,string="Visible",compute='_compute_show_visible',
        help='Technical field used to decide whether the button should be displayed.')
    # For Cash Requisition Many2one
    requisition_id = fields.Many2one('waaneiza.cashier.cash.req',string="Requisition Reference",domain="[('state','=', 'done'),('is_draw','!=', 'Yes')]")
    req_id = fields.Many2one('waaneiza.cashier.cash.req',string="Req Reference")
    process_id = fields.Many2one('hr.employee', 'Process Name',related='requisition_id.requested_by_process',store=True)
    process_code_employee = fields.Char(string='Process Code',compute='_get_processinfo',index=True, store=True)
    
    company_id = fields.Many2one('res.company','Company Name', compute='_get_processinfo',index=True, copy=False, store=True, readonly=False)
    department_id = fields.Many2one('hr.department',string='Department', index=True, copy=False, store=True, readonly=False, compute='_get_processinfo')
    type_of_cashdrawing = fields.Char(string="Type of Cash Drawing")
    
    reason_for_cashdrawing = fields.Char(string="Reason for Cashdrawing",required=True)
    type_of_cashdrawing_select = fields.Selection([
        ('BCI', 'BCI'),('BCO', 'BCO'),('ECI', 'ECI'),('ECO', 'ECO'),
        ('IOI', 'IOI'),('ICO', 'ICO'),('OCI', 'OCI'),('OCO', 'OCO'),
        ('LCI', 'LCI'),('LCO', 'LCO'),('CIO', 'CIO'),('COO', 'COO'),
        ('ACO', 'ACO'),('ACI', 'ACI'),('PCO', 'PCO'),
    ], string='Type of Cash Drawing', readonly=True, index=True, copy=False, default='ECO', tracking=True)
    
    # amount = fields.Float(string="Amount",store=True)
    # Eaindra
    amount = fields.Float(string="Amount",compute='_compute_deficit_amount',index=True,store=True)
    amount_by_mmk = fields.Float(string="Amount (MMK)",store=True)
    exchange_rate = fields.Float(string="Exchange Rate")
    re_amount = fields.Float(string="Re Amount",compute='_compute_deficit_amount',index=True,store=True)
    deficit_amt = fields.Float(string="Deficit Amount",index=True,store=True)

    currency = fields.Many2one('res.currency',string="Currency", store=True, readonly=False,required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('toagree', 'To Agree'),
        ('agree', 'Agree'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    paid_by_name = fields.Many2one('hr.employee.information', 'Paid By Name')
    paid_by_staff_id = fields.Char(related="paid_by_name.staff_id",string="Staff ID",store=True,index=True)
    process_code_casher = fields.Char(string='Process Code')
    paid_emp_id = fields.Integer(string="Employee ID")
    
    received_by_name = fields.Many2one('hr.employee.information',string='Received_by_name', index=True, copy=False, store=True, readonly=False, compute='_get_processinfo')
    received_by_staff_id = fields.Char(related="received_by_name.staff_id",string="Staff ID",store=True,index=True)
    
    show_validate = fields.Boolean(
        compute='_compute_show_validate',
        help='Technical field used to decide whether the button "Validate" should be displayed.')
    show_attatch = fields.Boolean(
        compute='_compute_show_validate',
        help='Technical field used to decide whether the button "Validate" should be displayed.')
    expense_settlement_lines = fields.One2many('waaneiza.exp.sett','cash_drawing_srn',string="Expense Settlement Lines", index=True, copy=False, store=True, readonly=False)
    # Eaindra
    expense_settlement = fields.Many2one('waaneiza.exp.sett',string="Expense Settlement", index=True, store=True)
    expense_settlement_id = fields.Many2one('waaneiza.exp.sett',string="Expense Settlement", index=True, store=True)

    invoice_count = fields.Integer(compute="_compute_invoice", string='Bill Count', copy=False, default=0, store=True)
    invoice_ids = fields.Many2many('waaneiza.exp.sett', compute="_compute_invoice", string='Bills', copy=False, store=True)
    attachment = fields.Binary(string="Document")
    document_name = fields.Char(string="File Name")
    attachment_number = fields.Integer('Number of Attachments', compute='_compute_attachment_number')

    # Connect Expense Module
    is_advance = fields.Char(string="Is advance?",compute='_compute_show_code',store=True,default='No',
        help='Technical field used to decide whether the field "Cash Out Code" should be displayed.')
    is_advance_test = fields.Char("Is advance Test",store=True)
    is_advance_amount = fields.Float(string="Expense Advance Amount",store=True)

    # Start For Daily Cashbook Report
    bank_amount = fields.Float(string="Bank Amount")
    bank_account = fields.Char(string="Bank Account")
    bank_name = fields.Selection([
        ('KBZ Bank', 'KBZ Bank'),
        ('AYA Bank', 'AYA Bank'),
        ('Yoma Bank (Myanmar Plaza)', 'Yoma Bank (Myanmar Plaza)'),
        ('Myanmar Citizen Bank', 'Myanmar Citizen Bank'),
    ], string='Bank Name', index=True,store=True)
    person = fields.Selection([
        ('All', 'All'),
        ('KBZ Bank', 'KBZ Bank'),
        ('AYA Bank', 'AYA Bank'),
        ('Yoma Bank (Myanmar Plaza)', 'Yoma Bank (Myanmar Plaza)'),
        ('Myanmar Citizen Bank', 'Myanmar Citizen Bank'),
    ], string='Bank Name', index=True)
    person_name = fields.Char(string="Person Name",related="process_id.name",store=True)
    # End For Daily Cashbook Report
    #For Advance Return

    return_line = fields.Many2one('waaneiza.expense.return',string="Return Reference")
    cash_out_name = fields.Char(string="Cash Name",related='return_line.cash_out_name')
    is_visible = fields.Boolean(default=False,string="Visible",compute='_compute_show_visible',
        help='Technical field used to decide whether the button should be displayed.')
    
    ########### Purchase Module Connect ###########
    purchase_code = fields.Many2one('purchase.order',string="Purchase Code")
    is_visible_purcode = fields.Boolean(default=False,string="Visible",
        help='Technical field used to decide whether the button should be displayed.')
    ###############################################

    @api.onchange('type_of_cashdrawing_select')
    def onchange_show_purcode(self):
        for rec in self:
            if rec.type_of_cashdrawing_select == 'PCO':
                 rec.is_visible_purcode= True  
            else:
                 rec.is_visible_purcode= False

    @api.onchange('purchase_code')
    def onchange_amount(self):
        if self.purchase_code:
            self.env.cr.execute("""select amount_total from purchase_order po where name = '%s' """ % (self.purchase_code.name))
            res = self.env.cr.fetchone()
            self.amount = res and res[0] or 0.0
        else:
            self.amount = 0.0

    # Connect Expense Module
    @api.onchange('is_advance_amount')           
    def _compute_show_code(self):
         for rec in self:
            if rec.is_advance_amount >= rec.amount:
                rec.is_advance = 'Yes'
                rec.is_advance_test = 'Yes'
            else:
                rec.is_advance = 'No'
                rec.is_advance_test = 'No'

    # Eaindra
    @api.onchange('requisition_id','expense_settlement_id','return_line')
    def _compute_deficit_amount(self):
        
        if self.return_line.id > 0:
            self.amount = self.return_line.return_amount
            self.re_amount=self.return_line.return_amount
        else:
            self.amount = self.requisition_id.total_amount
            id = self.expense_settlement_id.id
            if id > 0:
                deficit_amount = self.expense_settlement_id.total_expense_amount - self.expense_settlement_id.amount
            # self.amount = self.expense_settlement_id.total_expense_amount - self.expense_settlement_id.amount
                print("deficit Amount--------",deficit_amount)
                if deficit_amount > 0:
                    self.amount = deficit_amount
                    self.deficit_amt = deficit_amount


    @api.onchange('requisition_id')
    def _compute_total_amount(self):
        for rec in self:
            if rec.requisition_id != rec.return_line.requisition_id:
                rec.amount = rec.requisition_id.total_amount
            else:
                rec.amount = rec.return_line.return_amount

    @api.onchange('expense_settlement_id')           
    def _compute_show_deficit(self):
         for rec in self:
            if rec.return_line.id == 0 and rec.expense_settlement_id.id > 0:
                rec.cash_out_code=rec.expense_settlement_id.cash_out_code
                rec.type_of_cashdrawing_select = rec.expense_settlement_id.cash_drawing_srn.type_of_cashdrawing_select
                rec.requisition_id= rec.expense_settlement_id.requisition_id
                rec.reason_for_cashdrawing= rec.expense_settlement_id.cash_drawing_srn.reason_for_cashdrawing
                rec.currency= rec.expense_settlement_id.cash_drawing_srn.currency
                rec.paid_by_name= rec.expense_settlement_id.cash_drawing_srn.paid_by_name
                rec.paid_by_staff_id= rec.expense_settlement_id.cash_drawing_srn.paid_by_staff_id
                rec.process_code_casher= rec.expense_settlement_id.cash_drawing_srn.process_code_casher
                rec.paid_by_name= rec.expense_settlement_id.cash_drawing_srn.paid_by_name
            else:
                pass

    @api.onchange('return_line')           
    def _compute_show_req(self):
         for rec in self:
            if rec.expense_settlement_id.id == 0 and rec.return_line.id >0 :
                rec.cash_out_code=rec.return_line.sett_id.cash_out_code
                rec.type_of_cashdrawing_select = rec.return_line.sett_id.cash_drawing_srn.type_of_cashdrawing_select
                rec.requisition_id= rec.return_line.sett_id.requisition_id
                rec.reason_for_cashdrawing= rec.return_line.sett_id.cash_drawing_srn.reason_for_cashdrawing
                rec.currency= rec.return_line.sett_id.cash_drawing_srn.currency
                rec.paid_by_name= rec.return_line.sett_id.cash_drawing_srn.paid_by_name
                rec.paid_by_staff_id= rec.return_line.sett_id.cash_drawing_srn.paid_by_staff_id
                rec.process_code_casher= rec.return_line.sett_id.cash_drawing_srn.process_code_casher
                rec.paid_by_name= rec.return_line.sett_id.cash_drawing_srn.paid_by_name
            else:
                pass

    @api.onchange('type_of_drawing')
    def _compute_show_visible(self):
        for rec in self:
            if rec.type_of_drawing =='bank':
                rec.is_visible= True  
            else:
                rec.is_visible= False

    ########## Start Attachement Files ##########
    def attach_document(self, **kwargs):
        pass
    
    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group([('res_model', '=', 'waaneiza.cashier.cashdrawing'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for expense in self:
            expense.attachment_number = attachment.get(expense._origin.id, 0)
    
    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')
        res['domain'] = [('res_model', '=', 'waaneiza.cashier.cashdrawing'), ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'waaneiza.cashier.cashdrawing', 'default_res_id': self.id}
        return res
    ########## End Attachement Files ##########

    @api.depends('expense_settlement_lines')
    def _compute_invoice(self):
        for order in self:
            invoices = order.mapped('expense_settlement_lines')
            order.invoice_ids = invoices
            order.invoice_count = len(invoices)
    
    # Connect Expense module
    # SrNo Sequence
    # def write(self, vals):
    #     if any(state=='done' for state in set(self.mapped('state'))):
    #         raise UserError(_("No edit in done state"))
    #     else:
    #         return super().write(vals)
            
    def unlink(self):
        for rec in self:
            if rec.state =='done':
                raise ValidationError(_("You cannot delete cashdrawing with 'Done' State"))
        rtn = super(WaaneizaCashierCashdrawing,self).unlink()
        return rtn
   
    
    @api.model
    def create(self, vals):
        if vals.get('cash_out_code', _('New')) == _('New'):
            code = self.env['ir.sequence'].next_by_code(
                    'waaneiza.cashier.cashdrawing.eco') or _('New')
            company = self.env['res.company'].browse(vals.get('company_id'))
            year = datetime.now().strftime('%y')
            name1 ="/"
            name2="-"
            vals['cash_out_code'] = str(company.name) + str(year)+ str(name1)+str(vals['type_of_cashdrawing_select'])+str(name2)+str(code)  
        # result = super(WaaneizaExpCashdrawing, self).create(vals)
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'waaneiza.cashier.cashdrawing.srn') or _('New')
            vals['name'] =  str(vals['name']) 
        result = super(WaaneizaCashierCashdrawing, self).create(vals)
        return result
    
    def action_advance_settlement(self):
        return {
            'res_model': 'waaneiza.exp.sett',
            'type': 'ir.actions.act_window',
            'tag': 'reload',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref("waaneiza_expense_cashier.waaneiza_settlement_form_view").id,
            'target': 'self.'
        }
 
    @api.depends('state')
    def _compute_show_validate(self):
        for picking in self:
            if picking.state == 'done':
                picking.show_validate = True
                picking.show_attatch = False
            else:
                picking.show_validate = False
                picking.show_attatch = True

    def action_view_invoice(self, invoices=False, context=None):
        if not invoices:
            # Invoice_ids may be filtered depending on the user. To ensure we get all
            # invoices related to the purchase order, we read them in sudo to fill the
            # cache.
            # self.sudo()._read(['invoice_ids'])
            invoices = self.invoice_ids
        if len(invoices) > 1:
            result = self.env['ir.actions.act_window']._for_xml_id('waaneiza_expense_cashier.action_waaneiza_settlement')
            result['domain'] = [('id', 'in', invoices.ids)]
            return result

        elif len(invoices) <= 1:
            return {
            'res_model': 'waaneiza.exp.sett',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref("waaneiza_expense_cashier.waaneiza_settlement_form_view").id,
            'target': 'self.',
            'res_id': invoices.id
        }
        
    def action_confirm(self):
        self.state = "confirm"

    # Eaindra
    def action_to_agree(self):
        self.state = "toagree"
    
    def action_agree(self):
        self.state = "agree"

    def action_draft(self):
        self.state = "draft"

    def action_done(self):
        self.state = "done"
        self.requisition_id.is_draw = 'Yes'
        for rec in self:
            if rec.deficit_amt >= 0:
                rec.expense_settlement_id.amount += rec.amount
                rec.expense_settlement_id.total_receipt = rec.expense_settlement_id.amount

    def action_cancel(self):
        self.state = "cancel"

    # Get Process/Employee Information
    @api.depends('process_id')
    def _get_processinfo(self):
        for rec in self:
            rec.department_id = rec.process_id.department_id
            rec.process_code_employee = rec.process_id.process_code
            rec.received_by_name = rec.process_id.emp_info_ids
            rec.company_id = rec.process_id.company_id

    # Number of Process for each employee
    @api.onchange('paid_by_name')
    def _onchange_paid_by_name(self):
        self.paid_emp_id = self.paid_by_name.id 
        self.env.cr.execute("""select process_code from hr_employee
                                where hr_employee.emp_info_ids=%s""" % (self.paid_emp_id))
        res = self.env.cr.fetchone()
        self.process_code_casher = res and res[0]
        
    # @api.constrains("amount")
    # def change_amount(self):
    #     if self.amount==0.0:
    #         raise UserError(_('Amount should not be zero.'))

            
            
    
    
            