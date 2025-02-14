import casbin
from tests.test_enforcer import get_examples, TestCaseBase


class TestDistributedApi(TestCaseBase):
    def get_enforcer(self, model=None, adapter=None):
        return casbin.DistributedEnforcer(
            model,
            adapter,
        )

    def test(self):
        e = self.get_enforcer(
            get_examples("rbac_model.conf"), get_examples("rbac_policy.csv")
        )

        e.add_policy_self(
            False,
            "p",
            "p",
            [
                ["alice", "data1", "read"],
                ["bob", "data2", "write"],
                ["data2_admin", "data2", "read"],
                ["data2_admin", "data2", "write"],
            ],
        )
        e.add_policy_self(False, "g", "g", [["alice", "data2_admin"]])

        self.assertTrue(e.enforce("alice", "data1", "read"))
        self.assertFalse(e.enforce("alice", "data1", "write"))
        self.assertTrue(e.enforce("bob", "data2", "write"))
        self.assertFalse(e.enforce("bob", "data2", "read"))
        self.assertTrue(e.enforce("data2_admin", "data2", "read"))
        self.assertTrue(e.enforce("data2_admin", "data2", "write"))
        self.assertTrue(e.enforce("alice", "data2", "read"))
        self.assertTrue(e.enforce("alice", "data2", "write"))

        e.update_policy_self(
            False, "p", "p", ["alice", "data1", "read"], ["alice", "data1", "write"]
        )
        e.update_policy_self(
            False, "g", "g", ["alice", "data2_admin"], ["tom", "alice"]
        )

        self.assertFalse(e.enforce("alice", "data1", "read"))
        self.assertTrue(e.enforce("alice", "data1", "write"))
        self.assertFalse(e.enforce("bob", "data2", "read"))
        self.assertTrue(e.enforce("bob", "data2", "write"))
        self.assertTrue(e.enforce("data2_admin", "data2", "read"))
        self.assertTrue(e.enforce("data2_admin", "data2", "write"))
        self.assertFalse(e.enforce("tom", "data1", "read"))
        self.assertTrue(e.enforce("tom", "data1", "write"))

        e.remove_policy_self(False, "p", "p", [["alice", "data1", "write"]])

        self.assertFalse(e.enforce("alice", "data1", "read"))
        self.assertFalse(e.enforce("alice", "data1", "write"))
        self.assertFalse(e.enforce("bob", "data2", "read"))
        self.assertTrue(e.enforce("bob", "data2", "write"))
        self.assertTrue(e.enforce("data2_admin", "data2", "read"))
        self.assertTrue(e.enforce("data2_admin", "data2", "write"))
        self.assertFalse(e.enforce("alice", "data2", "read"))
        self.assertFalse(e.enforce("alice", "data2", "write"))

        e.remove_filtered_policy_self(False, "p", "p", 0, "bob", "data2", "write")
        e.remove_filtered_policy_self(False, "g", "g", 0, "tom", "data2_admin")

        self.assertFalse(e.enforce("alice", "data1", "read"))
        self.assertFalse(e.enforce("alice", "data1", "write"))
        self.assertFalse(e.enforce("bob", "data2", "read"))
        self.assertFalse(e.enforce("bob", "data2", "write"))
        self.assertTrue(e.enforce("data2_admin", "data2", "read"))
        self.assertTrue(e.enforce("data2_admin", "data2", "write"))
        self.assertFalse(e.enforce("tom", "data1", "read"))
        self.assertFalse(e.enforce("tom", "data1", "write"))

        e.clear_policy_self(False)
        self.assertFalse(e.enforce("alice", "data1", "read"))
        self.assertFalse(e.enforce("alice", "data1", "write"))
        self.assertFalse(e.enforce("bob", "data2", "read"))
        self.assertFalse(e.enforce("bob", "data2", "write"))
        self.assertFalse(e.enforce("data2_admin", "data2", "read"))
        self.assertFalse(e.enforce("data2_admin", "data2", "write"))
