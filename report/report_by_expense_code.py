from odoo import api, fields, models, tools

class ReportByExpenseCode(models.Model):
    _name = 'report.by.expense.code'
    _description = 'Report By Expense Code'
    _auto = False
   
    account_code = fields.Many2one("waaneiza.exp.acc.code",string="Account Code")
    code_heading = fields.Char(string="Main Heading")
    account_code_sub = fields.Many2one("waaneiza.exp.acc.code.sub",string="Account sub Code")
    sub_heading = fields.Char(string="Sub Heading") 
    amount = fields.Float(string="Amount")
    currency= fields.Many2one('res.currency','Currency')
    line_date = fields.Date(string='Date')

    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'report_by_expense_code')
        self.env.cr.execute(""" 
            CREATE OR REPLACE VIEW report_by_expense_code AS (
                SELECT
                    row_number() OVER () AS id,
                    Line.account_code,
                    line.code_heading,
                    Line.account_code_sub,
                    line.sub_heading,
                    Line.amount,
                    Line.line_date,
                    line.currency
                    FROM (
                        SELECT
                            CAST(wec.line_date as Date) as line_date,
                            wec.account_code as account_code,
                            wec.code_description as code_heading,
                            wec.account_code_sub as account_code_sub,
                            wec.code_description_sub as sub_heading,
                            sum(wec.amount) as amount,
                            wec.currency as currency
                            FROM waaneiza_exp_info wec
                            group by 
                            wec.line_date,wec.account_code,wec.code_description,wec.account_code_sub,wec.code_description_sub,wec.currency
                    ) as line 
            )
        """)

   