from .base import BaseGenerator


class PriceCustomerGroupsGenerator(BaseGenerator):

    @property
    def columns(self):
        return ["GROUPCODE", "GROUPNAME", "PRICINGPRIORITY"]

    def generate(self, stores):
        if not stores:
            return []
        rows = []
        first = stores[0]
        # Legal entity level group (priority 1)
        rows.append({
            "GROUPCODE": first["LEGALENTITY"],
            "GROUPNAME": f"{first['LEGALENTITY']} - {first['FASCIA']} {first['COUNTRY']}",
            "PRICINGPRIORITY": "1",
        })
        # Store level groups (priority 5)
        for r in stores:
            rows.append({
                "GROUPCODE": r["STOREID"],
                "GROUPNAME": f"{r['STOREID']} - {r['STORENAME']}",
                "PRICINGPRIORITY": "5",
            })
        return rows
