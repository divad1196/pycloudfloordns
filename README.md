# README

This repository wraps the cloudfloordns API into a python library.
The set of features supported is limited to our current usage and may grow accordingly to our needs.

## Features
All features can be accessed through the `Client` class:
* Generic get/post/patch/delete methods that handle the result errors
* records: all CRUD operations + `.is_same(...)` method to compare 2 records (see limitations)
* domains: list all domains

NOTE: All objects (records/domains/...) are validated and wrapped inside a python class for convenience.

```python
from cloudfloordns import Client, Record, Domain

client = Client()

domains = client.domains.list()
mydomain = domains[0]

my_record = Record(...)
client.records.create(mydomain, my_record)

client.records.list(mydomain)
```

### Known Limitations
* The API is really old and still use Swagger v1 (Swagger v2 has been out since [2014-09-08](https://swagger.io/specification/v2/))
* Authentication parameters are passed in the body.
  * This is considered unsafe since the body can easily be logged (same for the url). The credentials should have been passed in HTTP headers.
  * The standard does not allow to send a body with a GET method, some libraries may therefore not send the body.
* The [online documentation](https://apiv2.mtgsy.net/docs/v1) contains wrong/incomplete informations
  * Wrong types (e.g. IDs are said to be of type `int` when they are `str`).
  * Required parameters are not explicited
  * Create operation (POST method) acts **silently** as an Update operation (PATCH method) on conflict instead of throwing an error.

  The current result is obtained through manual experimentation
* The Create/Update/Delete operations don't return any information about the remote data (e.g. New state, including the generated ID)
  => The only workaround to retrieve the changes is to make a request
* The API doesn't provide a way to retrieve a single object (domain/record/...) by its ID. The only way is to ask for all objects and filter them based on unique groupe of attributes.
  This limitation force us to provide a comparison method `.is_same(...)` to be able to check the remote objects and identify the corresponding one.
  ```python
  client = Client()
  my_record = Record(...)
  client.records.create("mydomain.com", my_record)

  remote_records = client.records.list("mydomain.com")
  created_record = next((r for r in remote_records if my_record.is_same(r)), None)
  ```
  This consume a lot more bandwidth than required (hopefully, the server response is fast enough).
  The results should be cached as much as possible

## Run the project:

1. Enter your virtual environment doing `poetry shell` (only need to do that once in the terminal)
2. Run the project
   ```python
   python cloudfloordns
   ```

## Develop
* Add a library using `poetry add mypackage` (same as you would do with `pip install mypackage`)
* Edit only the sources in `cloudfloordns/`
* Check our online documentation for useful libraries.
