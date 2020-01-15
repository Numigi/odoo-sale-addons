odoo.define("sale_persistent_product_warning", function(require){

var AbstractField = require("web.AbstractField");
var core = require("web.core");
var Dialog = require("web.Dialog");
var fieldRegistry = require("web.field_registry");
var _t = core._t;

var ProductWarning = AbstractField.extend({
    className: "o_sale_persistent_product_warning",
    tagName: "span",
    description: "",
    supportedFieldTypes: ["text", "char"],

    events: _.extend({}, AbstractField.prototype.events, {
        "click": "_onClick"
    }),

    _render: function () {
        if (this.value) {
            this.$el.addClass("fa fa-exclamation");
        }
    },

    _onClick(event) {
        event.stopPropagation();
        this._openWarningDialog();
    },

    _openWarningDialog(){
        return new Dialog(this, {
            size: "medium",
            buttons: [
                this._getCloseButtonValues(),
            ],
            $content: $("<div>", {
                text: this.value,
            }),
            title: this._getWarningTitle(),
        }).open();
    },

    _getWarningTitle(){
        var productName = this._getProductDisplayName();
        return _t("Warning for {}").replace("{}", productName);
    },

    _getProductDisplayName(){
        return this.recordData.product_id.data.display_name;
    },

    _getCloseButtonValues(){
        return {
            text: _t("Ok"),
            close: true,
        };
    },
});

fieldRegistry.add("sale_persistent_product_warning", ProductWarning);

});
