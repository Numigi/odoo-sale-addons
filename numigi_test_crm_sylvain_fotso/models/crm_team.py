from  odoo import models, fields, api


class CrmTeam(models.Model):
    _inherit = 'crm.team'
        
    x_members_emails= fields.Char(
        string="Email des membres",
        compute='_compute_members_emails', 
        store=True
        )


    @api.depends('member_ids', 'member_ids.email')
    def _compute_members_emails(self):
        for team in self:
            emails= [m.email for m in team.member_ids if m.email]
            team.x_members_emails=','.join(emails) if emails else ""
    
    @api.onchange('user_id')
    def add_leader_to_members(self):
        if self.user_id and self.user_id not in self.member_ids:
            self.member_ids =[(4, self.user_id.id)]


