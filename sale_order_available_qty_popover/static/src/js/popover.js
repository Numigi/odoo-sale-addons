odoo.define("sale_order_available_qty_popover", function(require){

const AbstractField = require("web.AbstractField")
const core = require("web.core")
const Dialog = require("web.Dialog")
const registry = require("web.field_registry")
const _t = core._t
const QWeb = core.qweb

const Popover = AbstractField.extend({
    supportedFieldTypes: ["float"],
    template: "SaleOrderAvailableQtyPopover",
    description: "",

    events: _.extend({}, AbstractField.prototype.events, {
        "click .fa-info-circle": "_onClick",
    }),

    _render() {
        this._super.apply(this, arguments)
        this._prepareOrHidePopover();
    },

    _reset() {
        this._super.apply(this, arguments)
        this.$("[data-toggle=\"popover\"]").popover('dispose');
        this.renderElement();
        this._prepareOrHidePopover();
    },

    _prepareOrHidePopover() {
        if (this._shouldDisplayWidget()) {
            this._setPopover();
            this._setIconColor();
        }
        else {
            this._hideWidget();
        }
    },

    _hideWidget() {
        this.$el.addClass("d-none");
    },

    _onClick(event) {
        this.$el.find(".fa-info-circle").prop("special_click", true)
    },

    isSet() {
        return this._shouldDisplayWidget()
    },

    _shouldDisplayWidget() {
        const productType = this.record.data.product_type
        return productType === "product"
    },

    _setPopover() {
        const $content = $(QWeb.render("SaleOrderAvailableQtyPopoverDetails", {
            qty: this.value,
            uom: this._getUomDisplayName(),
        }))
        const $qty = $content.find(".o_sale_order_available_qty_popover__qty")
        $qty.on("click", event => {
            event.preventDefault()
            this._onQuantityClick()
        })
        const $button = this.$("[data-toggle=\"popover\"]")
        $button.popover({
            content: $content,
            html: true,
            placement: "left",
            title: _t("Availability"),
            trigger: "manual",
            animation: false,
        })
        openPopoverOnHover($button)
    },

    _onQuantityClick() {
        this.$("[data-toggle=\"popover\"]").popover("hide")
        this.do_action({
            res_model: "stock.quant",
            name: _t("Available Quantity"),
            views: [[false, "list"], [false, "form"]],
            type: "ir.actions.act_window",
            domain: [
                ["product_id", "=", this._getProductId()],
                ["location_id.company_id", "=", odoo.session_info.company_id],
                ["location_id.usage", "in", ["internal", "transit"]],
            ],
        })
    },

    _getProductId() {
        const product = this.record.data.product_id;
        return product ? product.data.id : null;
    },

    _getUomDisplayName() {
        const uom = this.record.data.product_default_uom;
        return uom ? uom.data.display_name : null;
    },

    _setIconColor() {
        const color = this.record.data.available_qty_popover_color
        this.$el.find('i.fa-info-circle').css('color', color)
    },
})

/**
 * Make the popover open on mouse over.
 *
 * Bootstrap-popover come with an option trigger="hover".
 * However, this option has limitations.
 * When overring the box, it disapears.
 *
 * A better implementation can be found here:
 * https://embed.plnkr.co/plunk/K6WPaM
 */
function openPopoverOnHover($el) {
    $el.on("mouseenter", () => {
        $el.popover("show")
        $(".popover").on("mouseleave", () => {
            $el.popover("hide")
        })
    })
    $el.on("mouseleave", () => {
        setTimeout(() => {
            if (!$(".popover:hover").length) {
                $el.popover("hide")
            }
        }, 300)
    })
}

registry.add("sale_order_available_qty_popover", Popover)

})
