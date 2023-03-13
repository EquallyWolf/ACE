from pathlib import Path
import pandas as pd

from ace.utils import Logger

logger = Logger.from_toml(config_file_name="logs.toml", log_name="data")


class IntentClassifierDataset:
    """
    A class to store the dataset for the intent classifier.

    Attributes:
        file: Path
            The path to the dataset file.

        shuffle: bool
            Whether to shuffle the dataset or not.

        seed: int
            The seed to use for shuffling the dataset.
    """

    def __init__(self, file: Path, shuffle: bool = False, seed: int = 42) -> None:
        self._seed = seed
        self.data = self._load_data(file, shuffle)

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, index: int) -> tuple[str, str]:
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

        returns: A tuple of training and test datasets.
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

        returns: A pandas DataFrame with the data.
        """
        data = pd.read_csv(file)
        if shuffle:
            data = data.sample(frac=1, random_state=self._seed)
        return data
