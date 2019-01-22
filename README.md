# asset_store_full
A RESTFul API for managing assets such as satellites, antennas etc

## Dependencies
1. Python (3.5.0 or higher)
2. pip (18.1 or higher)
2. Django (2.1.4 or higher)
3. Django REST Framework (3.9.0 or higher)

## Install instructions
1. Clone this repository locally
2. The permissions on the bash shell scripts need to changed to 755 with command `chmod 755 *.sh`
3. Execute the script `install.sh`
    - Python is expected to be installed by the user
    - OPTIONAL: if pip is not up-to-date, upgrade pip with command `pip install --upgrade pip`
    - This script installs all the dependencies except python and pip, using pip
    - This script installs the missing required packages, if your system already has the required package installed, it skips the installation of that package
  
## Scope of the API Input and Output
The API is only tested with JSON input and output. XML as input is NOT tested.

## API Methods allowed
1. `GET /api/v1/assets/`: This request with the specified URL retrieves ALL the assets in the asset store. Make a note of the '/' at the end of URL, it's required. May return additional optional attributes for each asset in the response.
2. `GET /api/v1/assets/<asset_name>`: This request with the specified URL retrieves a single asset with the asset_name specified in the URL.  May return additional optional attributes for the asset in the response.
3. `POST /api/v1/assets/`: This request with the specified URL attempts to create ALL of the assets from the JSON payload or nothing in case of one or more errors in the payload. Make a note of the '/' at the end of the URL, it's required.
4. `PUT /api/v1/assets/<asset_name>`: This request allows for adding/updating optional attributes (`diameter`,`radome`,`gain`) to a single asset

## API Methods NOT allowed
1. `PUT /api/v1/assets/`: This type of requests is NOT allowed. Attempting this request will yield a response of `405 Method Not Allowed`
2. `DELETE /api/v1/assets/`: This type of requests is NOT allowed. Assets are not allowed to be deleted as per the specification of the problem
3. `DELETE /api/v1/assets/<asset_name>`: This type of requests is NOT allowed. Assets are not allowed to be deleted as per the specification of the problem

## API Authentication and Authorization
1. Authentication: As per the specification, there is no authentication scheme implemented. However, as per the spec, `X-User` header is required for the POST request
2. Authorization: Only an admin user is allowed to POST assets 

## API Design Choices
1. The API is designed such that it allows for multiple versions that may or may not be backwards compatible. Hence the version number in the path. This design choice is made to make clients of the API aware of different versions and potential compatibility issues.
2. POST request handler is implemented following an ALL or Nothing paradigm. If all the assets in the payload are valid, the handler performs a BULK creation of all of the assets from the payload. But if even one asset in the payload is not valid, the entire payload is rejected.
3. Response for the POST method contains one to one mapping from the request payload. The response payload indicates the asset_name and errors (a list of errors) for each of the asset from the request. If there are valid assets in the request payload, the validity is indicated in the errors field for asset_name, but the asset is not created in the system because of other assets in the request being invalid.
4. Also the order errors in the response payload for POST request preserves the order of assets given in the request payload, this choice is made to make it easier for the clients to process the errors.
5. The paradigm used for requests is to allow for different HTTP methods to dictate which one of (Create, Read, Update, and Delete) methods on the asset resource in the asset store. Because of this different class based views are defined for different HTTP methods. A single base view class each for URLs `/api/v1/assets/` and `/api/v1/assets/<asset_name>` is defined. Each of these base view class redirects the request to class based view defined for the corresponding HTTP method. 
6. `PUT` (bulk update) and `DELETE` methods on the path `/api/v1/assets/` path are implemented but the handlers for these methods just return a `405 Method Not Allowed` response. This is because the bulk update and deletion of an asset are not allowed per the specification of the problem.
7. `PUT` (individual asset update) on the path `/api/v1/assets/<asset_name>` is allowed as per the specification to either add new valid attributes for an asset or to update an existing attribute for an asset. If the payload contains even a single invalid attribute, the whole request gets rejected.
8. `GET` for the path `/api/v1/assets` allows for filtering based on `asset_class` or `asset_type` attributes. Response may contain asset details such as `diameter`, `radome` or `gain`.
9. `GET` for the path `/api/v1/assets/<asset_name>` returns asset details such as `diameter`, `radome` or `gain` when applicable and available.

## Database for the API
The database used for this API is the Django provided SQLite database. 

## Database design
1. Asset Details: There are additional optional attributes defined for an asset based on the asset_class of the asset. These attributes are captured in a table `AssetDetail`. AssetDetail is defined per Asset. There could be mutltiple AssetDetail entries per Asset. 
2. Asset Details Metadata: This table contains definitions for valid attributes and data types of attributes stored in AssetDetail table. The attributes and their data types are defined per asset_class. This table is created during database initialization and the definitions are static.

## Running the API server
The script `runserver.sh` is provided as a convenience to run the server for this API application. This script attempts to create and migrate the necessary database schema for the API before starting up the server.

## Testing the API
1. To verify the basic correctness of the implementation, some tests are provided in `tests.py` inside the `assets` application. To sanity check the installation of the API, you can run the command `python manage.py test`.
2. A postman collection (`Asset_Store_Full_API.postman_collection`) is provided at the root of this repository to easily verify the API. This collection expects the API to be deployed on port 8000 on your local server (127.0.0.1). The collection contains requests for CRUD HTTP methods (POST, GET, PUT, DELETE).

## Known Bugs
1. On windows OS, the first time a PUT request is made with any body content, the server does not respond. If you make this request again, the reponse received is the expected `405 Method Not Allowed`. This is a known bug and will be resolved at a future time. Note that if the PUT request does NOT contain any body this problem does not arise.
