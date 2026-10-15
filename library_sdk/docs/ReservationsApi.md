# library_sdk.ReservationsApi

All URIs are relative to *http://localhost:8000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**cancel_reservation**](ReservationsApi.md#cancel_reservation) | **DELETE** /reservations/{reservation_id} | Cancel Reservation


# **cancel_reservation**
> cancel_reservation(reservation_id)

Cancel Reservation

### Example


```python
import library_sdk
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
    api_instance = library_sdk.ReservationsApi(api_client)
    reservation_id = 56 # int | 

    try:
        # Cancel Reservation
        api_instance.cancel_reservation(reservation_id)
    except Exception as e:
        print("Exception when calling ReservationsApi->cancel_reservation: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **reservation_id** | **int**|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Successful Response |  -  |
**404** | Reservation not found |  -  |
**422** | Validation error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

