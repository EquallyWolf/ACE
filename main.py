r"""
########################################################################################
#                              ___       ______  _______                               #
#                             /   \     /      ||   ____|                              #
#                            /  ^  \   |  ,----'|  |__                                 #
#                           /  /_\  \  |  |     |   __|                                #
#                          /  _____  \ |  `----.|  |____                               #
#                         /__/     \__\ \______||_______|                              #
#                                                                                      #
#                                                                                      #
#    Welcome to ACE, the Artificial Consciousness Engine!                              #
#                                                                                      #
#    ACE is a digital assistant, designed to help you with your daily tasks and keep   #
#    you in the loop with your life and the world.                                     #
#                                                                                      #
########################################################################################
"""

import warnings

from ace.utils import Logger

warnings.filterwarnings("ignore")

logger = Logger.from_toml(config_file_name="logs.toml", log_name="main")

with logger.log_context(
    "info",
    "Importing modules in 'ace.py'",
    "Finished importing modules.",
):
    import typer

    from ace.interfaces import CLI, GUI

app = typer.Typer()


@app.command()
def cli(
    no_header: bool = typer.Option(
        False,
        "--no-header",
        "-nh",
        help="Don't show the header.",
        show_default=True,
    ),
) -> None:
    """
    Run the ACE program, using the command line interface.
    """
    interface = CLI(show_header=not no_header, header=__doc__)
    logger.log("info", "Starting ACE.")
    interface.run()


@app.command()
def gui(
    no_header: bool = typer.Option(
        False,
        "--no-header",
        "-nh",
        help="Don't show the header.",
        show_default=True,
    ),
) -> None:
    """
    Run the ACE program, using the graphical user interface.
    """
    header = "\n\n".join(
        [
            "Welcome to ACE, the Artificial Consciousness Engine!",
            "ACE is a digital assistant, designed to help you with your daily tasks and keep you in the loop with your life and the world.",
        ]
    )

    interface = GUI(show_header=not no_header, header=header)
    logger.log("info", "Starting ACE.")
    interface.run()


@app.command()
def pipeline(
    no_train: bool = typer.Option(
        False,
        "--no-train",
        "-nt",
        help="Don't run training before testing.",
        show_default=True,
    ),
    no_test: bool = typer.Option(
        False,
        "--no-test",
        "-ns",
        help="Don't run testing after training.",
        show_default=True,
    ),
) -> None:
    """
    Train and test the AI models.
    """
    logger.log("info", "Starting the AI pipeline.")
    from ace.ai import models

    models_available = {
        "intent_classifier": models.IntentClassifierModel,
    }

    # Show a menu of the available models and let the user choose one.
    typer.echo("Available models:")
    for i, model in enumerate(models_available):
        typer.echo(f"{i + 1}. {model}")
    typer.echo()

    logger.log("info", f"Available models: {models_available}")

    # Create a model object based on the user's choice.
    model_choice = typer.prompt("Choose a model", type=int) - 1
    while model_choice not in range(len(models_available)):
        typer.echo("Invalid choice.")
        model_choice = typer.prompt("Choose a model", type=int) - 1
    model_name = list(models_available.keys())[model_choice]

    logger.log("info", f"Chosen model: {model_name}")

    config = models.IntentClassifierModelConfig.from_toml("config/ai.toml")

    # Train the model.
    if not no_train:
        typer.echo("===================== Training the model =====================")
        config.mode = "train"

        model = models_available[model_name](config)
        model.train()

    # Test the model.
    if not no_test:
        config.mode = "test"
        model = models_available[model_name](config)

        typer.echo("===================== Testing the model =====================")
        typer.echo("Type 'q' to quit.")
        while True:
            query = typer.prompt("Enter a query")
            logger.log("info", f"Query: {query}")

            if query == "q":
                break

            result = model.predict(query)
            logger.log("info", f"Intent: {result}")

            typer.echo(f"Intent: {result}")


if __name__ == "__main__":
    app()
