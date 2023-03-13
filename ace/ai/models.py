import os
from dataclasses import dataclass
from pathlib import Path
from typing import Union
from statistics import stdev, mean

import spacy
import toml
from spacy.tokens import DocBin
from tqdm import tqdm

from ace.ai import data
from ace.utils import Logger

SEED = 42
CONFIG_PATH = os.path.join("config", "ai.toml")

logger = Logger.from_toml(config_file_name="logs.toml", log_name="models")


@dataclass
class IntentClassifierModelConfig:
    """
    A dataclass to hold the configuration for the intent classifier.

    Attributes
    ----------
        spacy_model: str
            The name of the spaCy model to use.

        data_path: Path
            The path to the dataset file.

        train_percentage: float
            The percentage of the dataset to use for training.

        train_data_save_path: str
            The path to save the training data to.

        test_data_save_path: str
            The path to save the test data to.

        rebuild_config: bool
            Whether to rebuild the configuration or not.

        rebuild_data: bool
            Whether to rebuild the data or not.

        best_model_location: str
            The path to save the best model to.

        threshold: float
            The threshold to use for the intent classifier.

        base_config: str
            The path to the base configuration file.

        output_dir: str
            The path to save the model to.

        mode: str
            Whether to run the model in train or test mode.

    Methods
    ---------
        from_toml(path: Union[str, Path]) -> IntentClassifierModelConfig
            Load the configuration from the TOML file.
    """

    spacy_model: str = "en"
    data_path: str = "data/intents/intents.csv"
    train_percentage: float = 0.5
    train_data_save_path: str = "data/intents/train.spacy"
    valid_data_save_path: str = "data/intents/dev.spacy"
    rebuild_config: bool = False
    rebuild_data: bool = False
    best_model_location: str = "models/intents/model-best"
    threshold: float = 0.5
    base_config: str = "data/intents/base_config.cfg"
    output_dir: str = "models/intents"
    mode: str = "train"

    @staticmethod
    def from_toml(
        config_file: Union[str, None] = None
    ) -> "IntentClassifierModelConfig":
        """
        Load the configuration from a TOML file. Leave the config_file parameter
        empty to load the configuration from the default location: config/ai.toml.

        returns: An IntentClassifierModelConfig object.
        """
        config = toml.load(config_file or CONFIG_PATH)
        return IntentClassifierModelConfig(**config["IntentClassifierModelConfig"])


@dataclass
class NERModelConfig:
    """
    A dataclass to hold the configuration for the NER model.

    Attributes
    ----------
        spacy_model: str
            The name of the spaCy model to use.
    """

    spacy_model: str = "en_core_web_md"

    @staticmethod
    def from_toml(config_file: Union[str, None] = None) -> "NERModelConfig":
        """
        Load the configuration from a TOML file. Leave the config_file parameter
        empty to load the configuration from the default location: config/ai.toml.

        returns: An NERModelConfig object.
        """
        config = toml.load(config_file or CONFIG_PATH)
        return NERModelConfig(**config["NERModelConfig"])


class IntentClassifierModel:
    """
    A class to represent a model that can classify the intents
    of the given text.

    Attributes
    ----------
        config: IntentClassifierModelConfig
            The configuration for the model.

    Methods
    ---------
        predict(text: str)
            Predict the intent of the given text.

        train()
            Train the model using the given configuration.
    """

    def __init__(
        self, config: IntentClassifierModelConfig = IntentClassifierModelConfig()
    ) -> None:
        self.config = config
        self.nlp = self._load_spacy_model(self.config.spacy_model)

    def predict(self, text: str) -> str:
        """
        Predict the intent of the given text.

        returns: The predicted intent as a string.
        """
        doc = self.nlp(text.strip().lower() if text else "")
        prediction = max(doc.cats, key=doc.cats.get)  # type: ignore

        return (
            "unknown"
            if self._confidence(doc.cats) < self.config.threshold
            else prediction
        )

    def train(self) -> None:  # pragma: no cover
        """
        Prepares the data and trains the model using the given configuration.

        returns: None
        """
        if self.config.rebuild_data:
            logger.log("debug", f"Preparing data using: {self.config}")
            self._prepare_data()

        base_config = Path(self.config.base_config)
        full_config = base_config.with_name("config.cfg")

        if self.config.rebuild_config:
            with logger.log_context(
                "debug", "Building spaCy config", "spaCy config built"
            ):
                os.system(
                    f"poetry run python -m spacy init fill-config {base_config} {full_config}"
                )

        with logger.log_context(
            "debug",
            f"Training {type(self).__name__} using spaCy",
            f"{type(self).__name__} trained using spaCy",
        ):
            os.system(
                f"poetry run python -m spacy train {full_config} --output {Path(self.config.output_dir)}"
            )

    def _load_spacy_model(
        self, spacy_model: str = "en"
    ) -> spacy.language.Language:  # pragma: no cover
        """
        Helper function to load the correct spaCy language model.

        returns: A spaCy language model based on the given spaCy model name.
        """
        if self.config.mode == "train":
            return (
                spacy.blank(spacy_model)
                if spacy_model == "en"
                else spacy.load(spacy_model)
            )
        return spacy.load(self.config.best_model_location)

    def _make_spacy_docs(
        self,
        data: list[tuple[str, str]],
        for_training: bool = True,
    ) -> list:  # pragma: no cover
        """
        Helper function to create take a list of texts and labels and
        create a list of spaCy docs.

        returns: A list of spaCy docs.
        """
        docs = []
        for doc, label in tqdm(
            self.nlp.pipe(data, as_tuples=True),
            total=len(data),
            desc="Creating train docs" if for_training else "Creating valid docs",
        ):
            doc.cats[label] = 1
            docs.append(doc)

        return docs

    def _prepare_data(self) -> None:  # pragma: no cover
        """
        Helper function to prepare and save the data for training and validation.

        returns: None
        """
        dataset = data.IntentClassifierDataset(
            Path(self.config.data_path), shuffle=True
        )
        train_data, test_data = dataset.split(self.config.train_percentage)

        train_docs = self._make_spacy_docs(train_data.values.tolist())
        test_docs = self._make_spacy_docs(test_data.values.tolist(), False)

        train_bin = DocBin(docs=train_docs)
        test_bin = DocBin(docs=test_docs)

        train_bin.to_disk(self.config.train_data_save_path)
        test_bin.to_disk(self.config.valid_data_save_path)

    def _confidence(self, predictions: dict) -> float:  # pragma: no cover
        """
        Helper function to calculate the confidence of the model's prediction.
        This is done by getting the standard deviation of the prediction and
        dividing it by the mean of the predictions.

        returns: confidence score as a float.
        """
        sorted_predictions = sorted(
            predictions.items(), key=lambda x: x[1], reverse=True
        )
        logger.log("debug", f"Predictions: {sorted_predictions}")
        if all(x[1] == 0 for x in sorted_predictions):
            return 0
        return stdev([x[1] for x in sorted_predictions]) / mean(
            [x[1] for x in sorted_predictions]
        )


class NERModel:

    """
    A class to represent a model that can extract named entities
    from the given text.

    Attributes
    ----------
        config: NERModelConfig
            The configuration for the model.

    Methods
    ---------
        predict(text: str)
            Predict the named entities of the given text.

        train()
            Train the model using the given configuration.
    """

    def __init__(self, config: NERModelConfig = NERModelConfig()) -> None:
        self.config = config
        self.nlp = self._load_spacy_model(self.config.spacy_model)

    def predict(self, text: str) -> list[tuple[str, str]]:
        """
        Predict the named entities of the given text.

        returns: A list of tuples containing the named entity and its label, empty list
        if no entities found.
        """
        doc = self.nlp(text.strip() if text else "")
        return [(ent.text, ent.label_) for ent in doc.ents]

    def _load_spacy_model(
        self, spacy_model: str = "en"
    ) -> spacy.language.Language:  # pragma: no cover
        """
        Helper function to load the correct spaCy language model.

        returns: A spaCy language model based on the given spaCy model name.
        """
        return (
            spacy.blank(spacy_model) if spacy_model == "en" else spacy.load(spacy_model)
        )
