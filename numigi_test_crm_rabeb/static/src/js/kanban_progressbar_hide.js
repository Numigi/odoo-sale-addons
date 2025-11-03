odoo.define('numigi_test_crm_rabeb.kanban_progressbar_hide', function (require) {
    'use strict';

    var KanbanColumnProgressBar = require('web.KanbanColumnProgressBar');
    var session = require('web.session');

    KanbanColumnProgressBar.include({
        /**
         * @override
         */
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                // Vérifier que nous sommes sur le modèle crm.lead
                var parent = self.getParent();
                var modelName = parent && parent.modelName;

                // Appliquer uniquement sur crm.lead (Opportunités/Pipeline)
                if (modelName === 'crm.lead') {
                    // Masquer pour tous SAUF les Sales Managers
                    return session.user_has_group('sales_team.group_sale_manager').then(function(has_group) {
                        if (!has_group) {
                            self.$el.hide();
                        }
                    });
                }
            });
        },
    });
});