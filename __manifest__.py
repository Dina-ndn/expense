# -*- coding: utf-8 -*-
{
    'name': "Waaneiza Expense and Cashier",

    'summary': "Waaneiza Expense and Cashier App",

    'description': """
Long description of module's purpose
    """,

    'author': "WWS",
    'website': "www.waaneiza.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','board','mrp','product', 'stock', 'resource','sale','purchase'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/activity.xml',
        'data/mail_templates.xml',
         #expense_view
        'views/waaneiza_exp_acc_code.xml',
        'views/waaneiza_exp_acc_code_sub.xml',
        'views/waaneiza_exp_norm.xml',
        'views/waaneiza_cashier_cash_req.xml',
        # 'wizard/waaneiza_exp_refuse_reason_views.xml',
        'views/waaneiza_cashier_cashdrawing_views.xml',#cashier
        'views/waaneiza_exp_sett.xml',
        'views/waaneiza_exp_return.xml',
         #cashier
        'views/cashier_cash_in_transfer_views.xml',
        'views/type_of_transfer_views.xml',
        'report/waaneiza_advance_cash_report_views.xml',
        'report/waaneiza_daily_cashin_cashbook_views.xml',
        'report/waaneiza_daily_cashout_cashbook_views.xml',
        'views/waaneiza_cashbook_dashboard_views.xml',

        #Resource
        'views/waaneiza_utilization_view.xml',
        'views/waaneiza_resource_view.xml',
        
        #expense_report,
        'report/expense_advance_report.xml',
        'report/cashier_cashdrawing_views.xml',#cashier
        'report/report_waaneiza_sett.xml',
        'report/report_waaneiza_return.xml',
        'report/expense_advance_report_sett.xml',
        'report/nom_expense_report_view.xml',
        'report/report_by_expense_code_view.xml',
        'report/exp_req_report.xml',
        'report/exp_return_report.xml',
        'report/exp_return_noti_report.xml',
        'data/sequence.xml',
        'report/opening_closing_views.xml',
        'views/cashbook_dashboard.xml',
        'report/report_cash_in_transfer_hb.xml',
        'report/report_waaneiza_requisition.xml',
        'report/report_waaneiza_cashdrawing.xml',
        'report/expense_report_for_cashier_views.xml',
        'report/expense_resource_report.xml',
        'report/utilization_expense_report.xml',
        'report/expense_resource_sett.xml',
        #FP
        'views/income_statement.xml',
        'views/financial_position_views.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

