# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ast import Store
import string
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import format_datetime

class WaaneizaUtilization(models.Model):
    _name = "waaneiza.utilization"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Waaneiza Utilization"
    _rec_name = "sr_name"

    sr_name = fields.Char(string="Sr.No:", store=True, required=True,default=lambda self: _('New'))
    process_name = fields.Many2one('hr.employee', string="Process Name", required=True, tracking=True,store=True)
    description = fields.Char(string="Description", required=True)
    process_code = fields.Char(string="Process Code", related="process_name.process_code")
    company_id = fields.Many2one("res.company",string="Company",related="process_name.company_id",store=True)
    department_id = fields.Many2one('hr.department',string='Department Name',related="process_name.department_id",store=True)
    type_of_uti = fields.Selection([
        ('ALL', 'ALL'),
        ('Presnet', 'Presnet'),
        ('Damage', 'Damage'),
        ('Waste', 'Waste'),
        ('Resource', 'Resource'),
        ('Sample', 'Sample'),
    ], string='Type of Utilization', readonly=True, index=True, copy=False, default='ALL', tracking=True)
    datetime = fields.Datetime(string="Receive Date/Time (24 hr format)",required=True,store=True)

    util_details_lines = fields.One2many('waaneiza.utilization.info','uti_id',string="Utilization Info Lines", index=True, copy=False, store=True, readonly=False, required=True)
    # requisition_details_lines = fields.One2many('waaneiza.cashier.req.details','requisition_id',string="Requisition Details Lines", index=True, copy=False, store=True, readonly=False, required=True)
    total_amount = fields.Float(string="Total",compute="_compute_amount", index=True, copy=False, store=True, readonly=False)
    currency_id = fields.Many2one('res.currency',string="Currency")

    uti_by_name = fields.Many2one('hr.employee.information',related="process_name.emp_info_ids",string="Utilization By Name", required=True)
    staff_id_uti = fields.Char(string='Staff_ID',index=True, copy=False, store=True, readonly=False,related="uti_by_name.staff_id")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('toapprove', 'To Approve'),
        ('approve','Approved'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    #Approver
    approved_by_user = fields.Many2one('res.users', related="approved_by_process.user_id",string="Approved By User")
    approved_by_process = fields.Many2one('hr.employee', string="Approved By Process", tracking=True,required=True)
    approved_by_name = fields.Many2one('hr.employee.information', related="approved_by_process.emp_info_ids",string="Approved By Name")
    approved_job_id = fields.Many2one('hr.job',string="Rank", related="approved_by_process.job_id")
    approved_department_id = fields.Many2one('hr.department',string="Department", related="approved_by_process.department_id")
    staff_id_approve = fields.Char(string='Staff_ID', index=True, copy=False, store=True, readonly=False,related="approved_by_name.staff_id")
    is_advance = fields.Char(string="Is advance?",store=True,default='No',
        help='Technical field used to decide whether the field "Cash Out Code" should be displayed.')
    #state
    def action_confirm(self):
        self.state = 'confirm'
    
    def action_draft(self):
        self.state = "draft"
    
    def action_submit_to_approve(self):
        self.state = "toapprove"
        self.check_activity_update()
    
    def action_done(self):
        self.state = "done"

    def action_cancel(self):
        self.state = "draft"

    @api.model
    def create(self, vals):
        if vals.get('sr_name', _('New')) == _('New'):
            vals['sr_name'] = self.env['ir.sequence'].next_by_code(
                'waaneiza.utilization.seq') or _('New')
            vals['sr_name'] =  str(vals['sr_name']) 
        result = super(WaaneizaUtilization, self).create(vals)
        return result

    def unlink(self):
        for rec in self:
            if rec.state =='done':
                raise ValidationError(_("You cannot delete record with 'Done' State"))
        rtn = super(WaaneizaUtilization,self).unlink()
        return rtn  

    # @api.depends('uti_by_name')
    # def _get_staff_info(self):
    #     for rec in self:
    #         rec.staff_id_uti = rec.uti_by_name.id

    # @api.depends('approved_by_name')
    # def _get_employee_info(self):
    #     for rec in self:
    #         rec.staff_id_approve = rec.approved_by_name.id


     #get process code
    # @api.onchange('staff_id_approve')
    # def _onchange_transfer_by_name(self):
    #     self.env.cr.execute("""select process_code from hr_employee
    #                             where hr_employee.emp_info_ids=%s""" % (self.staff_id_approve))
    #     res = self.env.cr.fetchone()
    #     self.approve_by_process = res and res[0]

     #compute amount
    @api.depends('util_details_lines')
    def _compute_amount(self):
        for rec in self:
            total = 0.0
            for exp in rec.util_details_lines:
                total +=  exp.total
            rec.total_amount = total

    ############### Start For Checker Approval Function ###############
    is_visible_check = fields.Boolean(default=False,string="Visible",compute='_compute_show_visible_check',
        help='Technical field used to decide whether the button should be displayed.')

    @api.onchange('state')
    def _compute_show_visible_check(self):
        for rec in self:
            if rec.state not in ('draft','confirm','cancel','approve','done'):
                if self.approved_by_process.user_id == self.env.user:
                    rec.is_visible_check= True
                else:
                    rec.is_visible_check= False  
            else:
                rec.is_visible_check= False  

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
        filtered_sheet = self.filtered(lambda s: s.state in ['toapprove'])
        if not filtered_sheet:
            return notification
        for sheet in filtered_sheet:
            sheet.write({'state': 'approve', 'approved_by_user':sheet.approved_by_user.id or self.env.user.id})
        notification['params'].update({
            'title': _('The expense reports were successfully checked.'),
            'type': 'success',
            'next': {'type': 'ir.actions.act_window_close'},
        })
        # self.approved_submit = self.env.user.name
        # for rec in self:
        #     approve_one_string = str(rec.approved_by_process.name)
        #     if rec.approved_submit == approve_one_string:
        #         rec.approved_name = str(rec.approved_by_name.name)
        #         rec.approved_job = str(rec.approved_job_id.name)
        #         rec.approved_department = str(rec.approved_department_id.name)
        self.check_activity_update()
        return notification

    def _get_responsible_for_check(self):
        if self.approved_by_user:
            return self.approved_by_user

    def check_activity_update(self):
        for expense_report in self.filtered(lambda hol: hol.state == 'toapprove'):
            self.activity_schedule(
                'waaneiza_expense_cashier.mail_act_util_approval',
                user_id=expense_report.sudo()._get_responsible_for_check().id or self.env.user.id)
        self.filtered(lambda hol: hol.state == 'approve').activity_feedback(['waaneiza_expense_cashier.mail_act_util_approval'])
        self.filtered(lambda hol: hol.state in ('draft', 'cancel')).activity_unlink(['waaneiza_expense_cashier.mail_act_util_approval'])

    ################ End For Checker Approval Function ###############
    


class WaaneizaUtilizationInfo(models.Model):
    _name = 'waaneiza.utilization.info'
    _description = 'waaneiza Utilization Info'
    
    uti_id = fields.Many2one('waaneiza.utilization', string="Info ID",ondelete='cascade')
    product_id = fields.Many2one('product.product',string="Product Name",store=True)
    bom_id = fields.Many2one('mrp.bom', 'Bill of Material',help="Bill of Materials allow you to define the list of required components to make a finished product.") 
    # help="Bill of Materials allow you to define the list of required components to make a finished product.")
    product_qty = fields.Float(string="Qty")
    product_tml_id = fields.Many2one('product.template',related="product_id.product_tmpl_id",string="Product Template",store=True)
    paid_id = fields.Integer(string="Product ID")
    # price_unit = fields.Float(string='Unit Price', required=True, digits='Product Price',related="product_tml_id.list_price",store=True)
    currency = fields.Many2one('res.currency',string="Currency")
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure',related="product_tml_id.uom_id",store=True)
    total = fields.Float(string="Total",compute='_compute_total',store=True)
    price_unit = fields.Float(string="Price")
    # 
    
    @api.onchange('product_tml_id')
    def _onchange_product(self):
        self.paid_id = self.product_tml_id.id
        self.env.cr.execute("""select list_price from product_template
                                where id=%s""" % (self.paid_id))
        res = self.env.cr.fetchone()
        self.price_unit = res and res[0]

    @api.depends('product_qty')
    def _compute_total(self):
        for rec in self:
            rec.total = rec.product_qty*rec.price_unit