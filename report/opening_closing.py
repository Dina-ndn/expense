from odoo import api, fields, models, tools
from odoo.tools import format_datetime
from datetime import datetime, time

class OpeningClosing(models.Model):
    _name = 'opening.closing'
    _description = 'Opening Closing Balance'
    _auto = False
    
    date = fields.Date(string="Date")
    opening_cash_balance = fields.Float(string="Cash Opening Amount")
    closing_cash_balance = fields.Float(string="Cash Closing Amount")

    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'opening_closing')
        self.env.cr.execute(""" 
            CREATE OR REPLACE VIEW opening_closing AS (
                SELECT
                    row_number() OVER () AS id,
                    date as date,
                    CASE
                        WHEN opening_cash_balance IS NULL 
                        THEN MAX(closing_cash_balance) over (PARTITION BY i
                        ORDER BY date)
                        ELSE opening_cash_balance
                        END AS opening_cash_balance,
                    cashin_cash_amount as cashin_cash_amount,
                    cashout_cash_amount as cashout_cash_amount,
                    CASE
                        WHEN closing_cash_balance IS NULL 
                        THEN MAX(closing_cash_balance) over (PARTITION BY j
                        ORDER BY date)
                        ELSE closing_cash_balance
                        END AS closing_cash_balance,
                    CASE
                        WHEN opening_bank_balance IS NULL 
                        THEN MAX(closing_bank_balance) over (PARTITION BY k
                        ORDER BY date)
                        ELSE opening_bank_balance
                        END AS opening_bank_balance,
                    cashin_bank_amount as cashin_bank_amount,
                    cashout_bank_amount as cashout_bank_amount,
                    CASE
                        WHEN closing_bank_balance IS NULL 
                        THEN MAX(closing_bank_balance) over (PARTITION BY l
                        ORDER BY date)
                        ELSE closing_bank_balance
                        END AS closing_bank_balance
                FROM(
                    SELECT
                        date,
                        opening_cash_balance,
                        cashin_cash_amount,
                        cashout_cash_amount,
                        closing_cash_balance,
                        COUNT(opening_cash_balance) OVER (order by date) AS i,
                        COUNT(closing_cash_balance) OVER (order by date) AS j,
                        opening_bank_balance,
                        cashin_bank_amount,
                        cashout_bank_amount,
                        closing_bank_balance,
                        COUNT(opening_bank_balance) OVER (order by date) AS k,
                        COUNT(closing_bank_balance) OVER (order by date) AS l
                    FROM waaneiza_opening_closing_alldate
                ) as line
                    
            )
        """)

   
    @api.model
    def get_details_opening(self):
        query = '''select opening_cash_balance as opening_cash_amount,
                    closing_cash_balance as closing_cash_amount
                  from opening_closing where date = DATE(NOW())'''
        self._cr.execute(query)
        data = self._cr.dictfetchall()
        opening_cash_amount = []
        for record in data:
            opening_cash_amount.append(record.get('opening_cash_amount'))
        closing_cash_amount = []
        for record in data:
            closing_cash_amount.append(record.get('closing_cash_amount'))
        return {
            'opening_cash_amount': opening_cash_amount,
            'closing_cash_amount': closing_cash_amount,
        }

    @api.model
    def get_bank_opening(self):
        # query = '''select sum(amount_untaxed_invoiced) as invoiced,
        #     sum(amount_untaxed_to_invoice) as to_invoice,sum(timesheet_cost) as 
        #     time_cost,
        #     sum(expense_cost) as expen_cost,
        #     sum(margin) as payment_details from project_profitability_report'''
        query = '''select opening_bank_balance as opening_bank_balance,
                    closing_bank_balance as closing_bank_balance
                  from opening_closing where date = DATE(NOW())'''
        self._cr.execute(query)
        data = self._cr.dictfetchall()
        opening_bank_balance = []
        for record in data:
            opening_bank_balance.append(record.get('opening_bank_balance'))
        closing_bank_balance = []
        for record in data:
            closing_bank_balance.append(record.get('closing_bank_balance'))
        return {
            'opening_bank_balance': opening_bank_balance,
            'closing_bank_balance': closing_bank_balance,
        }


    @api.model
    def get_details_opening_all_date(self,employee_selection):
        # query1 = '''select opening_cash_balance as opening_cash_amount 
        #           from opening_closing where id=(select min(id) from opening_closing)'''
        query1 = '''select opening_cash_balance as opening_cash_amount
                    from opening_closing where id=1'''
        self._cr.execute(query1)
        data1 = self._cr.dictfetchall()
        query2 = '''select 
                    closing_cash_balance as closing_cash_amount
                    from opening_closing where id=(select max(id) from opening_closing)'''
        self._cr.execute(query2)
        data2 = self._cr.dictfetchall()
        opening_cash_amount = []
        for record in data1:
            opening_cash_amount.append(record.get('opening_cash_amount'))
        closing_cash_amount = []
        for record in data2:
            closing_cash_amount.append(record.get('closing_cash_amount'))

        return {
            'opening_cash_amount': opening_cash_amount,
            'closing_cash_amount': closing_cash_amount,
        }

    @api.model
    def get_bank_opening_all_date(self,employee_selection):
        # query1 = '''select opening_cash_balance as opening_cash_amount 
        #           from opening_closing where id=(select min(id) from opening_closing)'''
        query1 = '''select opening_bank_balance as opening_bank_balance
                    from opening_closing where id=1'''
        self._cr.execute(query1)
        data1 = self._cr.dictfetchall()
        query2 = '''select 
                    closing_bank_balance as closing_bank_balance
                    from opening_closing where id=(select max(id) from opening_closing)'''
        self._cr.execute(query2)
        data2 = self._cr.dictfetchall()
        opening_bank_balance = []
        for record in data1:
            opening_bank_balance.append(record.get('opening_bank_balance'))
        closing_bank_balance = []
        for record in data2:
            closing_bank_balance.append(record.get('closing_bank_balance'))

        return {
            'opening_bank_balance': opening_bank_balance,
            'closing_bank_balance': closing_bank_balance,
        }


    @api.model
    def get_tot_opening_closing(self,input_date,employee_selection,inputDateEnd):
        in_date = datetime.now().strftime('%y-%m-%d')
        flag=1
        cut_date = datetime.now().strftime('%d')
        cut_month = datetime.now().strftime('%m')
        cut_yeat = datetime.now().strftime('%y')
        if inputDateEnd!='null':
            in_month = datetime.strftime(datetime.strptime(inputDateEnd, "%Y-%m-%d"), "%m")
            in_day = datetime.strftime(datetime.strptime(inputDateEnd, "%Y-%m-%d"), "%d")
            in_year = datetime.strftime(datetime.strptime(inputDateEnd, "%Y-%m-%d"), "%y")
            if cut_yeat ==in_year:
                if cut_month==in_month:
                    if in_day > cut_date:
                        flag=0
                    else:
                         flag=1
                elif in_month > cut_month:
                    flag=0
                else:
                    flag=1
            elif cut_yeat > in_year:
                flag=0
            else:
                flag=1
        if input_date!='null':
            if input_date!='null' and inputDateEnd=='null':
                query1 = '''select opening_cash_balance as o_cash_amount,
                      closing_cash_balance as c_cash_amount
                      from opening_closing where date = %s'''
                self._cr.execute(query1,(input_date,))
                data = self._cr.dictfetchall()
                o_cash_amount = []
                for record in data:
                    o_cash_amount.append(record.get('o_cash_amount'))
                c_cash_amount = []
                for record in data:
                    c_cash_amount.append(record.get('c_cash_amount'))

                return {
                'o_cash_amount': o_cash_amount,
                'c_cash_amount': c_cash_amount,
            }
            elif input_date!='null' and inputDateEnd!='null' and flag==0:
                query2 = """
                    select opening_cash_balance as o_cash_amount
                    from opening_closing where date = %s """
                self._cr.execute(query2,(input_date,))
                data1 = self._cr.dictfetchall()
                query3 = """
                    select closing_cash_balance as c_cash_amount
                    from opening_closing where date = DATE(NOW()) """
                self._cr.execute(query3)
                data2 = self._cr.dictfetchall()
                o_cash_amount = []
                for record in data1:
                    o_cash_amount.append(record.get('o_cash_amount'))
                c_cash_amount = []
                for record in data2:
                    c_cash_amount.append(record.get('c_cash_amount'))
                return {
                'o_cash_amount': o_cash_amount,
                'c_cash_amount': c_cash_amount,
                }
            elif input_date!='null' and inputDateEnd!='null' and flag==1:
                query2 = """
                    select opening_cash_balance as o_cash_amount
                    from opening_closing where date = %s """
                self._cr.execute(query2,(input_date,))
                data1 = self._cr.dictfetchall()
                query4 = """
                    select closing_cash_balance as c_cash_amount
                    from opening_closing where date = %s """
                self._cr.execute(query4,(inputDateEnd,))
                data2 = self._cr.dictfetchall()
                o_cash_amount = []
                for record in data1:
                    o_cash_amount.append(record.get('o_cash_amount'))
                c_cash_amount = []
                for record in data2:
                    c_cash_amount.append(record.get('c_cash_amount'))
                return {
                'o_cash_amount': o_cash_amount,
                'c_cash_amount': c_cash_amount,
                }

        elif input_date =='null':
            if input_date=='null' and inputDateEnd!='null' and flag==1:
                query = """
                select opening_cash_balance as o_cash_amount,
                    closing_cash_balance as c_cash_amount
                    from opening_closing where date = %s
                """
                self._cr.execute(query,(inputDateEnd,))
            elif input_date=='null' and inputDateEnd!='null' and flag==0:
                query = """
                select opening_cash_balance as o_cash_amount,
                    closing_cash_balance as c_cash_amount
                    from opening_closing where date = DATE(NOW())
                """
                self._cr.execute(query)
            # elif input_date=='null' and inputDateEnd=='null' and employee_selection=='null':
            #     query = '''select opening_cash_balance as o_cash_amount,
            #           closing_cash_balance as c_cash_amount
            #           from opening_closing where date = DATE(NOW())'''
            #     self._cr.execute(query)
            elif input_date=='null' and inputDateEnd=='null':
                query1 = '''select opening_cash_balance as o_cash_amount
                    from opening_closing where id=4'''
                self._cr.execute(query1)
                data1 = self._cr.dictfetchall()
                query2 = '''select 
                    closing_cash_balance as c_cash_amount
                    from opening_closing where id=(select max(id) from opening_closing)'''
                self._cr.execute(query2)
                data2 = self._cr.dictfetchall()
                o_cash_amount = []
                for record in data1:
                    o_cash_amount.append(record.get('o_cash_amount'))
                c_cash_amount = []
                for record in data2:
                    c_cash_amount.append(record.get('c_cash_amount'))

                return {
                'o_cash_amount': o_cash_amount,
                'c_cash_amount': c_cash_amount,
                    }

        data = self._cr.dictfetchall()
        o_cash_amount = []
        for record in data:
            o_cash_amount.append(record.get('o_cash_amount'))
        c_cash_amount = []
        for record in data:
            c_cash_amount.append(record.get('c_cash_amount'))

        return {
            'o_cash_amount': o_cash_amount,
            'c_cash_amount': c_cash_amount,
            }


    @api.model
    def get_bank_tot_opening_closing(self,input_date,employee_selection,inputDateEnd):
        in_date = datetime.now().strftime('%y-%m-%d')
        flag=1
        cut_date = datetime.now().strftime('%d')
        cut_month = datetime.now().strftime('%m')
        cut_yeat = datetime.now().strftime('%y')
        if inputDateEnd!='null':
            in_month = datetime.strftime(datetime.strptime(inputDateEnd, "%Y-%m-%d"), "%m")
            in_day = datetime.strftime(datetime.strptime(inputDateEnd, "%Y-%m-%d"), "%d")
            in_year = datetime.strftime(datetime.strptime(inputDateEnd, "%Y-%m-%d"), "%y")
            if cut_yeat ==in_year:
                if cut_month==in_month:
                    if in_day > cut_date:
                        flag=0
                    else:
                         flag=1
                elif in_month > cut_month:
                    flag=0
                else:
                    flag=1
            elif cut_yeat > in_year:
                flag=0
            else:
                flag=1
        if input_date!='null':
            if input_date!='null' and inputDateEnd=='null':
                query1 = '''select opening_bank_balance as o_bank_amount,
                      closing_bank_balance as c_bank_amount
                      from opening_closing where date = %s'''
                self._cr.execute(query1,(input_date,))
                data = self._cr.dictfetchall()
                o_bank_amount = []
                for record in data:
                    o_bank_amount.append(record.get('o_bank_amount'))
                c_bank_amount = []
                for record in data:
                    c_bank_amount.append(record.get('c_bank_amount'))

                return {
                'o_bank_amount': o_bank_amount,
                'c_bank_amount': c_bank_amount,
            }
            elif input_date!='null' and inputDateEnd!='null' and flag==0:
                query2 = """
                    select opening_bank_balance as o_bank_amount
                    from opening_closing where date = %s """
                self._cr.execute(query2,(input_date,))
                data1 = self._cr.dictfetchall()
                query3 = """
                    select closing_bank_balance as c_bank_amount
                    from opening_closing where date = DATE(NOW()) """
                self._cr.execute(query3)
                data2 = self._cr.dictfetchall()
                o_bank_amount = []
                for record in data1:
                    o_bank_amount.append(record.get('o_bank_amount'))
                c_bank_amount = []
                for record in data2:
                    c_bank_amount.append(record.get('c_bank_amount'))
                return {
                'o_bank_amount': o_bank_amount,
                'c_bank_amount': c_bank_amount,
                }
            elif input_date!='null' and inputDateEnd!='null' and flag==1:
                query2 = """
                    select opening_bank_balance as o_bank_amount
                    from opening_closing where date = %s """
                self._cr.execute(query2,(input_date,))
                data1 = self._cr.dictfetchall()
                query4 = """
                    select closing_bank_balance as c_bank_amount
                    from opening_closing where date = %s """
                self._cr.execute(query4,(inputDateEnd,))
                data2 = self._cr.dictfetchall()
                o_bank_amount = []
                for record in data1:
                    o_bank_amount.append(record.get('o_bank_amount'))
                c_bank_amount = []
                for record in data2:
                    c_bank_amount.append(record.get('c_bank_amount'))
                return {
                'o_bank_amount': o_bank_amount,
                'c_bank_amount': c_bank_amount,
                }

        elif input_date =='null':
            if input_date=='null' and inputDateEnd!='null' and flag==1:
                query = """
                select opening_bank_balance as o_bank_amount,
                    closing_bank_balance as c_bank_amount
                    from opening_closing where date = %s
                """
                self._cr.execute(query,(inputDateEnd,))
            elif input_date=='null' and inputDateEnd!='null' and flag==0:
                query = """
                select opening_bank_balance as o_bank_amount,
                    closing_bank_balance as c_bank_amount
                    from opening_closing where date = DATE(NOW())
                """
                self._cr.execute(query)
            # elif input_date=='null' and inputDateEnd=='null' and employee_selection=='null':
            #     query = '''select opening_cash_balance as o_cash_amount,
            #           closing_cash_balance as c_cash_amount
            #           from opening_closing where date = DATE(NOW())'''
            #     self._cr.execute(query)
            elif input_date=='null' and inputDateEnd=='null':
                query1 = '''select opening_bank_balance as o_bank_amount
                    from opening_closing where id=4'''
                self._cr.execute(query1)
                data1 = self._cr.dictfetchall()
                query2 = '''select 
                    closing_bank_balance as c_bank_amount
                    from opening_closing where id=(select max(id) from opening_closing)'''
                self._cr.execute(query2)
                data2 = self._cr.dictfetchall()
                o_bank_amount = []
                for record in data1:
                    o_bank_amount.append(record.get('o_bank_amount'))
                c_bank_amount = []
                for record in data2:
                    c_bank_amount.append(record.get('c_bank_amount'))

                return {
                'o_bank_amount': o_bank_amount,
                'c_bank_amount': c_bank_amount,
                    }

        data = self._cr.dictfetchall()
        o_bank_amount = []
        for record in data:
            o_bank_amount.append(record.get('o_bank_amount'))
        c_bank_amount = []
        for record in data:
            c_bank_amount.append(record.get('c_bank_amount'))

        return {
            'o_bank_amount': o_bank_amount,
            'c_bank_amount': c_bank_amount,
            }

    @api.model
    def get_total_amount(self):
        # query = '''select sum(amount_untaxed_invoiced) as invoiced,
        #     sum(amount_untaxed_to_invoice) as to_invoice,sum(timesheet_cost) as 
        #     time_cost,
        #     sum(expense_cost) as expen_cost,
        #     sum(margin) as payment_details from project_profitability_report'''
        # query = '''select sum(cash_amount) as cashin_amount
        #           from waaneiza_daily_cashin_cashbook where CAST(datetime as date) = DATE(NOW())'''
        query = '''SELECT COALESCE(sum(opening_cash_balance),0) + COALESCE(sum(cashin_cash_amount),0) + COALESCE(sum(opening_bank_balance),0)+ COALESCE(sum(cashin_bank_amount),0) AS cashin_sum,
            COALESCE(sum(closing_cash_balance),0)  + COALESCE(sum(closing_bank_balance),0)+ COALESCE(sum(cashout_bank_amount),0) AS cashout_sum
            FROM opening_closing where date = DATE(NOW())'''
        self._cr.execute(query)
        data = self._cr.dictfetchall()
        cashin_sum = []
        for record in data:
            cashin_sum.append(record.get('cashin_sum'))
        cashout_sum = []
        for record in data:
            cashout_sum.append(record.get('cashout_sum'))
        return {
            'cashin_sum': cashin_sum,
            'cashout_sum': cashout_sum,
        }

    @api.model
    def get_total_amount_by_date(self):
        # query = '''select sum(amount_untaxed_invoiced) as invoiced,
        #     sum(amount_untaxed_to_invoice) as to_invoice,sum(timesheet_cost) as 
        #     time_cost,
        #     sum(expense_cost) as expen_cost,
        #     sum(margin) as payment_details from project_profitability_report'''
        # query = '''select sum(cash_amount) as cashin_amount
        #           from waaneiza_daily_cashin_cashbook where CAST(datetime as date) = DATE(NOW())'''
        query = '''SELECT (SELECT COALESCE(SUM(opening_cash_balance), 0) from opening_closing where id=1) +(SELECT COALESCE(SUM(opening_bank_balance), 0) from opening_closing where id=1)+ 
            (SELECT COALESCE(SUM(cashin_cash_amount), 0) FROM opening_closing)+(SELECT COALESCE(SUM(cashin_bank_amount), 0) FROM opening_closing)
            as cashin_sum,
            (SELECT COALESCE(SUM(closing_cash_balance), 0) from opening_closing where id=(select max(id) from opening_closing)) +(SELECT COALESCE(SUM(closing_bank_balance), 0) from opening_closing where id=(select max(id) from opening_closing))+ 
            (SELECT COALESCE(SUM(cashout_cash_amount), 0) FROM opening_closing)+(SELECT COALESCE(SUM(cashout_bank_amount), 0) FROM opening_closing)
            as cashout_sum '''
        self._cr.execute(query)
        data = self._cr.dictfetchall()
        cashin_sum = []
        for record in data:
            cashin_sum.append(record.get('cashin_sum'))
        cashout_sum = []
        for record in data:
            cashout_sum.append(record.get('cashout_sum'))
        return {
            'cashin_sum': cashin_sum,
            'cashout_sum': cashout_sum,
        }


    @api.model
    def get_total_amount_date(self,input_date,employee_selection,inputDateEnd):
        in_date = datetime.now().strftime('%y-%m-%d')
        flag=1
        cut_date = datetime.now().strftime('%d')
        cut_month = datetime.now().strftime('%m')
        cut_yeat = datetime.now().strftime('%y')
        if inputDateEnd!='null':
            in_month = datetime.strftime(datetime.strptime(inputDateEnd, "%Y-%m-%d"), "%m")
            in_day = datetime.strftime(datetime.strptime(inputDateEnd, "%Y-%m-%d"), "%d")
            in_year = datetime.strftime(datetime.strptime(inputDateEnd, "%Y-%m-%d"), "%y")
            if cut_yeat ==in_year:
                if cut_month==in_month:
                    if in_day > cut_date:
                        flag=0
                    else:
                         flag=1
                elif in_month > cut_month:
                    flag=0
                else:
                    flag=1
            elif cut_yeat > in_year:
                flag=0
            else:
                flag=1
        if input_date!='null':
            if input_date!='null' and inputDateEnd=='null':
                query1 = '''SELECT COALESCE(sum(opening_cash_balance),0) + COALESCE(sum(cashin_cash_amount),0) + COALESCE(sum(opening_bank_balance),0)+ COALESCE(sum(cashin_bank_amount),0) AS cashin_sum,
                COALESCE(sum(closing_cash_balance),0) + COALESCE(sum(closing_bank_balance),0)+ COALESCE(sum(cashout_cash_amount),0)+COALESCE(sum(cashout_bank_amount),0) AS cashout_sum
                FROM opening_closing where date = %s'''
                self._cr.execute(query1,(input_date,))
                data = self._cr.dictfetchall()
                cashin_sum = []
                for record in data:
                    cashin_sum.append(record.get('cashin_sum'))
                cashout_sum = []
                for record in data:
                    cashout_sum.append(record.get('cashout_sum'))
                return {
                'cashin_sum': cashin_sum,
                'cashout_sum': cashout_sum,
                 }
            elif input_date!='null' and inputDateEnd!='null' and flag==0:
                query2 = """
                    SELECT (SELECT COALESCE(SUM(opening_cash_balance), 0) from opening_closing where date = %s) +(SELECT COALESCE(SUM(opening_bank_balance), 0) from opening_closing where date = DATE(NOW()))+ 
                    (SELECT COALESCE(SUM(cashin_cash_amount), 0) FROM opening_closing where date <= DATE(NOW()))+(SELECT COALESCE(SUM(cashin_bank_amount), 0) FROM opening_closing where date <= DATE(NOW()))
                as cashin_sum,
                (SELECT COALESCE(SUM(closing_cash_balance), 0) from opening_closing where id=(select max(id) from opening_closing)) +(SELECT COALESCE(SUM(closing_bank_balance), 0) from opening_closing where id=(select max(id) from opening_closing))+ 
                (SELECT COALESCE(SUM(cashout_cash_amount), 0) FROM opening_closing where date <= DATE(NOW()))+(SELECT COALESCE(SUM(cashout_bank_amount), 0) FROM opening_closing where date <= DATE(NOW()))
                as cashout_sum """
                self._cr.execute(query2,(input_date,))
                data = self._cr.dictfetchall()
                cashin_sum = []
                for record in data:
                    cashin_sum.append(record.get('cashin_sum'))
                cashout_sum = []
                for record in data:
                    cashout_sum.append(record.get('cashout_sum'))
                return {
                'cashin_sum': cashin_sum,
                'cashout_sum': cashout_sum,
                 }
            elif input_date!='null' and inputDateEnd!='null' and flag==1:
                query2 = """
                    SELECT (SELECT COALESCE(SUM(opening_cash_balance), 0) from opening_closing where date = %s) +(SELECT COALESCE(SUM(opening_bank_balance), 0) from opening_closing where date = %s)+ 
                    (SELECT COALESCE(SUM(cashin_cash_amount), 0) FROM opening_closing where date <= %s)+(SELECT COALESCE(SUM(cashin_bank_amount), 0) FROM opening_closing where date <= %s)
                    as cashin_sum,
                    (SELECT COALESCE(SUM(closing_cash_balance), 0) from opening_closing where date=%s) +(SELECT COALESCE(SUM(closing_bank_balance), 0) from opening_closing where date=%s)+ 
                    (SELECT COALESCE(SUM(cashout_cash_amount), 0) FROM opening_closing where date <= %s)+(SELECT COALESCE(SUM(cashout_bank_amount), 0) FROM opening_closing where date <= %s)
                    as cashout_sum """
                self._cr.execute(query2,(input_date,input_date,inputDateEnd,inputDateEnd,inputDateEnd,inputDateEnd,inputDateEnd,inputDateEnd,))
                data = self._cr.dictfetchall()
                cashin_sum = []
                for record in data:
                    cashin_sum.append(record.get('cashin_sum'))
                cashout_sum = []
                for record in data:
                    cashout_sum.append(record.get('cashout_sum'))
                return {
                'cashin_sum': cashin_sum,
                'cashout_sum': cashout_sum,
                 }

        elif input_date =='null':
            if input_date=='null' and inputDateEnd!='null' and flag==1:
                query = """
                 SELECT COALESCE(sum(opening_cash_balance),0) + COALESCE(sum(cashin_cash_amount),0) + COALESCE(sum(opening_bank_balance),0)+ COALESCE(sum(cashin_bank_amount),0) AS cashin_sum,
                COALESCE(sum(closing_cash_balance),0) + COALESCE(sum(closing_cash_balance),0) + COALESCE(sum(closing_bank_balance),0)+ COALESCE(sum(cashout_bank_amount),0) AS cashout_sum
                FROM opening_closing where date = %s
                """
                self._cr.execute(query,(inputDateEnd,))
            elif input_date=='null' and inputDateEnd!='null' and flag==0:
                query = """
               SELECT COALESCE(sum(opening_cash_balance),0) + COALESCE(sum(cashin_cash_amount),0) + COALESCE(sum(opening_bank_balance),0)+ COALESCE(sum(cashin_bank_amount),0) AS cashin_sum,
                COALESCE(sum(closing_cash_balance),0) + COALESCE(sum(closing_cash_balance),0) + COALESCE(sum(closing_bank_balance),0)+ COALESCE(sum(cashout_bank_amount),0) AS cashout_sum
                FROM opening_closing where date = DATE(NOW())
                """
                self._cr.execute(query)
            elif input_date=='null' and inputDateEnd=='null':
                query1 = '''SELECT (SELECT COALESCE(SUM(opening_cash_balance), 0) from opening_closing where id=1) +(SELECT COALESCE(SUM(opening_bank_balance), 0) from opening_closing where id=1)+ 
                (SELECT COALESCE(SUM(cashin_cash_amount), 0) FROM opening_closing where id<=(select max(id) from opening_closing))+(SELECT COALESCE(SUM(cashin_bank_amount), 0) FROM opening_closing where id<=(select max(id) from opening_closing))
                as cashin_sum,
                (SELECT COALESCE(SUM(closing_cash_balance), 0) from opening_closing where id=(select max(id) from opening_closing)) +(SELECT COALESCE(SUM(closing_bank_balance), 0) from opening_closing where id=(select max(id) from opening_closing))+ 
                (SELECT COALESCE(SUM(cashout_cash_amount), 0) FROM opening_closing where id<=(select max(id) from opening_closing))+(SELECT COALESCE(SUM(cashout_bank_amount), 0) FROM opening_closing where id<=(select max(id) from opening_closing))
                as cashout_sum'''
                self._cr.execute(query1)
                data = self._cr.dictfetchall()
                cashin_sum = []
                for record in data:
                    cashin_sum.append(record.get('cashin_sum'))
                cashout_sum = []
                for record in data:
                    cashout_sum.append(record.get('cashout_sum'))
                return {
                'cashin_sum': cashin_sum,
                'cashout_sum': cashout_sum,
                 }

        data = self._cr.dictfetchall()
        cashin_sum = []
        for record in data:
            cashin_sum.append(record.get('cashin_sum'))
        cashout_sum = []
        for record in data:
            cashout_sum.append(record.get('cashout_sum'))
        return {
            'cashin_sum': cashin_sum,
            'cashout_sum': cashout_sum,
                 }

