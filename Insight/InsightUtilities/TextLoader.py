from .InsightSingleton import InsightSingleton
import asyncio
from functools import partial
import threading
import os
import InsightLogger


class TextLoader(metaclass=InsightSingleton):
    """Loads and caches static text data for prompts and localization"""
    def __init__(self):
        self._textCache = {}
        self._lock = threading.Lock()
        self._textpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "TextResources")
        self.logger = InsightLogger.InsightLogger.get_logger('InsightUtilities.TextLoader', 'InsightUtilities.log', child=True)

    def _load_text(self, textPath):
        try:
            filePath = textPath.lower().replace('.txt', '').split('.')
            filePath[-1] += ".txt"
            with open(os.path.join(self._textpath, *filePath)) as f:
                return f.read()
        except FileNotFoundError:
            text = "The text path was not found: {}".format(textPath)
        except Exception as ex:
            text = "Error when attempting to load text file: {} for {}".format(ex, textPath)
        print(text)
        self.logger.error(text)
        return text

    def _get_text(self, resource: str, language: str):
        textPath = resource.lower().replace('.txt', '')
        textPath += ("_" + language.lower())
        with self._lock:
            text = self._textCache.get(textPath)
            if isinstance(text, str):
                return text
            else:
                self.logger.info("Required disk IO for '{}'".format(textPath))
                text = self._load_text(textPath)
                self.logger.info("Got '{}' for path: {}".format(text, textPath))
                self._textCache[textPath] = text
                return text

    @classmethod
    def text_sync(cls, resource:str, language="en"):
        return cls()._get_text(resource, language)

    @classmethod
    async def text_async(cls, resource:str, language="en"):
        return await asyncio.get_event_loop().run_in_executor(None, partial(cls().text_sync, resource, language))
