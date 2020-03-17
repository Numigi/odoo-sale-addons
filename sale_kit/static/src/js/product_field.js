odoo.define("sale_kit.product_field", function(require){

const registry = require("web.field_registry")
const relationalFields = require('web.relational_fields')
const FieldMany2one = relationalFields.ListFieldMany2One;

const ProductMany2one = FieldMany2one.extend({
    _render() {
        this._super.apply(this, arguments);

        if (this._isKitComponentLine() && this._isReadonlyMode()) {
            this._addKitComponentCaret();
        }
    },

    _isReadonlyMode() {
        return this.mode === "readonly";
    },

    _isKitComponentLine() {
        return !this.recordData.is_kit && this.recordData.kit_reference;
    },

    _addKitComponentCaret() {
        const caret = $("<i></i>");
        caret.addClass("fa");
        caret.addClass("fa-caret-right");
        caret.addClass("o_sale_kit_component_caret");
        this.$el.prepend(caret);
    },
});

registry.add("sale_kit_product_many2one", ProductMany2one);

});
