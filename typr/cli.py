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


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--terminate-phrase",
    "terminate_phrases",
    multiple=True,
    type=str,
    default=terminate_phrases,
)
def type(terminate_phrases):
    x = Xdo()
    first_message = True
    try:
        for text in speech_to_text(terminate_phrases):
            if not first_message:
                text = text.strip()
            x.enter_text_window(CURRENTWINDOW, text.encode("utf8"))
            first_message = False
    except HeardTerminatePhrase:
        x.enter_text_window(CURRENTWINDOW, "👋".encode("utf8"))
        time.sleep(0.5)
        x.send_keysequence_window(CURRENTWINDOW, b"BackSpace")


def easy_notifications():
    notify_client = pynotifier.NotificationClient()
    notify_client.register_backend(platform.Backend())

    def _(title, message):
        n = pynotifier.Notification(title=title, message=message)
        notify_client.notify_all(n)

    return _


@cli.command()
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
        for text in speech_to_text(terminate_phrases):
            if notify and notify_send is not None:
                notify_send(title="typr copied text", message=text.strip())
            pyperclip.copy(text.strip())
    except HeardTerminatePhrase:
        pass


if __name__ == "__main__":
    cli()
