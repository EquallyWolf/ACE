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


if __name__ == "__main__":
    app()
