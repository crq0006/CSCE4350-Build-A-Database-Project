import main

def setup_function():
    main.database.clear()


def test_set_and_get():
    main.SET("name", "Realpersonguy")
    assert main.GET("name") == "Realpersonguy"


def test_overwrite():
    main.SET("name", "Realpersonguy")
    main.SET("name", "Alex")
    assert main.GET("name") == "Alex"


def test_delete():
    main.SET("name", "Realpersonguy")
    assert main.DEL("name") is True
    assert main.GET("name") is None


def test_exists():
    main.SET("name", "Realpersonguy")
    assert main.EXISTS("name") is True
    assert main.EXISTS("missing") is False