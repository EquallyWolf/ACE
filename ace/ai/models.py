import os
from dataclasses import dataclass
from pathlib import Path

import spacy
import toml
from spacy.tokens import DocBin
from tqdm import tqdm

from ace.ai import data

SEED = 42
CONFIG_PATH = os.path.join("config", "ai.toml")


@dataclass
class IntentClassifierModelConfig:
    """
    A dataclass to hold the configuration for the intent classifier.
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
    def from_toml(config_file: str | None = None) -> "IntentClassifierModelConfig":
        """
        Load the configuration from a TOML file. Leave the config_file parameter
        empty to load the configuration from the default location.

        returns: An IntentClassifierModelConfig object.
        """
        config = toml.load(config_file or CONFIG_PATH)
        return IntentClassifierModelConfig(**config["IntentClassifierModelConfig"])


class IntentClassifierModel:
    """
    A class to represent a model that can classify the intents
    of the given text.
    """

    def __init__(
        self, config: IntentClassifierModelConfig = IntentClassifierModelConfig()
    ) -> None:
        self.config = config
        self.nlp = self._load_spacy_model(self.config.spacy_model)

    def predict(self, text: str) -> str:
        """
        Predict the intent of the given text.
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
        """
        if self.config.rebuild_data:
            self._prepare_data()

        base_config = Path(self.config.base_config)
        full_config = base_config.with_name("config")

        if self.config.rebuild_config:
            os.system(
                f"poetry run python -m spacy init fill-config {base_config} {full_config}"
            )

        os.system(
            f"poetry run python -m spacy train {full_config} --output {Path(self.config.output_dir)}"
        )

    def _load_spacy_model(
        self, spacy_model: str = "en"
    ) -> spacy.language.Language:  # pragma: no cover
        """
        Helper function to load the correct spaCy language model.

        returns: A spaCy language model.
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
        Helper function to calculate the difference between the highest and second
        highest confidence scores.

        returns: The percentage difference between the highest and second highest
        """
        sorted_predictions = sorted(
            predictions.items(), key=lambda x: x[1], reverse=True
        )
        if all(x[1] == 0 for x in sorted_predictions):
            return 0
        return (
            sorted_predictions[0][1] - sorted_predictions[1][1]
        ) / sorted_predictions[0][1]


if __name__ == "__main__":  # pragma: no cover
    intent_classifier_model = IntentClassifierModel(
        IntentClassifierModelConfig.from_toml()
    )
    intent_classifier_model.train()
