from odoo import api, fields, models, tools

class ExpenseResourceReport(models.Model):
    _name = 'expense.resource.report'
    _description = 'Resource Expense Report'
    _auto = False

    resource_date = fields.Date(string='Date')
    process_id = fields.Many2one('hr.employee','Process Name') 
    department_name = fields.Many2one('hr.department','Department Name')
    uti_name = fields.Many2one('waaneiza.utilization',string="Voucher No.")
    vr_name = fields.Char(string="Settlement Sr No.")
    currency= fields.Many2one('res.currency','Currency')
    company_id = fields.Many2one('res.company','Company Name') 
    account_code = fields.Many2one('waaneiza.exp.acc.code.sub',string="Account sub Code",store=True)
    account_description= fields.Char(string="Account Description")
    vendor_name= fields.Char(string="Vendor Name")
    description= fields.Char(string="Description")
    amount= fields.Float(string="Amount")
    advance_id = fields.Many2one('waaneiza.resource.advance',string="Resource Settlement ID")
    info_id = fields.Many2one('waaneiza.resource.info',string="Info ID")
    
    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'expense_resource_report')
        self.env.cr.execute(""" 
            CREATE OR REPLACE VIEW expense_resource_report AS (
                SELECT
                    row_number() OVER () AS id,
                    line.resource_date,
                    Line.vr_name,
                    Line.uti_name,
                    line.account_code,
                    line.account_description,
                    line.process_id,
                    line.department_name,
                    line.vendor_name,
                    line.amount,
                    line.currency,
                    Line.company_id,
                    Line.advance_id,
                    Line.description,
                    line.info_id
                    FROM (
                        SELECT
                            w.process_name as process_id,
                            w.company_id as company_id,
                            w.department_id as department_name,
                            CAST(w.datetime as Date) as resource_date,
                            w.vr_name as vr_name,
                            w.uti_name as uti_name,
                            w.id as advance_id,
                            ws.id as info_id,
                            ws.account_code_sub as account_code,
                            ws.account_description as account_description,
                            ws.vendor_id as vendor_name,
                            ws.description as description,
                            ws.amount as amount,
                            ws.currency as currency
                            FROM waaneiza_resource_advance w
                            JOIN waaneiza_resource_info ws on(ws.info_id = w.id)
                            group by 
                            CAST(w.datetime as Date),w.process_name,w.department_id,w.company_id,
                            w.vr_name,w.uti_name,ws.description,w.id,ws.account_code_sub,ws.account_description,ws.amount,ws.id,ws.vendor_id                   
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
    
    
    