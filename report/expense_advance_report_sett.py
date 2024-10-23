from odoo import api, fields, models, tools

class ExpenseAdvanceReportSett(models.Model):
    _name = 'expense.advance.report.sett'
    _description = 'Expense Advance Settlement Report'
    _auto = False
    
    draw_date = fields.Date(string='Cash Drawing Date')
    sett_date = fields.Date(string='Settlement Date')
    cash_out_code = fields.Char(string='Cash Out Code')
    employee_id = fields.Many2one('hr.employee','Process Name') 
    department_name = fields.Many2one('hr.department','Department Name')
    name = fields.Char(string="Voucher No.")  
    description = fields.Char(string="Description")
    drawing_amount = fields.Float(string="Drawing Amount") 
    sett_amount = fields.Float(string="Settlement Amount")
    return_amount = fields.Float(string="Return Amount")
    net_amount = fields.Float(string="Net Amount")
    currency= fields.Many2one('res.currency','Currency')
    company_id = fields.Many2one('res.company','Company Name')
    cashdrawing_id = fields.Many2one('waaneiza.cashier.cashdrawing',string="Cashdrawing ID")
    advance_id = fields.Many2one('waaneiza.exp.sett',string="Advance Settlement ID")
   
    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'expense_advance_report_sett')
        self.env.cr.execute(""" 
            CREATE OR REPLACE VIEW expense_advance_report_sett AS (
                SELECT
                    row_number() OVER () AS id,
                    line.employee_id,
                    Line.company_id,
                    line.draw_date,
                    line.sett_date,
                    line.name,
                    line.cashdrawing_id,
                    line.advance_id,
                    line.department_name,
                    Line.currency,
                    Line.drawing_amount,
                    Line.sett_amount,
                    Line.cash_out_code, 
                    Line.description,
                    Line.return_amount,
                    Line.net_amount
                    FROM (
                        SELECT
                            wec.process_id as employee_id,
                            wec.company_id as company_id,
                            CAST(wec.datetime as Date) as draw_date,
                            CAST(wes.sett_date as Date) as sett_date,
                            wec.name as name,
                            wec.id as cashdrawing_id,
                            wes.id as advance_id,
                            wec.department_id as department_name,
                            wes.amount as drawing_amount,
                            wec.currency as currency,
                            wes.before_return as sett_amount,
                            wec.cash_out_code as cash_out_code,
                            wec.reason_for_cashdrawing as description,
                            sum(wer.amount) as return_amount,
                            sum(wes.net_surplus) as net_amount
                            FROM waaneiza_cashier_cashdrawing wec
                            JOIN waaneiza_exp_sett wes on(wes.cash_drawing_id = wec.id)
                            LEFT JOIN waaneiza_expense_return wer on(wer.sett_id = wes.id)
                            WHERE wes.state = 'done'  
                            group by 
                            wec.process_id,wec.company_id,CAST(wec.datetime as Date),wec.id,wes.id,
                            CAST(wes.sett_date as Date),wec.process_id,wec.name,wec.department_id,wec.amount,wes.total_expense_amount,wec.currency,wec.cash_out_code, wec.reason_for_cashdrawing                      
                    ) as line 
            )
        """)
    @api.onchange('current_employee_id')
    def _compute_employee_id(self):
        employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        self.current_employee_id = employee_rec

    def action_view_invoice(self, advance=False):
        if not advance:
            # self.sudo()._read(['advance_id'])
            advance = self.advance_id

            return {
            'res_model': 'waaneiza.exp.sett',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref("waaneiza_expense_cashier.waaneiza_settlement_form_view").id,
            'target': 'self.',
            'context': {},
            'res_id': self.advance_id.id
        }
    
    def action_get_attachment_view(self):
        cashdrawing = self.cashdrawing_id

        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')
        res['domain'] = [('res_model', '=', 'waaneiza.cashier.cashdrawing'), ('res_id', 'in', cashdrawing.ids)]
        res['context'] = {'default_res_model': 'waaneiza.cashier.cashdrawing', 'default_res_id': cashdrawing.id}
        return res


    def action_dosomething(self):
        cashdrawing = self.cashdrawing_id
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')
        res['domain'] = [('res_model', '=', 'waaneiza.cashier.cashdrawing'), ('res_id', 'in', cashdrawing.ids)]
        res['context'] = {'default_res_model': 'waaneiza.cashier.cashdrawing', 'default_res_id': cashdrawing.id}
        return res
    # @api.depends('current_user')
    # def _compute_user_id(self):
    #     for rec in self:
    #         self.env.cr.execute("""select id from hr_employee
    #                                 where hr_employee.user_id=%s""" % (self.current_user.id))
    #         res = self.env.cr.fetchone()
    #         self.user_id = res and res[0]
    
    
    