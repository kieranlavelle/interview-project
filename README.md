# interview-project


# formatting of responses.

One of the decisions made while writing the API was how to format responses. The choices were:
1. A format / view that is specific to the front-end. I.e converting the `cost_in_pence` into a string formatted with a pound sign so `2000` would become `£20.00`. 
2. A format where the response model that could easily be consumed by a front-end or another micro-service i.e having the `cost` represented as an integer, which is the cost per day in GBP pence.

The decision was made to go with format 2, as this keeps the code base flexible.