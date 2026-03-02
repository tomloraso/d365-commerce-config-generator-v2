from .base import BaseGenerator


class RetailStoreAddressBooksGenerator(BaseGenerator):

    @property
    def columns(self):
        return ["RETAILCHANNELID", "ADDRESSBOOKNAME", "ADDRESSBOOKTYPE"]

    def generate(self, stores):
        cust_book = self.setting("organisation", "customer_address_book")
        staff_book = self.setting("organisation", "staff_address_book")
        rows = []
        for r in stores:
            store_id = r["STOREID"].zfill(4)
            rows.append({"RETAILCHANNELID": store_id, "ADDRESSBOOKNAME": cust_book, "ADDRESSBOOKTYPE": "Customer"})
            rows.append({"RETAILCHANNELID": store_id, "ADDRESSBOOKNAME": staff_book, "ADDRESSBOOKTYPE": "Employee"})
        return rows
