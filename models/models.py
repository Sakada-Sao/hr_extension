# -*- coding: utf-8 -*-

import logging

from openerp import models, fields, api

_logging = logging.getLogger(__name__)

# class hr_extension(models.Model):
#     _name = 'hr.employee'
#     _inherit = 'hr.employee'
#
#     history = fields.Char(string="History", required=False, )
#     work_date = fields.Date(string="Working Starting Date", required=False, )

class hr_payslip_extend(models.Model):
    _name = 'hr.payslip'
    _inherit = 'hr.payslip'

    # hr_payslip_worked_days
    def get_work_day(self, cr, uid, ids, context=None):
        emp_id = ''
        worked_hours = 0.0
        worked_days = self.pool.get('hr.payslip.worked_days')
        contract_id = ''
        payslip_id = ''
        state = ""

        for payslip in self.browse(cr, uid, ids, context=context):
            contract_id = payslip.contract_id
            payslip_id = payslip.id
            state = payslip.state

            if payslip.employee_id:
                for emp_id in payslip.employee_id:
                    emp_id = emp_id.id
            if payslip.contract_id:
                for contract in payslip.contract_id:
                    contract_id = contract.id

        cr.execute('select * from hr_attendance where employee_id=%s and name>=%s and name <= %s and action=%s', (emp_id, payslip.date_from, payslip.date_to, 'sign_out'))

        attendances = cr.dictfetchall()
        for attendance in attendances:
            worked_hours = worked_hours + attendance['worked_hours']


        if state != 'done':
            cr.execute("delete from hr_payslip_worked_days where code = 'actual_work'")
            worked_days.create(cr, uid, {
                'code': 'actual_work',
                'contract_id': contract_id,
                'payslip_id': payslip_id,
                'number_of_days':  worked_hours / 24,
                'number_of_hours': worked_hours,
                'name': 'name',
                'sequence': 10,
                }, context=context)

        return True

class hr_contract_extension(models.Model):
    _name = 'hr.contract'
    _inherit = 'hr.contract'

    @api.depends('spouse', 'minor_child')
    def _cal_child_allowance(self):
        # _logging.warn("----------------------------------------------> " + str(self.wage))
        result = (self.spouse + self.minor_child) * 75000
        for record in self:
            record.calculate_child_allowance = result

    @api.depends('wage')
    def _cal_basic_dollar(self):
        result = self.wage
        for record in self:
            record.calculate_basic_dollar = result

    @api.depends('wage')
    def _cal_basic_riel(self):

        result = self.wage * 4063
        for record in self:
            record.calculate_basic_riel = result

    @api.depends('calculate_basic_riel', 'calculate_child_allowance')
    def _cal_salary_tax(self):

        result = self.calculate_basic_riel - self.calculate_child_allowance
        for record in self:
            record.calculate_salary_tax = result

    @api.depends('calculate_basic_riel', 'calculate_child_allowance')
    def _cal_tax_in_riel(self):

        # calculate = 0
        result = self.calculate_basic_riel - self.calculate_child_allowance
        if result < 500000:
            calculate = result * 0
        elif result <= 1250000:
            calculate = (result * 0.05) - 25000
        elif result <= 8500000:
            calculate = (result * 0.1) - 87500
        elif result <= 12500000:
            calculate = (result * 0.15) - 512500
        else:
            calculate = (result * 0.2) - 1137000

        for record in self:
            record.calculate_tax_salary_in_riel = calculate

    @api.depends('calculate_tax_salary_in_riel')
    def _cal_tax_in_dollar(self):

        result = self.calculate_tax_salary_in_riel / 4063
        for record in self:
            record.calculate_tax_salary_in_dollar = result

    @api.depends('calculate_tax_salary_in_dollar', 'calculate_basic_dollar')
    def _cal_paid_amount(self):

        result = self.calculate_basic_dollar - self.calculate_tax_salary_in_dollar
        for record in self:
            record.paid_amount = result


    def _emp_working_hour(self):
        return 0

    spouse = fields.Float(string="Spouse", required=False, )
    minor_child = fields.Float(string="Minor Children", required=False, )
    calculate_child_allowance = fields.Float("Child Allowance", compute="_cal_child_allowance", store=True,)
    calculate_basic_dollar = fields.Float("Basic in Dollar", compute="_cal_basic_dollar", store=True)
    calculate_basic_riel = fields.Float("Basic in Riel", compute="_cal_basic_riel", store=True)
    calculate_salary_tax = fields.Float("Salary Tax", compute="_cal_salary_tax", store=True)
    calculate_tax_salary_in_riel = fields.Float("Tax in Riel", compute="_cal_tax_in_riel", store=True)
    calculate_tax_salary_in_dollar = fields.Float("Tax in Dollar", compute="_cal_tax_in_dollar", store=True)
    paid_amount = fields.Float("Paid Amount", compute="_cal_paid_amount", store=True)

