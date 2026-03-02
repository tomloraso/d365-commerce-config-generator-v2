from .base import BaseGenerator


class RetailChannelPriceGroupGenerator(BaseGenerator):

    @property
    def columns(self):
        return ["GROUPCODE", "RETAILCHANNELID"]

    def generate(self, stores):
        if not stores:
            return []
        legal_entity = stores[0]["LEGALENTITY"]
        rows = []
        for r in stores:
            store_id = r["STOREID"]
            rows.append({"GROUPCODE": store_id, "RETAILCHANNELID": store_id})
            rows.append({"GROUPCODE": legal_entity, "RETAILCHANNELID": store_id})
        return rows
