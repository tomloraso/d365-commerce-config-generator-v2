from .base import BaseGenerator


class StoresGenerator(BaseGenerator):

    @property
    def columns(self):
        return [
            "RETAILCHANNELID", "BANKDROPCALCULATION", "CLOSINGMETHOD", "CREATELABELSFORZEROPRICE",
            "CULTURENAME", "CURRENCY", "DATABASENAME", "DEFAULTCUSTOMERACCOUNT",
            "DEFAULTCUSTOMERLEGALENTITY", "DEFAULTDIMENSIONDISPLAYVALUE", "GENERATESITEMLABELS",
            "GENERATESSHELFLABELS", "HIDETRAININGMODE", "INVENTORYLOOKUP", "LAYOUTID",
            "MAXIMUMPOSTINGDIFFERENCE", "MAXIMUMTEXTLENGTHONRECEIPT", "MAXROUNDINGAMOUNT",
            "MAXROUNDINGTAXAMOUNT", "MAXSHIFTDIFFERENCEAMOUNT", "MAXTRANSACTIONDIFFERENCEAMOUNT",
            "NUMBEROFTOPORBOTTOMLINES", "OFFLINEPROFILENAME", "ONESTATEMENTPERDAY", "OPENFROM",
            "OPENTO", "OPERATINGUNITNUMBER", "PAYMENTMETHODTOREMOVEORADD", "PRICEINCLUDESSALESTAX",
            "PRODUCTCATEGORYHIERARCHYNAME", "PRODUCTNUMBERONRECEIPT", "PURCHASEORDERITEMFILTER",
            "ROUNDINGACCOUNTLEDGERDIMENSIONDISPLAYVALUE", "ROUNDINGTAXACCOUNT",
            "SEPARATESTATEMENTPERSTAFFTERMINAL", "SERVICECHARGEPERCENTAGE", "SERVICECHARGEPROMPT",
            "SQLSERVERNAME", "STARTAMOUNTCALCULATION", "STATEMENTMETHOD", "STATEMENTPOSTASBUSINESSDAY",
            "STOREAREA", "STORENUMBER", "TAXGROUPCODE", "TAXGROUPLEGALENTITY",
            "TENDERDECLARATIONCALCULATION", "USECUSTOMERBASEDTAX", "USECUSTOMERBASEDTAXEXEMPTION",
            "USEDEFAULTCUSTOMERACCOUNT", "USEDESTINATIONBASEDTAX", "WAREHOUSEID",
            "WAREHOUSEIDFORCUSTOMERORDER", "WAREHOUSELEGALENTITY", "CHANNELTIMEZONE",
            "CHANNELTIMEZONEINFOID",
        ]

    def generate(self, stores):
        prefix = self.setting("store", "operating_unit_prefix")
        pmt_remove = self.setting("payment", "payment_method_to_remove")
        price_tax = self.setting("store", "price_includes_sales_tax")
        hierarchy = self.setting("store", "product_category_hierarchy_name")
        layout_pattern = self.setting("store", "layout_id_pattern")
        tax_pattern = self.setting("store", "tax_group_pattern")
        dim_pattern = self.setting("store", "dimension_display_value_pattern")
        channel_tz = self.setting("timezone", "channel_timezone")
        channel_tz_id = self.setting("timezone", "channel_timezone_info_id")
        receipt_text_len = self.setting("store", "maximum_text_length_on_receipt")

        rows = []
        for r in stores:
            store_id = r["STOREID"]
            country_code_upper = r.get("COUNTRYCODE", "").strip().upper()
            layout_id = layout_pattern.replace("{country}", r["COUNTRY"])
            tax_group = tax_pattern.replace("{country_code_upper}", country_code_upper)
            dim_value = dim_pattern.replace("{store_id}", store_id)

            rows.append({
                "RETAILCHANNELID": store_id,
                "BANKDROPCALCULATION": "SumBankDrop",
                "CLOSINGMETHOD": "PosBatch",
                "CREATELABELSFORZEROPRICE": "No",
                "CULTURENAME": r["LANGUAGE"],
                "CURRENCY": r["CURRENCY"],
                "DATABASENAME": "",
                "DEFAULTCUSTOMERACCOUNT": store_id,
                "DEFAULTCUSTOMERLEGALENTITY": r["LEGALENTITY"],
                "DEFAULTDIMENSIONDISPLAYVALUE": dim_value,
                "GENERATESITEMLABELS": "No",
                "GENERATESSHELFLABELS": "No",
                "HIDETRAININGMODE": "No",
                "INVENTORYLOOKUP": "No",
                "LAYOUTID": layout_id,
                "MAXIMUMPOSTINGDIFFERENCE": "999999999999999.000000",
                "MAXIMUMTEXTLENGTHONRECEIPT": receipt_text_len,
                "MAXROUNDINGAMOUNT": ".000000",
                "MAXROUNDINGTAXAMOUNT": ".000000",
                "MAXSHIFTDIFFERENCEAMOUNT": "999999999999999.000000",
                "MAXTRANSACTIONDIFFERENCEAMOUNT": "999999999999999.000000",
                "NUMBEROFTOPORBOTTOMLINES": "0",
                "OFFLINEPROFILENAME": "",
                "ONESTATEMENTPERDAY": "Yes",
                "OPENFROM": "00:00:00",
                "OPENTO": "00:00:00",
                "OPERATINGUNITNUMBER": f"{prefix}{store_id}",
                "PAYMENTMETHODTOREMOVEORADD": pmt_remove,
                "PRICEINCLUDESSALESTAX": price_tax,
                "PRODUCTCATEGORYHIERARCHYNAME": hierarchy,
                "PRODUCTNUMBERONRECEIPT": "None",
                "PURCHASEORDERITEMFILTER": "No",
                "ROUNDINGACCOUNTLEDGERDIMENSIONDISPLAYVALUE": "",
                "ROUNDINGTAXACCOUNT": "",
                "SEPARATESTATEMENTPERSTAFFTERMINAL": "No",
                "SERVICECHARGEPERCENTAGE": ".000000",
                "SERVICECHARGEPROMPT": "",
                "SQLSERVERNAME": "",
                "STARTAMOUNTCALCULATION": "SumStartAmount",
                "STATEMENTMETHOD": "Total",
                "STATEMENTPOSTASBUSINESSDAY": "No",
                "STOREAREA": ".000000",
                "STORENUMBER": store_id,
                "TAXGROUPCODE": tax_group,
                "TAXGROUPLEGALENTITY": r["LEGALENTITY"],
                "TENDERDECLARATIONCALCULATION": "LastTender",
                "USECUSTOMERBASEDTAX": "No",
                "USECUSTOMERBASEDTAXEXEMPTION": "No",
                "USEDEFAULTCUSTOMERACCOUNT": "No",
                "USEDESTINATIONBASEDTAX": "No",
                "WAREHOUSEID": store_id,
                "WAREHOUSEIDFORCUSTOMERORDER": store_id,
                "WAREHOUSELEGALENTITY": r["LEGALENTITY"],
                "CHANNELTIMEZONE": channel_tz,
                "CHANNELTIMEZONEINFOID": channel_tz_id,
            })
        return rows
