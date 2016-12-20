# Multi User Blog

This repository has code for multi user blog.
Since the code runs on Google App Engine, install `google-cloud-sdk` first.
The documents about google-cloud-sdk can be found at <https://cloud.google.com/sdk/docs/>.

## Usage

On the top directory, start the server:

```bash
$ dev_appserver.py .
```

Optionally, datastore path can be set when the server starts:

```bash
$ dev_appserver.py --datastore_path=[PATH_TO_DATASTORE] .
```


Once the server starts up, go to the browser and request:

```
http://localhost:8080/
```
