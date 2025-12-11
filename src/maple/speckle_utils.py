from os import getenv

from specklepy.api.client import Account, SpeckleClient
from specklepy.api.credentials import get_account_from_token, get_default_account
from specklepy.core.api.models import ModelWithVersions, Version
from specklepy.objects import Base
from specklepy.transports.server.server import ServerTransport

from specklepy.api import operations


def get_token() -> str | None:
    """
    Get the token to authenticate with Speckle.
    The token should be under the env variable 'SPECKLE_TOKEN'
    """

    token = getenv("SPECKLE_TOKEN")
    return token


def account_match_host(account: Account, host: str) -> bool:
    url = account.serverInfo.url
    host_url = host.replace("https://", "")
    host_url = host_url.replace("/", "")
    return url == host_url


def get_last_obj(project_id: str, model_id: str, *, logger) -> Base:
    """
    Gets the last object for the specified stream_id
    """
    logger.info("Getting object from speckle")
    host = getenv("SPECKLE_HOST")
    if not host:
        host = "https://app.speckle.systems"
    logger.info("Using Speckle host: %s", host)
    client = SpeckleClient(host)
    # authenticate the client with a token
    token = get_token()
    if token:
        logger.info("Auth with token")
        account = get_account_from_token(token, host)
        client.authenticate_with_token(token)
    else:
        account = get_default_account()
        if account and account_match_host(account, host):
            logger.info("Auth with default account")
            client.authenticate_with_account(account)
        else:
            logger.warning("No auth present")

    # project_id = get_project_id()
    # model_id = get_model_id()
    transport = ServerTransport(client=client, stream_id=project_id)

    models = client.model.get_models(project_id=project_id)
    found_model = next(filter(lambda x: x.id == model_id, models.items), None)
    if not found_model:
        raise Exception("Model not found: ", model_id)

    model: ModelWithVersions = client.model.get_with_versions(
        project_id=project_id, model_id=found_model.id
    )

    versions = model.versions.items
    if len(versions) == 0:
        raise Exception("Model contains no versions.")
    if type(versions[0]) is not Version:
        raise Exception("Type of element is not Model: ", type(versions[0]))
    last_obj_id = versions[0].referenced_object

    if not last_obj_id:
        raise Exception("No object_id")
    last_obj = operations.receive(obj_id=last_obj_id, remote_transport=transport)

    # cache the current obj
    # init(last_obj)
    return last_obj
