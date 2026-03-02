from .base import BaseGenerator


class OperatingUnitContactGenerator(BaseGenerator):

    @property
    def columns(self):
        return ["TYPE", "LOCATOR", "OMOPERATINGUNITNUMBER", "PURPOSE"]

    def generate(self, stores):
        prefix = self.setting("organisation", "operating_unit_prefix")
        return [{
            "TYPE": "Phone",
            "LOCATOR": r.get("PHONE", ""),
            "OMOPERATINGUNITNUMBER": f"{prefix}{r['STOREID']}",
            "PURPOSE": "Business",
        } for r in stores]
