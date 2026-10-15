# BookDetail

Book with its currently active reservations (used by GET /books/{id}).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | 
**title** | **str** |  | 
**author** | **str** |  | 
**total_copies** | **int** |  | 
**available_copies** | **int** |  | 
**reservations** | [**List[ReservationOut]**](ReservationOut.md) |  | [optional] [default to []]

## Example

```python
from library_sdk.models.book_detail import BookDetail

# TODO update the JSON string below
json = "{}"
# create an instance of BookDetail from a JSON string
book_detail_instance = BookDetail.from_json(json)
# print the JSON string representation of the object
print(BookDetail.to_json())

# convert the object into a dict
book_detail_dict = book_detail_instance.to_dict()
# create an instance of BookDetail from a dict
book_detail_from_dict = BookDetail.from_dict(book_detail_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


