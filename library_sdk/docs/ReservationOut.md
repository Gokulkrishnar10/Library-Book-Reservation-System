# ReservationOut


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | 
**book_id** | **int** |  | 
**user_name** | **str** |  | 
**reservation_date** | **datetime** |  | 
**expires_at** | **datetime** |  | 

## Example

```python
from library_sdk.models.reservation_out import ReservationOut

# TODO update the JSON string below
json = "{}"
# create an instance of ReservationOut from a JSON string
reservation_out_instance = ReservationOut.from_json(json)
# print the JSON string representation of the object
print(ReservationOut.to_json())

# convert the object into a dict
reservation_out_dict = reservation_out_instance.to_dict()
# create an instance of ReservationOut from a dict
reservation_out_from_dict = ReservationOut.from_dict(reservation_out_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


