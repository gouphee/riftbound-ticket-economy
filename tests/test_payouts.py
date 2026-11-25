import unittest

from riftbound_tickets.payouts.rules import saturday_placement, saturday_top8_split, win_record_payout


class PayoutTests(unittest.TestCase):
    def test_historical_changes(self):
        self.assertEqual(win_record_payout(5, 1, 0, rounds=6, table={6:48,5:36,4:24}), 36)
        self.assertEqual(win_record_payout(5, 0, 0, rounds=5, table={5:45,4:30,3:15}), 45)
        self.assertEqual(win_record_payout(5, 0, 0, rounds=5, table={5:50,4:30,3:15}), 50)

    def test_draws_do_not_round_up_to_wins(self):
        self.assertEqual(win_record_payout(3, 1, 2, rounds=6, table={6:48,5:36,4:24}), 0)
        self.assertEqual(win_record_payout(4, 1, 1, rounds=6, table={6:48,5:36,4:24}), 24)

    def test_unknown_and_out_of_scope_records(self):
        self.assertIsNone(win_record_payout(None, 0, 0, rounds=5, table={5:50}))
        self.assertIsNone(win_record_payout(6, 0, 0, rounds=5, table={5:50}))
        self.assertIsNone(win_record_payout(5, 1, 0, rounds=5, table={5:50}))
        self.assertIsNone(saturday_placement(None))

    def test_sunday_same_five_six_win_tickets(self):
        for wins in [5, 6]:
            self.assertEqual(win_record_payout(wins, 6-wins, 0, rounds=6, table={6:40,5:40,4:30}), 40)

    def test_every_saturday_boundary(self):
        expected={1:432,2:288,3:216,4:216,5:144,8:144,9:72,16:72,17:48,32:48,33:24,64:24,65:18,128:18,129:0}
        for rank, ticket in expected.items():
            with self.subTest(rank=rank): self.assertEqual(saturday_placement(rank),ticket)

    def test_split_conserves_pool_and_is_not_added(self):
        self.assertEqual(sum(saturday_placement(p) for p in range(1,9)),1728)
        self.assertEqual([saturday_top8_split(p) for p in range(1,9)],[216]*8)
        self.assertEqual(sum(saturday_placement(p) for p in range(1,129)),4992)
        self.assertEqual(sum(saturday_top8_split(p) for p in range(1,129)),4992)

    def test_rejects_invalid_numbers(self):
        for bad in [True,-1,1.5,"5"]:
            with self.assertRaises(ValueError): win_record_payout(bad,0,0,rounds=5,table={5:50})
        for bad in [0,False,-1]:
            with self.assertRaises(ValueError): saturday_placement(bad)
