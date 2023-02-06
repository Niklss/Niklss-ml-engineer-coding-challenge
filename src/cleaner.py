import re
from abc import ABC, abstractmethod
from typing import List


class MTCleaner(ABC):
    """
    This class performs an abstraction of any future cleaning function that might be easily added to MT text
    preprocessing pipeline
    """
    @staticmethod
    @abstractmethod
    def __call__(text: str, *args, **kwargs) -> str:
        """
        :param text: Text to be preprocessed
        :param args:
        :param kwargs:
        :return: Preprocessed text
        """
        ...


class HTMLTags(MTCleaner):
    """
    This class performs a html tag cleaning
    """
    @staticmethod
    def __call__(text, *args, **kwargs):
        return re.sub(r'&.*?;', '', text)


class XMLTags(MTCleaner):
    """
    This class performs a xml tag cleaning
    """
    @staticmethod
    def __call__(text, *args, **kwargs):
        return re.sub(r'<.*?>', '', text)


class MarkupTags(MTCleaner):
    """
    This class performs a markup tag cleaning
    """
    @staticmethod
    def __call__(text, *args, **kwargs):
        return re.sub(r'%\w+_\w+%', '', text)


class Strip(MTCleaner):
    """
    This class performs stripping
    """
    @staticmethod
    def __call__(text, *args, **kwargs):
        return text.strip()


class MTCleanerPipeline:
    """
    This class performs a cleaning over any iterable. To initialize a class you need to pass a list of MTCleaner's
    """
    def __init__(self, cleaners: List[MTCleaner]):
        """
        :param cleaners: MTCleaners that will clean the text
        """
        self.cleaners = cleaners

    def _clean(self, text: str) -> str:
        """
        Internal function that sequentially performs cleaning on one str
        :param text: input text
        :return: cleaned text
        """
        for cleaner in self.cleaners:
            text = cleaner(text)
        return text

    def __call__(self, data: iter) -> tuple:
        """
        Performing a cleaning over iterable of strings
        :param data: Iterable of strings. Lists, Tuples, any class with __iter__.
        :return: tuple of cleaned data
        """
        return tuple(map(self._clean, data))
