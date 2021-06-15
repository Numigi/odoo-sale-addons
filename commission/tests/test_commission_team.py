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

        cls.manager_user = cls.env["res.users"].create(
            {"name": "manager", "email": "manager@test.com", "login": "managing"}
        )

        cls.manager = cls.env["hr.employee"].create(
            {
                "name": "Bob",
                "user_id": cls.manager_user.id,
            }
        )

        cls.department = cls.env["hr.department"].create(
            {
                "name": "Dunder Mifflin",
                "manager_id": cls.manager.id,
            }
        )
        cls.employee.department_id = cls.department

        cls.manager_category = cls.env["commission.category"].create(
            {
                "name": "standard",
                "basis": "my_team_commissions",
            }
        )

        cls.target = cls._create_target(cls.manager, cls.manager_category, 40000)
        cls.target.fixed_rate = 0.05

        cls.employee_target = cls._create_target(cls.employee, cls.category, 100000)
        cls.employee_target.fixed_rate = 0.05

        cls.interval_rate = 0.05

        cls.invoice = cls._create_invoice(amount=400000)

    def test_child_targets(self):
        child_targets = self.target._get_child_targets()
        assert self.employee_target == child_targets

    def test_manager_total_fixed(self):
        self.target.compute()
        assert (
            self.target.commissions_total
            == 400000 * self.employee_target.fixed_rate * self.target.fixed_rate
        )

    @data(
        (0, 0, 1),
        (0, 50, 1),  # 50% of 2k == 1k <= 1k
        (30, 70, 0.5),  # (1k - 0.6k) / (1.4k - 0.6k)
        (100, 100, 0),
    )
    @unpack
    def test_manager_completion_interval(self, slice_from, slice_to, completion):
        rate = self._create_rate(slice_from, slice_to)
        self.manager_category.rate_type = "interval"
        self.target.compute()
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
        rate = self._create_rate(slice_from, slice_to, self.interval_rate)
        self.manager_category.rate_type = "interval"
        self.target.compute()
        assert rate.subtotal == subtotal
