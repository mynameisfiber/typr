#!/usr/bin/env python3

import string
import time

import speech_recognition as sr


class HeardTerminatePhrase(InterruptedError):
    pass


def speech_to_text(debug=False, terminate_phrases=None, **whisper_params):
    r = sr.Recognizer()
    m = sr.Microphone()
    with m as source:
        r.energy_threshold = 4_000
        while True:
            if debug:
                print("Listening for text")
            audio = r.listen(source)
            if debug:
                print("Recognizing text")
                start_time = time.time()
            text = r.recognize_faster_whisper(audio, **whisper_params)
            if debug:
                print(f"Recognition too {time.time() - start_time:0.4f}s")

            text_slug = text.lower().strip().strip(string.punctuation)
            if text_slug in terminate_phrases:
                raise HeardTerminatePhrase(text_slug)
            elif text_slug:  # check that the text isn't just punctuation
                yield text
            elif debug:
                print("Could not find any text within audio segment")
