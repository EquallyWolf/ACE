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


class TestLoadEntities:

    def test_load_entities(self) -> None:
        raw_entities = data.load_entities(entities_directory="tests/data/rules/entities")

        assert len(raw_entities) == 2

        for entity in raw_entities:
            assert entity in ["example_entity1", "example_entity2"]

    def test_load_entities_invalid_directory(self) -> None:
        with pytest.raises(FileNotFoundError):
            data.load_entities(entities_directory="tests/data/rules/invalid")


class TestLoadIntents:
    def test_load_intents(self) -> None:
        raw_intents = data.load_intents(intents_directory="tests/data/rules/intents")

        assert len(raw_intents) == 2

        for intent in raw_intents:
            assert intent in ["example1", "example2"]

    def test_load_intents_invalid_directory(self) -> None:
        with pytest.raises(FileNotFoundError):
            data.load_intents(intents_directory="tests/data/rules/invalid")


class TestGenerateIntentDataset:
    @pytest.mark.parametrize(
        "attempts, num_examples, dataset_length",
        [
            (1, 1, 1),
            (1, 2, 2),
            (2, 1, 1),
            (2, 2, 2),
            (3, 1, 1),
            (5, 4, 4),

        ],
    )
    def test_generate_intent_dataset(self, attempts, num_examples, dataset_length) -> None:
        entities_directory = "tests/data/rules/entities"
        intents_directory = "tests/data/rules/intents"

        raw_entities = data.load_entities(entities_directory=entities_directory)
        raw_intents = data.load_intents(intents_directory=intents_directory)

        dataset, num_fails = data.generate_intent_dataset(
            raw_entities=raw_entities, raw_intents=raw_intents, attempts=attempts, num_examples=num_examples
        )

        for intent in dataset:
            assert len(dataset[intent]) == dataset_length

        assert num_fails == 0

    @pytest.mark.parametrize(
        "attempts, num_examples, fails",
        [
            (1, 10, 1),
            (2, 10, 2),
            (5, 50, 5),
        ],
    )
    def test_generate_intent_dataset_non_zero_fails(self, attempts, num_examples, fails) -> None:
        entities_directory = "tests/data/rules/entities"
        intents_directory = "tests/data/rules/intents"

        raw_entities = data.load_entities(entities_directory=entities_directory)
        raw_intents = data.load_intents(intents_directory=intents_directory)

        dataset, num_fails = data.generate_intent_dataset(
            raw_entities=raw_entities, raw_intents=raw_intents, attempts=attempts, num_examples=num_examples
        )

        assert num_fails == fails


class TestSaveDataset:
    def test_save_dataset(self) -> None:
        dataset = {
            "intent1": ["example1", "example2"],
            "intent2": ["example3", "example4"],
        }

        save_dir = "tests/data/datasets"
        save_filename = "test_dataset.csv"

        data.save_dataset(dataset=dataset, directory=save_dir, filename=save_filename)

        assert Path(f"{save_dir}/{save_filename}").exists()

        Path(f"{save_dir}/{save_filename}").unlink()
        Path(f"{save_dir}").rmdir()

    def test_invalid_file_type(self) -> None:
        dataset = {
            "intent1": ["example1", "example2"],
            "intent2": ["example3", "example4"],
        }

        save_dir = "tests/data/datasets"
        save_filename = "test_dataset.txt"

        with pytest.raises(ValueError):
            data.save_dataset(dataset=dataset, directory=save_dir, filename=save_filename)

        assert not Path(f"{save_dir}/{save_filename}").exists()
