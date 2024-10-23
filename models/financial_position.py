from odoo import api, fields, models, _


class FinancialPositionReport(models.Model):
    _name = 'financial.position'
    _description = 'Financial Position Report'

    name = fields.Char(string="Sr.No:", readonly=True, required=True, copy=False, index=True, default=lambda self: _('New'))

    income_statement_id = fields.Many2one('income.statement',string="Income Statement Reference")
    # income_statement = fields.Many2one('income.statement',string="Income Statement")
    process_id = fields.Many2one('hr.employee',related="income_statement_id.process_id",string="Process")
    company_id = fields.Many2one('res.company',related="income_statement_id.company_id",string='Company',store=True)
    from_date = fields.Date(string='From Date',related="income_statement_id.from_date",store=True)
    to_date = fields.Date(string='To Date',related="income_statement_id.to_date",store=True)
    attachment = fields.Binary(string="Document")

    # Non-current Assets
    land = fields.Float(string='Lands')
    building_fixture = fields.Float(string='Buildings & Building Fixtures')
    furniture_fixture = fields.Float(string='Furnitures & Fixtures')
    operation_equipment = fields.Float(string='Operation Equipments')
    vehicle = fields.Float(string='Vehicles')
    tool_equipment = fields.Float(string='Tools & Equipments')
    office_equipment = fields.Float(string='Office Equipments')
    ict_equipment = fields.Float(string='ICT Equipments')
    non_hybrid_assets = fields.Float(string='Hybrid Assets')
    license = fields.Float(string='Licenses')
    total_non_current_crd = fields.Float(string='Total Non-current Assets',compute="_compute_total_noncurrent_assets",store=True)
    total_non_current_deb = fields.Float(string='Total Non-current Assets',compute="_compute_total_noncurrent_assets",store=True)

    # Current Assets
    inventory = fields.Float(string='Inventory')
    hybrid_assets = fields.Float(string='Hybrid Assets')
    trade_receivable = fields.Float(string='Trade Receivable')
    deposit_receivable = fields.Float(string='Deposit Receivable')
    deffered_expenditure = fields.Float(string='Deffered Expenditure')
    prepaid_expense = fields.Float(string='Prepaid Expense')
    corporate_receivable = fields.Float(string='Corporate Receivable')
    advanced_cash = fields.Float(string='Advanced Cash')
    cash_at_bank = fields.Float(string='Cash At Bank')
    cash_in_hand = fields.Float(string='Cash In Hand')
    total_current_assets_crd = fields.Float(string='Total Current Assets',compute="_compute_total_current_assets",store=True)
    total_current_assets_deb = fields.Float(string='Total Current Assets',compute="_compute_total_current_assets",store=True)
    total_tangible_assets = fields.Float(string='TOTAL TANGIBLE ASSETS',compute="_compute_total_assets",store=True)
    total_assets = fields.Float(string='TOTAL ASSETS',compute="_compute_total_assets",store=True)

    # Equities
    paid_up_share_capital = fields.Float(string='Paid up Share Capital')
    call_in_arrear = fields.Float(string='Call In Arrears')
    preference_share = fields.Float(string='Preference Shares')
    revaluation_reserve = fields.Float(string='Revaluation Reserve')
    retained_earning = fields.Float(string='Retained Earning')
    net_profit = fields.Float(string='Net profit/(loss) for the period',related="income_statement_id.net_profit",store=True)
    total_equities_crd = fields.Float(string='TOTAL EQUITIES',compute="_compute_total_equities",store=True)
    total_equities_deb = fields.Float(string='TOTAL EQUITIES',compute="_compute_total_equities",store=True)

    # Non-current Liabilities
    bank_loans = fields.Float(string='Bank Loans')
    departmental_share_deposits = fields.Float(string='Departmental Share Deposits')
    external_loans = fields.Float(string='External Loans')
    total_non_current_liabilites = fields.Float(string='Total Non-current Liabilite',compute="_compute_non_current_liabilities",store=True)

    # Current Liabilities
    trade_payable = fields.Float(string='Trade Payable')
    deposit_payable = fields.Float(string='Deposit Payable')
    corporae_payable = fields.Float(string='Corporate Payable')
    tax_payable = fields.Float(string='Tax Payable')
    intrest_payable = fields.Float(string='Intrest Payable')
    accrued_expenses = fields.Float(string='Accrued Expense')
    total_current_liabilities = fields.Float(string='Total Current Liabilities',compute="_compute_current_liabilities",store=True)

    total_liabilities = fields.Float(string='TOTAL LIABILITIES',compute="_compute_total_equities_liabilities",store=True)
    total_equities_liabilities = fields.Float(string='TOTAL EQUITIES AND LIABILITIES',compute="_compute_total_equities_liabilities",store=True)
    total_financial_amount = fields.Float(string='TOTAL Amount',compute="_compute_total_financial_amount",store=True)

    @api.depends('land','building_fixture','furniture_fixture','operation_equipment','vehicle','tool_equipment','office_equipment','ict_equipment','non_hybrid_assets','license')
    def _compute_total_noncurrent_assets(self):
        for order in self:
            order.total_non_current_crd = order.land + order.building_fixture + order.furniture_fixture + order.operation_equipment + order.vehicle + order.tool_equipment + order.office_equipment + order.ict_equipment + order.non_hybrid_assets + order.license
            
            order.total_non_current_deb = order.total_non_current_crd
    
    @api.depends('inventory','hybrid_assets','trade_receivable',        'deposit_receivable',
    'deffered_expenditure','prepaid_expense','corporate_receivable','advanced_cash','cash_at_bank','cash_in_hand')
    def _compute_total_current_assets(self):
        for order in self:
            order.total_current_assets_crd = order.inventory + order.hybrid_assets + order.trade_receivable + order.deposit_receivable + order.deffered_expenditure + order.prepaid_expense + order.corporate_receivable + order.advanced_cash + order.cash_in_hand + order.cash_at_bank

            order.total_current_assets_deb = order.total_current_assets_crd
    
    @api.depends('total_non_current_deb','total_current_assets_deb')
    def _compute_total_assets(self):
        for res in self:
            res.total_tangible_assets = res.total_non_current_deb + res.total_current_assets_deb
            res.total_assets = res.total_non_current_deb + res.total_current_assets_deb

    # Advance Cash / Cash In Hand / Cash At Bank
    @api.onchange('process_id')
    def onchange_process_id(self):
        if self.process_id:
            self.env.cr.execute("""select amount
                            from waaneiza_advance_cash_report
                            where process_id = 'ICT Process 1' and (DATE(date) >= '%s' AND DATE(date) <= '%s')"""% (self.from_date,self.to_date))
            res = self.env.cr.fetchone()
            self.advanced_cash = res and res[0] or 0.0

        if self.process_id.name == 'Cashier Process':
            self.env.cr.execute("""select closing_cash_balance, closing_bank_balance
                            from opening_closing
                            where date = '%s'"""% (self.to_date))
            res = self.env.cr.fetchone()
            self.cash_in_hand = res[0] or 0.0
            self.cash_at_bank = res[1] or 0.0
    
    # Total Equities
    @api.depends('paid_up_share_capital','call_in_arrear','preference_share','revaluation_reserve','retained_earning','net_profit')
    def _compute_total_equities(self):
        for order in self:
            order.total_equities_crd = order.paid_up_share_capital + order.call_in_arrear + order.preference_share + order.revaluation_reserve + order.retained_earning + order.net_profit
            
            order.total_equities_deb = order.total_equities_crd
    
    # Non-current Liabilities
    @api.depends('bank_loans','departmental_share_deposits','external_loans')
    def _compute_non_current_liabilities(self):
        for order in self:
            order.total_non_current_liabilites = order.bank_loans + order.departmental_share_deposits + order.external_loans
    
    # Current Liabilities
    @api.depends('trade_payable','deposit_payable','corporae_payable','tax_payable','intrest_payable','accrued_expenses')
    def _compute_current_liabilities(self):
        for order in self:
            order.total_current_liabilities = order.trade_payable + order.deposit_payable + order.corporae_payable + order.tax_payable + order.intrest_payable + order.accrued_expenses
    
    # TOTAL LIABILITIES
    @api.depends('total_non_current_liabilites','total_current_liabilities','total_equities_deb')
    def _compute_total_equities_liabilities(self):
        for order in self:
            order.total_liabilities = order.total_non_current_liabilites + order.total_current_liabilities
            order.total_equities_liabilities = order.total_liabilities + order.total_equities_deb
    
    # TOTAL
    @api.depends('total_assets','total_equities_liabilities','total_equities_deb')
    def _compute_total_financial_amount(self):
        for order in self:
            order.total_financial_amount = order.total_assets - order.total_equities_liabilities