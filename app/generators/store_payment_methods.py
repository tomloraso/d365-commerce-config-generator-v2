from .base import BaseGenerator


class StorePaymentMethodsGenerator(BaseGenerator):

    @property
    def columns(self):
        return [
            "RETAILCHANNELID", "PAYMENTMETHODNUMBER", "ABOVEMINIMUMTENDERID", "ACCOUNTTYPE",
            "ACCOUNTTYPEGIFTCARDCOMPANY", "ACTIVEACCOUNT", "ALLOWFLOAT", "ALLOWOVERTENDER",
            "ALLOWRETURNNEGATIVE", "ALLOWUNDERTENDER", "ASKFORDATE", "BANKBAGACCOUNTTYPE",
            "BANKBAGLEDGERDIMENSIONDISPLAYVALUE", "CHANGETENDERID", "COMPRESSPAYMENTENTRIES",
            "CONNECTORNAME", "COUNTINGREQUIRED", "DEFAULTDIMENSIONDISPLAYVALUE",
            "DIFFACCBIGDIFFLEDGERDIMENSIONDISPLAYVALUE", "DIFFERENCEACCLEDGERDIMENSIONDISPLAYVALUE",
            "ENDORSECHECK", "FRONTOFCHECK", "FUNCTION", "GIFTCARDCASHOUTTHRESHOLD",
            "GIFTCARDCOMPANY", "GIFTCARDITEMID", "HIDECARDINPUTDETAILSINPOS",
            "LEDGERDIMENSIONDISPLAYVALUE", "LEDGERDIMENSIONGIFTCARDCOMPANYDISPLAYVALUE",
            "LINENUMINTRANSACTION", "MAXCOUNTINGDIFFERENCE", "MAXIMUMAMOUNTALLOWED",
            "MAXIMUMAMOUNTENTERED", "MAXIMUMOVERTENDERAMOUNT", "MAXNORMALDIFFERENCEAMOUNT",
            "MAXRECOUNT", "MINIMUMAMOUNTALLOWED", "MINIMUMAMOUNTENTERED", "MINIMUMCHANGEAMOUNT",
            "MULTIPLYINTENDEROPERATIONS", "NAME", "OPENDRAWER", "PAYACCOUNTBILL", "PAYMTERMID",
            "POSCOUNTENTRIES", "POSOPERATION", "ROUNDING", "ROUNDINGMETHOD", "SAFEACCOUNTTYPE",
            "SAFEACTIVEACCOUNT", "SEEKAUTHORIZATION", "SIGCAPENABLED", "SIGNATURECAPTUREMINAMOUNT",
            "TAKENTOBANK", "TAKENTOSAFE", "UNDERTENDERAMOUNT",
        ]

    def _base_row(self, store_id, legal_entity):
        """Shared defaults that every tender inherits before overrides."""
        la = self.s.get("ledger_accounts", {})
        diff_acct = la.get("difference_account", "119005")
        dim_pattern = self.setting("store", "dimension_display_value_pattern")
        dim_value = dim_pattern.replace("{store_id}", store_id)
        return {
            "RETAILCHANNELID": store_id,
            "PAYMENTMETHODNUMBER": "",
            "ABOVEMINIMUMTENDERID": "",
            "ACCOUNTTYPE": "Ledger",
            "ACCOUNTTYPEGIFTCARDCOMPANY": "Ledger",
            "ACTIVEACCOUNT": "No",
            "ALLOWFLOAT": "No",
            "ALLOWOVERTENDER": "No",
            "ALLOWRETURNNEGATIVE": "No",
            "ALLOWUNDERTENDER": "Yes",
            "ASKFORDATE": "No",
            "BANKBAGACCOUNTTYPE": "Ledger",
            "BANKBAGLEDGERDIMENSIONDISPLAYVALUE": "",
            "CHANGETENDERID": "",
            "COMPRESSPAYMENTENTRIES": "No",
            "CONNECTORNAME": "",
            "COUNTINGREQUIRED": "No",
            "DEFAULTDIMENSIONDISPLAYVALUE": "",
            "DIFFACCBIGDIFFLEDGERDIMENSIONDISPLAYVALUE": "",
            "DIFFERENCEACCLEDGERDIMENSIONDISPLAYVALUE": "",
            "ENDORSECHECK": "No",
            "FRONTOFCHECK": "No",
            "FUNCTION": "Card",
            "GIFTCARDCASHOUTTHRESHOLD": ".000000",
            "GIFTCARDCOMPANY": legal_entity.upper(),
            "GIFTCARDITEMID": "",
            "HIDECARDINPUTDETAILSINPOS": "No",
            "LEDGERDIMENSIONDISPLAYVALUE": "",
            "LEDGERDIMENSIONGIFTCARDCOMPANYDISPLAYVALUE": "",
            "LINENUMINTRANSACTION": "",
            "MAXCOUNTINGDIFFERENCE": ".000000",
            "MAXIMUMAMOUNTALLOWED": ".000000",
            "MAXIMUMAMOUNTENTERED": ".000000",
            "MAXIMUMOVERTENDERAMOUNT": ".000000",
            "MAXNORMALDIFFERENCEAMOUNT": ".000000",
            "MAXRECOUNT": "0",
            "MINIMUMAMOUNTALLOWED": ".000000",
            "MINIMUMAMOUNTENTERED": ".000000",
            "MINIMUMCHANGEAMOUNT": ".000000",
            "MULTIPLYINTENDEROPERATIONS": "No",
            "NAME": "",
            "OPENDRAWER": "No",
            "PAYACCOUNTBILL": "No",
            "PAYMTERMID": "NET0",
            "POSCOUNTENTRIES": "No",
            "POSOPERATION": "",
            "ROUNDING": ".000000",
            "ROUNDINGMETHOD": "None",
            "SAFEACCOUNTTYPE": "Ledger",
            "SAFEACTIVEACCOUNT": "No",
            "SEEKAUTHORIZATION": "No",
            "SIGCAPENABLED": "No",
            "SIGNATURECAPTUREMINAMOUNT": ".000000",
            "TAKENTOBANK": "No",
            "TAKENTOSAFE": "No",
            "UNDERTENDERAMOUNT": ".000000",
            # store these for reference in overrides
            "_dim_value": dim_value,
            "_store_id": store_id,
        }

    def generate(self, stores):
        if not stores:
            return []

        legal_entity = stores[0]["LEGALENTITY"]
        pmt = self.s.get("payment", {})
        la = self.s.get("ledger_accounts", {})
        connector = pmt.get("card_connector_name", "")
        gc_item = pmt.get("gift_card_item_id", "GiftCardExt")
        dim_pattern = self.s.get("store", {}).get("dimension_display_value_pattern", "-{store_id}-STORE-SDR-")
        cash_ledger = la.get("cash_ledger", "821701")
        bank_bag_ledger = la.get("bank_bag_ledger", "821602")
        diff_acct = la.get("difference_account", "119005")
        bfv_ledger = la.get("black_friday_voucher_ledger", "917023")
        cn_ledger = la.get("credit_note_ledger", "917012")
        gc_ledger = la.get("gift_card_ledger", "917002")

        t_cash = pmt.get("tender_id_cash", "1")
        t_bfv = pmt.get("tender_id_black_friday_voucher", "1023")
        t_cn = pmt.get("tender_id_credit_note", "631")
        t_gc = pmt.get("tender_id_gift_card", "650")
        t_card = pmt.get("tender_id_card", "660")
        t_float = pmt.get("tender_id_float_remove", "9999")

        rows = []
        for r in stores:
            store_id = r["STOREID"].zfill(4)
            dim_value = dim_pattern.replace("{store_id}", store_id)

            # --- Cash ---
            rows.append({
                **self._base_row(store_id, legal_entity),
                "PAYMENTMETHODNUMBER": t_cash,
                "ACTIVEACCOUNT": "Yes",
                "ALLOWFLOAT": "Yes",
                "ALLOWOVERTENDER": "Yes",
                "ALLOWUNDERTENDER": "Yes",
                "BANKBAGLEDGERDIMENSIONDISPLAYVALUE": bank_bag_ledger,
                "CHANGETENDERID": t_cash,
                "COUNTINGREQUIRED": "Yes",
                "DEFAULTDIMENSIONDISPLAYVALUE": dim_value,
                "DIFFACCBIGDIFFLEDGERDIMENSIONDISPLAYVALUE": diff_acct,
                "DIFFERENCEACCLEDGERDIMENSIONDISPLAYVALUE": diff_acct,
                "FUNCTION": "Normal",
                "GIFTCARDCOMPANY": legal_entity.upper(),
                "LEDGERDIMENSIONDISPLAYVALUE": cash_ledger,
                "LINENUMINTRANSACTION": t_cash,
                "NAME": "Cash",
                "OPENDRAWER": "Yes",
                "POSCOUNTENTRIES": "Yes",
                "POSOPERATION": "200",
                "ROUNDING": ".00",
                "TAKENTOBANK": "Yes",
                "TAKENTOSAFE": "Yes",
                "_dim_value": dim_value,
                "_store_id": store_id,
            })

            # --- Black Friday Voucher ---
            rows.append({
                **self._base_row(store_id, legal_entity),
                "PAYMENTMETHODNUMBER": t_bfv,
                "CONNECTORNAME": connector,
                "GIFTCARDCOMPANY": legal_entity.lower(),
                "GIFTCARDITEMID": gc_item,
                "LEDGERDIMENSIONDISPLAYVALUE": bfv_ledger,
                "LEDGERDIMENSIONGIFTCARDCOMPANYDISPLAYVALUE": f"{bfv_ledger}----",
                "LINENUMINTRANSACTION": t_bfv,
                "NAME": "Black Friday Voucher",
                "POSOPERATION": "214",
                "_dim_value": dim_value,
                "_store_id": store_id,
            })

            # --- Credit Note ---
            rows.append({
                **self._base_row(store_id, legal_entity),
                "PAYMENTMETHODNUMBER": t_cn,
                "CONNECTORNAME": connector,
                "GIFTCARDCOMPANY": legal_entity.upper(),
                "GIFTCARDITEMID": gc_item,
                "LEDGERDIMENSIONDISPLAYVALUE": cn_ledger,
                "LEDGERDIMENSIONGIFTCARDCOMPANYDISPLAYVALUE": f"{cn_ledger}----",
                "LINENUMINTRANSACTION": t_cn,
                "NAME": "Credit Note",
                "POSOPERATION": "214",
                "_dim_value": dim_value,
                "_store_id": store_id,
            })

            # --- Gift Card ---
            rows.append({
                **self._base_row(store_id, legal_entity),
                "PAYMENTMETHODNUMBER": t_gc,
                "CONNECTORNAME": connector,
                "GIFTCARDCOMPANY": legal_entity.upper(),
                "GIFTCARDITEMID": gc_item,
                "LEDGERDIMENSIONDISPLAYVALUE": gc_ledger,
                "LEDGERDIMENSIONGIFTCARDCOMPANYDISPLAYVALUE": f"{gc_ledger}----",
                "LINENUMINTRANSACTION": t_gc,
                "NAME": "Gift Card",
                "POSOPERATION": "214",
                "_dim_value": dim_value,
                "_store_id": store_id,
            })

            # --- Card (EFT) ---
            rows.append({
                **self._base_row(store_id, legal_entity),
                "PAYMENTMETHODNUMBER": t_card,
                "GIFTCARDCOMPANY": legal_entity.upper(),
                "LEDGERDIMENSIONDISPLAYVALUE": cash_ledger,
                "LINENUMINTRANSACTION": t_card,
                "NAME": "Card",
                "POSOPERATION": "201",
                "_dim_value": dim_value,
                "_store_id": store_id,
            })

            # --- Tender Remove / Float ---
            rows.append({
                **self._base_row(store_id, legal_entity),
                "PAYMENTMETHODNUMBER": t_float,
                "FUNCTION": "TenderRemoveFloat",
                "GIFTCARDCOMPANY": legal_entity.lower(),
                "LINENUMINTRANSACTION": t_float,
                "NAME": "Tender remove/float",
                "OPENDRAWER": "Yes",
                "POSOPERATION": "1201",
                "_dim_value": dim_value,
                "_store_id": store_id,
            })

        # Strip internal helper keys before writing
        clean_cols = set(self.columns)
        return [{k: v for k, v in row.items() if k in clean_cols} for row in rows]
