from .base import BaseGenerator


class CustomersV3Generator(BaseGenerator):

    @property
    def columns(self):
        return [
            "CUSTOMERACCOUNT", "ACCOUNTSTATEMENT", "ADDRESSBOOKS", "ADDRESSCITY",
            "ADDRESSCOUNTRYREGIONID", "ADDRESSCOUNTRYREGIONISOCODE", "ADDRESSDESCRIPTION",
            "ADDRESSLOCATIONROLES", "ADDRESSSTREET", "ADDRESSZIPCODE", "ALLOWONACCOUNT",
            "COLLECTIONLETTERCODE", "CREDITCARDADDRESSVERIFICATION",
            "CREDITCARDADDRESSVERIFICATIONISAUTHORIZATIONVOIDEDONFAILURE",
            "CREDITCARDADDRESSVERIFICATIONLEVEL", "CREDITCARDCVC", "CREDITLIMIT",
            "CREDITLIMITISMANDATORY", "CREDMANCUSTUNLIMITEDCREDIT", "CREDMANEXCLUDE",
            "CUSTOMERGROUPID", "LANGUAGEID", "NAMEALIAS", "OVERRIDESALESTAX", "PARTYTYPE",
            "PAYMENTTERMS", "PAYMENTTERMSBASEDAYS", "PAYMENTUSECASHDISCOUNT",
            "PERSONANNIVERSARYDAY", "PERSONANNIVERSARYMONTH", "PERSONANNIVERSARYYEAR",
            "PERSONFIRSTNAME", "PERSONLASTNAME", "PERSONMARITALSTATUS", "PRIORITY",
            "RECEIPTOPTION", "SALESCURRENCYCODE", "SALESTAXGROUP",
        ]

    def generate(self, stores):
        address_book = self.setting("organisation", "customer_address_book")
        customer_group = self.setting("organisation", "customer_group_id")
        last_name = self.setting("organisation", "customer_last_name_suffix")

        rows = []
        for r in stores:
            rows.append({
                "CUSTOMERACCOUNT": r["STOREID"],
                "ACCOUNTSTATEMENT": "Always",
                "ADDRESSBOOKS": address_book,
                "ADDRESSCITY": r["CITY"],
                "ADDRESSCOUNTRYREGIONID": r["ISOCODE"],
                "ADDRESSCOUNTRYREGIONISOCODE": r["ISOCODE"],
                "ADDRESSDESCRIPTION": "Address",
                "ADDRESSLOCATIONROLES": "Business",
                "ADDRESSSTREET": r["ADDRESS"],
                "ADDRESSZIPCODE": r.get("POSTCODE", ""),
                "ALLOWONACCOUNT": "No",
                "COLLECTIONLETTERCODE": "None",
                "CREDITCARDADDRESSVERIFICATION": "None",
                "CREDITCARDADDRESSVERIFICATIONISAUTHORIZATIONVOIDEDONFAILURE": "No",
                "CREDITCARDADDRESSVERIFICATIONLEVEL": "Accept",
                "CREDITCARDCVC": "None",
                "CREDITLIMIT": ".000000",
                "CREDITLIMITISMANDATORY": "No",
                "CREDMANCUSTUNLIMITEDCREDIT": "No",
                "CREDMANEXCLUDE": "No",
                "CUSTOMERGROUPID": customer_group,
                "LANGUAGEID": r["LANGUAGE"],
                "NAMEALIAS": r["STORENAME"],
                "OVERRIDESALESTAX": "No",
                "PARTYTYPE": "Person",
                "PAYMENTTERMS": "NET0",
                "PAYMENTTERMSBASEDAYS": "0",
                "PAYMENTUSECASHDISCOUNT": "Normal",
                "PERSONANNIVERSARYDAY": "0",
                "PERSONANNIVERSARYMONTH": "None",
                "PERSONANNIVERSARYYEAR": "0",
                "PERSONFIRSTNAME": r["STORENAME"],
                "PERSONLASTNAME": last_name,
                "PERSONMARITALSTATUS": "None",
                "PRIORITY": "AllocationPriority10",
                "RECEIPTOPTION": "RetailEx3",
                "SALESCURRENCYCODE": r["CURRENCY"],
                "SALESTAXGROUP": r["TAXGROUP"],
            })
        return rows
