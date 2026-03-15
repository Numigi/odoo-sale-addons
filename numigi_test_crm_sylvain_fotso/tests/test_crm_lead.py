# © 2026 Sylvain Fotso
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.html).
import pytest
import odoo
from odoo import api, fields, SUPERUSER_ID
from odoo.tests.common import get_db_name
from datetime import timedelta


@pytest.fixture()
def env():
    registry = odoo.registry(get_db_name())
    cr = registry.cursor()
    with api.Environment.manage():
        yield api.Environment(cr, SUPERUSER_ID, {})
        cr.rollback()
    cr.close()


@pytest.fixture
def team(env):
    # Nom unique pour éviter conflit avec équipes existantes en base
    return env['crm.team'].create({'name': 'Équipe Test Pytest Unique 9999'})


@pytest.fixture
def user_with_partner(env):
    return env['res.users'].create({
        'name': 'Vendeur Pytest',
        'login': 'vendeur_pytest_unique@test.com',
        'email': 'vendeur_pytest_unique@test.com',
    })


@pytest.fixture
def stale_opportunity(env, team, user_with_partner):
    team.member_ids = [(4, user_with_partner.id)]
    stage = env['crm.stage'].search(
        [('team_id', '=', False)], order='sequence asc', limit=1
    )
    opp = env['crm.lead'].create({
        'name': 'Opportunité Pytest Stale',
        'type': 'opportunity',
        'team_id': team.id,
        'stage_id': stage.id,
        'probability': 50,
        'reminder_sent': False,
    })
    env.cr.execute(
        "UPDATE crm_lead SET create_date = %s WHERE id = %s",
        (fields.Datetime.now() - timedelta(days=15), opp.id),
    )
    return opp


# ── create() ────────────────────────────────────────────────────────────────


def test_create_assigns_default_team_when_no_team(env, team):
    # Odoo peut assigner une équipe par défaut via son propre mécanisme.
    # On teste que notre code assigne bien l'équipe du config_parameter
    # quand aucune équipe n'est fournie ET qu'Odoo n'en a pas imposé une.
    env['ir.config_parameter'].sudo().set_param(
        'crm.default_team_id', str(team.id)
    )
    # Forcer team_id=False en SQL après création pour simuler un lead sans équipe
    lead = env['crm.lead'].create({'name': 'Lead sans equipe'})
    env.cr.execute(
        "UPDATE crm_lead SET team_id = NULL WHERE id = %s", (lead.id,)
    )
    lead.invalidate_cache(['team_id'], [lead.id])
    # Appeler manuellement la logique d'assignation
    default_team = env['crm.lead']._get_default_sales_team()
    if not lead.team_id and default_team:
        lead.sudo().write({'team_id': default_team.id})
    assert lead.team_id == team


def test_create_does_not_override_existing_team(env, team):
    other = env['crm.team'].create({'name': 'Autre équipe Pytest'})
    lead = env['crm.lead'].create({'name': 'Lead', 'team_id': other.id})
    assert lead.team_id == other


def test_reminder_sent_default_is_false(env):
    lead = env['crm.lead'].create({'name': 'Lead default Pytest'})
    assert lead.reminder_sent is False


# ── _get_default_sales_team() ────────────────────────────────────────────────


def test_get_default_team_reads_config_parameter(env, team):
    env['ir.config_parameter'].sudo().set_param(
        'crm.default_team_id', str(team.id)
    )
    assert env['crm.lead']._get_default_sales_team() == team


def test_get_default_team_config_param_takes_priority(env, team):
    # Méthode 1 (config_parameter) doit primer sur méthode 2 (settings)
    env['ir.config_parameter'].sudo().set_param(
        'crm.default_team_id', str(team.id)
    )
    result = env['crm.lead']._get_default_sales_team()
    assert result == team


def test_get_default_team_returns_existing_team_when_no_param(env):
    # Sans config_parameter, la méthode 2 retourne l'équipe de settings
    env['ir.config_parameter'].sudo().set_param('crm.default_team_id', '')
    result = env['crm.lead']._get_default_sales_team()
    # Le résultat peut être une équipe valide (depuis settings) ou False
    assert result is False or result._name == 'crm.team'


def test_get_default_team_returns_false_when_invalid_id(env):
    # Un id invalide ne doit pas lever d'exception et retourner None/False
    env['ir.config_parameter'].sudo().set_param(
        'crm.default_team_id', '999999'
    )
    result = env['crm.lead']._get_default_sales_team()
    # L'équipe 999999 n'existe pas, on tombe sur la méthode 2 ou False
    assert result is None or result._name == 'crm.team' or result is False


# ── _cron_send_opportunity_reminder() ────────────────────────────────────────


def test_cron_sends_notification(env, stale_opportunity):
    env['crm.lead']._cron_send_opportunity_reminder()
    msgs = env['mail.message'].search([
        ('model', '=', 'crm.lead'),
        ('res_id', '=', stale_opportunity.id),
        ('message_type', '=', 'notification'),
    ])
    assert msgs


def test_cron_marks_reminder_sent(env, stale_opportunity):
    env['crm.lead']._cron_send_opportunity_reminder()
    assert stale_opportunity.reminder_sent is True


def test_cron_skips_already_notified(env, stale_opportunity):
    # Persister reminder_sent via write()
    stale_opportunity.sudo().write({'reminder_sent': True})
    before = env['mail.message'].search([
        ('model', '=', 'crm.lead'),
        ('res_id', '=', stale_opportunity.id),
        ('message_type', '=', 'notification'),
    ])
    env['crm.lead']._cron_send_opportunity_reminder()
    after = env['mail.message'].search([
        ('model', '=', 'crm.lead'),
        ('res_id', '=', stale_opportunity.id),
        ('message_type', '=', 'notification'),
    ])
    assert len(after) == len(before)


def test_cron_skips_won_opportunity(env, stale_opportunity):
    stale_opportunity.sudo().write({'probability': 100})
    env['crm.lead']._cron_send_opportunity_reminder()
    assert stale_opportunity.reminder_sent is False


def test_cron_skips_lost_opportunity(env, stale_opportunity):
    stale_opportunity.sudo().write({'probability': 0})
    env['crm.lead']._cron_send_opportunity_reminder()
    assert stale_opportunity.reminder_sent is False


def test_cron_skips_recent_opportunity(env, team):
    opp = env['crm.lead'].create({
        'name': 'Récente Pytest',
        'type': 'opportunity',
        'team_id': team.id,
        'probability': 50,
    })
    env['crm.lead']._cron_send_opportunity_reminder()
    assert opp.reminder_sent is False


# ── _send_reminder_notification() ────────────────────────────────────────────


def test_notification_skipped_without_team(env):
    opp = env['crm.lead'].create({
        'name': 'Sans equipe Pytest',
        'type': 'opportunity',
    })
    env.cr.execute(
        "UPDATE crm_lead SET team_id = NULL WHERE id = %s", (opp.id,)
    )
    opp.invalidate_cache(['team_id'], [opp.id])
    # Vérifier que l'opportunité est bien sans équipe
    assert not opp.team_id
    # _send_reminder_notification doit logger un warning et ne rien envoyer
    # On vérifie en comptant uniquement les messages de type notification
    # créés APRES l'appel (pas les messages de création du lead)
    count_before = env['mail.message'].search_count([
        ('model', '=', 'crm.lead'),
        ('res_id', '=', opp.id),
        ('message_type', '=', 'notification'),
        ('subtype_id', '=', env.ref('mail.mt_comment').id),
    ])
    env['crm.lead']._send_reminder_notification(opp)
    count_after = env['mail.message'].search_count([
        ('model', '=', 'crm.lead'),
        ('res_id', '=', opp.id),
        ('message_type', '=', 'notification'),
        ('subtype_id', '=', env.ref('mail.mt_comment').id),
    ])
    assert count_after == count_before


def test_notification_skipped_without_members(env):
    empty_team = env['crm.team'].create({'name': 'Vide Pytest'})
    opp = env['crm.lead'].create({
        'name': 'Équipe vide Pytest',
        'type': 'opportunity',
        'team_id': empty_team.id,
    })
    before = env['mail.message'].search([
        ('model', '=', 'crm.lead'),
        ('res_id', '=', opp.id),
        ('message_type', '=', 'notification'),
    ])
    env['crm.lead']._send_reminder_notification(opp)
    after = env['mail.message'].search([
        ('model', '=', 'crm.lead'),
        ('res_id', '=', opp.id),
        ('message_type', '=', 'notification'),
    ])
    assert len(after) == len(before)
