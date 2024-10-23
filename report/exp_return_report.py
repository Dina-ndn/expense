from odoo import api, fields, models, tools

class ExpReturnReport(models.Model):
    _name = 'exp.return.report'
    _description = 'Waaneiza Expense Return Report'
    _auto = False
   
    date = fields.Date(string='Date')
    vr_no = fields.Char(string="Voucher No.")  
    process_id = fields.Many2one('hr.employee.information','Requested Process Name')
    reason_for_cash_return = fields.Char(string="Reason for Cash Return ",)
    currency= fields.Many2one('res.currency','Currency')
    amount = fields.Float(string="Return Amount")
    company_id = fields.Many2one('res.company','Company Name')
    advance_id = fields.Many2one('waaneiza.expense.return',string="cashdrawing")
    total_expense = fields.Float(string="Total Settlement Amount")
    total_drawing = fields.Float(string="Total Drawing Amount")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('toagree', 'To Agree'),
        ('agree', 'Agree'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'exp_return_report')
        self.env.cr.execute(""" 
            CREATE OR REPLACE VIEW exp_return_report AS (
                SELECT
                    row_number() OVER () AS id,
                    line.date,
                    line.vr_no,
                    line.process_id,
                    line.advance_id,
                    line.currency,
                    line.amount,
                    Line.total_expense,
                    Line.total_drawing,
                    Line.state,
                    Line.company_id
                    FROM (
                        SELECT
                            wr.id as advance_id, 
                            CAST(wr.datetime as date) as date,
                            wr.name as vr_no,
                            wr.return_by_name as process_id,
                            wr.currency as currency,
                            wr.total_expense as total_expense,
                            wr.total_drawing as total_drawing,
                            wr.amount as amount,
                            wr.state as state,
                            wr.company_id as company_id
                            from waaneiza_expense_return wr
                            WHERE wr.return_type ='woc'            
                    ) as line 
            )
        """)



    def action_view_invoice(self, advance=False):
        if not advance:
            # self.sudo()._read(['advance_id'])
            advance = self.advance_id

            return {
            'res_model': 'waaneiza.expense.return',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref("waaneiza_expense_cashier.waaneiza_return_form_view").id,
            'target': 'self.',
            'context': {},
            'res_id': self.advance_id.id
        }
