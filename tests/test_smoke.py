import stai


def test_package_version() -> None:
    assert stai.__version__ == "0.1.0a1"
