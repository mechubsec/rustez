"""classify_error keeps rustnetconf 0.19's transport errors typed as before."""

from rustez.exceptions import (
    ConnectAuthError,
    ConnectError,
    ConnectTimeoutError,
    TransportError,
    classify_error,
)

TRANSPORT = "netconf error: transport error: "


def classify(text):
    return type(classify_error(RuntimeError(text)))


def test_local_credential_errors_stay_auth_errors():
    assert classify(TRANSPORT + "credentials error: failed to read SSH key file") is ConnectAuthError


def test_local_setup_errors_keep_their_0_18_class():
    # 0.18 said "connection failed: failed to spawn ProxyCommand", a TransportError.
    assert classify(TRANSPORT + "configuration error: failed to spawn ProxyCommand `nc`") is (
        TransportError
    )


def test_a_broken_auth_exchange_is_not_rejected_credentials():
    text = TRANSPORT + "connection failed: password auth exchange failed: disconnected"
    assert classify(text) is TransportError


def test_connection_failures_keep_their_0_18_classes():
    assert classify(TRANSPORT + "connection failed: connection refused") is TransportError
    assert classify(TRANSPORT + "connection failed: connect timed out") is ConnectTimeoutError


def test_device_rpc_text_cannot_impersonate_a_transport_error():
    rpc = "netconf error: RPC error: server error: [OperationFailed] "
    for phrase in ("credentials error: x", "configuration error: x"):
        err = classify_error(RuntimeError(rpc + phrase))
        assert not isinstance(err, (ConnectError, TransportError)), (phrase, type(err))
    # The older generic "connect" substring rule still applies here, unchanged;
    # the new anchored branch must not turn it into a TransportError.
    assert classify(rpc + "connection failed: x") is ConnectError
