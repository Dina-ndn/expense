from odoo import api, fields, models, tools

class ExpReqReport(models.Model):
    _name = 'exp.req.report'
    _description = 'Waaneiza Expense Cash Requisition Report'
    _auto = False
   
    date = fields.Date(string='Date')
    vr_no = fields.Char(string="Voucher No.")  
    process_id = fields.Many2one('hr.employee','Requested Process Name')
    currency= fields.Many2one('res.currency','Currency')
    amount = fields.Float(string="Requisition Amount")
    company_id = fields.Many2one('res.company','Company Name')
    advance_id = fields.Many2one('waaneiza.cashier.cash.req',string="cashdrawing")
    state = fields.Selection([
        ('draft', 'draft'),
        ('tocheck', 'To Check'),
        ('checked', 'Checked'),
        # ('tosubmit', 'To Approve'),
        ('confirm', 'To Approve'),
        ('approve', 'Approved'),
        ('refuse', 'Refuse'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
    ], string='Status', readonly=True,default='draft')

    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'exp_req_report')
        self.env.cr.execute(""" 
            CREATE OR REPLACE VIEW exp_req_report AS (
                SELECT
                    row_number() OVER () AS id,
                    line.date,
                    line.vr_no,
                    line.process_id,
                    line.advance_id,
                    line.currency,
                    line.amount,
                    Line.state,
                    Line.company_id
                    FROM (
                        SELECT
                            wq.id as advance_id, 
                            wq.date as date,
                            wq.name as vr_no,
                            wq.requested_by_process as process_id,
                            wq.currency_id as currency,
                            wq.total_amount as amount,
                            wq.state as state,
                            wq.company_id as company_id
                            from waaneiza_cashier_cash_req wq
                            WHERE wq.is_draw ='No'           
                    ) as line  
            )
        """)



    def action_view_invoice(self, advance=False):
        if not advance:
            advance = self.advance_id.id
            return {
            'res_model': 'waaneiza.cashier.cash.req',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref("waaneiza_expense_cashier.waaneiza_cashier_cash_req_form_view").id,
            'target': 'self.',
            'context': {},
            'res_id': self.advance_id.id
        }
