from odoo import api, fields, models, tools

class ExpenseAdvanceReport(models.Model):
    _name = 'expense.advance.report'
    _description = 'Waaneiza Advance Cash Report'
    _auto = False
   
    date = fields.Date(string='Date')
    cash_in_out_code = fields.Char(string='Cash In Out Code')
    vr_no = fields.Char(string="Voucher No.")  
    process_id = fields.Many2one('hr.employee','Process Name')
    remark = fields.Char(string="Remark")
    currency= fields.Many2one('res.currency','Currency')
    amount = fields.Float(string="Cashier Drawing Amount")
    expense_amount = fields.Float(string="Expense Settlement Amount")
    company_id = fields.Many2one('res.company','Company Name')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True,default='draft')

    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'expense_advance_report')
        self.env.cr.execute(""" 
            CREATE OR REPLACE VIEW expense_advance_report AS (
                SELECT
                    row_number() OVER () AS id,
                    line.date,
                    Line.cash_in_out_code,
                    line.vr_no,
                    line.process_id,
                    line.remark,
                    line.currency,
                    line.amount,
                    line.expense_amount,
                    Line.state,
                    Line.company_id
                    FROM (
                        SELECT
                            wcc.datetime as Date,
                            wcc.cash_out_code as cash_in_out_code,
                            wcc.name as vr_no,
                            wcc.process_id as process_id,
                            wcc.reason_for_cashdrawing as remark,
                            wcc.currency as currency,
                            wcc.amount as amount,
                            wcc.state as state,
                            wcc.company_id as company_id,
                            wcc.is_advance_amount as expense_amount
                            from waaneiza_cashier_cashdrawing wcc
                            WHERE wcc.amount>wcc.is_advance_amount             
                    ) as line 
            )
        """)