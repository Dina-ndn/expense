from odoo import api, fields, models, tools

class OpeningClosingAllDate(models.Model):
    _name = 'opening.closing.all.date'
    _description = 'Opening Closing Balance All Date'
    _auto = False
    
    date = fields.Date(string="Date")
    opening_cash_balance = fields.Float(string="Cash Opening Amount")
    opening_bank_balance = fields.Float(string="Bank Opening Amount")
    closing_cash_balance = fields.Float(string="Cash Closing Amount")
    closing_bank_balance = fields.Float(string="Bank Closing Amount")

    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'opening_closing_all_date')
        self.env.cr.execute(""" 
            CREATE OR REPLACE VIEW opening_closing_all_date AS (
                SELECT
                    row_number() OVER () AS id,
                    line.date as date,
                    Line.opening_cash_balance as opening_cash_balance,
                    Line.closing_cash_balance as closing_cash_balance,
                    Line.opening_bank_balance as opening_bank_balance,
                    Line.closing_bank_balance as closing_bank_balance
                    from(
                        select
                            date,
                            w.opening_cash_balance,
                            w.closing_cash_balance,
                            w.opening_bank_balance,
                            w.closing_bank_balance
                            from waaneiza_opening_closing_alldate w
                       ) as line 
            )
        """)