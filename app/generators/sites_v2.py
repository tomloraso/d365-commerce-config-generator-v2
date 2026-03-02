from .base import BaseGenerator


class SitesV2Generator(BaseGenerator):

    @property
    def columns(self):
        return [
            "SITEID", "ISPRIMARYADDRESSASSIGNED",
            "ISRECEIVINGWAREHOUSEOVERRIDEALLOWED", "SITENAME", "SITETIMEZONE",
        ]

    def generate(self, stores):
        # One row per unique COUNTRY value
        seen = set()
        rows = []
        for r in stores:
            country = r["COUNTRY"]
            if country in seen:
                continue
            seen.add(country)
            rows.append({
                "SITEID": country,
                "ISPRIMARYADDRESSASSIGNED": "No",
                "ISRECEIVINGWAREHOUSEOVERRIDEALLOWED": "No",
                "SITENAME": f"{country} {r['FASCIA']}",
                "SITETIMEZONE": self.setting("timezone", "site_timezone"),
            })
        return rows
