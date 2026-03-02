from .base import BaseGenerator


class InventoryAislesGenerator(BaseGenerator):

    @property
    def columns(self):
        return [
            "WAREHOUSEID", "AISLEID", "AISLENAME",
            "AISLENUMBER", "ISSORTORDERCODEASSIGNEDDESCENDING", "MANUALSTARTINGSORTORDERCODE",
        ]

    def generate(self, stores):
        return [{
            "WAREHOUSEID": r["STOREID"],
            "AISLEID": "Default",
            "AISLENAME": "Default",
            "AISLENUMBER": "0",
            "ISSORTORDERCODEASSIGNEDDESCENDING": "No",
            "MANUALSTARTINGSORTORDERCODE": "0",
        } for r in stores]
