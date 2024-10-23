from odoo import api, fields, models, tools
from odoo.tools import format_datetime
from datetime import datetime, time

class CashoutCashbook(models.Model):
    _name = 'cashout.cashbook'
    _description = 'Cash Book Cashout'
    _auto = False
   
    
    srn = fields.Char(string="Vr No")
    code = fields.Char(string="Cash out Code")
    cash_amount = fields.Float(string="Cash Amount")
    kbz_bank = fields.Float(string="KBZ Bank")
    citizen_bank = fields.Float(string="Myanmar Citizen Bank")
    yoma_bank = fields.Float(string="YOMA Bank")
    aya_bank = fields.Float(string="AYA Bank")
    person = fields.Char(string="Person")
    description = fields.Char(string="Description")
    datetime = fields.Date(string="Datetime")

    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'cashout_cashbook')
        self.env.cr.execute(""" 
            CREATE OR REPLACE VIEW cashout_cashbook AS (
                SELECT
                    row_number() OVER () AS id,
                    line.datetime,
                    line.srn,
                    line.code,
                    line.person,
                    line.description,
                    line.cash_amount,
                    line.kbz_bank,
                    Line.aya_bank,
                    Line.yoma_bank,
                    Line.citizen_bank
                    FROM (
                        select 
                            sum(wcr.cash_amount) AS cash_amount,
                            wcr.srn AS srn,
                            case when wcr.bank_name ='KBZ Bank'
                            then sum(wcr.bank_amount) 
                            end as kbz_bank,
                            case when wcr.bank_name ='AYA Bank'
                            then sum(wcr.bank_amount) 
                            end as aya_bank,
                            case when wcr.bank_name ='Yoma Bank (Myanmar Plaza)'
                            then sum(wcr.bank_amount) 
                            end as yoma_bank,
                            case when wcr.bank_name ='Myanmar Citizen Bank'
                            then sum(wcr.bank_amount) 
                            end as citizen_bank,
                            wcr.code As code,
                            wcr.person As person,
                            wcr.description As description,
                            CAST(wcr.datetime as date) As datetime
                            FROM waaneiza_daily_cashout_cashbook wcr 
                            group by  wcr.srn,wcr.code,wcr.person,wcr.description,wcr.datetime,wcr.bank_name          
                    ) as line 
            )
        """)

    @api.model
    def get_cashout_data(self):
        """

        Summery:
            when the page is loaded get the data from different models and transfer to the js file.
            return a dictionary variable.
        return:
            type:It is a dictionary variable. This dictionary contain data that affecting project task table.

        """
        # self._cr.execute('''select project_task.name as task_name,pro.name as project_name from project_task
        #   Inner join project_project as pro on project_task.project_id = pro.id ORDER BY project_name ASC''')
        self._cr.execute('''select CAST(datetime as date) as date,srn as srn ,code as code,COALESCE(person,'N/A') as person,COALESCE(description,'N/A') as description,cash_amount as cash_amount,
            COALESCE(kbz_bank,0) as kbz_bank,COALESCE(aya_bank,0) as aya_bank,COALESCE(yoma_bank,0) as yoma_bank,COALESCE(citizen_bank,0) as citizen_bank from cashout_cashbook
                           where CAST(datetime as date) = DATE(NOW()) ORDER BY date ASC''')
        data = self._cr.fetchall()
        cashout = []
        for rec in data:
            b = list(rec)
            cashout.append(b)
        return {
            'cashout': cashout
        }


    @api.model
    def get_cashout_data_by_date(self,input_date,employee_selection,inputDateEnd):
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
                query ='''select CAST(datetime as date) as date,srn as srn ,code as code,person as person,description as description,cash_amount as cash_amount,
                            COALESCE(kbz_bank,0) as kbz_bank,COALESCE(aya_bank,0) as aya_bank,
                            COALESCE(yoma_bank,0) as yoma_bank,COALESCE(citizen_bank,0) as citizen_bank 
                            from cashout_cashbook
                           where person = %s ORDER BY datetime ASC'''
                self._cr.execute(query, (employee_name,))
            elif employee_selection != "null" and input_date != 'null' and inputDateEnd=='null':
                query ='''select CAST(datetime as date) as date,srn as srn ,code as code,person as person,description as description,cash_amount as cash_amount,
               COALESCE(kbz_bank,0) as kbz_bank,COALESCE(aya_bank,0) as aya_bank,COALESCE(yoma_bank,0) as yoma_bank,COALESCE(citizen_bank,0) as citizen_bank from cashout_cashbook
                           where datetime = %s and person =%s ORDER BY datetime ASC'''
                self._cr.execute(query,(input_date,employee_name))
            elif employee_selection != "null" and input_date == 'null' and inputDateEnd!='null':
                query ='''select CAST(datetime as date) as date,srn as srn ,code as code,person as person,description as description,cash_amount as cash_amount,
                            COALESCE(kbz_bank,0) as kbz_bank,COALESCE(aya_bank,0) as aya_bank,
                            COALESCE(yoma_bank,0) as yoma_bank,COALESCE(citizen_bank,0) as citizen_bank 
                            from cashout_cashbook
                           where datetime = %s and person =%s ORDER BY datetime ASC'''
                self._cr.execute(query,(inputDateEnd,employee_name))
            elif employee_selection != "null" and input_date != 'null' and inputDateEnd!='null':
                query ='''select CAST(datetime as date) as date,srn as srn ,code as code,person as person,description as description,cash_amount as cash_amount,
                            COALESCE(kbz_bank,0) as kbz_bank,COALESCE(aya_bank,0) as aya_bank,
                            COALESCE(yoma_bank,0) as yoma_bank,COALESCE(citizen_bank,0) as citizen_bank 
                            from cashout_cashbook
                           where datetime between %s and %s and person =%s ORDER BY datetime ASC'''
                self._cr.execute(query,(input_date,inputDateEnd,employee_name))
        elif employee_selection == 'null':
            if employee_selection == 'null' and input_date!= 'null'and inputDateEnd=='null':
                query ='''select CAST(datetime as date) as date,srn as srn ,code as code,person as person,description as description,cash_amount as cash_amount,
                            COALESCE(kbz_bank,0) as kbz_bank,COALESCE(aya_bank,0) as aya_bank,
                            COALESCE(yoma_bank,0) as yoma_bank,COALESCE(citizen_bank,0) as citizen_bank 
                            from cashout_cashbook
                           where datetime = %s ORDER BY datetime ASC'''
                self._cr.execute(query, (input_date,))
            elif employee_selection == 'null' and input_date!= 'null'and inputDateEnd!='null':
                query ='''select CAST(datetime as date) as date,srn as srn ,code as code,person as person,description as description,cash_amount as cash_amount,
                            COALESCE(kbz_bank,0) as kbz_bank,COALESCE(aya_bank,0) as aya_bank,
                            COALESCE(yoma_bank,0) as yoma_bank,COALESCE(citizen_bank,0) as citizen_bank 
                            from cashout_cashbook
                           where datetime between %s and %s ORDER BY datetime ASC'''
                self._cr.execute(query, (input_date,inputDateEnd,))
            elif employee_selection == 'null' and input_date== 'null'and inputDateEnd!='null':
                query ='''select CAST(datetime as date) as date,srn as srn ,code as code,person as person,description as description,cash_amount as cash_amount,
                            COALESCE(kbz_bank,0) as kbz_bank,COALESCE(aya_bank,0) as aya_bank,
                            COALESCE(yoma_bank,0) as yoma_bank,COALESCE(citizen_bank,0) as citizen_bank 
                            from cashout_cashbook
                           where datetime <= %s ORDER BY datetime ASC'''
                self._cr.execute(query, (inputDateEnd,))
            elif employee_selection == "null" and input_date == 'null' and inputDateEnd=='null':
                query ='''select CAST(datetime as date) as date,srn as srn ,code as code,person as person,description as description,cash_amount as cash_amount,
                            COALESCE(kbz_bank,0) as kbz_bank,COALESCE(aya_bank,0) as aya_bank,
                            COALESCE(yoma_bank,0) as yoma_bank,COALESCE(citizen_bank,0) as citizen_bank 
                            from cashout_cashbook
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
        
        self._cr.execute('''select CAST(datetime as date) as date,srn as srn ,code as code,COALESCE(person,'N/A') as person,COALESCE(description,'N/A') as description,cash_amount as cash_amount,
                            COALESCE(kbz_bank,0) as kbz_bank,COALESCE(aya_bank,0) as aya_bank,
                            COALESCE(yoma_bank,0) as yoma_bank,COALESCE(citizen_bank,0) as citizen_bank 
                            from cashout_cashbook
                            ORDER BY date ASC''')
        data = self._cr.fetchall()
        cashoutall = []
        for rec in data:
            b = list(rec)
            cashoutall.append(b)
        return {
            'cashoutall': cashoutall
        }

