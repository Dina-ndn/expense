from odoo import api, fields, models, tools

class WaaneizaCashinTransferReport(models.Model):
    _name = 'waaneiza.cashin.transfer.report'
    _description = 'Waaneiza Bank Transfer Report'
    _auto = False
   
    
    bank_name = fields.Char(string="Bank Name")
    srn = fields.Char(string="Vr No")
    code = fields.Many2one('cashier.cash.in.transfer',string="Code")
    bank_amount = fields.Float(string="Bank Amount")
    cash_amount = fields.Float(string="Cash Amount")
    person = fields.Char(string="Person")
    description = fields.Char(string="Description")
    datetime = fields.Datetime(string="Datetime")


    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'waaneiza_cashin_transfer_report')
        self.env.cr.execute(""" 
            CREATE OR REPLACE VIEW waaneiza_cashin_transfer_report AS (
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
                        SELECT 
                            htb.datetime As datetime,
                            htb.name As srn,
                            htb.cash_in_code As code,
                            htb.person As person,
                            htb.description As description,
                            htb.cash_in_cash_amount AS cash_amount,
                            htb.cash_in_bank_amount AS bank_amount,
                            htb.bank_name AS bank_name
                            FROM hand_to_bank_transfer htb
                            where htb.state = 'done'
                            UNION
                            SELECT 
                            bth.datetime As datetime,
                            bth.name As srn,
                            bth.cash_in_code As code,
                            bth.person As person,
                            bth.description As description,
                            bth.cash_in_cash_amount AS cash_amount,
                            bth.cash_in_bank_amount AS bank_amount,
                            bth.cash_in_bank AS bank_name
                            FROM bank_to_hand_transfer bth  
                            where bth.state = 'done'
                            UNION
                            SELECT 
                            btb.datetime As datetime,
                            btb.name As srn,
                            btb.code As code,
                            btbd.person As person,
                            btbd.description As description,
                            btbd.cash_in_cash_amount AS cash_amount,
                            btbd.cash_in_bank_amount AS bank_amount,
                            btbd.to_bank AS bank_name
                            from bank_to_bank_transfer btb
                            join bank_to_bank_transfer_details btbd on btbd.bank_transfer_id = btb.id
                            where btb.state = 'done'
                            UNION
                            SELECT 
                            cit.datetime As datetime,
                            cit.name As srn,
                            cit.cash_in_code As code,
                            cit.type_name As person,
                            cit.remarks As description,
                            cit.cash_amount AS cash_amount,
                            cit.bank_amount AS bank_amount,
                            cit.cash_in_bank AS bank_name
                            from cashier_cash_in_transfer cit
                            where cit.state = 'done'
                    ) as line 
            )
        """)