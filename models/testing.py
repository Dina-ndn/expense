name = fields.Char(string="Sr No", readonly=True, required=True, copy=False, index=True, default=lambda self: _('New'))
    sett_id = fields.Many2one('waaneiza.exp.sett','Advance Settlement Reference')
    process_id = fields.Many2one('hr.employee','Process Name',related='sett_id.process_id')
    datetime = fields.Datetime(string="Date / Time (24 hr format)",required=True,tracking=True)
    # sett_date = fields.Date(string="s")
    process_code_employee = fields.Char(string='Process Code',related='sett_id.process_code_employee')
    department_id = fields.Many2one('hr.department', related='sett_id.department_id',string="Department")
    type_of_cashdrawing = fields.Selection([
        ('eco', 'ECO'),
    ], string='Type of Cashdrawing', default='eco', related='sett_id.type_of_cashdrawing')
    # cash_out_code = fields.Char(string="Cash Out Code",related="sett_id.cash_out_code")
    cash_out_code = fields.Many2one('waaneiza.cashier.cashdrawing',related="sett_id.cash_out_code",string="Cash Out Code")
    company_id = fields.Many2one('res.company','Company Name', compute='_get_processinfo',index=True, copy=False, store=True, readonly=False)
    reason_for_cash_return = fields.Char(string="Reason for Cash Return ",required=True)
    net_amount = fields.Float(string="Amount", related='sett_id.net_surplus')
    amount = fields.Float(string="Return Amount", compute='_get_net_amount',index=True, copy=False, store=True, readonly=False)
    currency = fields.Many2one('res.currency',string="Currency",related='sett_id.currency',readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    show_validate = fields.Boolean(
        compute='_compute_show_validate',
        help='Technical field used to decide whether the button "Validate" should be displayed.')

    return_by_name = fields.Many2one("hr.employee.information", string="Returned By", tracking=True)
    return_by_job = fields.Many2one("hr.job", string="Rank", related="return_by_name.job_id")
    staff_id_return = fields.Integer(string='Staff_ID', index=True, copy=False, store=True, readonly=False, compute='_get_employeeinfo')

    receive_by_name = fields.Many2one("hr.employee.information", string="Recevied By Name",tracking=True)
    receive_by_job = fields.Many2one("hr.job", string="Rank", related="receive_by_name.job_id")
    staff_id_receive = fields.Integer(string='Staff_ID', index=True, copy=False, store=True, readonly=False, compute='_get_staff_info')
    # sett_date = fields.Datetime(string="Settment Date",related='sett_id.date')
    # drawing_date_string = fields.Date(string="Cashdrawing Date",compute='get_drawing_date')
    sett_date = fields.Datetime(string="Settment Date",related='sett_id.sett_date')
    sett_date_string = fields.Date(string="Settment Date Date",compute='get_sett_date')

    @api.depends('net_amount')
    def _get_net_amount(self):
        for rec in self:
            rec.amount = abs(rec.sett_id.net_surplus)

    @api.depends('process_id')
    def _get_processinfo(self):
        for rec in self:
            rec.company_id = rec.process_id.company_id

    @api.depends('expense_settlement_lines')
    def _compute_invoice(self):
        for order in self:
            invoices = order.mapped('expense_settlement_lines')
            order.invoice_ids = invoices
            order.invoice_count = len(invoices)

    # SrNo Sequence
    # def write(self, vals):
    #     if any(state=='done' for state in set(self.mapped('state'))):
    #         raise UserError(_("No edit in done state"))
    #     else:
    #         return super().write(vals)
            
    def unlink(self):
        for rec in self:
            if rec.state =='done':
                raise ValidationError(_("You cannot delete cash return with 'Done' State"))
        rtn = super(WaaneizaExpenseReturn,self).unlink()
        return rtn


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'waaneiza.exp.return.srn') or _('New')
            vals['name'] =  str(vals['name']) 
        result = super(WaaneizaExpenseReturn, self).create(vals)

    @api.depends('state')
    def _compute_show_validate(self):
        for expense in self:
            if expense.state == 'done':
                expense.show_validate = True
            # elif picking.state not in ('draft','confirmed'):
            #     picking.show_validate = False
            else:
                expense.show_validate = False
        
    def action_confirm(self):
        self.state = "confirm"


    def action_draft(self):
        self.state = "draft"

    def action_done(self):
        self.state = "done"

    def action_cancel(self):
        self.state = "draft"

    @api.depends('receive_by_name')
    def _get_staff_info(self):
        for rec in self:
            rec.staff_id_receive = rec.receive_by_name.id

    @api.depends('return_by_name')
    def _get_employeeinfo(self):
        for rec in self:
            rec.staff_id_return = rec.return_by_name.id


    @api.depends('state')
    def _compute_show_validate(self):
        for picking in self:
            if picking.state == 'done':
                picking.show_validate = True
            # elif picking.state not in ('draft','confirmed'):
            #     picking.show_validate = False
            else:
                picking.show_validate = False

    # @api.constrains(' drawing_date_string', 'date')
    # def _check_dates(self):
    #     if any(self.filtered(lambda overtime: overtime. drawing_date_string > overtime.date)):
    #         raise ValidationError(_("Settlement 'Date' must not be earlier than 'Drawing Date'."))

    # Get Process/Employee Information
    # @api.depends('process_id')
    # def _get_processinfo(self):
    #     for rec in self:
    #         rec.department_id = rec.process_id.department_id
    #         rec.process_code_employee = rec.process_id.process_code
    #         rec.received_by_name = rec.process_id.emp_info_ids
    #         rec.staff_id = rec.process_id.emp_info_ids.id
    #         rec.company_id = rec.process_id.company_id
    
    # Get Employee Information
    # @api.depends('paid_by_name')
    # def _get_employeeinfo(self):
    #     for rec in self:
    #         rec.staff_id_casher = rec.paid_by_name.id

    # # Number of Process for each employee
    # @api.onchange('staff_id_casher')
    # def _onchange_paid_by_name(self):
    #     self.env.cr.execute("""select process_code from hr_employee
    #                             where hr_employee.emp_info_ids=%s""" % (self.staff_id_casher))
    #     res = self.env.cr.fetchone()
    #     self.process_code_casher = res and res[0]
            
    @api.depends('sett_date')
    def get_sett_date(self):
        for rec in self:
            rec.sett_date_string=rec.sett_date.date()

    @api.constrains('sett_date', 'datetime')
    def _check_dates(self):
        if any(self.filtered(lambda overtime: overtime.sett_date > overtime.datetime)):
            raise ValidationError(_(" 'Return Date' must not be earlier than 'Settlement Date'."))
    
            