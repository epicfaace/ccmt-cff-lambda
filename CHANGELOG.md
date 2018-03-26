lambdas:
prod: 1.1.15
dev: 1.1.15
beta: 1.1.14

## 1.1.16 (tba)
- Allow couponCodes_used to use dictionaries instead:
```json
	"vfree234701": {
		"responses": {
			"id": 2,
			"id2": 3,
			"id3": 1
    },
    "participants": {
      "id1": 5
    }
	}
```
- And in couponCodes, countBy is allowed to be done:
```json
	"ticketfree234701": {
		"max": 30,
		"countBy": "participants",
		"amount": "-participants.race:5K * 5 - participants.race:10K * 10"
	}
```
- Fix doctests in util.

## 1.1.15
3/25/2018
- Fix email error logging in CloudWatch.
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