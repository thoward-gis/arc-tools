ValidateDomains

Geoprocessing tool that checks attribute values in all fields in a feature class to ensure they adhere to the workspace domains. If errors are found, an ERROR_MESSAGE field is added to the input feature class where error messages are inserted.

### Parameters

**Input dataset** | *Table or Feature Class* | required input
* The input table or feature class.

**Ignore NULL Values** | *Boolean* | required input
* Optionally ignore NULL values if fields with domains applied.
