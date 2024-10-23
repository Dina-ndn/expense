# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class WaaneizaExpRefuseWizard(models.TransientModel):
    """This wizard can be launched from an he.expense (an expense line)
    or from an hr.expense.sheet (En expense report)
    'hr_expense_refuse_model' must be passed in the context to differentiate
    the right model to use.
    """

    _name = "waaneiza.exp.refuse.wizard"
    _description = "Expense Refuse Reason Wizard"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    reason = fields.Char(string='Reason', required=True, tracking=True)
    hr_expense_ids = fields.Many2many('waaneiza.cashier.cash.req')
    # hr_expense_sheet_id = fields.Many2one('hr.expense.sheet')

    @api.model
    def default_get(self, fields):
        res = super(WaaneizaExpRefuseWizard, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])
        refuse_model = self.env.context.get('waaneiza_exp_refuse_model')
        if refuse_model == 'waaneiza.cashier.cash.req':
            res.update({
                'hr_expense_ids': active_ids,
                # 'hr_expense_sheet_id': False,
            })
        elif refuse_model == 'waaneiza.cashier.cash.req':
            res.update({
                'hr_expense_ids': active_ids[0] if active_ids else False,
                'hr_expense_ids': [],
            })
        return res

    def expense_refuse_reason(self):
        self.ensure_one()
        if self.hr_expense_ids:
            self.hr_expense_ids.refuse_expense(self.reason)
        # if self.hr_expense_sheet_id:
        #     self.hr_expense_sheet_id.refuse_sheet(self.reason)

        return {'type': 'ir.actions.act_window_close'}
