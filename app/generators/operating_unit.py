from .base import BaseGenerator


class OperatingUnitGenerator(BaseGenerator):

    @property
    def columns(self):
        return [
            "OPERATINGUNITNUMBER", "ADDRESSCOUNTRYREGIONID", "ADDRESSCOUNTRYREGIONISOCODE",
            "ADDRESSDESCRIPTION", "ADDRESSLOCATIONROLES", "ADDRESSSTREET", "ADDRESSZIPCODE",
            "LANGUAGEID", "NAME", "OPERATINGUNITTYPE", "ADDRESSCITY",
        ]

    def generate(self, stores):
        prefix = self.setting("store", "operating_unit_prefix")
        rows = []
        for r in stores:
            rows.append({
                "OPERATINGUNITNUMBER": f"{prefix}{r['STOREID']}",
                "ADDRESSCOUNTRYREGIONID": r["ISOCODE"],
                "ADDRESSCOUNTRYREGIONISOCODE": r.get("COUNTRYCODE", ""),
                "ADDRESSDESCRIPTION": "Address",
                "ADDRESSLOCATIONROLES": "Business",
                "ADDRESSSTREET": r["ADDRESS"],
                "ADDRESSZIPCODE": r.get("POSTCODE", ""),
                "LANGUAGEID": r["LANGUAGE"],
                "NAME": r["STORENAME"],
                "OPERATINGUNITTYPE": "RetailChannel",
                "ADDRESSCITY": r["CITY"],
            })
        return rows
