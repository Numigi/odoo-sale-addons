# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import pytest
from .common import TestCommissionCase
from datetime import date
from ddt import ddt, data, unpack
from odoo.exceptions import AccessError


@ddt
class TestCommissionTeam(TestCommissionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.team_manager_user = cls._create_user(
            name="TeamManager", email="team-manager@testmail.com"
        )
        cls.team_manager_user.groups_id = cls.env.ref("commission.group_team_manager")
        cls.team_manager = cls._create_employee(user=cls.team_manager_user)

        cls.president_user = cls._create_user(
            name="President", email="president@testmail.com"
        )
        cls.president_user.groups_id = cls.env.ref("commission.group_team_manager")
        cls.president = cls._create_employee(user=cls.president_user)

        cls.team_category = cls._create_category(
            name="Manager", basis="my_team_commissions"
        )

        cls.manager_target = cls._create_target(
            employee=cls.team_manager,
            category=cls.team_category,
            target_amount=40000,
            fixed_rate=0.05,
        )
        cls.team_category.child_category_ids = cls.category

        cls.team = cls._create_team("Sales U.S.", cls.team_manager_user)
        cls.team.member_ids = cls.user
        cls.parent_team = cls._create_team("Sales North America", cls.president_user)
        cls.parent_team.member_ids = cls.team_manager_user | cls.president_user

        cls.manager_target.included_teams_ids |= cls.team
        cls.employee_target = cls._create_target(target_amount=100000, fixed_rate=0.05)

        cls.interval_rate = 0.05

    def test_compute_show_invoices(self):
        self.manager_target.set_confirmed_state()
        assert not self.manager_target.show_invoices

    def test_compute_show_child_targets(self):
        self.manager_target.set_confirmed_state()
        assert self.manager_target.show_child_targets

    def test_compute_show_child_targets__draft_state(self):
        self.manager_target.set_draft_state()
        assert not self.manager_target.show_child_targets

    def test_view_child_targets(self):
        self.manager_target.child_target_ids = self.employee_target
        action = self.manager_target.view_child_targets()
        domain = action["domain"]
        targets = self.env["commission.target"].search(domain)
        assert targets == self.employee_target

    def test_child_targets(self):
        child_targets = self.manager_target._get_child_targets()
        assert self.employee_target == child_targets

    def test_compute_target(self):
        self.employee_target.total_amount = 2000
        self.manager_target.compute()
        assert self.manager_target.child_target_ids == self.employee_target
        assert self.manager_target.child_commission_amount == 2000
        assert self.manager_target.base_amount == 2000

    def test_multiple_teams(self):
        new_team = self._create_team("Multi", self.team_manager_user)
        self.manager_target.included_teams_ids |= new_team

        new_user = self._create_user(name="Bob")
        new_employee = self._create_employee(user=new_user)
        new_user.sale_team_id = new_team
        new_employee_target = self._create_target(
            target_amount=100000, fixed_rate=0.05, employee=new_employee
        )

        children = self.manager_target._get_child_targets()

        assert self.employee_target in children
        assert new_employee_target in children

    def test_child_targets_wrong_department(self):
        self.employee_target.employee_id = self._create_employee()
        self._compute_manager_target()
        assert not self.manager_target.child_target_ids

    def test_child_targets_wrong_company(self):
        self.employee_target.company_id = self._create_company(name="Other Company")
        self._compute_manager_target()
        assert not self.manager_target.child_target_ids

    def test_child_targets_date_out_of_range(self):
        wrong_date_range = self._create_date_range(
            "Q3", date(2020, 8, 17), date(2020, 11, 17)
        )

        self.employee_target.date_range_id = wrong_date_range

        child_targets = self.manager_target._get_child_targets()
        assert not child_targets

    def test_manager_total_fixed(self):
        self.employee_target.total_amount = 400000 * 0.05
        self._compute_manager_target()
        assert (
            self.manager_target.total_amount
            == 400000 * self.employee_target.fixed_rate * self.manager_target.fixed_rate
        )

    @data(
        (0, 0, 100),
        (0, 0.5, 100),  # 50% of 2k == 1k <= 1k
        (0.3, 0.7, 50),  # (1k - 0.6k) / (1.4k - 0.6k)
        (1, 1, 0),
    )
    @unpack
    def test_manager_completion_interval(self, slice_from, slice_to, completion):
        rate = self._create_target_rate(self.manager_target, slice_from, slice_to)
        self.team_category.rate_type = "interval"
        self.employee_target.total_amount = 400000 * 0.05
        self._compute_manager_target()
        assert rate.completion_rate == completion

    @data(
        (0, 0, 0),
        (0, 0.5, 1000),  # 50% of 2k = 1k
        (0.3, 0.7, 400),  # 50% of 800 = 400
        (0.5, 1, 0),  # 50% of 0 = 0
        (1, 1, 0),
    )
    @unpack
    def test_manager_subtotal_interval(self, slice_from, slice_to, subtotal):
        rate = self._create_target_rate(
            self.manager_target,
            slice_from,
            slice_to,
            self.interval_rate,
        )
        self.team_category.rate_type = "interval"
        self.employee_target.total_amount = 400000 * 0.05
        self._compute_manager_target()
        assert rate.subtotal == subtotal

    def test_sorted_by_dependency(self):
        rset = (
            self.manager_target | self.employee_target
        )._sorted_by_category_dependency()
        assert rset[0] == self.employee_target
        assert rset[1] == self.manager_target

    def test_no_child_categories(self):
        self.team_category.child_category_ids = None
        self.employee_target.total_amount = 400000 * 0.05
        self._compute_manager_target()
        assert self.manager_target.total_amount == 0

    def test_new_team_category_spreads_rates(self):
        new_category = self.env["commission.category"].create(
            {
                "name": "New",
                "rate_type": "interval",
                "basis": "my_sales",
            }
        )
        first_rate = self._create_category_rate(new_category, 0, 50, self.interval_rate)
        second_rate = self._create_category_rate(
            new_category, 50, 100, self.interval_rate * 2
        )
        rates = first_rate | second_rate

        self.employee_target.category_id = new_category
        self.employee_target.onchange_category_id()

        assert rates.mapped("slice_from") == self.employee_target.rate_ids.mapped(
            "slice_from"
        )
        assert rates.mapped("slice_to") == self.employee_target.rate_ids.mapped(
            "slice_to"
        )
        assert rates.mapped(
            "commission_percentage"
        ) == self.employee_target.rate_ids.mapped("commission_percentage")

    def test_target_access_domain(self):
        targets = self._search_manager_targets()
        assert targets == self.employee_target | self.manager_target

    def test_access__own_target(self):
        self.manager_target.sudo(self.team_manager_user).check_extended_security_all()

    def test_access__not_own_target(self):
        self.manager_target.employee_id = self._create_employee()
        with pytest.raises(AccessError):
            self.manager_target.sudo(self.team_manager_user).check_extended_security_all()

    def test_access__target_of_employee_in_own_team(self):
        self.employee_target.sudo(self.team_manager_user).check_extended_security_all()

    def test_access__target_of_employee_in_child_team(self):
        self.employee_target.sudo(self.president_user).check_extended_security_all()

    def test_access__target_of_employee_not_in_own_team(self):
        self.team.user_id = self._create_employee().user_id
        with pytest.raises(AccessError):
            self.employee_target.sudo(self.team_manager_user).check_extended_security_all()

    def _compute_manager_target(self):
        self.manager_target.sudo(self.manager_user).compute()

    def _compute_employee_target(self):
        self.employee_target.sudo(self.manager_user).compute()

    def _search_manager_targets(self):
        domain = (
            self.env["commission.target"]
            .sudo(self.team_manager_user)
            .get_extended_security_domain()
        )
        return self.env["commission.target"].search(domain)
