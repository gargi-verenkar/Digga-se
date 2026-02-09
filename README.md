# events

Periodically extracts cultural events data from multiple external APIs.

## Solution Architecture

### 1. Fetchers
Nightly scheduled jobs trigger a number of fetchers (Cloud Functions), which fetches events from a number of different
event sources.

Each fetcher:
 - read the data from source system
 - map source entities to [internal_event_schema](cloud_functions/events/schemas/internal_event_schema.json)
 - apply filters to skip existing unchanged events and invalid events
 - send message to `events` Pub/Sub topic

### 2. Processing
Cloud Function `process_event` process each event to assign:
 - category
 - venue
 - themes
 - genres and subgenres

and send it to `sync_to_external` Pub/Sub topic.

### 3. Publishing
Cloud Function `push_to_bubble`:
 - map event format from internal to external schema
 - check if the event is valid
 - send the event to rest api endpoint

## Cloud Scheduler Jobs
Scheduled fetchers can be found [here](https://console.cloud.google.com/cloudscheduler?inv=1&invt=AbeOZw&project=digga-se&supportedpurview=project).


## Fetcher failed policy
Alerting policy for failed fetchers can be found [here](https://console.cloud.google.com/monitoring/alerting/policies/2548683877675974779?inv=1&invt=AbeOZw&project=digga-se&supportedpurview=project).

## Venue REST API endpoints
There are [create_venue](cloud_functions/create_venue) and [update_venue](cloud_functions/update_venue) endpoints that allow to create and change venue record in the database.

## Deployment

### Deploy fetchers
Execute Cloud Build config for fetchers:
```shell
gcloud beta builds submit --config cloudbuild-fetchers.yaml \
                          --service-account projects/digga-se/serviceAccounts/cloud-build-sa@digga-se.iam.gserviceaccount.com
```

### Deploy `process_event` function
Execute Cloud Build config for `process_event` function:
```shell
gcloud beta builds submit --config cloudbuild-process_event.yaml \
                          --service-account projects/digga-se/serviceAccounts/cloud-build-sa@digga-se.iam.gserviceaccount.com
```

### Deploy `push_to_bubble` function
Execute Cloud Build config for `push_to_bubble` function:
```shell
gcloud beta builds submit --config cloudbuild-push_to_bubble.yaml \
                          --service-account projects/digga-se/serviceAccounts/cloud-build-sa@digga-se.iam.gserviceaccount.com
```

### Deploy venue api
Execute Cloud Build:
```shell
gcloud beta builds submit --config cloudbuild.yaml \
                          --service-account projects/digga-se/serviceAccounts/cloud-build-sa@digga-se.iam.gserviceaccount.com
```
