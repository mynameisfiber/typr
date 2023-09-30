import time

import click

from xdo import Xdo, CURRENTWINDOW
import pyperclip

import pynotifier
from pynotifier.backends import platform

from .speech_to_text import speech_to_text, HeardTerminatePhrase


terminate_phrases = [
    "stop",
    "terminate",
    "exit",
    "end process",
    "stop listening",
]


def easy_notifications():
    notify_client = pynotifier.NotificationClient()
    notify_client.register_backend(platform.Backend())

    def _(title, message):
        n = pynotifier.Notification(title=title, message=message)
        notify_client.notify_all(n)

    return _


@click.group(context_settings=dict(show_default=True))
@click.option(
    "--terminate-phrase",
    "terminate_phrases",
    help="Phrases to listen for that will cause typr to terminate",
    multiple=True,
    type=str,
    default=terminate_phrases,
)
@click.option("--debug", default=False, is_flag=True)
@click.option(
    "--language",
    help="Recognition language, ie 'english' or 'chinese'. Leave empty for auto-detect.",
    type=str,
    default=None,
)
@click.option(
    "--model",
    default="base",
    help="Model type to use. See https://github.com/openai/whisper#available-models-and-languages",
)
@click.option(
    "--prompt",
    default=None,
    type=str,
    help="Optional text to provide as a prompt for the first window. This can be used to provide, or 'prompt-engineer' a context for transcription, e.g. custom vocabularies, proper nouns, gender agreement.",
)
@click.pass_context
def cli(ctx, model, terminate_phrases, language, prompt, debug):
    """
    hello
    """
    ctx.obj = {
        "speech_recognition_params": {
            "terminate_phrases": terminate_phrases,
            "language": language,
            "model": model,
            "initial_prompt": prompt,
            "debug": debug,
        }
    }


@cli.command(help="Echos speech to text results to stdout")
@click.pass_context
def echo(ctx):
    try:
        for text in speech_to_text(**ctx.obj["speech_recognition_params"]):
            click.echo(text + "\n")
    except HeardTerminatePhrase:
        click.echo("Terminating" + "\n")


@cli.command(help="Types speech to text results using libxdo")
@click.pass_context
def type(ctx):
    x = Xdo()
    first_message = True
    try:
        for text in speech_to_text(**ctx.obj["speech_recognition_params"]):
            if not first_message:
                text = text.strip()
            x.enter_text_window(CURRENTWINDOW, text.encode("utf8"))
            first_message = False
    except HeardTerminatePhrase:
        x.enter_text_window(CURRENTWINDOW, "👋".encode("utf8"))
        time.sleep(0.5)
        x.send_keysequence_window(CURRENTWINDOW, b"BackSpace")


@cli.command(help="Copies speech to text results to the clipboard")
@click.option("--notify", is_flag=True, default=True)
@click.option(
    "--terminate-phrase",
    "terminate_phrases",
    multiple=True,
    type=str,
    default=terminate_phrases,
)
def copy(terminate_phrases, notify):
    notify_send = None
    if notify:
        notify_send = easy_notifications()
    try:
        for text in speech_to_text(**ctx.obj["speech_recognition_params"]):
            if notify and notify_send is not None:
                notify_send(title="typr copied text", message=text.strip())
            pyperclip.copy(text.strip())
    except HeardTerminatePhrase:
        pass


if __name__ == "__main__":
    cli()
