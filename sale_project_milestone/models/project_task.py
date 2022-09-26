# © 2022-today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class ProjectTask(models.Model):

    _inherit = "project.task"

    def _compute_sol_ids(self, condition=False):
        domain = [('is_service', '=', True), ('is_expense', '=', False),
                  ('state', 'in', ['sale', 'done'])]
        if condition:
            domain += condition
        sale_line_ids = self.env['sale.order.line'].search(domain)
        return {'domain': {'sale_line_id': [('id', 'in', sale_line_ids.ids)]}}

    @api.onchange("milestone_id")
    def _onchange_milestone_id_set_sale_order_line(self):
        self.sale_line_id = self.milestone_id.sale_line_id \
            if self.milestone_id else False

    @api.onchange("milestone_id")
    def _onchange_domain_sale_line_id(self):
        # Compute sale_line_id domain using project's sale order
        if self.milestone_id:
            return {'domain':
                    {'sale_line_id':
                     [('milestone_id', '=', self.milestone_id.id)]}
                    }
        elif not self.milestone_id and self.project_id.sale_order_id:
            condition = [('order_id', '=', self.project_id.sale_order_id.id)]
            return self._compute_sol_ids(condition=condition)

        else:
            return self._compute_sol_ids()

    @api.onchange("project_id")
    def _onchange_project_id_domain_sale_line_id(self):
        if self.project_id.sale_order_id:
            condition = [('order_id', '=', self.project_id.sale_order_id.id)]
            return self._compute_sol_ids(condition=condition)
        else:
            return self._compute_sol_ids()
