from odoo import api, fields, models, tools

class WaaneizaCashinCashoutCashbook(models.Model):
    _name = 'waaneiza.cashin.cashout.cashbook'
    _description = 'Cashin Cashout Cashbook'
    _auto = False
    
    date = fields.Date(string="Date")
    cashin_cash_amount = fields.Float(string="Cashin Cash Amount")
    cashin_bank_amount = fields.Float(string="Cashin Bank Amount")
    cashout_cash_amount = fields.Float(string="Cashout Cash Amount")
    cashout_bank_amount = fields.Float(string="Cashout Bank Amount")

    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'waaneiza_cashin_cashout_cashbook')
        self.env.cr.execute(""" 
            CREATE OR REPLACE VIEW waaneiza_cashin_cashout_cashbook AS (
                SELECT
                    row_number() OVER () AS id,
                    line.date,
                    sum(line.cashin_cash_amount) as cashin_cash_amount,
                    sum(line.cashin_bank_amount) as cashin_bank_amount,
                    sum(line.cashout_cash_amount) as cashout_cash_amount,
                    sum(line.cashout_bank_amount) as cashout_bank_amount
                    from(
	                    select
                        date(cashin.datetime) as date,
                        cashin.cash_amount as cashin_cash_amount,
                        cashin.bank_amount as cashin_bank_amount,
                        0 as cashout_cash_amount,
                        0 as cashout_bank_amount
                        from waaneiza_daily_cashin_cashbook cashin
                        union all
                        select
                        date(cashout.datetime) as date,
                        0 as cashin_cash_amount,
                        0 as cashin_bank_amount,
                        cashout.cash_amount as cashout_cash_amount,
                        cashout.bank_amount as cashout_bank_amount
                        from waaneiza_daily_cashout_cashbook cashout
                    ) as line
                    group by line.date
            )
        """)