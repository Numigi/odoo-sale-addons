from odoo import  api, fields, models, _
from dateutil.relativedelta import relativedelta


class CrmLead(models.Model):
    _inherit = "crm.lead"


    def notif_lead(self):
        next_date = self.create_date + relativedelta(day=10) 
        if next_date < fields.Date.context_today(self):
            msg =f"Bonjour,\nMerci de donner une suite à cette opportunité {self.name}.\n\nCordialement."
            self.message_post(body=msg, partner_ids=[rec.id for rec in self.team_id.member_ids])
