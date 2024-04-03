"""
Collection of classes and functions for loading and manipulating data for the AI models.

#### Classes:

IntentClassifierDataset:
    All the data and functionality needed to train an intent classifier model.

#### Functions: None
"""

import itertools
from pathlib import Path
import re
import csv

import pandas as pd
from tqdm import tqdm

from ace.utils import Logger

logger = Logger.from_toml(config_file_name="logs.toml", log_name="data")


class IntentClassifierDataset:
    """
    All the data and functionality needed to train an intent classifier model.

    #### Parameters:

    file: Path
        The path to the file containing the data.

    shuffle: bool = False
        Whether or not to shuffle the data.

    seed: int (default: 42)
        The seed to use when shuffling the data.

    #### Methods:

    intents: list
        A list of all the intents in the dataset.

    split(train_percentage: float) -> tuple[pd.DataFrame, pd.DataFrame] (default: 0.8)
        Split the dataset into a training and test set.
    """

    def __init__(self, file: Path, shuffle: bool = False, seed: int = 42) -> None:
        self._seed = seed
        self.data = self._load_data(file, shuffle)

    def __len__(self) -> int:
        """
        The length of the dataset.

        #### Parameters: None

        #### Returns: int
            The length of the dataset.

        #### Raises: None
        """
        return len(self.data)

    def __getitem__(self, index: int) -> tuple[str, str]:
        """
        Get a tuple of the phrase and intent at the given index.

        #### Parameters:

        index: int
            The index of the data to get.

        #### Returns: tuple[str, str]
            A tuple of the phrase and intent at the given index.

        #### Raises: None
        """
        result = self.data.iloc[index]
        return result["phrase"], result["intent"]

    @property
    def intents(self) -> list:
        """
        A list of all the intents in the dataset.
        """
        return self.data["intent"].unique().tolist()

    def split(self, train_percentage: float) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Split the dataset into a training and test set.

        #### Parameters:

        train_percentage: float
            The percentage of the dataset to use for training.

        #### Returns: tuple[pd.DataFrame, pd.DataFrame]
            A tuple of the training and test sets.

        #### Raises: None
        """

        with logger.log_context(
            "info",
            "Splitting dataset into training and test sets.",
            "Finished splitting dataset into training and test sets.",
        ):
            train = self.data.sample(frac=train_percentage, random_state=self._seed)
            test = self.data.drop(train.index)
            logger.log(
                "debug", f"Training length = {len(train)} :: Test Length {len(test)}"
            )
            return train, test

    def _load_data(self, file: Path, shuffle: bool) -> pd.DataFrame:
        """
        Helper function to load the data from the given file.

        #### Parameters:

        file: Path
            The path to the file containing the data.

        shuffle: bool
            Whether or not to shuffle the data.

        #### Returns: pd.DataFrame
            The data loaded from the given file.

        #### Raises: None
        """
        data = pd.read_csv(file)
        if shuffle:
            data = data.sample(frac=1, random_state=self._seed)
        return data


def load_entities(entities_directory: str = "data/rules/entities") -> dict:
    """
    Load the entities into a dictionary from the entities files.

    #### Parameters:

    entities_directory: str (default: "data/rules/entities")
        The directory containing the entity files.

    #### Returns: dict
        A dictionary of the entities and their values.

    #### Raises: FileNotFoundError
        If no entities are found in the given directory.
    """
    entities_dir = Path(entities_directory)

    with logger.log_context(
        "info",
        f"Loading raw entities dictionary from: {entities_dir}",
        "Finished creating raw entities",
    ):
        entities = {}
        for entity in entities_dir.glob("*.entity"):
            logger.log("debug", f"Loading entity: {entity}")

            content = entity.read_text().splitlines()

            if not content:
                logger.log("warning", f"Skipping empty entity file: {entity}")
                continue

            entities[entity.stem] = content

        # If entities is empty, then we have no entities
        if not entities:
            logger.log("fatal", "No entities found.")
            raise FileNotFoundError(f"No entities found in directory '{entities_dir}'.")

        return entities


def load_intents(intents_directory: str = "data/rules/intents") -> dict:
    """
    Load the intents into a dictionary from the intents files.

    #### Parameters:

    intents_directory: str (default: "data/rules/intents")
        The directory containing the intent files.

    #### Returns: dict
        A dictionary of the intents and their values.

    #### Raises: FileNotFoundError
        If no intents are found in the given directory.
    """
    intents_dir = Path(intents_directory)

    with logger.log_context(
        "info",
        f"Loading raw intents dictionary from: {intents_dir}",
        "Finished creating raw intents",
    ):
        intents = {
            intent.stem: intent.read_text().splitlines()
            for intent in intents_dir.glob("*.intent")
        }

        # If intents is empty, then we have no intents
        if not intents:
            logger.log("fatal", "No intents found.")
            raise FileNotFoundError(f"No intents found in directory '{intents_dir}'.")

    return intents


def generate_intent_dataset(
    raw_intents: dict, raw_entities: dict, num_examples: int = 100
) -> dict[str, set[str] | list[str]]:
    """
    Generates all combinations of intents and entities, but only if the entity is in the intent.

    #### Parameters:

    raw_intents: dict
        A dictionary of the intents and their values.

    raw_entities: dict
        A dictionary of the entities and their values.

    num_examples: int (default: 100)
        The number of examples to generate for each intent.

    #### Returns: dict[str, set[str] | list[str]
        The generated dataset.
            format: {intent: {example1, example2, ...}}
                    {intent: [example1, example2, ...]}

    #### Raises: None
    """

    dataset = {}
    for intent, intent_templates in tqdm(raw_intents.items(), desc="Creating dataset"):
        logger.log("info", f"Creating dataset for intent '{intent}'.")

        examples = []
        for template in intent_templates:
            logger.log("debug", f"Generating examples for template: {template}")

            # Check if we have any entities in the template
            entities = re.findall(r"{(.*?)}", template)
            logger.log("debug", f"Entities in template: {entities}")

            if not entities:
                examples.append(template)
                continue

            # Generate all possible combinations of entities
            try:
                examples = list(
                    map(
                        lambda combination: template.format(
                            **dict(zip(entities, combination))
                        ),
                        itertools.product(
                            *[raw_entities[entity] for entity in entities]
                        ),
                    )
                )
            except KeyError as e:
                logger.log("warning", f"No entity examples found for: {e}")
                continue

        dataset[intent] = set(examples[:num_examples])

    # Check if we have any examples
    if not dataset:
        logger.log("critical", "No examples generated.")
        raise ValueError("No examples generated.")

    logger.log("info", f"Dataset: {dataset}")

    return dataset


def save_dataset(
    dataset: dict[str, set[str] | list[str]],
    directory: str,
    filename: str = "dataset.csv",
) -> None:
    """
    Save the dataset to the given format.

    #### Parameters:

    dataset: dict[str, set[str] | list[str]]
        The dataset to save.

    directory: str
        The directory to save the dataset to.

    filename: str (default: "dataset.csv")
        The name of the file to save the dataset to.

    #### Returns: None

    #### Raises: ValueError
        If the file type is not supported.
    """
    root_dir = Path(directory)
    root_dir.mkdir(parents=True, exist_ok=True)

    save_path = root_dir / filename

    handlers = {
        ".csv": _save_as_csv,
    }

    with logger.log_context(
        "info",
        f"Saving dataset to: {save_path}",
        "Finished saving dataset.",
    ):
        if handler := handlers.get(save_path.suffix):
            handler(dataset, save_path)
        else:
            logger.log("critical", f"Unsupported file type: {save_path.suffix}")
            raise ValueError(f"Unsupported file type: {save_path.suffix}")


def _save_as_csv(dataset: dict[str, set[str] | list[str]], save_path: Path) -> None:
    """
    Save the dataset as a CSV file.

    #### Parameters:

    dataset: dict[str, set[str] | list[str]]
        The dataset to save.

    save_path: Path
        The path to save the dataset to.

    #### Returns: None

    #### Raises: None
    """
    with open(save_path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["phrase", "intent"])
        for intent, examples in dataset.items():
            for example in examples:
                writer.writerow([example, intent])
