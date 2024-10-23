from ast import Store
import string
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import format_datetime

class WaaneizaTypeTransfer(models.Model):
    _name = "waaneiza.type.transfer"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Waaneiza Cash Transfer Type"

    name = fields.Char(string="Sr.No:", readonly=True, required=True, copy=False, index=True, default=lambda self: _('New'))
    datetime = fields.Datetime(string="Date/Time(24hr format)")
    code = fields.Char(string="Code")
    transfer_cash_amount = fields.Float(string="Transfer Cash Amount")
    currency = fields.Many2one('res.currency',string="Currency", store=True, readonly=False)
    bank_name = fields.Selection([
        ('kbz', 'KBZ'),
        ('aya', 'AYA'),
    ], string='Bank Name', index=True, default='kbz')
    bank_account_number = fields.Char(string="Bank Account Number")

    transfered_by_name = fields.Many2one('hr.employee.information', 'Transfer by Name')
    transfered_nrc = fields.Char('NRC')
    transfered_process_code = fields.Char("Process Code")

    approved_by_name = fields.Many2one('hr.employee.information', 'Received by Name')
    approved_nrc = fields.Char('NRC')
    approved_process_code = fields.Char("Process Code")

    bank_transfer_lines = fields.One2many('waaneiza.type.transfer.details','bank_transfer_id',string="Bank Transfer Details Lines", index=True, copy=False, store=True, readonly=False, required=True)

class HandToBankTransfer(models.Model):
    _name = "hand.to.bank.transfer"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Waaneiza Hand to Bank Transfer Type"

    name = fields.Char(string="Sr.No:", readonly=True, required=True, copy=False, index=True, default=lambda self: _('New'))
    datetime = fields.Datetime(string="Date/Time(24hr format)")

    code = fields.Char(string="Code", required=True,store=True, index=True, default=lambda self: _('New'))
    cash_in_code = fields.Char(string="Cash  Code",compute="_compute_cash_in_out_code",index=True,store=True)
    cash_out_code = fields.Char(string="Cash Out Code",compute="_compute_cash_in_out_code",index=True,store=True)
    company_id = fields.Many2one("res.company",string="Company")

    transfer_cash_amount = fields.Float(string="Bank Amount")
    cash_in_cash_amount = fields.Float(string="Cash In Cash Amount",default=0)
    cash_in_bank_amount = fields.Float(string="Cash In Bank Amount",compute="_compute_transfer_amount",index=True,store=True)
    cash_out_cash_amount = fields.Float(string="Cash Out Cash Amount",compute="_compute_transfer_amount",index=True,store=True)
    cash_out_bank_amount = fields.Float(string="Cash Out Bank Amount",default=0)
    # in_hand_amout = fields.Float(string="Cash",default=0)

    person = fields.Selection([
        ('All', 'All'),
        ('KBZ Bank', 'KBZ Bank'),
        ('AYA Bank', 'AYA Bank'),
        ('Yoma Bank (Myanmar Plaza)', 'Yoma Bank (Myanmar Plaza)'),
        ('Myanmar Citizen Bank', 'Myanmar Citizen Bank'),
    ], string='Bank Name', index=True)
    description = fields.Char(string="description")

    currency = fields.Many2one('res.currency',string="Currency", store=True, readonly=False)
    bank_name = fields.Selection([
        ('KBZ Bank', 'KBZ Bank'),
        ('AYA Bank', 'AYA Bank'),
        ('Yoma Bank (Myanmar Plaza)', 'Yoma Bank (Myanmar Plaza)'),
        ('Myanmar Citizen Bank', 'Myanmar Citizen Bank'),
    ], string='Bank Name', index=True,store=True, default='KBZ Bank')
    bank_account_number = fields.Char(string="Bank Account Number")
    cash_out_bank = fields.Selection([
        ('KBZ Bank', 'KBZ Bank'),
        ('AYA Bank', 'AYA Bank'),
        ('Yoma Bank (Myanmar Plaza)', 'Yoma Bank (Myanmar Plaza)'),
        ('Myanmar Citizen Bank', 'Myanmar Citizen Bank'),
    ], string='Bank Name', index=True,store=True)

    transfered_by_name = fields.Many2one('hr.employee.information', 'Transfer by Name')
    transfered_nrc = fields.Char('NRC')
    transfered_process_code = fields.Char("Process Code")
    transfered_emp_id = fields.Integer(string="Employee ID")

    approved_by_name = fields.Many2one('hr.employee.information', 'Received by Name')
    approved_nrc = fields.Char('NRC')
    approved_process_code = fields.Char("Process Code")
    approved_emp_id = fields.Integer(string="Employee ID")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('code', _('New')) == _('New'):
            code = self.env['ir.sequence'].next_by_code(
                    'waaneiza.cashier.htb.transfer') or _('New')
            company = self.env['res.company'].browse(vals.get('company_id'))
            
            vals['code'] = str(company.name) + str(code)  
       
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'waaneiza.cashier.htb.transfer.srn') or _('New')
            vals['name'] =  str(vals['name']) 
        result = super(HandToBankTransfer, self).create(vals)
        return result

    def unlink(self):
        for rec in self:
            if rec.state =='done':
                raise ValidationError(_("You cannot delete record with 'Done' State"))
        rtn = super(HandToBankTransfer,self).unlink()
        return rtn  

    @api.depends('code')
    def _compute_cash_in_out_code(self):
        for rec in self:
            rec.cash_in_code = rec.code
            rec.cash_out_code = rec.code

    @api.depends('transfer_cash_amount')
    def _compute_transfer_amount(self):
        for rec in self:
            rec.cash_in_bank_amount = rec.transfer_cash_amount
            rec.cash_out_cash_amount = rec.transfer_cash_amount
    
    @api.onchange('transfered_by_name')
    def _onchange_transfer_by_name(self):
        self.transfered_emp_id = self.transfered_by_name.id 
        self.env.cr.execute("""select process_code from hr_employee
                                where hr_employee.emp_info_ids=%s""" % (self.transfered_emp_id))
        res = self.env.cr.fetchone()
        self.transfered_process_code = res and res[0]
    
    @api.onchange('approved_by_name')
    def _onchange_approved_by_name(self):
        self.approved_emp_id = self.approved_by_name.id 
        self.env.cr.execute("""select process_code from hr_employee
                                where hr_employee.emp_info_ids=%s""" % (self.approved_emp_id))
        res = self.env.cr.fetchone()
        self.approved_process_code = res and res[0]
    
    def action_confirm(self):
        self.state = "confirm"

    def action_draft(self):
        self.state = "draft"

    def action_done(self):
        self.state = "done"

    def action_cancel(self):
        self.state = "cancel"

class BanktoHandTransfer(models.Model):
    _name = "bank.to.hand.transfer"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Waaneiza Bank to Hand Transfer Type"

    name = fields.Char(string="Sr.No:", readonly=True, required=True, copy=False, index=True, default=lambda self: _('New'))
    datetime = fields.Datetime(string="Date/Time(24hr format)")

    code = fields.Char(string="Code", required=True,store=True, index=True, default=lambda self: _('New'))
    cash_in_code = fields.Char(string="Cash  Code",compute="_compute_cash_in_out_code",index=True,store=True)
    cash_out_code = fields.Char(string="Cash Out Code",compute="_compute_cash_in_out_code",index=True,store=True)
    company_id = fields.Many2one("res.company",string="Company")

    transfer_cash_amount = fields.Float(string="Amount")
    cash_in_cash_amount = fields.Float(string="Cash In Cash Amount",compute="_compute_transfer_amount",index=True,store=True)
    cash_in_bank_amount = fields.Float(string="Cash In Bank Amount",default=0)
    cash_out_cash_amount = fields.Float(string="Cash Out Cash Amount",default=0)
    cash_out_bank_amount = fields.Float(string="Cash Out Bank Amount",compute="_compute_transfer_amount",index=True,store=True)
    
    person = fields.Selection([
        ('All', 'All'),
        ('KBZ Bank', 'KBZ Bank'),
        ('AYA Bank', 'AYA Bank'),
        ('Yoma Bank (Myanmar Plaza)', 'Yoma Bank (Myanmar Plaza)'),
        ('Myanmar Citizen Bank', 'Myanmar Citizen Bank'),
    ], string='Bank Name', index=True)
    description = fields.Char(string="description")

    currency = fields.Many2one('res.currency',string="Currency", store=True, readonly=False,required=True)
    bank_name = fields.Selection([
        ('KBZ Bank', 'KBZ Bank'),
        ('AYA Bank', 'AYA Bank'),
        ('Yoma Bank (Myanmar Plaza)', 'Yoma Bank (Myanmar Plaza)'),
        ('Myanmar Citizen Bank', 'Myanmar Citizen Bank'),
    ], string='Bank Name', index=True, default='KBZ Bank')
    cash_in_bank = fields.Selection([
        ('KBZ Bank', 'KBZ Bank'),
        ('AYA Bank', 'AYA Bank'),
        ('Yoma Bank (Myanmar Plaza)', 'Yoma Bank (Myanmar Plaza)'),
        ('Myanmar Citizen Bank', 'Myanmar Citizen Bank'),
    ], string='Bank Name', index=True)
    bank_account_number = fields.Char(string="Bank Account Number")
    # in_hand_amout = fields.Float(string="Cash Amount")

    transfered_by_name = fields.Many2one('hr.employee.information', 'Transfer by Name')
    transfered_nrc = fields.Char('NRC')
    transfered_process_code = fields.Char("Process Code")
    transfered_emp_id = fields.Integer(string="Employee ID")

    approved_by_name = fields.Many2one('hr.employee.information', 'Received by Name')
    approved_nrc = fields.Char('NRC')
    approved_process_code = fields.Char("Process Code")
    approved_emp_id = fields.Integer(string="Employee ID")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('code', _('New')) == _('New'):
            code = self.env['ir.sequence'].next_by_code(
                    'waaneiza.cashier.bth.transfer') or _('New')
            company = self.env['res.company'].browse(vals.get('company_id'))
            
            vals['code'] = str(company.name) + str(code)  
       
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'waaneiza.cashier.bth.transfer.srn') or _('New')
            vals['name'] =  str(vals['name']) 
        result = super(BanktoHandTransfer, self).create(vals)
        return result

    def unlink(self):
        for rec in self:
            if rec.state =='done':
                raise ValidationError(_("You cannot delete record with 'Done' State"))
        rtn = super(BanktoHandTransfer,self).unlink()
        return rtn 

    @api.depends('code')
    def _compute_cash_in_out_code(self):
        for rec in self:
            rec.cash_in_code = rec.code
            rec.cash_out_code = rec.code

    @api.depends('transfer_cash_amount')
    def _compute_transfer_amount(self):
        for rec in self:
            rec.cash_in_cash_amount = rec.transfer_cash_amount
            rec.cash_out_bank_amount = rec.transfer_cash_amount
    
    @api.onchange('transfered_by_name')
    def _onchange_transfer_by_name(self):
        self.transfered_emp_id = self.transfered_by_name.id 
        self.env.cr.execute("""select process_code from hr_employee
                                where hr_employee.emp_info_ids=%s""" % (self.transfered_emp_id))
        res = self.env.cr.fetchone()
        self.transfered_process_code = res and res[0]
    
    @api.onchange('approved_by_name')
    def _onchange_approved_by_name(self):
        self.approved_emp_id = self.approved_by_name.id 
        self.env.cr.execute("""select process_code from hr_employee
                                where hr_employee.emp_info_ids=%s""" % (self.approved_emp_id))
        res = self.env.cr.fetchone()
        self.approved_process_code = res and res[0]
    
    def action_confirm(self):
        self.state = "confirm"

    def action_draft(self):
        self.state = "draft"

    def action_done(self):
        self.state = "done"

    def action_cancel(self):
        self.state = "cancel"



class BanktoBankTransfer(models.Model):
    _name = "bank.to.bank.transfer"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Waaneiza Bank to Bank Transfer Type"

    name = fields.Char(string="Sr.No:", readonly=True, required=True, copy=False, index=True, default=lambda self: _('New'))
    datetime = fields.Datetime(string="Date/Time(24hr format)")
    code = fields.Char(string="Code")
    transfer_cash_amount = fields.Float(string="Bank Amount")
    currency = fields.Many2one('res.currency',string="Currency", store=True)
    bank_name = fields.Selection([
        ('KBZ Bank', 'KBZ Bank'),
        ('AYA Bank', 'AYA Bank'),
        ('Yoma Bank (Myanmar Plaza)', 'Yoma Bank (Myanmar Plaza)'),
        ('Myanmar Citizen Bank', 'Myanmar Citizen Bank'),
    ], string='Bank Name', index=True, default='KBZ Bank')
    bank_account_number = fields.Char(string="Bank Account Number")
    in_hand_amout = fields.Float(string="Cash",default=0)

    to_bank_amount = fields.Float(related="bank_transfer_lines.to_bank_amount",string="To Amount", index=True, store=True)
    # to_bank = fields.Char(related="bank_transfer_lines.to_bank",string="To Bank",index=True, store=True)

    transfered_by_name = fields.Many2one('hr.employee.information', 'Transfer by Name')
    transfered_nrc = fields.Char('NRC')
    transfered_process_code = fields.Char("Process Code")
    transfered_emp_id = fields.Integer(string="Employee ID")

    approved_by_name = fields.Many2one('hr.employee.information', 'Received by Name')
    approved_nrc = fields.Char('NRC')
    approved_process_code = fields.Char("Process Code")
    approved_emp_id = fields.Integer(string="Employee ID")

    bank_transfer_lines = fields.One2many('bank.to.bank.transfer.details','bank_transfer_id',string="Bank to Bank Transfer Details Lines", index=True, copy=False, store=True, readonly=False)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'bank.to.bank.transfer.srn') or _('New')
            vals['name'] =  str(vals['name']) 

        result = super(BanktoBankTransfer, self).create(vals)

        return result
        
    def unlink(self):
        for rec in self:
            if rec.state =='done':
                raise ValidationError(_("You cannot delete record with 'Done' State"))
        rtn = super(BanktoBankTransfer,self).unlink()
        return rtn 

    @api.onchange('transfered_by_name')
    def _onchange_transfer_by_name(self):
        self.transfered_emp_id = self.transfered_by_name.id 
        self.env.cr.execute("""select process_code from hr_employee
                                where hr_employee.emp_info_ids=%s""" % (self.transfered_emp_id))
        res = self.env.cr.fetchone()
        self.transfered_process_code = res and res[0]
    
    @api.onchange('approved_by_name')
    def _onchange_approved_by_name(self):
        self.approved_emp_id = self.approved_by_name.id 
        self.env.cr.execute("""select process_code from hr_employee
                                where hr_employee.emp_info_ids=%s""" % (self.approved_emp_id))
        res = self.env.cr.fetchone()
        self.approved_process_code = res and res[0]
    
    def action_confirm(self):
        self.state = "confirm"

    def action_draft(self):
        self.state = "draft"

    def action_done(self):
        self.state = "done"

    def action_cancel(self):
        self.state = "cancel"

class BankToBankTransferDetails(models.Model):
    _name = 'bank.to.bank.transfer.details'
    _description = 'Waaneiza Bank to Bank Transfer Details'
    
    bank_transfer_id = fields.Many2one('bank.to.bank.transfer', string="Bank to Bank Transfer ID")
    from_bank = fields.Selection([
        ('All', 'All'),
        ('KBZ Bank', 'KBZ Bank'),
        ('AYA Bank', 'AYA Bank'),
        ('Yoma Bank (Myanmar Plaza)', 'Yoma Bank (Myanmar Plaza)'),
        ('Myanmar Citizen Bank', 'Myanmar Citizen Bank'),
    ], string='Bank Name', index=True, default='All')

    datetime = fields.Datetime(related="bank_transfer_id.datetime",string="Date",index=True,store=True)

    cash_in_code = fields.Char(related="bank_transfer_id.code",string="Cash In Code",index=True,store=True)
    cash_out_code = fields.Char(related="bank_transfer_id.code",string="Cash Out Code",index=True,store=True)

    cash_in_cash_amount = fields.Float(string="Cash In Cash Amount",default=0)
    cash_in_bank_amount = fields.Float(string="Cash In Bank Amount",compute="_compute_transfer_amount",index=True,store=True)
    cash_out_cash_amount = fields.Float(string="Cash Out Cash Amount",default=0)
    cash_out_bank_amount = fields.Float(string="Cash Out Bank Amount",compute="_compute_transfer_amount",index=True,store=True)
    to_bank_amount = fields.Float(string="Amount")

    person = fields.Selection([
        ('All', 'All'),
        ('KBZ Bank', 'KBZ Bank'),
        ('AYA Bank', 'AYA Bank'),
        ('Yoma Bank (Myanmar Plaza)', 'Yoma Bank (Myanmar Plaza)'),
        ('Myanmar Citizen Bank', 'Myanmar Citizen Bank'),
    ], string='Bank Name', index=True)
    description = fields.Char(string="description")

    from_bank_amount = fields.Float(string="Amount")
    from_bank_currency = fields.Many2one('res.currency',string="Currency", store=True)
    exchange_rate = fields.Char(string="Exchange Rate")
    to_bank = fields.Selection([
        ('All', 'All'),
        ('KBZ Bank', 'KBZ Bank'),
        ('AYA Bank', 'AYA Bank'),
        ('Yoma Bank (Myanmar Plaza)', 'Yoma Bank (Myanmar Plaza)'),
        ('Myanmar Citizen Bank', 'Myanmar Citizen Bank'),
    ], string='Bank Name', index=True, default='All')
    # to_bank_amount = fields.Float(string="Amount")
    to_bank_currency = fields.Many2one('res.currency',string="Currency", store=True)

    @api.depends('from_bank_amount','to_bank_amount')
    def _compute_transfer_amount(self):
        for rec in self:
            rec.cash_in_bank_amount = rec.from_bank_amount
            rec.cash_out_bank_amount = rec.to_bank_amount

class WaaneizaTypeTransferDetails(models.Model):
    _name = 'waaneiza.type.transfer.details'
    _description = 'Waaneiza Cash Transfer Details'
    
    bank_transfer_id = fields.Many2one('waaneiza.type.transfer', string="Bank to Bank Transfer ID")
    from_bank = bank_name = fields.Selection([
    ('all', 'All'),
    ('kbz', 'KBZ'),
    ('aya', 'AYA'),
    ], string='From Bank', index=True, default='all')

    cash_in_code = fields.Char(related="bank_transfer_id.code",string="Cash In Code")
    cash_out_code = fields.Char(related="bank_transfer_id.code",string="Cash Out Code")

    from_bank_amount = fields.Float(string="Amount")
    cash_in_cash_amount = fields.Float(string="Cash In Cash Amount",default=0)
    cash_in_bank_amount = fields.Float(string="Cash In Bank Amount",compute="_compute_transfer_amount",index=True,store=True)
    cash_out_cash_amount = fields.Float(string="Cash Out Cash Amount",default=0)
    cash_out_bank_amount = fields.Float(string="Cash Out Bank Amount",compute="_compute_transfer_amount",index=True,store=True)
    to_bank_amount = fields.Float(string="Amount")

    person = fields.Many2one('res.company','Name')
    description = fields.Char(string="description")

    from_bank_currency = fields.Many2one('res.currency',string="Currency", store=True)
    exchange_rate = fields.Char(string="Exchange Rate")
    to_bank = bank_name = fields.Selection([
        ('all', 'All'),
        ('kbz', 'KBZ'),
        ('aya', 'AYA'),
    ], string='To Bank', index=True, default='all')
    to_bank_currency = fields.Many2one('res.currency',string="Currency", store=True)

    @api.depends('from_bank_amount','to_bank_amount')
    def _compute_transfer_amount(self):
        for rec in self:
            rec.cash_in_bank_amount = rec.from_bank_amount
            rec.cash_out_bank_amount = rec.to_bank_amount
