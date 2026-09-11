# Configuration Parameters - Payment Terminal Application

Quick lookup for parameters a semi-integrated POS may read/write through
`GetParameter`/`SetParameter`. Both operations use a `parameters` array of
`{ "key", "value" }` objects; the official protocol reference (§8) documents the
wire shape. `API=Y` means POS-settable. `API=N` means provisioned remotely by J.P.
Morgan Terminal Management Service (TMS).

## POS-settable parameters most integrations touch

| Area | Keys | Purpose / values |
| --- | --- | --- |
| Startup | `HWVENDORID` | Mandatory J.P. Morgan-assigned POS vendor id. Set once per session as the first POS-sent terminal operation after readiness. |
| Localization/demo | `LANG`, `ENGVAR`, `DEMOMODE`, `APPLOGO` | UI language, English variant, demo mode, logo file. |
| Timeouts | `TIME1`-`TIME7` | Generic UI, PIN, signature, screen saver, sleep, shutdown, outcome-screen timers in seconds. |
| Batch timing | `AUTOCLOSE` | Auto-close batch time, `HHMM`; `9999` disables. |
| Amount limits | `MINAMOUNT`, `MAXAMOUNT` | Minimum/maximum transaction amount; `0.00` disables. |
| Tip | `TIP`, `STATICTIP`, `TIPEXCEED`, `TIPPERC1`-`TIPPERC5`, `TIPAMT1`-`TIPAMT3` | Tip mode, static tip, approval threshold, suggested percentages/amounts. Percentages are scaled (`15000` = 15%); fixed amounts are cents. |
| Tax | `TAX`, `TAXPERCENT` | Tax prompt mode and percentage used to prepopulate tax amount. |
| Prompts | `INVOICENBR`, `CUSTOMERNBR`, `TICKETNBR`, `PURCHASENBR`, `ACCTNAME`, `LAST4DIGITS`, `DUPCHECK`, `CONFIRMAMT`, `CARDCHECK`, `TRANSRES` | Optional invoice/customer/ticket/purchase, fraud, duplicate, confirm-amount, ZIP/CVV2, and transaction-result prompts. |
| Signature | `SIGCAPTURE`, `SIGCONTROL`, `SIGSUP` | Signature capture/suppression behavior. |
| Receipts/reports | `RECEIPTOPT`, `REPORTOPT`, `HEADERLN1`-`HEADERLN6`, `FOOTLN1`-`FOOTLN3`, `PRTCOLS`, `RCPFNT`, `RPTFNT` | Receipt copies, report presentation, merchant header/footer, printer columns, font height. |
| Cashback | `CASHBACK1`-`CASHBACK3`, `CASHLIM` | Suggested cashback amounts and max cashback amount. |
| DCC | `DCCSUPPORT` | Dynamic Currency Conversion: `0` disabled, `1` enabled, `2` merchant-enabled/terminal-disabled. |
| SAF overrides | `SAFENTRY`, `SAFINTER` | Manual-entry and international-card behavior while Store and Forward is active. |
| Merchant/sub-merchant | `MCC`, `DBANAME`, `SMERCID`, `SMERC*` | Merchant category and aggregator/payment-facilitator sub-merchant fields. |
| Network/host | `DHCP`, `STATICIP`, `NETMASK`, `GATEWAY`, `DNS1`, `DNS2`, `HOST_IP`, `HOST_PORT`, `DEVICEGUID` | Terminal network and host routing values. Change only when directed by onboarding/support. |

## TMS-only parameters to recognize

| Area | Keys | Purpose |
| --- | --- | --- |
| Region/card entry | `COUNTRY`, `CURRENCY`, `EMVMODE`, `PINBYPASS`, `FALLBACKALLOWED`, `MSRALLOW`, `MANENTRY` | Country/currency, EMV mode, PIN bypass, fallback, magstripe/manual-entry support. |
| Risk/acceptance | `CVVREQ`, `AVSCHECK`, `COMMERCIAL`, `MAXREFUNDAMT`, `PARTIALVOID`, `PARTIALAPP`, `DEBITREF`, `EBTSUP`, `CASHBACK`, `CASHBACKEBT`, `CASHDISCOPT`, `CASHDISCPERC`, `NUMDAYSAUTH` | CVV/AVS, commercial cards, refund/partial/debit/EBT/cashback/cash-discount/open-auth controls. |
| Receipts/merchant identity | `TAXLABEL`, `PROCHEAD1`, `PROCHEAD2`, brand receipt flags (`VISARCP`, `MCRCP`, `DISCRCP`, `AMEXRCP`, `UPRCP`, `JCBRCP`, `INTERACRCP`), `BMERCID`, `MERCID`, `TERMID`, `STOREID` | Labels, processor DBA, TID/MID display, merchant and terminal ids. |
| Device operations | `REBTIME`, `SAF`, `SAFNUMBER`, `SAFSALETOTAL`, `SAFREFTOTAL`, `SAFSALEFLOOR`, `SAFREFMAX` | Daily reboot and Store and Forward enablement/limits. |

## Notes

- `PROVAMT` is required for `ReadCard cardType=1` to buffer a banking card; it must be
  greater than zero.
- Use `parameters` inside a `Transaction` to override prompt behavior for that one
  transaction, for example `TIP`/`TIPPERC*` for a sale with tip.
- Amounts are cents. Floats and time formats follow the official parameter docs.
- If a needed key is not listed here, fetch the portal source before inventing a
  setting or default.

## References

- [Configuration parameters](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fin-store-payments%2Fcapabilities%2Fpayment-terminal-application%2Fconfiguration-parameters.md)
- [Automatic operations](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fin-store-payments%2Fcapabilities%2Fpayment-terminal-application%2Fautomatic-operations.md)
- [Dynamic Currency Conversion](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fin-store-payments%2Fcapabilities%2Fpayment-terminal-application%2Fdynamic-currency-conversion.md)
- [Store and Forward](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fin-store-payments%2Fcapabilities%2Fpayment-terminal-application%2Fstore-and-forward.md)
- [Setup and management](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fin-store-payments%2Fcapabilities%2Fpayment-terminal-application%2Fsetup-and-management.md)
