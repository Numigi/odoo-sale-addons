/* Copyright 2023 Numigi
 * License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
 */
odoo.define('sale_stock.QtyAtDateWidget', function (require) {
    "use strict";

    var core = require('web.core');

    var SaleStockQtyAtDateWidget = require('sale_stock.QtyAtDateWidget');
    var widget_registry = require('web.widget_registry');

    var _t = core._t;

    var QtyAtDateWidget = SaleStockQtyAtDateWidget.extend({
        _setPopOver() {
            const $content = this._getContent();
            if (!$content) {
                return;
            }
            // please refer to https://www.w3schools.com/bootstrap/bootstrap_ref_js_popover.asp
            // DO NOT use on debug mode (conflict on hover)
            const options = {
                content: $content,
                html: true,
                placement: 'right',
                title: _t('Availability'),
                trigger: 'manual', // can take multiple values but "hover click" did click issue on "View Forecast" so manual is better
                delay: {'show': 0, 'hide': 100 },
            };
            // with trigger 'manual', define all event cases
            this.$el.popover(options).on("mouseenter", function() {
                var _this = this;
                $(this).popover("show");
                $(".popover").on("mouseleave", function() {
                    $(_this).popover('hide');
                });
                $(".action_open_forecast").on("click", function() {
                    $(_this).popover('hide');
                });
                }).on("mouseleave", function() {
                var _this = this;
                setTimeout(function() {
                    if (!$(".popover:hover").length) {
                    $(_this).popover("hide");
                    }
                }, 300);
                });
        },
    });

    widget_registry.add('qty_at_date_widget', QtyAtDateWidget);

    return QtyAtDateWidget;
    });
