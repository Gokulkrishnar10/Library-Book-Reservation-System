# library_sdk.BooksApi

All URIs are relative to *http://localhost:8000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_book**](BooksApi.md#create_book) | **POST** /books/ | Create Book
[**get_book**](BooksApi.md#get_book) | **GET** /books/{book_id} | Get Book
[**list_books**](BooksApi.md#list_books) | **GET** /books/ | List Books
[**reserve_book**](BooksApi.md#reserve_book) | **POST** /books/{book_id}/reserve | Reserve Book


# **create_book**
> BookOut create_book(book_create)

Create Book

### Example


```python
import library_sdk
from library_sdk.models.book_create import BookCreate
from library_sdk.models.book_out import BookOut
from library_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = library_sdk.Configuration(
    host = "http://localhost:8000"
)


# Enter a context with an instance of the API client
with library_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = library_sdk.BooksApi(api_client)
    book_create = library_sdk.BookCreate() # BookCreate | 

    try:
        # Create Book
        api_response = api_instance.create_book(book_create)
        print("The response of BooksApi->create_book:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BooksApi->create_book: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **book_create** | [**BookCreate**](BookCreate.md)|  | 

### Return type

[**BookOut**](BookOut.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_book**
> BookDetail get_book(book_id)

Get Book

### Example


```python
import library_sdk
from library_sdk.models.book_detail import BookDetail
from library_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = library_sdk.Configuration(
    host = "http://localhost:8000"
)


# Enter a context with an instance of the API client
with library_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = library_sdk.BooksApi(api_client)
    book_id = 56 # int | 

    try:
        # Get Book
        api_response = api_instance.get_book(book_id)
        print("The response of BooksApi->get_book:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BooksApi->get_book: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **book_id** | **int**|  | 

### Return type

[**BookDetail**](BookDetail.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**404** | Book not found |  -  |
**422** | Validation error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_books**
> List[BookOut] list_books()

List Books

### Example


```python
import library_sdk
from library_sdk.models.book_out import BookOut
from library_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = library_sdk.Configuration(
    host = "http://localhost:8000"
)


# Enter a context with an instance of the API client
with library_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = library_sdk.BooksApi(api_client)

    try:
        # List Books
        api_response = api_instance.list_books()
        print("The response of BooksApi->list_books:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BooksApi->list_books: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**List[BookOut]**](BookOut.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **reserve_book**
> ReservationOut reserve_book(book_id, reserve_in)

Reserve Book

### Example


```python
import library_sdk
from library_sdk.models.reservation_out import ReservationOut
from library_sdk.models.reserve_in import ReserveIn
from library_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = library_sdk.Configuration(
    host = "http://localhost:8000"
)


# Enter a context with an instance of the API client
with library_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = library_sdk.BooksApi(api_client)
    book_id = 56 # int | 
    reserve_in = library_sdk.ReserveIn() # ReserveIn | 

    try:
        # Reserve Book
        api_response = api_instance.reserve_book(book_id, reserve_in)
        print("The response of BooksApi->reserve_book:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BooksApi->reserve_book: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **book_id** | **int**|  | 
 **reserve_in** | [**ReserveIn**](ReserveIn.md)|  | 

### Return type

[**ReservationOut**](ReservationOut.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**404** | Book not found |  -  |
**409** | No copies available or duplicate reservation |  -  |
**422** | Validation error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

