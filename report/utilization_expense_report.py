from odoo import api, fields, models, tools

class UtilizationExpenseReport(models.Model):
    _name = 'utilization.expense.report'
    _description = 'Utilization Expense Report'
    _auto = False

    resource_date = fields.Date(string='Date')
    product_name = fields.Many2one('product.product', 'Product', readonly=True)
    description= fields.Char(string="Particular")
    u_type= fields.Char(string="Utilization Type")
    process_id = fields.Many2one('hr.employee','Process Name') 
    product_uom = fields.Many2one('uom.uom', string='Unit')
    product_qty = fields.Float(string="Qty")
    price_unit = fields.Float(string='Unit Price', required=True, digits='Product Price')
    total = fields.Float(string="Amount")
    currency= fields.Many2one('res.currency','Currency')
    company_id = fields.Many2one('res.company','Company Name') 
    advance_id = fields.Many2one('waaneiza.utilization',string="ResourceID")
    uti_id = fields.Many2one('waaneiza.utilization.info', string="Uti ID")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    
    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'utilization_expense_report')
        self.env.cr.execute(""" 
            CREATE OR REPLACE VIEW utilization_expense_report AS (
                SELECT
                    row_number() OVER () AS id,
                    line.resource_date,
                    Line.description,
                    Line.product_name,
                    Line.u_type,
                    Line.process_id,
                    Line.product_uom,
                    Line.product_qty,
                    Line.price_unit,
                    line.department_name,
                    line.total,
                    line.currency,
                    Line.company_id,
                    Line.advance_id,
                    Line.state,
                    line.uti_id
                    FROM (
                        SELECT
                            w.id as advance_id,
                            ws.id as uti_id,
                            CAST(w.datetime as Date) as resource_date,
                            w.process_name as process_id,
                            w.department_id as department_name,
                            w.description as description,
                            w.type_of_uti as u_type,
                            ws.product_id as product_name,
                            ws.product_uom as product_uom,
                            ws.product_qty as product_qty,
                            ws.price_unit as price_unit,
                            ws.total as total,
                            w.state as state,
                            w.company_id as company_id,
                            ws.currency as currency
                            FROM waaneiza_utilization w
                            JOIN waaneiza_utilization_info ws on(ws.uti_id = w.id)
                            WHERE w.state ='done'
                            group by 
                            w.id,ws.id,ws.id,CAST(w.datetime as Date),w.process_name,w.department_id, w.description,
                            w.type_of_uti,ws.product_id,ws.product_uom,ws.product_qty,ws.price_unit,ws.total,ws.price_unit, ws.total,
                            w.company_id,w.state,ws.currency                
                    ) as line 
                    
            )
        """)

    def action_view_invoice(self, advance=False):
        if not advance:
            # self.sudo()._read(['advance_id'])
            advance = self.advance_id

            return {
            'res_model': 'waaneiza.utilization',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref("waaneiza_expense_cashier.waaneiza_utilization_form_view").id,
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
    
    
    