odoo.define("sale_kit.kit_reference", function(require){

const registry = require("web.field_registry");
const relationalFields = require('web.relational_fields');
const SelectionField = relationalFields.FieldSelection;

const KitReferenceField = SelectionField.extend({
    _setValues() {
        this.values = this._getAvailableKitReferences().map((ref) => [ref, ref]);
        this.values.unshift([false, ""]);
    },

    _getAvailableKitReferences() {
    	const references = this.recordData.available_kit_references;
        return references ? references.split(",") : [];
    },
});

registry.add("sale_order_kit_reference", KitReferenceField);

});
