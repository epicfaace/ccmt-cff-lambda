(outdated) -- look at the form in cff_beta.forms for most up-to-date coupon codes used in tests.
Set couponCodes equal to:
```json
{
  "cff-unittest-coupon-code-maxed-out": {
    "max": 0,
    "amount": "-$total"
  },
  "cff-unittest-coupon-code-countBy-responses": {
    "max": -1,
    "amount": "-$total"
  },
  "cff-unittest-coupon-code-countBy-participants": {
    "max": 0,
    "countBy": "participants",
    "amount": "-participants.race:5K * 5 - participants.race:10K * 10"
  },
  "cff-unittest-coupon-code-countBy-maxed-out-at-30": {
    "amount": "-$total",
    "max": 30,
    "countBy": "participants"
  },
  "test": {
    "max": 4,
    "countBy": "participants",
    "amount": "-participants.race:5K * 5 - participants.race:10K * 10"
  },
  "sponsor": {
    "max": -1,
    "amount": "5000"
  }
}
```
Set couponCodes_used equal to:
```json
{
  "cff-unittest-coupon-code-countBy-maxed-out-at-30": {
    "participants": {
      "id1": 25,
      "id2": 5
    }
  }
}
```