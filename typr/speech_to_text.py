#!/usr/bin/env python3

import string

import speech_recognition as sr


class HeardTerminatePhrase(InterruptedError):
    pass


def speech_to_text(terminate_phrases=None, whisper_params=None):
    r = sr.Recognizer()
    m = sr.Microphone()
    whisper_params = whisper_params or {}
    with m as source:
        r.adjust_for_ambient_noise(source, duration=2)
        while True:
            print("Listening for text")
            audio = r.listen(source)
            text = r.recognize_whisper(audio, **whisper_params)

            text_slug = text.lower().strip().strip(string.punctuation)
            if text_slug in terminate_phrases:
                raise HeardTerminatePhrase(text_slug)
            yield text
            r.adjust_for_ambient_noise(source, duration=0.25)
