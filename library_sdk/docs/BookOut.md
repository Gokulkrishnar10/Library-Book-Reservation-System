# BookOut


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | 
**title** | **str** |  | 
**author** | **str** |  | 
**total_copies** | **int** |  | 
**available_copies** | **int** |  | 

## Example

```python
from library_sdk.models.book_out import BookOut

# TODO update the JSON string below
json = "{}"
# create an instance of BookOut from a JSON string
book_out_instance = BookOut.from_json(json)
# print the JSON string representation of the object
print(BookOut.to_json())

# convert the object into a dict
book_out_dict = book_out_instance.to_dict()
# create an instance of BookOut from a dict
book_out_from_dict = BookOut.from_dict(book_out_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


