lambdas:
prod: 1.1.14
dev: 1.1.14
beta: 1.1.14

## 1.1.14 (server side only)
3/24/2018
- From here on forth, client & server & wp plugin are using different versioning schemes.
- Allow for dataOptions to give you custom aggregations on formResponses:
```json
  "shirt_size",
  {"title": "Cotton shirt sizes", "colName": "shirt_size", "filter": {"key": "race", "value": "Mela"}},
  {"title": "Tek shirt sizes", "colName": "shirt_size", "filter": {"key": "race", "value": ["5K", "10K", "Half Marathon"]}},
```
- Changed timeout for lambda functions from 5s to 10s