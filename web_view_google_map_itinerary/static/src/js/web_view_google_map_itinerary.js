odoo.define('web_view_google_map_itinerary.see_in_google_maps', function (require) {
"use strict";

    var MapController = require('web_google_maps.MapController');
    var rpc = require('web.rpc');

    MapController.include({
        renderButtons: function($node) {
            this._super.apply(this, arguments);
            if (this.hasButtons && this.$buttons) {
                this.$buttons.on(
                    'click',
                    'button.o-map-button-see-in-google-maps',
                    this._onButtonSeeInGoogleMaps.bind(this)
                );
            }
        },
        _onButtonSeeInGoogleMaps: async function () {
            var record = this.model.get(this.handle);
            var googleMapUri = await rpc.query({
                model: this.modelName,
                method: 'get_google_maps_itinerary_uri',
                args: [record.res_ids, []],
            });
            window.open(googleMapUri);
        },
    });

    return MapController
})
