from .base import BaseGenerator


class InfoCodeTableAssignmentsGenerator(BaseGenerator):

    @property
    def columns(self):
        return [
            "REFTABLEID", "REFRELATION1", "REFRELATION2",
            "INFOCODEID", "INPUTREQUIRED", "SEQUENCE", "WHENREQUIRED",
        ]

    def generate(self, stores):
        info_code_id = self.setting("payment", "info_code_id")
        rows = []
        for r in stores:
            store_id = r["STOREID"].zfill(4)
            common = {
                "REFTABLEID": "RetailIncomeExpenseAccountTable",
                "REFRELATION1": store_id,
                "INFOCODEID": info_code_id,
                "INPUTREQUIRED": "Yes",
                "SEQUENCE": "0",
                "WHENREQUIRED": "None",
            }
            for account in ("PaidIn", "PaidOut", "Safe>Till", "Till>Safe"):
                rows.append({**common, "REFRELATION2": account})
        return rows
