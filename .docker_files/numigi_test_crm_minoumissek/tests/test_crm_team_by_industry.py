# # © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# # License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# from odoo.tests import Form
# from odoo.tests.common import SavepointCase


# class TestCrmTeamByIndustry(SavepointCase):
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         cls.industry = cls.env["res.partner.industry"].create({"name": "Industry"})
#         cls.default_sales_team = cls.env.ref("sales_team.team_sales_department")
#         cls.new_sale_team = cls.env["crm.team"].create({"name": "SalesTeam"})

#     def test_onchange_main_industry_without_crm_team_id(self):
#         with Form(self.env["crm.lead"]) as crm_form:
#             crm_form.name = "CRM Test"
#             assert crm_form.team_id == self.default_sales_team
#             crm_form.industry_id = self.industry
#             assert crm_form.team_id == self.default_sales_team

#     def test_onchange_main_industry_with_crm_team_id(self):
#         self.industry.crm_team_id = self.new_sale_team

#         with Form(self.env["crm.lead"]) as crm_form:
#             crm_form.name = "CRM Test"
#             assert crm_form.team_id == self.default_sales_team
#             crm_form.industry_id = self.industry
#             assert crm_form.team_id == self.new_sale_team
