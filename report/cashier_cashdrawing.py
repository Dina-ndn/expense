from odoo import api, fields, models, tools

class CashierCashdrawing(models.Model):
    _name = 'cashier.cashdrawing'
    _description = 'Waaneiza Cashier Cash Drawing Report'
    _auto = False
   
    vr_no = fields.Char(string="Voucher No.")  
    cash_out_code = fields.Char(string="Cash Out Code")
    datetime = fields.Datetime(string="Date/Time (24 hr format)")
    process_id = fields.Many2one('hr.employee','Requested Process Name')
    reason = fields.Char(string="Reason for Drawing")
    amount = fields.Float(string="Requisition Amount")
    currency= fields.Many2one('res.currency','Currency')
    company_id = fields.Many2one('res.company','Company Name')
    state = fields.Char(string="Status")
    advance_id = fields.Many2one('waaneiza.cashier.cashdrawing',string="Cashier Cashdrawing")

    # Eaindra
    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'cashier_cashdrawing')
        self.env.cr.execute(""" 
            CREATE OR REPLACE VIEW cashier_cashdrawing AS (
                SELECT
                    row_number() OVER () AS id,
                    line.vr_no,
                    line.cash_out_code,
                    line.datetime,
                    line.process_id,
                    line.reason,
                    line.amount,
                    line.currency,
                    line.advance_id,
                    line.company_id,
                    line.state
                    FROM (
                        SELECT
                            wcd.id as advance_id, 
                            wcd.name as vr_no,
                            wcd.cash_out_code as cash_out_code,
                            wcd.datetime as datetime,
                            wcd.process_id as process_id,
                            wcd.reason_for_cashdrawing as reason,
                            wcd.amount as amount,
                            wcd.currency as currency,
                            wcd.company_id as company_id,
                            wcd.state as state
                            from waaneiza_cashier_cashdrawing wcd
                            WHERE wcd.state = 'toagree'        
                    ) as line 
            )
        """)

    def action_view_cashier_cashdrawing(self, advance=False):
        if not advance:
            advance = self.advance_id
            return {
            'res_model': 'waaneiza.cashier.cashdrawing',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref("waaneiza_expense_cashier.waaneiza_cashier_cashdrawing_form_view").id,
            'target': 'self.',
            'context': {},
            'res_id': self.advance_id.id
        }
