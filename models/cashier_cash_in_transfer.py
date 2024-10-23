# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime, time
from odoo.tools import format_datetime

class CashierCashInTransfer(models.Model):
    _name = "cashier.cash.in.transfer"
    _description = "Waaneiza Cashier Cash in Transfer"
    
    name = fields.Char(string="Sr No", readonly=True, required=True, copy=False, index=True, default=lambda self: _('New'))

    def _get_type_selection(self):
        selection = []
        for rec in self.env['hr.employee'].search([('company_id','=',self.env.company.id)]):
            selection += [('%s' % rec.name, '%s' % rec.name)]
        return selection

    type = fields.Selection([
        ('company', 'Company'),
        ('supplier', 'Supplier'),
        ('customer', 'Customer'),
        ('process', 'Process'),], string='Type', index=True, required=True)
    type_name = fields.Selection(_get_type_selection,string="Name")
    type_of_code = fields.Selection([
        ('SCI', 'SCI'),
        ('SHS', 'SHS'),
    ], string='Code', index=True, default='SCI')
    company_id = fields.Many2one('res.company','Company')
    datetime = fields.Datetime(string="Date / Time (24 hr format)")
    cash_in_code = fields.Char(string="Cash In Code", required=True,store=True, index=True, default=lambda self: _('New'))
    currency = fields.Many2one('res.currency',string="Currency", store=True, readonly=False,required=True)

    type_of_transfer = fields.Selection([
        ('hand', 'Cash'),
        ('bank', 'Bank'),
    ], string='Type of Transfer', index=True, store=True, default='hand')
    is_visible = fields.Boolean(default=False,string="Visible",compute='_compute_show_visible',
        help='Technical field used to decide whether the button should be displayed.')

    cash_in_transfer_lines = fields.One2many('cashier.cash.in.transfer.details','cash_transfer_id',string="CashinTransfer Details Lines", index=True, copy=False, store=True, readonly=False, required=True)
    total_amount = fields.Float(string="Total Amount", compute="_compute_total_amount",index=True, copy=False, store=True, readonly=False, tracking=True)
    # Start For CashBook Reports
    cash_amount = fields.Float(string="Cash Amount",compute="_compute_bank_cash_amount",store=True,index=True)
    bank_amount = fields.Float(string="Bank Amount",compute="_compute_bank_cash_amount",store=True,index=True)
    bank_account = fields.Char(string="Bank Account")
    cash_in_bank = fields.Selection([
        ('KBZ Bank', 'KBZ Bank'),
        ('AYA Bank', 'AYA Bank'),
        ('Yoma Bank (Myanmar Plaza)', 'Yoma Bank (Myanmar Plaza)'),
        ('Myanmar Citizen Bank', 'Myanmar Citizen Bank'),
    ], string='Bank Name', index=True)
    remarks = fields.Char(string="Description")
    # End For CashBook Reports

    transfered_by_name = fields.Many2one('hr.employee.information', 'Transfer by Name')
    transfered_staff_id = fields.Char(related="transfered_by_name.staff_id",string='Staff ID', store=True)
    transfered_process_code = fields.Char(string="Process Code", store=True)
    transfered_emp_id = fields.Integer(string="Employee ID")

    received_by_name = fields.Many2one('hr.employee.information', 'Received by Name')
    received_staff_id = fields.Char(related="received_by_name.staff_id",string="Staff ID", store=True)
    received_process_code = fields.Char(string="Process Code", store=True)
    received_emp_id = fields.Integer(string="Employee ID")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    bank_name_test = fields.Many2one('res.bank',string='Bank Name')
    bank_account_test = fields.Many2one('res.partner.bank',string='Bank Account')
    @api.model
    def create(self, vals):
        if vals.get('cash_in_code', _('New')) == _('New'):
            code = self.env['ir.sequence'].next_by_code(
                    'waaneiza.cashier.cashin.transfer') or _('New')
            company = self.env['res.company'].browse(vals.get('company_id'))
            year = datetime.now().strftime('%y')
            name1 ="/"
            name2="-"
            vals['cash_in_code'] = str(company.name) + str(year)+ str(name1)+str(vals['type_of_code'])+str(name2)+str(code)  
        # result = super(WaaneizaExpCashdrawing, self).create(vals)
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'waaneiza.cashier.cashin.transfer.srn') or _('New')
            vals['name'] =  str(vals['name']) 
        result = super(CashierCashInTransfer, self).create(vals)
        return result
    
    @api.onchange('transfered_by_name')
    def _onchange_transfer_by_name(self):
        self.transfered_emp_id = self.transfered_by_name.id 
        self.env.cr.execute("""select process_code from hr_employee
                                where hr_employee.emp_info_ids=%s""" % (self.transfered_emp_id))
        res = self.env.cr.fetchone()
        self.transfered_process_code = res and res[0]
    
    @api.onchange('received_by_name')
    def _onchange_received_by_name(self):
        self.received_emp_id = self.received_by_name.id 
        self.env.cr.execute("""select process_code from hr_employee
                                where hr_employee.emp_info_ids=%s""" % (self.received_emp_id))
        res = self.env.cr.fetchone()
        self.received_process_code = res and res[0]
         
    
    @api.onchange('transfered_by_name')
    def _onchange_processcode(self):
        for rec in self:
            if rec.transfered_by_name =='bank':
                rec.is_visible= True  
            else:
                rec.is_visible= False

    # Compute Total Amount
    @api.depends('cash_in_transfer_lines')
    def _compute_total_amount(self):
        for rec in self:
            total = 0.0
            for req in rec.cash_in_transfer_lines:
                total += req.amount
            rec.total_amount = total 

    @api.depends('type_of_transfer')
    def _compute_show_visible(self):
        for rec in self:
            if rec.type_of_transfer =='bank':
                rec.is_visible= True  
            else:
                rec.is_visible= False
    
    # Compute Bank/Cash Amount
    @api.depends('type_of_transfer','state')
    def _compute_bank_cash_amount(self):
        for rec in self:
            if rec.state == 'done':
                if rec.type_of_transfer == 'bank':
                    print("TEST------------",rec.type_of_transfer)
                    rec.bank_amount = rec.total_amount
                else:
                    rec.cash_amount = rec.total_amount
                
    
    def action_confirm(self):
        self.state = "confirm"

    def action_draft(self):
        self.state = "draft"

    def action_done(self):
        self.state = "done"

    def action_cancel(self):
        self.state = "cancel"

    def unlink(self):
        for rec in self:
            if rec.state =='done':
                raise ValidationError(_("You cannot delete record with 'Done' State"))
        rtn = super(CashierCashInTransfer,self).unlink()
        return rtn

class CashierCashInTransferDetails(models.Model):
    _name = 'cashier.cash.in.transfer.details'
    _description = 'Cash in Transfer Details'
    
    cash_transfer_id = fields.Many2one('cashier.cash.in.transfer', string="Cash in Transfer ID",ondelete='cascade')
    sr_no = fields.Integer(string="No")
    datetime = fields.Datetime(string="Date")
    vr_no = fields.Char(string="Vr No")
    code = fields.Char(string="Code")
    remarks = fields.Char(string="Remarks")
    amount = fields.Float(string="Amount")

    cash_amount = fields.Float(string="Cash Amount",index=True,store=True)
    bank_amount = fields.Float(string="Bank Amount",index=True,store=True)

    