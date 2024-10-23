# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import format_datetime

class WaaneizaExpenseReturn(models.Model):
    _name = "waaneiza.expense.return"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Waaneiza Expense Return"
    _rec_name = "name"
    
    name = fields.Char(string="Sr No", readonly=True, required=True, copy=False, index=True, default=lambda self: _('New'))
    sett_id = fields.Many2one('waaneiza.exp.sett','Advance Settlement Reference')
    process_id = fields.Many2one('hr.employee','Process Name',related='sett_id.process_id',stor=True)
    datetime = fields.Datetime(string="Date / Time (24 hr format)",required=True,tracking=True)
    process_code_employee = fields.Char(string='Process Code',related='sett_id.process_code_employee')
    department_id = fields.Many2one('hr.department', related='sett_id.department_id',string="Department")
    type_of_cashdrawing = fields.Selection([
        ('eco', 'ECO'),
    ], string='Type of Cashdrawing', default='eco')
    cashdrawing_id = fields.Many2one('waaneiza.cashier.cashdrawing',related="sett_id.cash_drawing_srn",string="Cash Drawing Srn",store=True)
    cash_out_code = fields.Char(string="Cash Out Code",related="sett_id.cash_out_code",store=True)
    company_id = fields.Many2one('res.company','Company Name', compute='_get_processinfo',index=True, copy=False, store=True, readonly=False)
    reason_for_cash_return = fields.Char(string="Reason for Cash Return ",required=True)
    net_amount = fields.Float(string="Amount", related='sett_id.net_surplus')
    amount = fields.Float(string="Return Amount", compute='_get_net_amount',index=True, copy=False, store=True, readonly=False)
    currency = fields.Many2one('res.currency',string="Currency",related='sett_id.currency',store=True,readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('toagree', 'To Agree'),
        ('agree', 'Agree'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    show_validate = fields.Boolean(
        compute='_compute_show_validate',
        help='Technical field used to decide whether the button "Validate" should be displayed.')

    return_by_name = fields.Many2one("hr.employee.information", string="Returned By", tracking=True)
    return_by_job = fields.Many2one("hr.job", string="Rank", related="return_by_name.job_id")
    staff_id_return = fields.Char(string='Staff_ID',related="return_by_name.staff_id", index=True, copy=False, store=True, readonly=False)

    receive_by_name = fields.Many2one("hr.employee.information", string="Recevied By Name",tracking=True)
    receive_by_job = fields.Many2one("hr.job", string="Rank", related="receive_by_name.job_id")
    staff_id_receive = fields.Char(string='Staff_ID',related="receive_by_name.staff_id", index=True, copy=False, store=True, readonly=False)
    # sett_date = fields.Datetime(string="Settment Date",related='sett_id.date')
    # drawing_date_string = fields.Date(string="Cashdrawing Date",compute='get_drawing_date')
    sett_date = fields.Datetime(string="Settment Date",related='sett_id.sett_date')
    sett_date_string = fields.Date(string="Settment Date Date",compute='get_sett_date')
    # Start For Daily Cashout Report
    cash_in_code = fields.Char(string="Cash In Code", readonly=True, required=True, copy=False, index=True, default=lambda self: _('New'))
    cash_amount = fields.Float(string="Cash Amount", compute='_get_net_amount',index=True, copy=False, store=True, readonly=False)
    bank_amount = fields.Float(string="Bank Amount")
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
    # End For Daily Cashout Report
    #add advance
    return_type = fields.Selection([
        ('wc', 'With Cash'),
        ('woc', 'Without Cash'),
    ], string='Type of Return', index=True, store=True, default='wc')
    total_expense = fields.Float(string="Total Settlement Amount", related='sett_id.total_expense_amount',store=True)
    total_drawing = fields.Float(string="Total Drawing Amount", related='sett_id.amount',store=True)
    requisition_id = fields.Many2one('waaneiza.cashier.cash.req',related="sett_id.requisition_id",store=True)
    cash_out_name = fields.Char(string="Cash Out Name",store=True)
    expense_cash_lines = fields.One2many('waaneiza.cashier.cashdrawing','return_line',string="Expense Return Lines", index=True, copy=False, store=True, readonly=False)
    is_visible = fields.Boolean(default=False,string="Visible",compute='_compute_show_visible',
        help='Technical field used to decide whether the button should be displayed.')
    
    is_visible_cash = fields.Boolean(default=False,string="Visible",compute='_compute_show_cash',
        help='Technical field used to decide whether the button should be displayed.')
    return_amount = fields.Float(string="Return amount",compute='_get_return_amount',store=True)
    return_amount2 = fields.Float(string="Return amount",compute='_get_return_amount',store=True)
    
    @api.depends('expense_cash_lines')
    def _compute_return(self):
        for order in self:
            invoices = order.mapped('expense_cash_lines')
            order.invoice_ids = invoices
            order.return_count = len(invoices)

    @api.onchange('sett_id')
    def _compute_type_cash(self):
        for rec in self:
            rec.type_of_cashdrawing = rec.sett_id.type_of_cashdrawing

    @api.depends('return_type')
    def _compute_show_cash(self):
        for rec in self:
            if rec.return_type == 'woc':
                if rec.state == 'done':
                    rec.is_visible_cash =True
                else:
                    rec.is_visible_cash =False
            else:
                rec.is_visible_cash=False

    @api.depends('amount')
    def _get_return_amount(self):
        for rec in self:
            rec.return_amount = rec.amount
            rec.return_amount2 = rec.amount


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'waaneiza.exp.return.srn') or _('New')
            vals['name'] =  str(vals['name']) 
        # Daily Cashout Report    
        if vals.get('cash_in_code', _('New')) == _('New'):
            if vals['type_of_cashdrawing']=='eco':
                vals['cash_in_code'] = self.env['ir.sequence'].next_by_code(
                    'waaneiza.cashier.cashreturn.eco') or _('New')
                company = self.env['res.company'].browse(vals.get('company_id'))
                vals['cash_in_code'] = str(company.name) + str(vals['cash_in_code']) 
        result = super(WaaneizaExpenseReturn, self).create(vals)
        return result

    @api.onchange('sett_id')
    def _get_net_amount(self):
        for rec in self:
            rec.amount = abs(rec.sett_id.net_surplus)
            rec.cash_out_name = rec.sett_id.cash_out_code

    @api.depends('process_id')
    def _get_processinfo(self):
        for rec in self:
            rec.company_id = rec.process_id.company_id

    # SrNo Sequence
    # def write(self, vals):
    #     if any(state=='done' for state in set(self.mapped('state'))):
    #         raise UserError(_("No edit in done state"))
    #     else:
    #         return super().write(vals)
            
    def unlink(self):
        for rec in self:
            if rec.state =='done':
                raise ValidationError(_("You cannot delete cash return with 'Done' State"))
        rtn = super(WaaneizaExpenseReturn,self).unlink()
        return rtn


    @api.depends('state')
    def _compute_show_validate(self):
        for expense in self:
            if expense.state == 'done':
                expense.show_validate = True
            else:
                expense.show_validate = False
        
    def action_confirm(self):
        self.state = "confirm"


    def action_draft(self):
        self.state = "draft"

    def action_done(self):
        self.state = "done"
        self.cashdrawing_id.is_advance_amount= self.cashdrawing_id.is_advance_amount+ self.net_amount
        self.sett_id.total_expense_amount = self.sett_id.total_expense_amount + self.amount

    def action_cancel(self):
        self.state = "draft"
    
    def action_to_agree(self):
        self.state = "toagree"

    def action_agree(self):
        self.state = "agree"

    @api.depends('receive_by_name')
    def _get_staff_info(self):
        for rec in self:
            rec.staff_id_receive = rec.receive_by_name.id

    @api.depends('return_by_name')
    def _get_employeeinfo(self):
        for rec in self:
            rec.staff_id_return = rec.return_by_name.id


    @api.depends('state')
    def _compute_show_validate(self):
        for picking in self:
            if picking.state == 'done':
                picking.show_validate = True
            # elif picking.state not in ('draft','confirmed'):
            #     picking.show_validate = False
            else:
                picking.show_validate = False
            
    @api.depends('sett_date')
    def get_sett_date(self):
        for rec in self:
            rec.sett_date_string=rec.sett_date.date()

    @api.constrains('sett_date', 'datetime')
    def _check_dates(self):
        if any(self.filtered(lambda overtime: overtime.sett_date > overtime.datetime)):
            raise ValidationError(_(" 'Return Date' must not be earlier than 'Settlement Date'."))
    
    #Add Advance
    # @api.onchange('return_type')
    # def get_return_type(self):
    #     for rec in self:
    #         if rec.return_type == 'woc':

    def action_view_cashdrawing(self):
        return {
            'res_model': 'waaneiza.cashier.cashdrawing',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref("waaneiza_expense_cashier.waaneiza_cashier_cashdrawing_form_view").id,
            'target': 'self.'
        }


    