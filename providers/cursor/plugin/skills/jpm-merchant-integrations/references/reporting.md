# Reporting

The Reporting API is a modular interface used to configure, customize, and retrieve reports across the payment lifecycle.

For additional information, refer to the [Reporting API overview](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Freporting%2Foverview.md)

## When to Use

- Reconcile settlement, deposit, dispute, and fee activity against your own records
- Run JPM's preset reports, or build custom reports with your own fields, filters, and sort order
- Generate reports ad hoc or on a daily schedule, then download them as files

## Authentication

Authentication is handled by the merchant's auth module (set up via the `jpm-oauth` skill). Import `getAccessToken` (or your language's equivalent) from that module and use it as `Authorization: Bearer <token>` on every Reporting API call. Do **not** reimplement OAuth here — the auth module already caches tokens correctly per JPM guidance.

## Base URLs

| Env | URL | Env var |
|-----|-----|---------|
| CAT | `https://api.reports.test.jpmorgan.com` | `JPM_REPORTING_URL` |
| PROD | `https://api.payments.jpmorgan.com` | `JPM_REPORTING_URL` |

Reporting doesn't share the `api-ms` host root used by Online Payments, 3DS, and Account Updater, and its CAT and PROD hosts sit on different domains — never derive one from the other. `JPM_REPORTING_URL` holds the host only, because the paths don't share one prefix: everything is under `/api/v1/…` except reporting groups, which are under `/v1/…`. Keep both as written — normalizing to one prefix will 404. If the merchant's RM provides a different Reporting host, use that.

## How Reporting works

``` mermaid
flowchart LR
    subgraph Merchant["🏪 Merchant"]
    end

    subgraph JPM["J.P.Morgan\nCommerce Platform"]
        API["Reporting API"]
        NAPI["Notifications API"]
        API -.-> NAPI
    end

    Merchant -- "1 · Run report" --> API
    Merchant -. "2 · Poll status" .-> API
    NAPI -. "2 · Status notification" .-> Merchant
    Merchant -- "3 · Download file" --> API

    style Merchant fill:#fff,stroke:#1a7a8a,color:#000
    style JPM fill:#1a7a8a,stroke:#1a7a8a,color:#fff
    style API fill:#d4f0f0,stroke:#1a7a8a,color:#000
    style NAPI fill:#fff,stroke:#1a7a8a,color:#000
```

### Getting the report URL

Generating a report doesn't return a link to it. `POST /api/v1/reports` only starts the run. To get a URL for viewing the report, make a second call to the report details endpoint once the run finishes:

1. `POST /api/v1/reports` to generate the report, then keep the returned `reportId`.
2. Wait until the run completes: poll `GET /api/v1/reports/{reportId}` or wait for a `reportStatusNotification` (see `jpm-notifications`).
3. `GET /api/v1/reports/{reportId}`. The fields under **`reportDetails.url`** in the response hold the URL for viewing the report.

Tell the merchant about this second call when you build or explain a Reporting integration. Code that stops after the `POST` has no way to show the user their report. If the merchant wants the file contents rather than a link, use `GET /api/v1/report-files/{reportId}` instead (see [Report Files](#report-files)).

## Relevant Documentation

##### Reporting

- [Report types](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Freporting%2Freport-types.md)
- [Reporting groups](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Freporting%2Freporting-groups.md) Let one report cover a set of entities instead of listing `entityIds` per call.
- [Attribute glossary](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Freporting%2Fattribute-catalogue.md) Valid values and definitions for attributes in the 3000 series report types.
- [Pagination](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Freporting%2Fpagination.md) Retrieve long-running reports without exceeding time-out limits.
- [Notifications](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Freporting%2Fnotifications.md) Integrate with the Notifications API to receive report status updates.
- [Testing](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Freporting%2Ftesting.md) Downloadable sample reports for creating test scenarios.

###### Integration options

- [Quick integration](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Freporting%2Fintegration-options%2Fquick-integration.md) Quickly integrate the Reporting API using preset reports.
- [Custom integration](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Freporting%2Fintegration-options%2Fcustom-integration.md) Customize your reports to retrieve only the information you require at the schedule of your choosing.

###### Report configurations

- [Advanced customizations](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Freporting%2Freport-configurations%2Fadvanced-customizations.md) Advanced configuration options, including aliases, aggregates, and calculated fields.
- [Scheduled and ad hoc](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Freporting%2Freport-configurations%2Fscheduled-and-adhoc.md) Scheduling options for ad hoc and recurring reports.

###### Preset reports

- [Preset reports](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Freporting%2Fpreset-reports%2Foverview.md) Pre-configured reports tailored to provide meaningful information on the payment lifecycle.
- [Authorization report](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Freporting%2Fpreset-reports%2Fauthorization-report.md) Summary of successful and unsuccessful authorizations per merchant order number.
- [Deposit details report](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Freporting%2Fpreset-reports%2Fdeposit-details-report.md) Details of successful deposit transactions with Interchange & Assessment fees.
- [Deposit activity summary report](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Freporting%2Fpreset-reports%2Fdeposit-activity-summary-report.md) Summary of Sales/Refunds, Fees/Adjustments, and Funds Transfer Activity.
- [Financial activity summary report](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Freporting%2Fpreset-reports%2Ffinancial-activity-summary-report.md) Conveyed/settled transactions, chargebacks, interchange fees, processing fees.
- [Transaction fee details report](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Freporting%2Fpreset-reports%2Ftransaction-fee-details.md) Sale, refund, fee, and adjustment details per merchant order number.
- [Funded transaction fee details report](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Freporting%2Fpreset-reports%2Ffunded-transaction-fee-details-report.md) Transactions, associated fees, and net financial activity for a reporting period.
- [Charge summary report](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Freporting%2Fpreset-reports%2Fcharge-summary-report.md) Details of fees charged and associated tax.
- [Dispute details report](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Freporting%2Fpreset-reports%2Fdispute-details-report.md) Chargebacks, ECP Returns, and debit adjustments across the dispute lifecycle.
- [Exception details report](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Freporting%2Fpreset-reports%2Fexception-details-report.md) Successful and unsuccessful transaction details (Declined/Rejected/Cancelled/On-Hold).
- [Interchange qualification report](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Freporting%2Fpreset-reports%2Finterchange-qualification-report.md) Transactions with Interchange qualification codes and details.
- [Token provisioning & lifecycle report](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Freporting%2Fpreset-reports%2Ftoken-lifecycle-report.md) Token and cryptogram provisioning across payment methods.
- [Consumer profile overview report](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Freporting%2Fpreset-reports%2Fconsumer-profile-report.md) Consumer profile status, contact info, and payment methods.
- [Account updater report](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Freporting%2Fpreset-reports%2Faccount-updated-report.md) Account updater activity volume, update types, and methods.

###### How To

- [Get report types](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Freporting%2Fhow-to%2Fget-report-types.md) View available report types and get details for a specific report type.
- [Manage report configurations](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Freporting%2Fhow-to%2Fmanage-report-configurations.md) Create, update, and get details of report configurations.
- [Run reports](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Freporting%2Fhow-to%2Frun-reports.md) Run ad-hoc reports and check report run status.
- [Retrieve report details](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Freporting%2Fhow-to%2Fretrieve-report-details.md) Retrieve report details for all or individual reports.
- [Retrieve report files](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Freporting%2Fhow-to%2Fretrieve-reports.md) Download reports via JSON payload or Commerce Center portal.
- [Manage reporting groups](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Freporting%2Fhow-to%2Fmanage-reporting-groups.md) Create, retrieve, and update reporting groups.
- [Reconcile standard reports](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Freporting%2Fhow-to%2Freconcile-standard-reports.md) Reconcile data across the payment lifecycle using standard reports.

---

## Sample Requests

Use these sample requests to understand how to interact with the Reporting API and implement the quick and custom integration options. When generating code use these examples as a reference. Values in `{…}` are placeholders; `<…>` tokens are sent as-is.

### Report Types

**Get a list of available report types**

```http
GET /api/v1/report-types
Authorization: Bearer {accessToken}
Content-Type: application/json
request-id: {requestId}
merchant-id: {merchantId}
```

**Get details for a specific report type**

```http
GET /api/v1/report-types/{reportTypeId}
Authorization: Bearer {accessToken}
Content-Type: application/json
request-id: {requestId}
merchant-id: {merchantId}
```

### Report Configurations

**Get a list of available report configurations**

```http
GET /api/v1/report-configs
Authorization: Bearer {accessToken}
Content-Type: application/json
request-id: {requestId}
merchant-id: {merchantId}
```

**Get details for a specific report configuration**

```http
GET /api/v1/report-configs/{configId}
Authorization: Bearer {accessToken}
Content-Type: application/json
request-id: {requestId}
merchant-id: {merchantId}
```

**Update an existing report configuration**

```http
PUT /api/v1/report-configs/{configId}
Authorization: Bearer {accessToken}
Content-Type: application/json
request-id: {requestId}
merchant-id: {merchantId}

{
  "reportName": "{reportName}"
}
```

### Reports

**Generate a report (adhoc) — quick integration**

```http
POST /api/v1/reports
Authorization: Bearer {accessToken}
Content-Type: application/json
request-id: {requestId}
merchant-id: {merchantId}

{
  "entityType": "PE",
  "entityIds": ["{entityId}"],
  "reportSections": [
    { "sectionReportTypeId": "{reportTypeId}", "sectionReportTypeName": "{reportTypeName}" }
  ],
  "frequencyConfig": {
    "scheduleFrequency": "adhoc",
    "reportingPeriodStartTimestamp": "{YYYY-MM-DD HH:MM:SS}",
    "reportingPeriodEndTimestamp": "{YYYY-MM-DD HH:MM:SS}"
  }
}
```

**Generate a report (adhoc) — custom integration**

```http
POST /api/v1/reports
Authorization: Bearer {accessToken}
Content-Type: application/json
request-id: {requestId}
merchant-id: {merchantId}

{
  "entityIds": ["{entityId}"],
  "reportSections": [
    {
      "sectionReportTypeName": "{reportTypeName}",
      "sectionReportTypeId": "{reportTypeId}",
      "sectionSelectedFields": [
        { "alias": "{columnName}", "constantValueText": "{constantValue}" },
        { "reportAttributeName": "{attributeName}" }
      ],
      "sectionSortOrderList": [
        { "reportAttributeName": "{attributeName}", "sortOrderCode": "asc" }
      ],
      "sectionFilterAttributeList": [
        { "reportAttributeName": "{attributeName}", "filterAttributeCode": "=\"{value}\"" }
      ]
    }
  ],
  "fileDelimiter": ",",
  "csvColumnNameDisplayIndicator": true,
  "reportConfigurationName": "{configName}",
  "reportConfigStatus": "active",
  "reportName": "{reportName}",
  "frequencyConfig": {
    "scheduleFrequency": "adhoc",
    "reportingPeriodStartTimestamp": "{YYYY-MM-DD HH:MM:SS}",
    "reportingPeriodEndTimestamp": "{YYYY-MM-DD HH:MM:SS}"
  }
}
```

**Generate a report (daily) — custom integration**

```http
POST /api/v1/reports
Authorization: Bearer {accessToken}
Content-Type: application/json
request-id: {requestId}
merchant-id: {merchantId}

{
  "entityIds": ["{entityId}"],
  "reportSections": [
    {
      "sectionReportTypeName": "{reportTypeName}",
      "sectionReportTypeId": "{reportTypeId}",
      "sectionSelectedFields": [
        { "alias": "{columnName}", "constantValueText": "{constantValue}" },
        { "reportAttributeName": "{attributeName}" }
      ],
      "sectionSortOrderList": [
        { "reportAttributeName": "{attributeName}", "sortOrderCode": "asc" }
      ],
      "sectionFilterAttributeList": [
        { "reportAttributeName": "{attributeName}", "filterAttributeCode": "=\"{value}\"" }
      ]
    }
  ],
  "fileDelimiter": ",",
  "reportConfigurationName": "{configName}",
  "reportFileName": "{fileNamePrefix},<Processing Entity ID>.<Report Type>.<frequency>.<From Date YYYY-MM-DD>.<To Date YYYY-MM-DD>",
  "reportHeader": "HDSR,<Processing Entity ID>,<Report Type>,<frequency>,<From Date YYYY-MM-DD>,<To Date YYYY-MM-DD>,<Generation Date YYYY-MM-DD>,<Generation Time HH:MM:SS>",
  "fileHeader": "BEGIN,ProcessingEntityId=<Processing Entity ID>,Frequency=<frequency>",
  "fileTrailer": "END,ProcessingEntityId=<Processing Entity ID>,Frequency=<frequency>",
  "csvColumnNameDisplayIndicator": true,
  "reportConfigStatus": "active",
  "reportName": "{reportName}",
  "frequencyConfig": {
    "scheduleFrequency": "daily",
    "reportFileScheduledTime": "{HH:MM:SS}",
    "reportingPeriodStartTime": "{HH:MM:SS}"
  }
}
```

**Get a list of available reports** — optionally filter with `?reportStartDate={YYYY-MM-DD}`

```http
GET /api/v1/reports
Authorization: Bearer {accessToken}
Content-Type: application/json
request-id: {requestId}
merchant-id: {merchantId}
```

**Get details for a specific report.** Call this after generating a report: the URL to view it is under `reportDetails.url` in the response (see [Getting the report URL](#getting-the-report-url)).

```http
GET /api/v1/reports/{reportId}
Authorization: Bearer {accessToken}
Content-Type: application/json
request-id: {requestId}
merchant-id: {merchantId}
```

### Report Files

**Download a report file**

```http
GET /api/v1/report-files/{reportId}
Authorization: Bearer {accessToken}
Content-Type: application/json
request-id: {requestId}
merchant-id: {merchantId}
```

### Reporting Groups

**Get reporting groups**

```http
GET /v1/reporting-groups?groupType={groupType}&groupId={groupId}
Authorization: Bearer {accessToken}
Content-Type: application/json
request-id: {requestId}
merchant-id: {merchantId}
```

**Create a reporting group**

```http
POST /v1/reporting-groups
Authorization: Bearer {accessToken}
Content-Type: application/json
request-id: {requestId}
merchant-id: {merchantId}

{
  "reportingGroupName": "{groupName}",
  "reportingGroupDescription": "{groupDescription}",
  "childEntityInfo": [
    {
      "entityType": "PE",
      "entityIds": ["{entityId}"]
    }
  ]
}
```

**Update a reporting group**

```http
PATCH /v1/reporting-groups/{groupId}
Authorization: Bearer {accessToken}
Content-Type: application/json
request-id: {requestId}
merchant-id: {merchantId}

{
  "reportingGroupType": "RGPE",
  "reportingGroupStatus": "inactive"
}
```
