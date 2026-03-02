from .base import BaseGenerator


class IncomeExpenseAccountsGenerator(BaseGenerator):

    @property
    def columns(self):
        return [
            "STORENUMBER", "ACCOUNTNUMBER", "ACCOUNTTYPE",
            "FRG_CASHMANISPARTOFSAFETRACKING", "FRG_INCOMEEXPENSEACCOUNTNOTVISIBLE",
            "FRG_INCOMEEXPENSEACTION", "LEDGERACCOUNTDISPLAYVALUE", "NAME", "SEARCHNAME",
        ]

    def generate(self, stores):
        la = self.s.get("ledger_accounts", {})
        coin_drop = la.get("coin_drop_ledger", "810105")
        eod_plus = la.get("eod_adj_plus_ledger", "119005")
        eod_minus = la.get("eod_adj_minus_ledger", "119006")
        paid_io = la.get("paid_in_out_ledger", "821603")
        safe_till = la.get("safe_till_ledger", "119006")

        account_templates = [
            ("Coin>Store",  "Income",  "No",  "No",  "None",              coin_drop, "Coin drop to store",       ""),
            ("EodAdj+1",    "Income",  "No",  "Yes", "None",              eod_plus,  "End of Day adjustment + 1", ""),
            ("EodAdj+2",    "Expense", "No",  "Yes", "None",              eod_minus, "End of Day adjustment + 2", ""),
            ("EodAdj-1",    "Income",  "No",  "Yes", "None",              eod_minus, "End of Day adjustment - 1", ""),
            ("EodAdj-2",    "Expense", "No",  "Yes", "None",              eod_plus,  "End of Day adjustment - 2", ""),
            ("PaidIn",      "Income",  "No",  "No",  "None",              paid_io,   "Paid In",                  "Paid In"),
            ("PaidOut",     "Expense", "No",  "No",  "None",              paid_io,   "Paid Out",                 "Paid Out"),
            ("Safe>Till",   "Income",  "Yes", "No",  "DecreaseCashSafe",  safe_till, "Safe to Till",             "Safe to Till"),
            ("Till>Safe",   "Expense", "Yes", "No",  "IncreaseCashSafe",  safe_till, "Safe to Till",             "Safe to Till"),
        ]

        rows = []
        for r in stores:
            store_number = r["STOREID"].zfill(4)
            for acct, atype, safe_track, not_visible, action, ledger, name, search in account_templates:
                rows.append({
                    "STORENUMBER": store_number,
                    "ACCOUNTNUMBER": acct,
                    "ACCOUNTTYPE": atype,
                    "FRG_CASHMANISPARTOFSAFETRACKING": safe_track,
                    "FRG_INCOMEEXPENSEACCOUNTNOTVISIBLE": not_visible,
                    "FRG_INCOMEEXPENSEACTION": action,
                    "LEDGERACCOUNTDISPLAYVALUE": ledger,
                    "NAME": name,
                    "SEARCHNAME": search,
                })
        return rows
