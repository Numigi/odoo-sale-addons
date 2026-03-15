# © 2026 Sylvain Fotso
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.html).
import pytest
import odoo
from odoo import api, SUPERUSER_ID
from odoo.tests.common import get_db_name


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
    return env['crm.team'].create({'name': 'Équipe Test'})


@pytest.fixture
def user1(env):
    return env['res.users'].create({
        'name': 'Membre 1',
        'login': 'membre1@test.com',
        'email': 'membre1@test.com',
    })


@pytest.fixture
def user2(env):
    return env['res.users'].create({
        'name': 'Membre 2',
        'login': 'membre2@test.com',
        'email': 'membre2@test.com',
    })


def test_members_emails_contains_all_emails(env, team, user1, user2):
    team.member_ids = [(4, user1.id), (4, user2.id)]
    assert 'membre1@test.com' in team.x_members_emails
    assert 'membre2@test.com' in team.x_members_emails


def test_members_emails_empty_without_members(env, team):
    assert team.x_members_emails == ''


def test_members_emails_excludes_users_without_email(env, team):
    user_no_email = env['res.users'].create({
        'name': 'Sans email',
        'login': 'sans_email@test.com',
    })
    team.member_ids = [(4, user_no_email.id)]
    assert team.x_members_emails == ''


def test_members_emails_updates_after_member_removed(env, team, user1, user2):
    team.member_ids = [(4, user1.id), (4, user2.id)]
    team.member_ids = [(3, user2.id)]
    assert 'membre2@test.com' not in team.x_members_emails


def test_leader_added_to_members(env, team, user1):
    team.user_id = user1
    team.add_leader_to_members()
    assert user1 in team.member_ids


def test_leader_not_duplicated_if_already_member(env, team, user1):
    team.member_ids = [(4, user1.id)]
    team.user_id = user1
    team.add_leader_to_members()
    count = len(team.member_ids.filtered(lambda u: u.id == user1.id))
    assert count == 1


def test_no_action_when_leader_is_empty(env, team):
    initial_count = len(team.member_ids)
    team.user_id = False
    team.add_leader_to_members()
    assert len(team.member_ids) == initial_count
