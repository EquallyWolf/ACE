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
        raw_entities = data.load_entities(
            entities_directory="tests/data/rules/entities"
        )

        assert len(raw_entities) == 2

        for entity in raw_entities:
            assert entity in ["example_entity1", "example_entity2"]

    def test_load_entities_invalid_directory(self) -> None:
        with pytest.raises(FileNotFoundError):
            data.load_entities(entities_directory="tests/data/rules/invalid")

    def test_load_entities_empty_entity(self) -> None:
        raw_entities = data.load_entities(
            entities_directory="tests/data/rules/validations/empty"
        )

        assert len(raw_entities) == 1


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
        "raw_intents, raw_entities, num_examples, expected_dataset",
        [
            (  # One intent, no entities, one example
                {"greet": ["hello"]},
                {},
                1,
                {"greet": {"hello"}},
            ),
            (  # One intent, no entities, two examples
                {"greet": ["hello"]},
                {},
                2,
                {"greet": {"hello"}},
            ),
            (  # One intent, one entity, two examples
                {"greet": ["hello {name}"]},
                {"name": ["Alice", "Bob"]},
                2,
                {"greet": {"hello Alice", "hello Bob"}},
            ),
            (  # One intent, multiple entities, two examples
                {"greet": ["hello {name} {age}"]},
                {"name": ["Alice", "Bob"], "age": ["10", "20"]},
                2,
                {"greet": {"hello Alice 10", "hello Alice 20"}},
            ),
            (  # One intent, multiple entities, more examples than combinations
                {"greet": ["hello {name} {age}"]},
                {"name": ["Alice", "Bob"], "age": ["10", "20"]},
                10,
                {
                    "greet": {
                        "hello Alice 10",
                        "hello Alice 20",
                        "hello Bob 10",
                        "hello Bob 20",
                    }
                },
            ),
            (  # Two intents, one entity, two examples
                {"greet": ["hello {name}"], "goodbye": ["goodbye {name}"]},
                {"name": ["Alice", "Bob"]},
                2,
                {
                    "greet": {"hello Alice", "hello Bob"},
                    "goodbye": {"goodbye Alice", "goodbye Bob"},
                },
            ),
        ],
    )
    def test_generate_intent_dataset(
        self, raw_intents, raw_entities, num_examples, expected_dataset
    ) -> None:

        dataset = data.generate_intent_dataset(raw_intents, raw_entities, num_examples)

        assert dataset == expected_dataset

    def test_generate_intent_dataset_no_data(self) -> None:
        with pytest.raises(ValueError):
            data.generate_intent_dataset(
                raw_intents={}, raw_entities={}, num_examples=1
            )


class TestSaveDataset:
    @pytest.mark.parametrize(
        "dataset",
        [
            {
                "intent1": ["example1", "example2"],
                "intent2": ["example3", "example4"],
            },
            {
                "intent1": {"example1", "example2"},
                "intent2": {"example3", "example4"},
            },
        ],
    )
    def test_save_dataset(self, dataset) -> None:
        save_dir = "tests/data/datasets"
        save_filename = "test_dataset.csv"

        data.save_dataset(dataset=dataset, directory=save_dir, filename=save_filename)

        assert Path(f"{save_dir}/{save_filename}").exists()

        Path(f"{save_dir}/{save_filename}").unlink()
        Path(f"{save_dir}").rmdir()

    @pytest.mark.parametrize(
        "dataset",
        [
            {
                "intent1": ["example1", "example2"],
                "intent2": ["example3", "example4"],
            },
            {
                "intent1": {"example1", "example2"},
                "intent2": {"example3", "example4"},
            },
        ],
    )
    def test_invalid_file_type(self, dataset) -> None:
        save_dir = "tests/data/datasets"
        save_filename = "test_dataset.txt"

        with pytest.raises(ValueError):
            data.save_dataset(
                dataset=dataset, directory=save_dir, filename=save_filename
            )

        assert not Path(f"{save_dir}/{save_filename}").exists()


class TestLoadUtterances:
    def test_load_utterances(self) -> None:
        utterances = data.load_utterances(utterances_directory="tests/data/speech")

        assert len(utterances) == 2

        for utterance in utterances:
            assert utterance in ["example1", "example2"]

    def test_load_utterances_invalid_directory(self) -> None:
        with pytest.raises(FileNotFoundError):
            data.load_utterances(utterances_directory="tests/data/invalid")
