# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestCommissionCase
from datetime import date
from ddt import ddt, data, unpack


@ddt
class TestCommissionTeam(TestCommissionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.manager_user = cls._create_user(
            name="Manager", email="manager@testmail.com"
        )

        cls.manager = cls._create_employee(user=cls.manager_user)

        cls.manager_category = cls._create_category(
            name="Manager", basis="my_team_commissions"
        )

        cls.manager_target = cls._create_target(
            employee=cls.manager,
            category=cls.manager_category,
            target_amount=40000,
            fixed_rate=0.05,
        )
        cls.manager_category.child_category_ids = cls.category

        cls.department = cls.env["hr.department"].create(
            {
                "name": "Dunder Mifflin",
                "manager_id": cls.manager.id,
            }
        )

        cls.employee.department_id = cls.department
        cls.employee_target = cls._create_target(target_amount=100000, fixed_rate=0.05)

        cls.interval_rate = 5

    def test_child_targets(self):
        child_targets = self.manager_target._get_child_targets()
        assert self.employee_target == child_targets

    def test_child_targets_wrong_department(self):
        foreing_user = self._create_user(name="Foreign", email="foreign@foreign.com")
        foreign_employee = self._create_employee(user=foreing_user)

        self._create_target(
            employee=foreign_employee,
            target_amount=100000,
        )

        child_targets = self.manager_target._get_child_targets()
        assert self.employee_target == child_targets

    def test_child_targets_wrong_company(self):
        company = self._create_company(name="Wrong")
        target = self._create_target(
            employee=self.employee,
            target_amount=100000
        )
        
        target.company_id = company

        child_targets = self.manager_target._get_child_targets()
        assert target not in child_targets

    def test_child_targets_date_out_of_range(self):
        wrong_date_range = self._create_date_range(
            "Q3", date(2020, 8, 17), date(2020, 11, 17)
        )

        self.employee_target.date_range_id = wrong_date_range

        child_targets = self.manager_target._get_child_targets()
        assert not child_targets

    def test_manager_total_fixed(self):
        self.employee_target.commissions_total = 400000 * 0.05
        self.manager_target.compute()
        assert (
            self.manager_target.commissions_total
            == 400000 * self.employee_target.fixed_rate * self.manager_target.fixed_rate
        )

    @data(
        (0, 0, 100),
        (0, 50, 100),  # 50% of 2k == 1k <= 1k
        (30, 70, 50),  # (1k - 0.6k) / (1.4k - 0.6k)
        (100, 100, 0),
    )
    @unpack
    def test_manager_completion_interval(self, slice_from, slice_to, completion):
        rate = self._create_target_rate(self.manager_target, slice_from, slice_to)
        self.manager_category.rate_type = "interval"
        self.employee_target.commissions_total = 400000 * 0.05
        self.manager_target.compute()
        assert rate.completion_rate == completion

    @data(
        (0, 0, 0),
        (0, 50, 1000),  # 50% of 2k = 1k
        (30, 70, 400),  # 50% of 800 = 400
        (50, 100, 0),  # 50% of 0 = 0
        (100, 100, 0),
    )
    @unpack
    def test_manager_subtotal_interval(self, slice_from, slice_to, subtotal):
        rate = self._create_target_rate(
            self.manager_target,
            slice_from,
            slice_to,
            self.interval_rate,
        )
        self.manager_category.rate_type = "interval"
        self.employee_target.commissions_total = 400000 * 0.05
        self.manager_target.compute()
        assert rate.subtotal == subtotal

    def test_sorted_by_dependency(self):
        rset = (
            self.manager_target | self.employee_target
        )._sorted_by_category_dependency()
        assert rset[0] == self.employee_target
        assert rset[1] == self.manager_target

    def test_no_child_categories(self):
        self.manager_category.child_category_ids.unlink()
        self.employee_target.commissions_total = 400000 * 0.05
        self.manager_target.compute()
        assert self.manager_target.commissions_total == 0

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
