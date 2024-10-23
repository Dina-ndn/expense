from odoo import api, fields, models, tools

class WaaneizaOpeningClosingBalance(models.Model):
    _name = 'waaneiza.opening.closing.balance'
    _description = 'Opening Closing Balance'
    _auto = False
    
    date = fields.Date(string="Date")
    cashin_cash_amount = fields.Float(string="Cashin Cash Amount")
    cashin_bank_amount = fields.Float(string="Cashin Bank Amount")
    cashout_cash_amount = fields.Float(string="Cashout Cash Amount")
    cashout_bank_amount = fields.Float(string="Cashout Bank Amount")
    opening_cash_balance = fields.Float(string="Cash Opening Amount")
    opening_bank_balance = fields.Float(string="Bank Opening Amount")
    closing_cash_amount = fields.Float(string="Cash Closing Amount")
    closing_bank_amount = fields.Float(string="Bank Closing Amount")

    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'waaneiza_opening_closing_balance')
        self.env.cr.execute(""" 
            CREATE OR REPLACE VIEW waaneiza_opening_closing_balance AS (
                SELECT
                    row_number() OVER () AS id,
                    line.date,
                    lag(closing_cash_amount,1,0::double precision) over (order by date) as opening_cash_balance,
                    line.cashin_cash_amount as cashin_cash_amount,
                    line.cashout_cash_amount as cashout_cash_amount,
                    line.closing_cash_amount,
                    lag(closing_bank_amount,1,0::double precision) over (order by date) as opening_bank_balance,
                    line.cashin_bank_amount as cashin_bank_amount,
                    line.cashout_bank_amount as cashout_bank_amount,
                    line.closing_bank_amount
                    from(
                        select
                            date,
                            cashin_cash_amount,
                            cashin_bank_amount,
                            cashout_cash_amount,
                            cashout_bank_amount,
                            sum(cashin_cash_amount) over(order by date) - sum(cashout_cash_amount) over(order by date) as closing_cash_amount,
                            sum(cashin_bank_amount) over(order by date) - sum(cashout_bank_amount) over(order by date) as closing_bank_amount
                            from waaneiza_cashin_cashout_cashbook
                    ) as line    
            )
        """)
        
    @api.model
    def get_details_opening(self):
        # query = '''select sum(amount_untaxed_invoiced) as invoiced,
        #     sum(amount_untaxed_to_invoice) as to_invoice,sum(timesheet_cost) as 
        #     time_cost,
        #     sum(expense_cost) as expen_cost,
        #     sum(margin) as payment_details from project_profitability_report'''
        query = '''select sum(opening_cash_balance) as opening_cash_amount,
                    sum(closing_cash_amount) as closing_cash_amount
                  from waaneiza_opening_closing_balance'''
        self._cr.execute(query)
        data = self._cr.dictfetchall()
        opening_cash_amount = []
        for record in data:
            opening_cash_amount.append(record.get('opening_cash_amount'))
        closing_cash_amount = []
        for record in data:
            closing_cash_amount.append(record.get('closing_cash_amount'))

        # to_invoice = []
        # for record in data:
        #     to_invoice.append(record.get('to_invoice'))
        #     record.get('to_invoice')
        # time_cost = []
        # for record in data:
        #     time_cost.append(record.get('time_cost'))

        # expen_cost = []
        # for record in data:
        #     expen_cost.append(record.get('expen_cost'))

        # payment_details = []
        # for record in data:
        #     payment_details.append(record.get('payment_details'))
        return {
            'opening_cash_amount': opening_cash_amount,
            'closing_cash_amount': closing_cash_amount,
            # 'to_invoice': to_invoice,
            # 'time_cost': time_cost,
            # 'expen_cost': expen_cost,
            # 'payment_details': payment_details,
        }