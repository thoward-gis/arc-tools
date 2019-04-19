PolylineEndpointsCalc

Geoprocessing tool that calculates the endpoint coordinates of ALL polyline types (single and multipart). Four new fields are added for Begin and End Point X, Y values and calculated values are inserted. User has option to save to new Feature Class instead of to the input.

### Parameters

**Input datasets** | *Feature Class* | required input
* The input polyline feature class. Can contain both single and multipart features.

**Output Feature Class** | *Feature Class* | optional input
* The output polyline feature class. User has option to make copy of input dataset and insert calculated values to the copy leaving the input dataset untouched.
