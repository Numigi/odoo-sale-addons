import pytest
from odoo.tests.common import TransactionCase

@pytest.mark.usefixtures("env")
class TestCrmTeam(TransactionCase):

    def test_emails_compute__should_return_member_emails(self):
        user = self.env['res.users'].create({
            'name': 'Anas OUASMI',
            'login': 'ouasmianas@gmail.com',
            'email': 'ouasmianas@gmail.com',
        })
        team = self.env['crm.team'].create({
            'name': 'Équipe Tests',
            'member_ids': [(6, 0, [user.id])],
        })
        assert 'ouasmianas@gmail.com' in team.emails, "Le champ 'emails' ne contient pas l’adresse du membre"

    def test_user_id_added_to_members__on_create(self):
        user = self.env['res.users'].create({
            'name': 'Abdellatif Benzbiria',
            'login': 'abdellatif.benzbiria@numigi.com',
            'email': 'abdellatif.benzbiria@numigi.com',
        })
        team = self.env['crm.team'].create({'name': 'Team Manager', 'user_id': user.id})
        assert user in team.member_ids, "Le responsable d’équipe n’a pas été ajouté aux membres à la création"

    def test_user_id_added_to_members__on_write(self):
        team = self.env['crm.team'].create({'name': 'Team Change'})
        user = self.env['res.users'].create({
            'name': 'User 2',
            'login': 'user2@numigi.com',
            'email': 'user2@numigi.com',
        })
        team.write({'user_id': user.id})
        assert user in team.member_ids, "Le responsable d’équipe n’a pas été ajouté aux membres après modification"
