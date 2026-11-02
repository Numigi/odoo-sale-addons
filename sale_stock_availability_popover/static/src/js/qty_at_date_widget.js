/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { QtyAtDateWidget } from "@sale_stock/widgets/qty_at_date_widget";

// Patch the standard widget to apply the custom color from the backend
patch(QtyAtDateWidget.prototype, {
    get colorClass() {
        const customColor = this.props.record.data.qty_available_color;
        if (customColor) {
            return customColor;
        }
        return super.colorClass;
    }
});