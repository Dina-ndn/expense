# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class c:\odoo\odoo15\waaneiza_expense_cashier(models.Model):
#     _name = 'c:\odoo\odoo15\waaneiza_expense_cashier.c:\odoo\odoo15\waaneiza_expense_cashier'
#     _description = 'c:\odoo\odoo15\waaneiza_expense_cashier.c:\odoo\odoo15\waaneiza_expense_cashier'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
