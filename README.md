The group assignment API handler

First I created a virtual Python environment using
> python3 -m venv .tnenv

To activate it run,
> source .tnenv/bin/activate  

To deactivate it run,
> deactivate

After activating .tnenv run,
> pip install -r requirements.txt

I marked group_assets as root in PyCharm. In production, the root would be the main backend handler 
calling this API.

Assumptions:
- user_id = owner_id, this is used to filter assets for the user calling the api.
- group_names are over-writable.
- Any new key-value (not in tags) in Assets data model is optional for api backwards compatibility

Design choices:
- For local testing, user's aws credentials need to be passed in the api request.
In production, user's credentials can be authenticated (fetched) using API gateway service  
- Single group vs multiple groups request in an api call 

    - single group api is clearer in coding but can be slower and needs multiple calls for more than one group assignments.
    - multiple groups api is more efficient and batch processed, but adds complexity and 
  needs error handling if one group fails, partially applying allowable groups.
The best design according to me is single grouping request api call as apis should be simple and fast to run.
  