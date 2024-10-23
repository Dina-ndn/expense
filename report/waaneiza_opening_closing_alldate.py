from odoo import api, fields, models, tools

class WaaneizaOpeningClosingalldate(models.Model):
    _name = 'waaneiza.opening.closing.alldate'
    _description = 'Opening Closing Balance All Date'
    _auto = False
    
    date = fields.Date(string="Date")
    opening_cash_balance = fields.Float(string="Cash Opening Amount")
    opening_bank_balance = fields.Float(string="Bank Opening Amount")
    closing_cash_balance = fields.Float(string="Cash Closing Amount")
    closing_bank_balance = fields.Float(string="Bank Closing Amount")

    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'waaneiza_opening_closing_alldate')
        self.env.cr.execute(""" 
            CREATE OR REPLACE VIEW waaneiza_opening_closing_alldate AS (
                SELECT
                    row_number() OVER () AS id,
                    line.date as date,
                    sum(line.opening_cash_balance) as opening_cash_balance,
                    sum(line.cashin_cash_amount) as cashin_cash_amount,
                    sum(line.cashout_cash_amount) as cashout_cash_amount,
                    sum(line.closing_cash_amount) as closing_cash_balance,
                    sum(line.opening_bank_balance) as opening_bank_balance,
                    sum(line.cashin_bank_amount) as cashin_bank_amount,
                    sum(line.cashout_bank_amount) as cashout_bank_amount,
                    sum(line.closing_bank_amount) as closing_bank_balance
                    from(
                        select
                            date,
                            opening_cash_balance,
                            cashin_cash_amount,
                            cashout_cash_amount,
                            closing_cash_amount,
                            opening_bank_balance,
                            cashin_bank_amount,
                            cashout_bank_amount,
                            closing_bank_amount
                            from waaneiza_opening_closing_balance w
                        union all
                        SELECT 
                            date_trunc('day', dd)::date,
                            null as opening_cash_balance,
                            0 as cashin_cash_amount,
                            0 as cashout_cash_amount,
                            null as closing_cash_amount,
                            null as opening_bank_balance,
                            0 as cashin_bank_amount,
                            0 as cashout_bank_amount,
                            null as closing_bank_amount
                            FROM generate_series(
                                '2024-04-01', CURRENT_DATE, interval '1 day'
                        ) AS dd
                    )
                    as line
                    group by date
                    order by line.date
             )
        """)