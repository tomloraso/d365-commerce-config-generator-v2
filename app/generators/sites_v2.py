from .base import BaseGenerator


class SitesV2Generator(BaseGenerator):

    @property
    def columns(self):
        return [
            "SITEID", "ISPRIMARYADDRESSASSIGNED",
            "ISRECEIVINGWAREHOUSEOVERRIDEALLOWED", "SITENAME", "SITETIMEZONE",
        ]

    def generate(self, stores):
        if not stores:
            return []
        r = stores[0]
        return [{
            "SITEID": r["COUNTRY"],
            "ISPRIMARYADDRESSASSIGNED": "No",
            "ISRECEIVINGWAREHOUSEOVERRIDEALLOWED": "No",
            "SITENAME": f"{r['COUNTRY']} {r['FASCIA']}",
            "SITETIMEZONE": self.setting("timezone", "site_timezone"),
        }]
