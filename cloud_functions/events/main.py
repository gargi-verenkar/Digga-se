import os

import flask
import functions_framework

from raw_events.vara_konserthus.fetcher import VaraKonserhusFetcher
from raw_events.axs.fetcher import AxsFetcher
from raw_events.billetto.fetcher import BillettoFetcher
from raw_events.eventim.fetcher import EventimFetcher
from raw_events.folkoperan.fetcher import FolkoperanFetcher
from raw_events.gronalund.fetcher import GronaLundFetcher
from raw_events.kulturbiljetter.fetcher import KulturbiljetterFetcher
from raw_events.kulturhusetstadsteatern.fetcher import KulturhusetstadsteaternFetcher
from raw_events.nortic.fetcher import NorticFetcher
from raw_events.ravinen.fetcher import RavinenFetcher
from raw_events.reginateatern.fetcher import ReginateaternFetcher
from raw_events.scalateatern.fetcher import ScalaTeaternFetcher
from raw_events.storateatern.fetcher import StoraTeaternFetcher
from raw_events.svenskakyrkan.fetcher import SvenskakyrkanFetcher
from raw_events.ticketmaster.fetcher import TicketmasterFetcher
from raw_events.tickster.fetcher import TicksterFetcher
from raw_events.engeln.fetcher import EngelnFetcher
from raw_events.glennmillercafe.fetcher import GlennMillerCafeFetcher
from raw_events.biocapitol.fetcher import BioCapitolFetcher
from raw_events.skansen.fetcher import SkansenFetcher
from raw_events.berwaldhallen.fetcher import BerwaldhallenFetcher
from raw_events.sofiero.fetcher import SofieroFetcher
from raw_events.helsingborg_arena.fetcher import HelsingborgArenaFetcher
from raw_events.helsingborg_stadsteater.fetcher import HelsingborgStadsteaterFetcher
from raw_events.helsingborg_konserthus.fetcher import HelsingborgKonserthusFetcher

@functions_framework.http
def fetch_axs(request: flask.Request):
    fetcher = AxsFetcher(
        gcp_project=get_env_var("GCP_PROJECT"),
        pubsub_topic=get_env_var("PUBSUB_TOPIC"),
        axs_api_key=get_env_var("AXS_API_KEY")
    )
    fetcher.fetch_events()
    return flask.Response(status=200)


@functions_framework.http
def fetch_billetto(request: flask.Request):
    fetcher = BillettoFetcher(
        gcp_project=get_env_var("GCP_PROJECT"),
        pubsub_topic=get_env_var("PUBSUB_TOPIC"),
        api_key=get_env_var("BILLETTO_API_KEY")
    )
    fetcher.fetch_events()
    return flask.Response(status=200)


@functions_framework.http
def fetch_eventim(request: flask.Request):
    fetcher = EventimFetcher(
        gcp_project=get_env_var("GCP_PROJECT"),
        pubsub_topic=get_env_var("PUBSUB_TOPIC"),
        username=get_env_var("EVENTIM_USERNAME"),
        password=get_env_var("EVENTIM_PASSWORD")
    )
    fetcher.fetch_events()
    return flask.Response(status=200)


@functions_framework.http
def fetch_folkoperan(request: flask.Request):
    fetcher = FolkoperanFetcher(
        gcp_project=get_env_var("GCP_PROJECT"),
        pubsub_topic=get_env_var("PUBSUB_TOPIC"),
        api_key=get_env_var("FOLKOPERAN_API_KEY")
    )
    fetcher.fetch_events()
    return flask.Response(status=200)


@functions_framework.http
def fetch_gronalund(request: flask.Request):
    fetcher = GronaLundFetcher(
        gcp_project=get_env_var("GCP_PROJECT"),
        pubsub_topic=get_env_var("PUBSUB_TOPIC")
    )
    fetcher.fetch_events()
    return flask.Response(status=200)


@functions_framework.http
def fetch_kulturbiljetter(request: flask.Request):
    fetcher = KulturbiljetterFetcher(
        gcp_project=get_env_var("GCP_PROJECT"),
        pubsub_topic=get_env_var("PUBSUB_TOPIC"),
        api_key=get_env_var("KULTURBILJETTER_API_KEY")
    )
    fetcher.fetch_events()
    return flask.Response(status=200)


@functions_framework.http
def fetch_kulturhusetstadsteatern(request: flask.Request):
    fetcher = KulturhusetstadsteaternFetcher(
        gcp_project=get_env_var("GCP_PROJECT"),
        pubsub_topic=get_env_var("PUBSUB_TOPIC")
    )
    fetcher.fetch_events()
    return flask.Response(status=200)


@functions_framework.http
def fetch_nortic(request: flask.Request):
    fetcher = NorticFetcher(
        gcp_project=get_env_var("GCP_PROJECT"),
        pubsub_topic=get_env_var("PUBSUB_TOPIC")
    )
    fetcher.fetch_events()
    return flask.Response(status=200)


@functions_framework.http
def fetch_ravinen(request: flask.Request):
    fetcher = RavinenFetcher(
        gcp_project=get_env_var("GCP_PROJECT"),
        pubsub_topic=get_env_var("PUBSUB_TOPIC")
    )
    fetcher.fetch_events()
    return flask.Response(status=200)


@functions_framework.http
def fetch_reginateatern(request: flask.Request):
    fetcher = ReginateaternFetcher(
        gcp_project=get_env_var("GCP_PROJECT"),
        pubsub_topic=get_env_var("PUBSUB_TOPIC"),
        username=get_env_var("REGINATEATERN_USERNAME"),
        password=get_env_var("REGINATEATERN_PASSWORD")
    )
    fetcher.fetch_events()
    return flask.Response(status=200)


@functions_framework.http
def fetch_scalateatern(request: flask.Request):
    fetcher = ScalaTeaternFetcher(
        gcp_project=get_env_var("GCP_PROJECT"),
        pubsub_topic=get_env_var("PUBSUB_TOPIC")
    )
    fetcher.fetch_events()
    return flask.Response(status=200)


@functions_framework.http
def fetch_storateatern(request: flask.Request):
    fetcher = StoraTeaternFetcher(
        gcp_project=get_env_var("GCP_PROJECT"),
        pubsub_topic=get_env_var("PUBSUB_TOPIC")
    )
    fetcher.fetch_events()
    return flask.Response(status=200)


@functions_framework.http
def fetch_svenskakyrkan(request: flask.Request):
    fetcher = SvenskakyrkanFetcher(
        gcp_project=get_env_var("GCP_PROJECT"),
        pubsub_topic=get_env_var("PUBSUB_TOPIC"),
        ocp_api_key=get_env_var("SVENSKAKYRKAN_OCP_API_KEY"),
        svk_api_key=get_env_var("SVENSKAKYRKAN_SVK_API_KEY")
    )
    fetcher.fetch_events()
    return flask.Response(status=200)


@functions_framework.http
def fetch_ticketmaster(request: flask.Request):
    fetcher = TicketmasterFetcher(
        gcp_project=get_env_var("GCP_PROJECT"),
        pubsub_topic=get_env_var("PUBSUB_TOPIC"),
        api_key=get_env_var("TICKETMASTER_API_KEY"),
        new_api_key=get_env_var("TICKETMASTER_INTERNATIONAL_DISCOVERY_API_KEY")
    )
    fetcher.fetch_events()
    return flask.Response(status=200)


@functions_framework.http
def fetch_tickster(request: flask.Request):
    fetcher = TicksterFetcher(
        gcp_project=get_env_var("GCP_PROJECT"),
        pubsub_topic=get_env_var("PUBSUB_TOPIC"),
        api_key=get_env_var("TICKSTER_API_KEY")
    )
    fetcher.fetch_events()
    return flask.Response(status=200)


@functions_framework.http
def fetch_vara_konserthus(request: flask.Request):
    fetcher = VaraKonserhusFetcher(
        gcp_project=get_env_var("GCP_PROJECT"),
        pubsub_topic=get_env_var("PUBSUB_TOPIC"),
        api_key=get_env_var("VARA_KONSERTHUS_API_KEY")
    )
    fetcher.fetch_events()
    return flask.Response(status=200)

@functions_framework.http
def fetch_glennmillercafe(request: flask.Request):
    fetcher = GlennMillerCafeFetcher(
        gcp_project=get_env_var("GCP_PROJECT"),
        pubsub_topic=get_env_var("PUBSUB_TOPIC"),
    )
    fetcher.fetch_events()
    return flask.Response(status=200)

@functions_framework.http
def fetch_engeln(request: flask.Request):
    fetcher = EngelnFetcher(
        gcp_project=get_env_var("GCP_PROJECT"),
        pubsub_topic=get_env_var("PUBSUB_TOPIC"),
    )
    fetcher.fetch_events()
    return flask.Response(status=200)

@functions_framework.http
def fetch_biocapitol(request: flask.Request):
    fetcher = BioCapitolFetcher(
        gcp_project=get_env_var("GCP_PROJECT"),
        pubsub_topic=get_env_var("PUBSUB_TOPIC"),
        api_key=get_env_var("BIO_CAPITOL_KEY"),
    )
    fetcher.fetch_events()
    return flask.Response(status=200)

@functions_framework.http
def fetch_skansen(request: flask.Request):
    fetcher = SkansenFetcher(
        gcp_project=get_env_var("GCP_PROJECT"),
        pubsub_topic=get_env_var("PUBSUB_TOPIC"),
    )
    fetcher.fetch_events()
    return flask.Response(status=200)

@functions_framework.http
def fetch_berwaldhallen(request: flask.Request):
    fetcher = BerwaldhallenFetcher(
        gcp_project=get_env_var("GCP_PROJECT"),
        pubsub_topic=get_env_var("PUBSUB_TOPIC"),
    )
    fetcher.fetch_events()
    return flask.Response(status=200)

@functions_framework.http
def fetch_sofiero(request: flask.Request):
    fetcher = SofieroFetcher(
        gcp_project=get_env_var("GCP_PROJECT"),
        pubsub_topic=get_env_var("PUBSUB_TOPIC"),
    )
    fetcher.fetch_events()
    return flask.Response(status=200)

@functions_framework.http
def fetch_helsingborg_arena(request: flask.Request):
    fetcher = HelsingborgArenaFetcher(
        gcp_project=get_env_var("GCP_PROJECT"),
        pubsub_topic=get_env_var("PUBSUB_TOPIC"),
    )
    fetcher.fetch_events()
    return flask.Response(status=200)

@functions_framework.http
def fetch_helsingborg_stadsteater(request: flask.Request):
    fetcher = HelsingborgStadsteaterFetcher(
        gcp_project=get_env_var("GCP_PROJECT"),
        pubsub_topic=get_env_var("PUBSUB_TOPIC"),
    )
    fetcher.fetch_events()
    return flask.Response(status=200)

@functions_framework.http
def fetch_helsingborg_konserthus(request: flask.Request):
    fetcher = HelsingborgKonserthusFetcher(
        gcp_project=get_env_var("GCP_PROJECT"),
        pubsub_topic=get_env_var("PUBSUB_TOPIC"),
    )
    fetcher.fetch_events()
    return flask.Response(status=200)

def get_env_var(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise EnvironmentError(f"Missing required environment variable: {name}")
    return value

if __name__ == "__main__":
    
    fetchers = [
        SofieroFetcher("digga-se", "events"),
        HelsingborgArenaFetcher("digga-se", "events"),
        HelsingborgStadsteaterFetcher("digga-se", "events"),
        HelsingborgKonserthusFetcher("digga-se", "events")
    ]

    for f in fetchers:
        print(f"--- Testing: {f.__class__.__name__} ---")
        f.fetch_events()