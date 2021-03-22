# Data loaders
## Simurg
### stations.py
Checks if station is valid

Usage:

`./stations.py irkj`

### ionospheric_series.py
Downloads series data from simurg.iszf.irk.ru

Arguments:

<table>
<tr><th>Argument</th><th>Description</th></tr>
<tr><td>site</td> <td>station</td></tr>
<tr><td>mail</td> <td>requesting email</td></tr>
<tr><td>folder </td> <td> data local destination</td></tr>
<tr><td>start-date, end-date </td> <td> date range of downloaded data (end-date default is datetime.today())</td></tr>
<tr><td>n-queries </td> <td> number of simultaneous queries</td></tr>
</table>
