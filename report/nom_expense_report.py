from odoo import api, fields, models, tools

class NomExpenseReport(models.Model):
    _name = 'nom.expense.report'
    _description = 'Expense Report'
    _auto = False
   
    draw_date = fields.Date(string='Cash Drawing Date')
    sett_date = fields.Date(string='Settlement Date')
    cash_out_code = fields.Char(string='Cash Out Code')
    process_id = fields.Many2one('hr.employee',string="Process")
    employee_id = fields.Many2one('hr.employee.information',string="Employee")
    department_name = fields.Char(string='Department Name')
    # name = fields.Char(string="Voucher No.")  
    description = fields.Char(string="Description")
    # sett_amount = fields.Float(string="Settlement Amount")
    # return_amount = fields.Float(string="Expense Nom")
    currency= fields.Many2one('res.currency','Currency')
    company_id = fields.Many2one('res.company','Company Name')
    cashdrawing_id = fields.Many2one('waaneiza.cashier.cashdrawing',string="Cashdrawing ID")
    advance_id = fields.Many2one('waaneiza.exp.sett',string="Advance Settlement ID")
    norm_exp_amount = fields.Float(string="Norm Amount")
    expense_amount = fields.Float(string="Expense Amount")
   
    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'nom_expense_report')
        self.env.cr.execute(""" 
            CREATE OR REPLACE VIEW nom_expense_report AS (
                SELECT
                    row_number() OVER () AS id,
                    line.company_id,
                    line.cashdrawing_id,
                    line.draw_date,
                    line.sett_date,
                    line.advance_id,
                    line.department_name,
                    line.process_id,
                    line.employee_id,
                    line.currency,
                    line.cash_out_code, 
                    line.description,
                    line.norm_exp_amount,
                    line.expense_amount
                    FROM (
                        SELECT
                            wes.process_id as process_id,
                            wes.employee_id as employee_id,
                            wes.company_id as company_id,
                            wes.cash_out_code as cashdrawing_id,
                            CAST(wes.drawing_date as Date) as draw_date,
                            CAST(wes.sett_date as Date) as sett_date,
                            wes.id as advance_id,
                            wes.department_id as department_name,
                            wes.currency as currency,
                            wes.cash_out_code as cash_out_code,
                            wei.description as description,
                            wei.norm_job_amount as norm_exp_amount,
                            wei.amount as expense_amount
                            FROM waaneiza_exp_sett wes
                            JOIN waaneiza_exp_info wei on (wes.id=wei.expense_id)
                            group by 
                            wes.process_id,wes.company_id,CAST(wes.drawing_date as Date),wes.id,
                            CAST(wes.sett_date as Date),wes.department_id,wes.currency,wes.cash_out_code, wei.description,wei.amount,wes.employee_id,wei.norm_job_amount                     
                    ) as line 
            )
        """)

    def action_view_invoice(self, advance=False):
        if not advance:
            self.sudo()._read(['advance_id'])
            advance = self.advance_id

            return {
            'res_model': 'waaneiza.exp.sett',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref("waaneiza_expense_cashier.waaneiza_settlement_form_view").id,
            'target': 'self.',
            'context': {},
            'res_id': advance.id
        }
    
    def action_get_attachment_view(self):
        cashdrawing = self.cashdrawing_id

        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')
        res['domain'] = [('res_model', '=', 'waaneiza.cashier.cashdrawing'), ('res_id', 'in', cashdrawing.ids)]
        res['context'] = {'default_res_model': 'waaneiza.cashier.cashdrawing', 'default_res_id': cashdrawing.id}
        return res
    
    # def _compute_norm_exp_amount(self):
    #     for rec in self:
    #         if rec.norm_exp_amount == 0.0 or rec.norm_exp_amount == 0:
    #             rec.norm_exp_amount = 10.7
