#!/bin/bash
# Script to set all required environment variables to be able to debug the different fetchers locally
# Note that you have to be logged in into GCP
# Before running some files locally, you can load the environment variables by doing:
# source set_env_variables.sh

export GCP_PROJECT="digga-se"
export PUBSUB_TOPIC="events"
export DB_NAME="events"
export DB_USER=$(gcloud secrets versions access latest --secret=db_user)
export DB_PASSWORD=$(gcloud secrets versions access latest --secret=db_password)
export DB_INSTANCE_CONNECTION_NAME=$(gcloud secrets versions access latest --secret=db_instance_connection_name)
export AXS_API_KEY=$(gcloud secrets versions access latest --secret=axs_api_key)
export BILLETTO_API_KEY=$(gcloud secrets versions access latest --secret=billetto_api_key)
export EVENTIM_USERNAME=$(gcloud secrets versions access latest --secret=eventim_username)
export EVENTIM_PASSWORD=$(gcloud secrets versions access latest --secret=eventim_password)
export FOLKOPERAN_API_KEY=$(gcloud secrets versions access latest --secret=folkoperan_api_key)
export KULTURBILJETTER_API_KEY=$(gcloud secrets versions access latest --secret=kulturbiljetter_api_key)
export REGINATEATERN_USERNAME=$(gcloud secrets versions access latest --secret=reginateatern_username)
export REGINATEATERN_PASSWORD=$(gcloud secrets versions access latest --secret=reginateatern_password)
export SVENSKAKYRKAN_OCP_API_KEY=$(gcloud secrets versions access latest --secret=svenskakyrkan_ocp_api_key)
export SVENSKAKYRKAN_SVK_API_KEY=$(gcloud secrets versions access latest --secret=svenskakyrkan_svk_api_key)
export TICKETMASTER_API_KEY=$(gcloud secrets versions access latest --secret=ticketmaster_api_key)
export TICKETMASTER_INTERNATIONAL_DISCOVERY_API_KEY=$(gcloud secrets versions access latest --secret=ticketmaster_international_disc_api_key
)
export TICKSTER_API_KEY=$(gcloud secrets versions access latest --secret=tickster_api_key)
export VARA_KONSERTHUS_API_KEY=$(gcloud secrets versions access latest --secret=vara_konserthus_api_key)
export OPENAI_API_KEY=$(gcloud secrets versions access latest --secret=openai_api_key)
export BIO_CAPITOL_KEY=$(gcloud secrets versions access latest --secret=bio_capitol_key)

echo "Environment variables set"