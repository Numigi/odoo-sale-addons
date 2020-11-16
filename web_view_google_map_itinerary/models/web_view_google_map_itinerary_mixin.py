from odoo import api, models


class WebViewGoogleMapItinerary(models.AbstractModel):
    _name = "web.view.google.map.itinerary.mixin"
    _description = "Web View Google Map Itinerary Mixin"

    @api.multi
    def get_google_maps_itinerary_uri(self):
        if not self:
            return ""
        url = "https://www.google.com/maps/dir/"
        query = "?api=1&waypoints="
        lat_field = self.get_lat_long_field_map().get(self._name, {}).get("lat")
        long_field = self.get_lat_long_field_map().get(self._name, {}).get("long")
        available_records = self.filtered(lambda r: r[lat_field] or r[long_field])
        query += "|".join(
            [
                ",".join([str(r[lat_field]), str(r[long_field])])
                for r in available_records
            ]
        )
        return url + query

    @api.model
    def get_lat_long_field_map(self):
        return {
            "res.partner": {"lat": "partner_latitude", "long": "partner_longitude"},
            "crm.lead": {"lat": "customer_latitude", "long": "customer_longitude"},
        }
