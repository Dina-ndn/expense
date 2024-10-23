from odoo import api, fields, models, tools

class WaaneizaAdvanceCashReport(models.Model):
    _name = 'waaneiza.advance.cash.report'
    _description = 'Waaneiza Advance Cash Report'
    _auto = False
   
    date = fields.Date(string='Date')
    cash_in_out_code = fields.Char(string='Cash In Out Code')
    vr_no = fields.Char(string="Voucher No.")  
    process_id = fields.Char(string="Process Name")
    remark = fields.Char(string="Remark")
    currency= fields.Char(string="Currency")
    amount = fields.Float(string="Cashier Settlement Amount")
    expense_amount = fields.Float(string="Expense Settlement Amount")
    net_surplus = fields.Float(string="Net Surplus/Net (deflicit)")


    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'waaneiza_advance_cash_report')
        self.env.cr.execute(""" 
            CREATE OR REPLACE VIEW waaneiza_advance_cash_report AS (
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
                    line.net_surplus
                    FROM (
                        SELECT
                            wcd.datetime as date,
                            wcd.cash_out_code as cash_in_out_code,
                            wcd.name as vr_no,
                            he.name as process_id,
                            wcd.reason_for_cashdrawing as remark,
                            currency.name as currency,
                            wcd.amount as amount,
                            wcd.is_advance_amount as expense_amount,
                            wes.net_surplus as net_surplus
                            from waaneiza_cashier_cashdrawing wcd
                            join hr_employee he on (he.id = wcd.process_id)
                            join res_currency currency on (currency.id = wcd.currency)  
                            left join waaneiza_exp_sett wes on (wes.cash_drawing_srn = wcd.id)
                            where (wcd.deficit_amt = 0 and wes.net_surplus is null and wcd.state='done') or (wcd.deficit_amt = 0 and wes.net_surplus != 0 and wcd.state='done')             
                    ) as line 
            )
        """)