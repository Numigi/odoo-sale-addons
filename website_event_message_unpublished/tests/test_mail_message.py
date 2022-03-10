# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime
from odoo.tests.common import SavepointCase


class TestMessage(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.event = cls.env["event.event"].create({
        	"name": "My Event",
            "date_begin": datetime.now(),
            "date_end": datetime.now(),
        })

    def test_message_post(self):
        message = self.event.message_post(body="Hello")
        assert not message.website_published
