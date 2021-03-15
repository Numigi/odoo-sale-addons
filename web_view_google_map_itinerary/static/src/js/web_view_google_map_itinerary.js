odoo.define('web_view_google_map_itinerary.see_in_google_maps', function (require) {
"use strict";

    var MapController = require('web_google_maps.MapController');
    var rpc = require('web.rpc');

    const buttonSelector = 'button.o-map-button-see-in-google-maps'

    MapController.include({
        renderButtons: function($node) {
            this._super.apply(this, arguments);
            if (this.hasButtons && this.$buttons) {
                this.$buttons.on(
                    'click',
                    buttonSelector,
                    this._onButtonSeeInGoogleMaps.bind(this)
                );
            }
        },
        _onButtonSeeInGoogleMaps: async function () {
            var url = "https://www.google.com/maps/dir/";
            var query = "?api=1&waypoints=";
            var params = [];
            var fieldLat = this.renderer.fieldLat;
            var fieldLng = this.renderer.fieldLng;
            _.each(this.renderer.state.data, function (record) {
                var lat = record.data[fieldLat];
                var lng = record.data[fieldLng];
                if (lat || lng) {
                    params.push(lat + "," + lng);
                };
            })
            query += params.join("|");
            window.open(url + query);
        },
        _update(state) {
            const result = this._super.apply(this, arguments);
            result.done(() => {
                this._updateSeeInGoogleButton(state)
            })
            return result
        },
        _updateSeeInGoogleButton(state) {
            const isGroupedView = state.groupedBy && state.groupedBy.length
            if (isGroupedView) {
                this._hideSeeInGoogleButton()
            }
            else {
                this._showSeeInGoogleButton()
            }
        },
        _hideSeeInGoogleButton() {
            this.$buttons.find(buttonSelector).hide()
        },
        _showSeeInGoogleButton() {
            this.$buttons.find(buttonSelector).show()
        },
    });

    return MapController;
})
