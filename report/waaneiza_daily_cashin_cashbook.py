from odoo import api, fields, models, tools
from odoo.tools import format_datetime
from datetime import datetime, time

class WaaneizaDailyCashinCashbook(models.Model):
    _name = 'waaneiza.daily.cashin.cashbook'
    _description = 'Waaneiza Daily Cash Book cashin'
    _auto = False
   
    bank_name = fields.Char(string="Bank Name")
    srn = fields.Char(string="Vr No")
    code = fields.Char(string="Cash in Code")
    bank_amount = fields.Float(string="Bank Amount")
    cash_amount = fields.Float(string="Cash Amount")
    person = fields.Char(string="Person")
    description = fields.Char(string="Description")
    datetime = fields.Date(string="Datetime")

    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'waaneiza_daily_cashin_cashbook')
        self.env.cr.execute(""" 
            CREATE OR REPLACE VIEW waaneiza_daily_cashin_cashbook AS (
                SELECT
                    row_number() OVER () AS id,
                    line.bank_name,
                    line.srn,
                    line.code,
                    line.bank_amount,
                    line.cash_amount,
                    line.person,
                    line.description,
                    line.datetime
                    FROM (
                        select 
                            wcit.cash_amount AS cash_amount,
                            wcit.srn AS srn,
                            wcit.bank_amount AS bank_amount,
                            wcit.bank_name AS bank_name,
                            wcit.code As code,
                            wcit.person As person,
                            wcit.description As description,
                            CAST(wcit.datetime as date) As datetime
                            FROM waaneiza_cashin_transfer_report wcit  
                            UNION
                            Select
                            wcr.amount AS cash_amount,
                            wcr.name AS srn,
                            wcr.bank_amount AS bank_amount,
                            wcr.bank_name AS bank_name,
                            wcr.cash_out_code As code,
                            wcr.person_name As person,
                            wcr.reason_for_cash_return As description,
                            CAST(wcr.datetime as date) As datetime
                            FROM waaneiza_expense_return wcr              
                    ) as line 
            )
        """)

    @api.model
    def get_cashin_amount(self):
        # query = '''select sum(amount_untaxed_invoiced) as invoiced,
        #     sum(amount_untaxed_to_invoice) as to_invoice,sum(timesheet_cost) as 
        #     time_cost,
        #     sum(expense_cost) as expen_cost,
        #     sum(margin) as payment_details from project_profitability_report'''
        # query = '''select sum(cash_amount) as cashin_amount
        #           from waaneiza_daily_cashin_cashbook where CAST(datetime as date) = DATE(NOW())'''
        query = '''select sum(cash_amount) as cashin_amount,sum(bank_amount) as bankin_amount
                  from waaneiza_daily_cashin_cashbook where datetime = DATE(NOW())'''
        self._cr.execute(query)
        data = self._cr.dictfetchall()
        cashin_amount = []
        for record in data:
            cashin_amount.append(record.get('cashin_amount'))
        bankin_amount = []
        for record in data:
            bankin_amount.append(record.get('bankin_amount'))
        return {
            'cashin_amount': cashin_amount,
             'bankin_amount': bankin_amount,
        }
    @api.model
    def get_cashin_amount_all_date(self):
        query = '''select sum(cash_amount) as cashin_amount,sum(bank_amount) as bankin_amount
                  from waaneiza_daily_cashin_cashbook'''
        self._cr.execute(query)
        data = self._cr.dictfetchall()
        cashin_amount = []
        for record in data:
            cashin_amount.append(record.get('cashin_amount'))
        bankin_amount = []
        for record in data:
            bankin_amount.append(record.get('bankin_amount'))
        return {
            'cashin_amount': cashin_amount,
            'bankin_amount': bankin_amount,
        }
    @api.model
    def get_cashin_amount_by_date(self,input_date,employee_selection,inputDateEnd):
        
        in_date = datetime.now().strftime('%y-%m-%d')
        if employee_selection != 'null':
            data = self.env['hr.employee'].search([('id','=',employee_selection)])
            employee_name = data['name']
        if employee_selection == 'null':
            if input_date =='null' and inputDateEnd=='null':
                query = """
                 select sum(cash_amount) as cashin_daily_amount,sum(bank_amount) as bankin_amount
                  from waaneiza_daily_cashin_cashbook where datetime = DATE(NOW())
                        """
                self._cr.execute(query, (input_date,))
            elif input_date !='null' and inputDateEnd=='null':
                query = """
                 select sum(cash_amount) as cashin_daily_amount,sum(bank_amount) as bankin_amount
                  from waaneiza_daily_cashin_cashbook where datetime = %s"""
                self._cr.execute(query, (input_date,))
            elif input_date =='null' and inputDateEnd!='null':
                query = """
                 select sum(cash_amount) as cashin_daily_amount,sum(bank_amount) as bankin_amount
                  from waaneiza_daily_cashin_cashbook where datetime <= %s
                        """
                self._cr.execute(query,(inputDateEnd,))
            elif input_date !='null' and inputDateEnd!='null':
                query = """
                 select sum(cash_amount) as cashin_daily_amount,sum(bank_amount) as bankin_amount
                  from waaneiza_daily_cashin_cashbook where datetime between %s and %s  """
                self._cr.execute(query, (input_date,inputDateEnd,))
        elif employee_selection != 'null':
            if input_date =='null' and inputDateEnd=='null' and employee_selection!='null':
                query = """
                 select sum(cash_amount) as cashin_daily_amount,sum(bank_amount) as bankin_amount
                  from waaneiza_daily_cashin_cashbook where person = %s """
                self._cr.execute(query, (employee_name,))
            elif input_date !='null' and inputDateEnd=='null' and employee_selection!='null':
                query = """
                 select sum(cash_amount) as cashin_daily_amount,sum(bank_amount) as bankin_amount
                  from waaneiza_daily_cashin_cashbook where person = %s and datetime = %s
                        """
                self._cr.execute(query, (employee_name,input_date,))
            elif input_date =='null' and inputDateEnd!='null' and employee_selection!='null':
                query = """
                 select sum(cash_amount) as cashin_daily_amount,sum(bank_amount) as bankin_amount
                  from waaneiza_daily_cashin_cashbook where person = %s and datetime <= %s
                        """
                self._cr.execute(query, (employee_name,inputDateEnd,))
            elif input_date !='null' and inputDateEnd!='null' and employee_selection!='null':
                query = """
                 select sum(cash_amount) as cashin_daily_amount,sum(bank_amount) as bankin_amount
                  from waaneiza_daily_cashin_cashbook where person = %s and datetime between %s and %s
                        """
                self._cr.execute(query, (employee_name,input_date,inputDateEnd,))
        data = self._cr.dictfetchall()
        cashin_daily_amount = []
        for record in data:
            cashin_daily_amount.append(record.get('cashin_daily_amount'))
        bankin_amount = []
        for record in data:
            bankin_amount.append(record.get('bankin_amount'))
        return {
            'cashin_daily_amount':cashin_daily_amount,
            'bankin_amount': bankin_amount,
        }

    @api.model
    def get_cashin_data(self):
        """

        Summery:
            when the page is loaded get the data from different models and transfer to the js file.
            return a dictionary variable.
        return:
            type:It is a dictionary variable. This dictionary contain data that affecting project task table.

        """
        # self._cr.execute('''select project_task.name as task_name,pro.name as project_name from project_task
        #   Inner join project_project as pro on project_task.project_id = pro.id ORDER BY project_name ASC''')
        self._cr.execute('''select CAST(datetime as date) as date,srn as srn ,code as code,person as person,description as description,cash_amount as cash_amount,bank_amount as bank_amount,bank_name as bank_name from waaneiza_daily_cashin_cashbook
                           where CAST(datetime as date) = DATE(NOW()) ORDER BY date ASC''')
        data = self._cr.fetchall()
        cashin = []
        for rec in data:
            b = list(rec)
            cashin.append(b)
        return {
            'cashin': cashin
        }


    @api.model
    def get_cashin_data_by_date(self,input_date,employee_selection,inputDateEnd):
        """

        Summery:
            when the page is loaded get the data from different models and transfer to the js file.
            return a dictionary variable.
        return:
            type:It is a dictionary variable. This dictionary contain data that affecting project task table.

        """
        # self._cr.execute('''select project_task.name as task_name,pro.name as project_name from project_task
        #   Inner join project_project as pro on project_task.project_id = pro.id ORDER BY project_name ASC''')
        in_date = datetime.now().strftime('%y-%m-%d')
        if employee_selection != 'null':
            data = self.env['hr.employee'].search([('id','=',employee_selection)])
            employee_name = data['name']
        if employee_selection != 'null':
            if employee_selection != "null" and input_date == 'null' and inputDateEnd=='null':
                query ='''select datetime as date,srn as srn ,code as code,person as person,description as description,cash_amount as cash_amount,bank_amount as bank_amount,bank_name as bank_name from waaneiza_daily_cashin_cashbook
                           where person = %s ORDER BY datetime ASC'''
                self._cr.execute(query, (employee_name,))
            elif employee_selection != "null" and input_date != 'null' and inputDateEnd=='null':
                query ='''select datetime as date,srn as srn ,code as code,person as person,description as description,cash_amount as cash_amount,bank_amount as bank_amount,bank_name as bank_name from waaneiza_daily_cashin_cashbook
                           where datetime = %s and person =%s ORDER BY datetime ASC'''
                self._cr.execute(query,(input_date,employee_name))
            elif employee_selection != "null" and input_date == 'null' and inputDateEnd!='null':
                query ='''select datetime as date,srn as srn ,code as code,person as person,description as description,cash_amount as cash_amount,bank_amount as bank_amount,bank_name as bank_name from waaneiza_daily_cashin_cashbook
                           where datetime = %s and person =%s ORDER BY datetime ASC'''
                self._cr.execute(query,(inputDateEnd,employee_name))
            elif employee_selection != "null" and input_date != 'null' and inputDateEnd!='null':
                query ='''select datetime as date,srn as srn ,code as code,person as person,description as description,cash_amount as cash_amount,bank_amount as bank_amount,bank_name as bank_name from waaneiza_daily_cashin_cashbook
                           where datetime between %s and %s and person =%s ORDER BY datetime ASC'''
                self._cr.execute(query,(input_date,inputDateEnd,employee_name))
        elif employee_selection == 'null':
            if employee_selection == 'null' and input_date!= 'null'and inputDateEnd=='null':
                query ='''select datetime as date,srn as srn ,code as code,person as person,description as description,cash_amount as cash_amount,bank_amount as bank_amount,bank_name as bank_name from waaneiza_daily_cashin_cashbook
                           where datetime = %s ORDER BY datetime ASC'''
                self._cr.execute(query, (input_date,))
            elif employee_selection == 'null' and input_date!= 'null'and inputDateEnd!='null':
                query ='''select datetime as date,srn as srn ,code as code,person as person,description as description,cash_amount as cash_amount,bank_amount as bank_amount,bank_name as bank_name from waaneiza_daily_cashin_cashbook
                           where datetime between %s and %s ORDER BY datetime ASC'''
                self._cr.execute(query, (input_date,inputDateEnd,))
            elif employee_selection == 'null' and input_date== 'null'and inputDateEnd!='null':
                query ='''select datetime as date,srn as srn ,code as code,person as person,description as description,cash_amount as cash_amount,bank_amount as bank_amount,bank_name as bank_name from waaneiza_daily_cashin_cashbook
                           where datetime <= %s ORDER BY datetime ASC'''
                self._cr.execute(query, (inputDateEnd,))
            elif employee_selection == "null" and input_date == 'null' and inputDateEnd=='null':
                query ='''select datetime as date,srn as srn ,code as code,person as person,description as description,cash_amount as cash_amount,bank_amount as bank_amount,bank_name as bank_name from waaneiza_daily_cashin_cashbook
                    ORDER BY datetime ASC'''
                self._cr.execute(query)

        data = self._cr.fetchall()
        cashin_change = []
        for rec in data:
            b = list(rec)
            cashin_change.append(b)
        return {
            'cashin_change': cashin_change
        }

    @api.model
    def get_cashin_all_data(self,employee_selection):
        """

        Summery:
            when the page is loaded get the data from different models and transfer to the js file.
            return a dictionary variable.
        return:
            type:It is a dictionary variable. This dictionary contain data that affecting project task table.

        """
        # self._cr.execute('''select project_task.name as task_name,pro.name as project_name from project_task
        #   Inner join project_project as pro on project_task.project_id = pro.id ORDER BY project_name ASC''')
        # if employee_selection != 'null':
        #     data = self.env['hr.employee'].search([('id','=',employee_selection)])
        #     employee_name = data['name']
        # if employee_selection == 'null':
        #     self._cr.execute('''select CAST(datetime as date) as date,srn as srn ,code as code,person as person,description as description,cash_amount as cash_amount,bank_amount as bank_amount,bank_name as bank_name from waaneiza_daily_cashin_cashbook
        #                    ORDER BY date ASC''')
        # elif employee_selection != 'null':
        #     query='''select CAST(datetime as date) as date,srn as srn ,code as code,person as person,description as description,cash_amount as cash_amount,bank_amount as bank_amount,bank_name as bank_name from waaneiza_daily_cashin_cashbook
        #                     where person = %s ORDER BY date ASC'''
        #     self._cr.execute(query,(employee_selection,))
        # else:
        #     self._cr.execute('''select CAST(datetime as date) as date,srn as srn ,code as code,person as person,description as description,cash_amount as cash_amount,bank_amount as bank_amount,bank_name as bank_name from waaneiza_daily_cashin_cashbook
        #                    ORDER BY date ASC''')
        self._cr.execute('''select CAST(datetime as date) as date,srn as srn ,code as code,person as person,description as description,cash_amount as cash_amount,bank_amount as bank_amount,bank_name as bank_name from waaneiza_daily_cashin_cashbook
                            ORDER BY date ASC''')
        data = self._cr.fetchall()
        cashinall = []
        for rec in data:
            b = list(rec)
            cashinall.append(b)
        return {
            'cashinall': cashinall
        }

        # query = '''select sum(amount_untaxed_invoiced) as invoiced,
        #     sum(amount_untaxed_to_invoice) as to_invoice,sum(timesheet_cost) as 
        #     time_cost,
        #     sum(expense_cost) as expen_cost,
        #     sum(margin) as payment_details from project_profitability_report'''
        # query = '''select sum(cash_amount) as cashin_amount
        #           from waaneiza_daily_cashin_cashbook where CAST(datetime as date) = DATE(NOW())'''
        # start_date = DATE(NOW())
        # print(c_date)
        # self._cr.execute(('''select cash_amount as cashin_daily_amount
        #                     from waaneiza_daily_cashin_cashbook where 
        #                     CAST(datetime as date) = 
        #                     %s'''%(start_date)))
        # date = input_date.toISOString().split('T')[0]
        # self._cr.execute(('''select sum(cash_amount) as cashin_daily_amount
        #            from waaneiza_daily_cashin_cashbook where CAST(datetime as date) = 
        #                       %s'''%(date)))
        # input_datetime = datetime.datetime.strptime(input_date, "%Y-%m-%d")
        # data = self.env['waaneiza.daily.cashin.cashbook'].search([('datetime','=',input_date)])
