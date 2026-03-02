from .base import BaseGenerator


class StoreHardwareStationGenerator(BaseGenerator):

    @property
    def columns(self):
        return ["STORENUMBER", "HARDWAREPROFILEID", "DESCRIPTION", "HARDWARESTATIONTYPE"]

    def generate(self, stores):
        pattern = self.setting("hardware", "hardware_profile_pattern")
        rows = []
        for r in stores:
            store_number = r["STOREID"].zfill(4)
            country_code = r.get("COUNTRYCODE", "").strip().upper()
            if not country_code:
                raise ValueError(
                    f"Store {store_number}: COUNTRYCODE is required for hardware station generation"
                )
            profile_id = pattern.replace("{country_code}", country_code)
            rows.append({
                "STORENUMBER": store_number,
                "HARDWAREPROFILEID": profile_id,
                "DESCRIPTION": profile_id,
                "HARDWARESTATIONTYPE": "Dedicated",
            })
        return rows
