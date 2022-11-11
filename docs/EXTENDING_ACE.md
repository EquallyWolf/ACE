<div align="center">

# Extending ACE

</div>

This document is intended to help you extend ACE. It will cover the following topics:

-   [Adding a new intent](#adding-a-new-intent)
-   [Adding a new action](#adding-a-new-action)

## Adding a new intent

To add a new intent, a selection of examples must be added to the [intents.csv](data/intents/intents.csv) file. The format of the file is as follows:

```csv
intent,example
```

Then configure the (base_config.cfg) spaCy config file with the desired settings. For more information on the config file, see the [spaCy documentation](https://spacy.io/usage/training#config).

The [ai.toml](config/ai.toml) file must also be configured with the desired settings, taking care to set the `method` option to `train`.

Then run the training by running the following command:

```shell
$ poetry run python -m "ace.ai.models"
```

## Adding a new action

To add a new response/action, add a new file to the [intents.py](ace/ai/intents.py) file. The format of the file is as follows:

```python
@_register(requires_text=True)
def intent_name(text: str) -> str:
    """The response to the intent."""
    return "The response to the intent."

@_register()
def intent_name() -> str:
    """The response to the intent."""
    return "The response to the intent."
```

The intent must return a string response.

If the intent requires text, the `requires_text` parameter for `@_register` must be set to `True`, which will allow the passing of the text to the intent for further processing.
