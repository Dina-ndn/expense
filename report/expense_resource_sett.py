from odoo import api, fields, models, tools

class ExpenseResourceSett(models.Model):
    _name = 'expense.resource.sett'
    _description = 'Resource Expense Sett'
    _auto = False

    resource_date = fields.Date(string='Date')
    process_id = fields.Many2one('hr.employee','Process Name') 
    department_name = fields.Many2one('hr.department','Department Name')
    uti_name = fields.Many2one('waaneiza.utilization',string="Voucher No.")
    vr_name = fields.Char(string="Sr No.") 
    currency= fields.Many2one('res.currency','Currency')
    company_id = fields.Many2one('res.company','Company Name') 
    description= fields.Char(string="Description")
    amount= fields.Float(string="Amount")
    advance_id = fields.Many2one('waaneiza.resource.advance',string="Resource Settlement ID")
    
    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'expense_resource_sett')
        self.env.cr.execute(""" 
            CREATE OR REPLACE VIEW expense_resource_sett AS (
                SELECT
                    row_number() OVER () AS id,
                    line.resource_date,
                    Line.vr_name,
                    Line.uti_name,
                    line.process_id,
                    line.department_name,
                    line.amount,
                    Line.company_id,
                    Line.advance_id,
                    Line.description,
                    line.currency
                    FROM (
                        SELECT
                            w.process_name as process_id,
                            w.company_id as company_id,
                            w.department_id as department_name,
                            CAST(w.datetime as Date) as resource_date,
                            w.vr_name as vr_name,
                            w.uti_name as uti_name,
                            w.id as advance_id,
                            w.total_amount as amount,
                            w.currency_id as currency,
                            w.description as description
                            FROM waaneiza_resource_advance w
                            group by 
                            CAST(w.datetime as Date),w.process_name,w.department_id,w.company_id,
                            w.vr_name,w.uti_name,w.id,w.total_amount,w.currency_id,w.description                   
                    ) as line 
                    
            )
        """)

    def action_view_invoice(self, advance=False):
        if not advance:
            # self.sudo()._read(['advance_id'])
            advance = self.advance_id

            return {
            'res_model': 'waaneiza.resource.advance',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref("waaneiza_expense_cashier.waaneiza_resource_form_view").id,
            'target': 'self.',
            'context': {},
            'res_id': self.advance_id.id
        }
    
    # def action_get_attachment_view(self):
    #     cashdrawing = self.cashdrawing_id

    #     self.ensure_one()
    #     res = self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')
    #     res['domain'] = [('res_model', '=', 'waaneiza.cashier.cashdrawing'), ('res_id', 'in', cashdrawing.ids)]
    #     res['context'] = {'default_res_model': 'waaneiza.cashier.cashdrawing', 'default_res_id': cashdrawing.id}
    #     return res
    
    
    