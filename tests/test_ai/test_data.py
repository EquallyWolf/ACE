from pathlib import Path

from ace.ai import data
import pytest


class TestIntentClassifierDataset:
    @pytest.fixture
    def dataset(self) -> data.IntentClassifierDataset:
        return data.IntentClassifierDataset(Path("data/intents/mock_intents.csv"))

    @pytest.fixture
    def dataset_with_shuffle(self) -> data.IntentClassifierDataset:
        return data.IntentClassifierDataset(
            Path("data/intents/mock_intents.csv"), shuffle=True
        )

    def test_intent_classifier_dataset_length(
        self, dataset, dataset_with_shuffle
    ) -> None:
        assert len(dataset) == 10
        assert len(dataset_with_shuffle) == 10

    def test_intent_classifier_dataset_intent_lengths(
        self, dataset, dataset_with_shuffle
    ) -> None:
        assert len(dataset.intents) == 3
        assert len(dataset_with_shuffle.intents) == 3

    def test_intent_classifier_dataset_get_item(self, dataset) -> None:
        assert dataset[0] == ("sentence 1", "example1")

    def test_intent_classifier_dataset_split(
        self, dataset, dataset_with_shuffle
    ) -> None:
        train, test = dataset.split(0.8)
        train_shuffled, test_shuffled = dataset_with_shuffle.split(0.8)

        assert len(train) == 8
        assert len(test) == 2

        assert len(train_shuffled) == 8
        assert len(test_shuffled) == 2
