from odoo import api, fields, models, tools
from odoo.tools import format_datetime
from datetime import datetime, time

class WaaneizaDailyCashoutCashbook(models.Model):
    _name = 'waaneiza.daily.cashout.cashbook'
    _description = 'Waaneiza Daily Cash Book cashout'
    _auto = False
   
    bank_name = fields.Char(string="Bank Name")
    srn = fields.Char(string="Vr No")
    code = fields.Char(string="Cash Out Code")
    bank_amount = fields.Float(string="Bank Amount")
    cash_amount = fields.Float(string="Cash Amount")
    person = fields.Char(string="Person")
    description = fields.Char(string="Description")
    datetime = fields.Date(string="Datetime")

    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'waaneiza_daily_cashout_cashbook')
        self.env.cr.execute(""" 
            CREATE OR REPLACE VIEW waaneiza_daily_cashout_cashbook AS (
                SELECT
                    row_number() OVER () AS id,
                    line.bank_name,
                    line.code,
                    line.srn,
                    line.bank_amount,
                    line.cash_amount,
                    line.person,
                    line.description,
                    line.datetime
                    FROM (
                        select 
                            wbt.cash_amount AS cash_amount,
                            wbt.srn AS srn,
                            wbt.bank_amount AS bank_amount,
                            wbt.bank_name AS bank_name,
                            wbt.code As code,
                            wbt.person As person,
                            wbt.description As description,
                            CAST(wbt.datetime as date) As datetime
                            FROM waaneiza_cashout_transfer_report wbt              
                    ) as line 
            )
        """)
    @api.model
    def get_cashout_data(self):
        self._cr.execute('''select CAST(datetime as date) as date,srn as srn ,code as code,person as person,description as description,cash_amount as cash_amount,bank_amount as bank_amount,bank_name as bank_name from waaneiza_daily_cashout_cashbook
                           where CAST(datetime as date) = DATE(NOW()) ORDER BY date ASC''')
        data = self._cr.fetchall()
        project_name = []
        for rec in data:
            b = list(rec)
            project_name.append(b)
        return {
            'project2': project_name
        }

    @api.model
    def get_cashout_data_by_date(self,input_date,employee_selection,inputDateEnd):

        in_date = datetime.now().strftime('%y-%m-%d')
        if employee_selection != 'null':
            data = self.env['hr.employee'].search([('id','=',employee_selection)])
            employee_name = data['name']
        if employee_selection != 'null':
            if employee_selection != "null" and input_date == 'null' and inputDateEnd=='null':
                query ='''select datetime as date,srn as srn ,code as code,person as person,description as description,cash_amount as cash_amount,bank_amount as bank_amount,bank_name as bank_name from waaneiza_daily_cashout_cashbook
                           where person = %s ORDER BY datetime ASC'''
                self._cr.execute(query, (employee_name,))
            elif employee_selection != "null" and input_date != 'null' and inputDateEnd=='null':
                query ='''select datetime as date,srn as srn ,code as code,person as person,description as description,cash_amount as cash_amount,bank_amount as bank_amount,bank_name as bank_name from waaneiza_daily_cashout_cashbook
                           where datetime = %s and person =%s ORDER BY datetime ASC'''
                self._cr.execute(query,(input_date,employee_name))
            elif employee_selection != "null" and input_date == 'null' and inputDateEnd!='null':
                query ='''select datetime as date,srn as srn ,code as code,person as person,description as description,cash_amount as cash_amount,bank_amount as bank_amount,bank_name as bank_name from waaneiza_daily_cashout_cashbook
                           where datetime = %s and person =%s ORDER BY datetime ASC'''
                self._cr.execute(query,(inputDateEnd,employee_name))
            elif employee_selection != "null" and input_date != 'null' and inputDateEnd!='null':
                query ='''select datetime as date,srn as srn ,code as code,person as person,description as description,cash_amount as cash_amount,bank_amount as bank_amount,bank_name as bank_name from waaneiza_daily_cashout_cashbook
                           where datetime between %s and %s and person =%s ORDER BY datetime ASC'''
                self._cr.execute(query,(input_date,inputDateEnd,employee_name))
        elif employee_selection == 'null':
            if employee_selection == 'null' and input_date!= 'null'and inputDateEnd=='null':
                query ='''select datetime as date,srn as srn ,code as code,person as person,description as description,cash_amount as cash_amount,bank_amount as bank_amount,bank_name as bank_name 
                from waaneiza_daily_cashout_cashbook
                           where datetime = %s ORDER BY datetime ASC'''
                self._cr.execute(query, (input_date,))
            elif employee_selection == 'null' and input_date!= 'null'and inputDateEnd!='null':
                query ='''select datetime as date,srn as srn ,code as code,person as person,description as description,cash_amount as cash_amount,bank_amount as bank_amount,bank_name as bank_name 
               from waaneiza_daily_cashout_cashbook
                           where datetime between %s and %s ORDER BY datetime ASC'''
                self._cr.execute(query, (input_date,inputDateEnd,))
            elif employee_selection == 'null' and input_date== 'null'and inputDateEnd!='null':
                query ='''select datetime as date,srn as srn ,code as code,person as person,description as description,cash_amount as cash_amount,bank_amount as bank_amount,bank_name as bank_name 
               from waaneiza_daily_cashout_cashbook
                           where datetime <= %s ORDER BY datetime ASC'''
                self._cr.execute(query, (inputDateEnd,))
            elif employee_selection == "null" and input_date == 'null' and inputDateEnd=='null':
                query ='''select datetime as date,srn as srn ,code as code,person as person,description as description,cash_amount as cash_amount,bank_amount as bank_amount,bank_name as bank_name 
                from waaneiza_daily_cashout_cashbook
                    ORDER BY datetime ASC'''
                self._cr.execute(query)
        data = self._cr.fetchall()
        cashout_change = []
        for rec in data:
            b = list(rec)
            cashout_change.append(b)
        return {
            'cashout_change': cashout_change
        }

    @api.model
    def get_cashout_all_data(self,employee_selection):
        # if employee_selection != 'null':
        #     data = self.env['hr.employee'].search([('id','=',employee_selection)])
        #     employee_name = data['name']
        # if employee_selection == 'null':
        #     self._cr.execute('''select CAST(datetime as date) as date,srn as srn ,code as code,person as person,description as description,cash_amount as cash_amount,bank_amount as bank_amount,bank_name as bank_name from waaneiza_daily_cashout_cashbook
        #                    ORDER BY date ASC''')
        # elif employee_selection != 'null':
        #     query='''select CAST(datetime as date) as date,srn as srn ,code as code,person as person,description as description,cash_amount as cash_amount,bank_amount as bank_amount,bank_name as bank_name from waaneiza_daily_cashout_cashbook
        #                    ORDER BY date ASC'''
        #     self._cr.execute(query,(employee_selection,))
        self._cr.execute('''select CAST(datetime as date) as date,srn as srn ,code as code,person as person,description as description,cash_amount as cash_amount,bank_amount as bank_amount,bank_name as bank_name from waaneiza_daily_cashout_cashbook
                          ORDER BY date ASC''')
        data = self._cr.fetchall()
        cashoutall = []
        for rec in data:
            b = list(rec)
            cashoutall.append(b)
        return {
            'cashoutall': cashoutall
        }
    @api.model
    def get_cashout_amount(self):
        # query = '''select sum(amount_untaxed_invoiced) as invoiced,
        #     sum(amount_untaxed_to_invoice) as to_invoice,sum(timesheet_cost) as 
        #     time_cost,
        #     sum(expense_cost) as expen_cost,
        #     sum(margin) as payment_details from project_profitability_report'''
        # query = '''select sum(cash_amount) as cashin_amount
        #           from waaneiza_daily_cashin_cashbook where CAST(datetime as date) = DATE(NOW())'''
        query = '''select sum(cash_amount) as cashout_amount,sum(bank_amount) as bankout_amount
                  from waaneiza_daily_cashout_cashbook where datetime = DATE(NOW())'''
        self._cr.execute(query)
        data = self._cr.dictfetchall()
        cashout_amount = []
        for record in data:
            cashout_amount.append(record.get('cashout_amount'))
        bankout_amount = []
        for record in data:
            bankout_amount.append(record.get('bankout_amount'))
        return {
            'cashout_amount': cashout_amount,
            'bankout_amount': bankout_amount,
        }
    @api.model
    def get_cashout_amount_all_date(self):
        query = '''select sum(cash_amount) as  cashout_amount,sum(bank_amount) as bankout_amount
                  from waaneiza_daily_cashout_cashbook'''
        self._cr.execute(query)
        data = self._cr.dictfetchall()
        cashout_amount = []
        for record in data:
            cashout_amount.append(record.get('cashout_amount'))
        bankout_amount = []
        for record in data:
            bankout_amount.append(record.get('bankout_amount'))
        return {
            'cashout_amount': cashout_amount,
            'bankout_amount': bankout_amount,
        }

    @api.model
    def get_cashout_amount_by_date(self,input_date,employee_selection,inputDateEnd):
        
        in_date = datetime.now().strftime('%y-%m-%d')
        if employee_selection != 'null':
            data = self.env['hr.employee'].search([('id','=',employee_selection)])
            employee_name = data['name']
        if employee_selection == 'null':
            if input_date =='null' and inputDateEnd=='null':
                query = """
                 select sum(cash_amount) as cashout_amount,sum(bank_amount) as bankout_amount
                  from waaneiza_daily_cashout_cashbook where datetime = DATE(NOW())
                        """
                self._cr.execute(query, (input_date,))
            elif input_date !='null' and inputDateEnd=='null':
                query = """
                 select sum(cash_amount) as cashout_amount,sum(bank_amount) as bankout_amount
                  from waaneiza_daily_cashout_cashbook where datetime = %s
                        """
                self._cr.execute(query, (input_date,))
            elif input_date =='null' and inputDateEnd!='null':
                query = """
                select sum(cash_amount) as cashout_amount,sum(bank_amount) as bankout_amount
                from waaneiza_daily_cashout_cashbook where datetime <= %s        """
                self._cr.execute(query,(inputDateEnd,))
            elif input_date !='null' and inputDateEnd!='null':
                query = """
                select sum(cash_amount) as cashout_amount,sum(bank_amount) as bankout_amount
                from waaneiza_daily_cashout_cashbook where datetime between %s and %s                     """
                self._cr.execute(query, (input_date,inputDateEnd,))
        elif employee_selection != 'null':
            if input_date =='null' and inputDateEnd=='null' and employee_selection!='null':
                query = """
                 select sum(cash_amount) as cashout_amount,sum(bank_amount) as bankout_amount
                  from waaneiza_daily_cashout_cashbook where person= %s
                        """
                self._cr.execute(query, (employee_name,))

            elif input_date !='null' and inputDateEnd=='null' and employee_selection!='null':
                query = """
                 select sum(cash_amount) as cashout_amount,sum(bank_amount) as bankout_amount
                  from waaneiza_daily_cashout_cashbook where person= %s and datetime = %s """
                self._cr.execute(query, (employee_name,input_date,))
            elif input_date =='null' and inputDateEnd!='null' and employee_selection!='null':
                query = """
                 select sum(cash_amount) as cashout_amount,sum(bank_amount) as bankout_amount
                  from waaneiza_daily_cashout_cashbook where person= %s and datetime <= %s
                        """
                self._cr.execute(query, (employee_name,inputDateEnd))
            elif input_date !='null' and inputDateEnd!='null' and employee_selection!='null':
                query = """
                 select sum(cash_amount) as cashout_amount,sum(bank_amount) as bankout_amount
                  from waaneiza_daily_cashout_cashbook where person= %s and datetime between %s and %s
                        """
                self._cr.execute(query, (employee_name,input_date,inputDateEnd))
        data = self._cr.dictfetchall()
        cashout_amount = []
        for record in data:
            cashout_amount.append(record.get('cashout_amount'))
        bankout_amount = []
        for record in data:
            bankout_amount.append(record.get('bankout_amount'))
        return {
            'cashout_amount':cashout_amount,
            'bankout_amount': bankout_amount,
        }