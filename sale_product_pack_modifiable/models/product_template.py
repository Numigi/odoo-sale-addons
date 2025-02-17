# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.depends(lambda self: self._get_pack_modifiable_invisible_depends())
    def _compute_pack_modifiable_invisible(self):
        """
        The pack modifiable field should be invisible when:
            - pack details are not displayed or
            - pack component prices are not detailed or not totalized

        """
        super()._compute_pack_modifiable_invisible()
        for product in self:
            product.pack_modifiable_invisible = (
                product.pack_type != "detailed"
                or product.pack_component_price not in ["detailed", "totalized"]
            )
