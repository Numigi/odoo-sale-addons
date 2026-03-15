# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    reminder_sent = fields.Boolean(
        string='Rappel envoyé',
        default=False,
        help='Indique si la notification de relance a déjà été envoyée.'
    )
   # ═══════════════════════════════════════════════════════════
    # CRÉATION — Assigne l'équipe de vente par défaut 
    # ══════════════════════════════════════════════════════════
   
    @api.model_create_multi
    def create(self, vals_list):
        records = super(CrmLead, self).create(vals_list)

        try:
            default_team = self._get_default_sales_team()
            leads_without_team = records.filtered(lambda r: not r.team_id)
            if default_team and leads_without_team:
                leads_without_team.sudo().write({'team_id': default_team.id})
        except Exception as e:
            _logger.error("CRM Default Team : Erreur lors de l'assignation : %s", e)

        return records

    
    @api.model
    def _get_default_sales_team(self):
        # 1. Lire depuis ir.config_parameter (clé utilisée par website_crm)
        team_id = self.env['ir.config_parameter'].sudo().get_param(
            'crm.default_team_id'
        )
        if team_id:
            team = self.env['crm.team'].sudo().browse(int(team_id))
            if team.exists():
                _logger.info("CRM Default Team : Équipe depuis config: '%s'", team.name)
                return team

        # 2. Lire depuis res.config.settings directement
        try:
            settings = self.env['res.config.settings'].sudo().create({})
            team = settings.crm_default_team_id
            settings.unlink()
            if team:
                # _logger.info("CRM Default Team : Équipe depuis settings: '%s'", team.name)
                return team
        except Exception as e:
            _logger.warning("CRM Default Team : settings échoué: %s", e)

    # ═════════════════════════════════════════════════════════════

    @api.model
    def _cron_send_opportunity_reminder(self):
        """
        Cron quotidien.
        
        """
        _logger.info("CRM Reminder : Démarrage du cron...")

        date_limit = fields.Datetime.now() - timedelta(days=10)

    
        stale_leads = self.search([
            ('type', '=', 'opportunity'),
            ('active', '=', True),
            ('probability', '!=', 100),          # exclure gagnées
            ('probability', '!=', 0),            # exclure perdues
            ('create_date', '<=', date_limit),   
            ('reminder_sent', '=', False),
        ])



        for lead in stale_leads:
            try:
                self._send_reminder_notification(lead)
                lead.sudo().write({'reminder_sent': True})
                _logger.info(
                    "CRM Reminder : ✔ Notification envoyée — '%s' (ID: %s)",
                    lead.name, lead.id
                )
            except Exception as e:
                _logger.error(
                    "CRM Reminder : ✗ Erreur pour '%s' (ID: %s) : %s",
                    lead.name, lead.id, e
                )

        _logger.info("CRM Reminder : Cron terminé.")

    def _send_reminder_notification(self, opportunity):
      
        team = opportunity.team_id
        if not team:
            _logger.warning(
                "CRM Reminder : Opportunité '%s' sans équipe, ignorée.", opportunity.name
            )
            return

    
        members = team.member_ids
        if not members:
            _logger.warning(
                "CRM Reminder : Équipe '%s' sans membres, ignorée.", team.name
            )
            return

       
        users_with_partner = members.filtered(lambda u: u.partner_id)
        if not users_with_partner:
            _logger.warning(
                "CRM Reminder : Aucun partenaire valide dans l'équipe '%s'.", team.name
            )
            return

       
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', '')
        opportunity_url = u"{}/web#id={}&model=crm.lead&view_type=form".format(
            base_url, opportunity.id
        )

        # Corps du message selon les specifications demandéees
        body = u"""
            <p>Bonjour,</p>
            <p>
                Merci de donner une suite à cette opportunité
                <a href="{url}" target="_blank">
                    <strong>{name}</strong>
                </a>.
            </p>
            <p>Cordialement.</p>
        """.format(url=opportunity_url, name=opportunity.name)

        subject = u"Relance : {} — en attente depuis plus de 10 jours".format(
            opportunity.name
        )

              
        notification_ids = [
            (0, 0, {
                'res_partner_id': user.partner_id.id,
                'notification_type': 'inbox',  # ← clé : envoie dans la boîte inbox
            })
            for user in users_with_partner
        ]

        self.env['mail.message'].sudo().create({
            'message_type': 'notification',
            'body': body,
            'subject': subject,
            'subtype_id': self.env.ref('mail.mt_comment').id,
            'model': 'crm.lead',
            'res_id': opportunity.id,
            'partner_ids': [(4, u.partner_id.id) for u in users_with_partner],
            'notification_ids': notification_ids,
            'author_id': self.env.ref('base.partner_root').id,
        })

        _logger.info(
            "CRM Reminder :  Notification inbox envoyée à %d membre(s) de '%s' pour '%s'.",
            len(users_with_partner), team.name, opportunity.name
        )
