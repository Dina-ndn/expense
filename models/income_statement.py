from odoo import api, fields, models, _


class IncomeStatementReport(models.Model):
    _name = 'income.statement'
    _description = 'Income Statement Report'

    name = fields.Char(string="Sr.No:", readonly=True, required=True, copy=False, index=True, default=lambda self: _('New'))
    company_id = fields.Many2one('res.company',string='Company')
    from_date = fields.Date(string='From Date', required=True)
    to_date = fields.Date(string='To Date', required=True)
    revenue = fields.Float(string='Revenue')
    other_income = fields.Float(string='Other Income')
    distribution = fields.Float(string='Distribution')
    selling = fields.Float(string='Selling')
    taxation = fields.Float(string='Taxation')
    interest = fields.Float(string='Interests')
    depreciation = fields.Float(string='depreciation')

    # Total
    total_expense = fields.Float(string='Total Amount', compute='_compute_total_expense')
    total_inbound = fields.Float(string='Total Inbound Amount', compute='_compute_total_inbound')
    total_products_purchase = fields.Float(string='Total Product Purchasing Amount',
                                           compute='_compute_total_products_purchase')
    total_raw_products = fields.Float(string='Total Raw Product Amount', compute='_compute_total_raw_products')
    cost_sale = fields.Float(string='Costs of Sale', compute='_compute_cost_sale')
    cost_selling = fields.Float(string='Costs of Sale', compute='_compute_cost_selling')
    ag_expense = fields.Float(string='Costs of Sale', compute='_compute_ag_expense')
    cost_distribution = fields.Float(string='Costs of Distribution', compute='_compute_cost_distribution')
    gross_profit = fields.Float(string='Gross Profit', compute='_compute_gross_profit')
    gross_distribution = fields.Float(string='Gross Profit', compute='_compute_gross_distribution')
    gross_selling = fields.Float(string='Gross Profit', compute='_compute_gross_selling')
    net_profit = fields.Float(string='Gross Profit', compute='_compute_net_profit')
    total_admin = fields.Float(string='Gross Profit', compute='_compute_admin')
    total_dd_promotion = fields.Float(string='Gross Profit', compute='_compute_dd_promotion')
    ebit = fields.Float(string='Gross Profit', compute='_compute_ebit')
    ebt = fields.Float(string='EBT', compute='_compute_ebt')
    # Percentage
    pro_purchase_percentage = fields.Float(string='Product Purchase Percentage',
                                           compute='_compute_pro_purchase_percentage')
    inbound_percentage = fields.Float(string='Inbound Percentage', compute='_compute_inbound_percentage')
    cost_sale_percentage = fields.Float(string='Cost of Sale Percentage', compute='_compute_cost_sale_percentage')
    raw_products_percentage = fields.Float(string='Raw Products Percentage', compute='_compute_raw_products_percentage')
    other_income_percentage = fields.Float(string='Other Income Percentage', compute='_compute_other_income_percentage')
    dis_percentage = fields.Float(string='Distribution Percentage', compute='_compute_dis_percentage')
    selling_percentage= fields.Float(string='Distribution Percentage', compute='_compute_selling_percentage')
    interest_percentage= fields.Float(string='Distribution Percentage', compute='_compute_interest_percentage')

    taxation_percentage= fields.Float(string='Distribution Percentage', compute='_compute_taxation_percentage')
    gross_profit_percentage = fields.Float(string='Gross Profit Percentage', compute='_compute_gross_profit_percentage')
    cost_distribution_percentage = fields.Float(string='Cost Distribution Percentage',
                                                compute='_compute_cost_distribution_percentage')
    gross_distribution_percentage = fields.Float(string='Gross Profit Percentage',
                                                 compute='_compute_gross_distribution_percentage')
    cost_selling_percentage = fields.Float(string='Other Income Percentage', compute='_compute_cost_selling_percentage')
    ag_expense_percentage = fields.Float(string='AG Expense Percentage', compute='_compute_ag_expense_percentage')
    dd_promotion_percentage = fields.Float(string='DD Promotion Percentage', compute='_compute_dd_promotion_percentage')

    gross_selling_percentage = fields.Float(string='Other Income Percentage',
                                            compute='_compute_gross_selling_percentage')
    net_profit_percentage = fields.Float(string='Other Income Percentage', compute='_compute_net_profit_percentage')
    admin_percentage = fields.Float(string='Administration Percentage', compute='_compute_admin_percentage')
    ebit_percentage = fields.Float(string='Administration Percentage', compute='_compute_ebit_percentage')
    ebt_percentage = fields.Float(string='Administration Percentage', compute='_compute_ebt_percentage')

    # Eaindra Expense
    current_user = fields.Many2one('res.users','Current User', default=lambda self: self.env.user)
    process_id = fields.Many2one('hr.employee',string="Process")
    process_id_id = fields.Integer(string="Process ID")
    parent_id = fields.Many2one('hr.employee','parent_id',related='process_id.parent_id')
    child_id = fields.Many2one('hr.employee',store=True,string="Child Process")
    child_expense_amount = fields.Float(string="Child Expense Amount",store=True)
    owner_expense_amount = fields.Float(string="Own Expense Amount",store=True)
    expense_amount = fields.Float(string="Expense Amount",compute="_compute_expense_amount")

    # state
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('done', 'Done'),
    ], string='Status', index=True, store=True, default='draft')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            code = vals['name'] = self.env['ir.sequence'].next_by_code(
                'income.statement.srn') or _('New')
            company = self.env['res.company'].browse(vals.get('company_id'))
            
            vals['name'] = str(company.name) + str(code) 
        result = super(IncomeStatementReport, self).create(vals)
        return result


    @api.onchange('current_user')
    def onchange_process_id(self):
        self.process_id = self.env['hr.employee'].search([('user_id', '=', self.current_user.id)])
        for rec in self:
            return {'domain':{'company_id':[('id','=',[p.id for p in rec.current_user.company_ids])]}}
        if self.process_id:
            for rec in self:
                return {'domain':{'child_id':[('parent_id','=',rec.process_id.id)]}}
    
    @api.onchange('process_id')
    def onchange_child_process_id(self):
        if self.process_id:
            for rec in self:
                return {'domain':{'child_id':[('parent_id','=',rec.process_id.id)]}}
    
    @api.onchange("process_id","from_date","to_date")
    def _onchange_temp_emp_id(self):
        if self.process_id:
            self.process_id_id = self.process_id.id
            child_expense = 0.0
            self.child_expense_amount = 0.0
            childrens = self.env['hr.employee'].search([('parent_id', '=', self.process_id_id)])
            
            if self.from_date and self.to_date:
                for child in childrens:
                    sub_child = self.env['hr.employee'].search([('parent_id', '=', child.id)])
                    if not sub_child:
                        self.env.cr.execute("""select sum(exp.before_return) from waaneiza_exp_sett exp join hr_employee on exp.process_id=hr_employee.id where hr_employee.parent_id=%s or hr_employee.id=%s and (DATE(exp.sett_date) >= '%s' AND DATE(exp.sett_date) <= '%s')""" % (child.id,child.id,self.from_date,self.to_date))
                        res = self.env.cr.fetchone()
                        child_expense =res and res[0] or 0.0
                        print("Child Expense",child_expense)
                        self.child_expense_amount += child_expense
                        print("Child Expense",self.child_expense_amount)

                self.env.cr.execute("""select sum(exp.before_return) from waaneiza_exp_sett exp join hr_employee on exp.process_id=hr_employee.id where hr_employee.id=%s and (DATE(exp.sett_date) >= '%s' AND DATE(exp.sett_date) <= '%s') """ % (self.process_id_id,self.from_date,self.to_date))
                res = self.env.cr.fetchone()
                self.owner_expense_amount = res and res[0] or 0.0
            else:
                for child in childrens:
                    sub_child = self.env['hr.employee'].search([('parent_id', '=', child.id)])
                    if not sub_child:
                        self.env.cr.execute("""select sum(exp.before_return) from waaneiza_exp_sett exp join hr_employee on exp.process_id=hr_employee.id where hr_employee.parent_id=%s or hr_employee.id=%s""" % (child.id,child.id))
                        res = self.env.cr.fetchone()
                        child_expense =res and res[0] or 0.0
                        print("Child Expense",child_expense)
                        self.child_expense_amount += child_expense
                        print("Child Expense",self.child_expense_amount)

                self.env.cr.execute("""select sum(exp.before_return) from waaneiza_exp_sett exp join hr_employee on exp.process_id=hr_employee.id where hr_employee.id=%s """ % (self.process_id_id))
                res = self.env.cr.fetchone()
                self.owner_expense_amount = res and res[0] or 0.0

    
    @api.depends('child_expense_amount','owner_expense_amount','child_id',"from_date","to_date")
    def _compute_expense_amount(self):
        if self.child_id:
            if self.from_date and self.to_date:
                self.env.cr.execute("""select sum(exp.before_return) from waaneiza_exp_sett exp join hr_employee on exp.process_id=hr_employee.id where hr_employee.id=%s and (DATE(exp.sett_date) >= '%s' AND DATE(exp.sett_date) <= '%s') """ % (self.child_id.id,self.from_date,self.to_date))
                res = self.env.cr.fetchone()
                self.expense_amount =res and res[0] or 0.0
            else:
                self.env.cr.execute("""select sum(exp.before_return) from waaneiza_exp_sett exp join hr_employee on exp.process_id=hr_employee.id where hr_employee.id=%s""" % (self.child_id.id))
                res = self.env.cr.fetchone()
                self.expense_amount =res and res[0] or 0.0
        else:
            for rec in self:
                rec.expense_amount = rec.child_expense_amount + rec.owner_expense_amount

    @api.depends('total_expense', 'revenue', 'total_inbound', 'total_products_purchase', 'total_raw_products')
    def _compute_cost_sale(self):
        for record in self:
            record.cost_sale = record.total_expense + record.total_inbound + record.total_products_purchase + record.total_raw_products

    # Gross Profit
    @api.depends('revenue', 'cost_sale', 'other_income')
    def _compute_gross_profit(self):
        for record in self:
            record.gross_profit = record.revenue + record.other_income - record.cost_sale

    # selling
    @api.depends('revenue', 'selling')
    def _compute_selling_percentage(self):
        for record in self:
            if record.revenue:
                record.selling_percentage = (record.selling / record.revenue) * 100
            else:
                record.selling_percentage = 0

    # taxation
    @api.depends('revenue', 'taxation')
    def _compute_taxation_percentage(self):
        for record in self:
            if record.revenue:
                record.taxation_percentage = (record.taxation / record.revenue) * 100
            else:
                record.taxation_percentage = 0
    

    def action_financial_position(self):
        return {
            'res_model': 'financial.position',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref("waaneiza_expense_cashier.view_financial_position_report_form").id,
            'target': 'self.'
        }
    
    def action_confirm(self):
        self.state = 'confirm'
    
    def action_draft(self):
        self.state = "draft"
    
    def action_done(self):
        self.state = "done"

    # taxation
    @api.depends('revenue', 'interest')
    def _compute_interest_percentage(self):
        for record in self:
            if record.revenue:
                record.interest_percentage = (record.interest / record.revenue) * 100
            else:
                record.interest_percentage = 0

    # distribution
    @api.depends('revenue', 'distribution')
    def _compute_dis_percentage(self):
        for record in self:
            if record.revenue:
                record.dis_percentage = (record.distribution / record.revenue) * 100
            else:
                record.dis_percentage = 0

    @api.depends('revenue', 'gross_profit')
    def _compute_gross_profit_percentage(self):
        for record in self:
            if record.revenue:
                record.gross_profit_percentage = (record.gross_profit / record.revenue) * 100
            else:
                record.gross_profit_percentage = 0

        # Cost of Distribution

    @api.depends('distribution', 'cost_sale', 'other_income')
    def _compute_cost_distribution(self):
        for record in self:
            record.cost_distribution = record.cost_sale + record.distribution

    @api.depends('revenue', 'gross_profit')
    def _compute_cost_distribution_percentage(self):
        for record in self:
            if record.revenue:
                record.cost_distribution_percentage = (record.gross_profit / record.revenue) * 100
            else:
                record.cost_distribution_percentage = 0

        # Gross of Distribution

    @api.depends('revenue', 'cost_sale', 'other_income')
    def _compute_gross_distribution(self):
        for record in self:
            record.gross_distribution = record.gross_profit - record.cost_distribution

    @api.depends('revenue', 'gross_profit')
    def _compute_gross_distribution_percentage(self):
        for record in self:
            if record.revenue:
                record.gross_distribution_percentage = (record.gross_distribution / record.revenue) * 100
            else:
                record.gross_distribution_percentage = 0

            # Cost of Selling

    @api.depends('selling', 'cost_sale', 'other_income')
    def _compute_cost_selling(self):
        for record in self:
            record.cost_selling = record.selling

    @api.depends('revenue', 'cost_selling')
    def _compute_cost_selling_percentage(self):
        for record in self:
            if record.revenue:
                record.cost_selling_percentage = (record.cost_selling / record.revenue) * 100
            else:
                record.cost_selling_percentage = 0

    # Gross profit of Selling
    @api.depends('gross_distribution', 'cost_selling')
    def _compute_gross_selling(self):
        for record in self:
            record.gross_selling = record.gross_distribution - record.cost_selling

    @api.depends('revenue', 'gross_selling')
    def _compute_gross_selling_percentage(self):
        for record in self:
            if record.revenue:
                record.gross_selling_percentage = (record.gross_selling / record.revenue) * 100
            else:
                record.gross_selling_percentage = 0

        # Net Profit

    @api.depends('ebt', 'taxation','expense_amount')
    def _compute_net_profit(self):
        for record in self:
            record.net_profit = record.ebt - record.taxation
            record.net_profit = record.expense_amount

    @api.depends('revenue', 'net_profit', 'expense_amount')
    def _compute_net_profit_percentage(self):
        for record in self:
            if record.revenue:
                record.net_profit_percentage = (record.net_profit / record.revenue) * 100
                record.net_profit_percentage = (record.expense_amount / record.revenue) * 100
            else:
                record.net_profit_percentage = 0

    # Costs of Sale Percentage
    @api.depends('revenue', 'cost_sale')
    def _compute_cost_sale_percentage(self):
        for record in self:
            if record.revenue:
                record.cost_sale_percentage = (record.cost_sale / record.revenue) * 100
            else:
                record.cost_sale_percentage = 0

    @api.depends('revenue', 'other_income')
    def _compute_other_income_percentage(self):
        for record in self:
            if record.revenue:
                record.other_income_percentage = (record.other_income / record.revenue) * 100
            else:
                record.other_income_percentage = 0

    @api.depends('from_date', 'to_date', 'company_id')
    def _compute_total_expense(self):
        for record in self:
            record.total_expense = record.calculate_total_expense()

    # Product Purchase Percentage
    @api.depends('revenue', 'total_products_purchase')
    def _compute_pro_purchase_percentage(self):
        for record in self:
            if record.revenue:
                record.pro_purchase_percentage = (record.total_products_purchase / record.revenue) * 100
            else:
                record.pro_purchase_percentage = 0

    def calculate_total_expense(self):
        self.ensure_one()
        from_date_str = self.from_date.strftime('%Y-%m-%d') if self.from_date else False
        to_date_str = self.to_date.strftime('%Y-%m-%d') if self.to_date else False

        if from_date_str and to_date_str:
            query = """
                SELECT COALESCE(SUM(a.total_expense_amount), 0)
                    FROM waaneiza_exp_sett a JOIN waaneiza_exp_info b
                    ON a.id=b.expense_id JOIN hr_employee c 
                    ON b.process_id=c.id
                    WHERE date >= %s AND date <= %s
                        AND a.company_id = %s
                        AND c.process_code LIKE %s
                        AND a.state LIKE %s
                   
            """
            params = (from_date_str, to_date_str, self.company_id.id, '%WWHICT001%', '%done%')

            self.env.cr.execute(query, params)
            result = self.env.cr.fetchone()
            return result[0] if result else 0
        else:
            return 0

    @api.depends('from_date', 'to_date', 'company_id')
    def _compute_total_inbound(self):
        for record in self:
            record.total_inbound = record.calculate_total_inbound()

        # Inbound Percentage

    @api.depends('revenue', 'total_inbound')
    def _compute_inbound_percentage(self):
        for record in self:
            if record.revenue:
                record.inbound_percentage = (record.total_inbound / record.revenue) * 100
            else:
                record.inbound_percentage = 0

    def calculate_total_inbound(self):
        self.ensure_one()
        from_date_str = self.from_date.strftime('%Y-%m-%d') if self.from_date else False
        to_date_str = self.to_date.strftime('%Y-%m-%d') if self.to_date else False

        if from_date_str and to_date_str:
            query = """
                SELECT COALESCE(SUM(a.total_expense_amount), 0)
                    FROM waaneiza_exp_sett a JOIN waaneiza_exp_info b
                    ON a.id=b.expense_id JOIN hr_employee c 
                    ON b.process_id=c.id
                    WHERE date >= %s AND date <= %s
                        AND a.company_id = %s
                        AND a.state LIKE %s
                        AND c.process_code LIKE %s

            """
            params = (from_date_str, to_date_str, self.company_id.id, '%done%', '%JO1234%')

            self.env.cr.execute(query, params)
            result = self.env.cr.fetchone()
            return result[0] if result else 0
        else:
            return 0

    @api.depends('from_date', 'to_date', 'company_id')
    def _compute_total_products_purchase(self):
        for record in self:
            record.total_products_purchase = record.calculate_total_products_purchase()

    def calculate_total_products_purchase(self):
        self.ensure_one()
        from_date_str = self.from_date.strftime('%Y-%m-%d') if self.from_date else False
        to_date_str = self.to_date.strftime('%Y-%m-%d') if self.to_date else False

        if from_date_str and to_date_str:
            query = """
                    SELECT COALESCE(SUM(a.total_expense_amount), 0)
                    FROM waaneiza_exp_sett a JOIN waaneiza_exp_info b
                    ON a.id=b.expense_id JOIN waaneiza_exp_acc_code c 
                    ON b.account_code=c.id
                    WHERE date >= %s AND date <= %s
                        AND a.company_id = %s
                        AND c.name LIKE %s

                """
            params = (from_date_str, to_date_str, self.company_id.id, '%EMC001%')

            self.env.cr.execute(query, params)
            result = self.env.cr.fetchone()
            return result[0] if result else 0
        else:
            return 0

    @api.depends('from_date', 'to_date', 'company_id')
    def _compute_total_raw_products(self):
        for record in self:
            record.total_raw_products = record.calculate_total_raw_products()

    def calculate_total_raw_products(self):
        self.ensure_one()
        from_date_str = self.from_date.strftime('%Y-%m-%d') if self.from_date else False
        to_date_str = self.to_date.strftime('%Y-%m-%d') if self.to_date else False

        if from_date_str and to_date_str:
            query = """
                    SELECT COALESCE(SUM(a.total_expense_amount), 0)
                    FROM waaneiza_exp_sett a JOIN waaneiza_exp_info b
                    ON a.id=b.expense_id JOIN hr_employee c 
                    ON b.process_id=c.id
                    WHERE date >= %s AND date <= %s
                        AND a.company_id = %s
                        AND c.process_code LIKE %s

                """
            params = (from_date_str, to_date_str, self.company_id.id, '%EO124%')

            self.env.cr.execute(query, params)
            result = self.env.cr.fetchone()
            return result[0] if result else 0
        else:
            return 0

    @api.depends('revenue', 'total_raw_products')
    def _compute_raw_products_percentage(self):
        for record in self:
            if record.revenue:
                record.raw_products_percentage = (record.total_raw_products / record.revenue) * 100
            else:
                record.raw_products_percentage = 0

    @api.depends('from_date', 'to_date', 'company_id')
    def _compute_admin(self):
        for record in self:
            record.total_admin = record.calculate_admin()

        # Administration Percentage

    @api.depends('revenue', 'total_admin')
    def _compute_admin_percentage(self):
        for record in self:
            if record.revenue:
                record.admin_percentage = (record.total_admin / record.revenue) * 100
            else:
                record.admin_percentage = 0

    def calculate_admin(self):
        self.ensure_one()
        from_date_str = self.from_date.strftime('%Y-%m-%d') if self.from_date else False
        to_date_str = self.to_date.strftime('%Y-%m-%d') if self.to_date else False

        if from_date_str and to_date_str:
            query = """
                SELECT COALESCE(SUM(a.total_expense_amount), 0)
                    FROM waaneiza_exp_sett a JOIN waaneiza_exp_info b
                    ON a.id=b.expense_id JOIN hr_employee c 
                    ON b.process_id=c.id
                    WHERE date >= %s AND date <= %s
                        AND a.company_id = %s
                        AND a.state LIKE %s
                        AND c.process_code LIKE %s

            """
            params = (from_date_str, to_date_str, self.company_id.id, '%done%', '%WWHADM001%')

            self.env.cr.execute(query, params)
            result = self.env.cr.fetchone()
            return result[0] if result else 0
        else:
            return 0

    # D&D Pormotion Calculation
    @api.depends('from_date', 'to_date', 'company_id')
    def _compute_dd_promotion(self):
        for record in self:
            record.total_dd_promotion = record.calculate_dd_promotion()

        # D &D promotion Percentage

    @api.depends('revenue', 'total_dd_promotion')
    def _compute_dd_promotion_percentage(self):
        for record in self:
            if record.revenue:
                record.dd_promotion_percentage = (record.total_dd_promotion / record.revenue) * 100
            else:
                record.dd_promotion_percentage = 0

    def calculate_dd_promotion(self):
        self.ensure_one()
        from_date_str = self.from_date.strftime('%Y-%m-%d') if self.from_date else False
        to_date_str = self.to_date.strftime('%Y-%m-%d') if self.to_date else False

        if from_date_str and to_date_str:
            query = """
                SELECT COALESCE(SUM(a.total_expense_amount), 0)
                    FROM waaneiza_exp_sett a JOIN waaneiza_exp_info b
                    ON a.id=b.expense_id JOIN hr_employee c 
                    ON b.process_id=c.id
                    WHERE date >= %s AND date <= %s
                        AND a.company_id = %s
                        AND a.state LIKE %s
                        AND c.process_code LIKE %s

            """
            params = (from_date_str, to_date_str, self.company_id.id, '%done%', '%EO%')

            self.env.cr.execute(query, params)
            result = self.env.cr.fetchone()
            return result[0] if result else 0
        else:
            return 0

    # A&G Expemse
    @api.depends('total_admin', 'total_dd_promotion', 'other_income')
    def _compute_ag_expense(self):
        for record in self:
            record.ag_expense = record.total_admin + record.total_dd_promotion

    @api.depends('revenue', 'ag_expense')
    def _compute_ag_expense_percentage(self):
        for record in self:
            if record.revenue:
                record.ag_expense_percentage = (record.ag_expense / record.revenue) * 100
            else:
                record.ag_expense_percentage = 0

    # EBIT
    @api.depends('gross_selling', 'ag_expense')
    def _compute_ebit(self):
        for record in self:
            record.ebit = record.gross_selling - record.ag_expense

    @api.depends('revenue', 'ebit')
    def _compute_ebit_percentage(self):
        for record in self:
            if record.revenue:
                record.ebit_percentage = (record.ebit / record.revenue) * 100
            else:
                record.ebit_percentage = 0

    # EBT
    @api.depends('ebit', 'interest')
    def _compute_ebt(self):
        for record in self:
            record.ebt = record.ebit - record.interest

    @api.depends('revenue', 'ebt')
    def _compute_ebt_percentage(self):
        for record in self:
            if record.revenue:
                record.ebt_percentage = (record.ebt / record.revenue) * 100
            else:
                record.ebt_percentage = 0
