"""
Collection of classes and functions for loading and manipulating data for the AI models.

#### Classes:

IntentClassifierDataset:
    All the data and functionality needed to train an intent classifier model.

#### Functions: None
"""

from pathlib import Path
import pandas as pd

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
        Get a tuple of the text and intent at the given index.

        #### Parameters:

        index: int
            The index of the data to get.

        #### Returns: tuple[str, str]
            A tuple of the text and intent at the given index.

        #### Raises: None
        """
        return tuple(self.data.iloc[index])

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
