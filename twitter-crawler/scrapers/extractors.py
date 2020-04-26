from .utils import get_logger

logger = get_logger()

retweeted_status_str = "retweeted_status"
quoted_status_str = "quoted_status"


class Extractor(object):

    def extract(self, attr, default=None):
        logger.error("NotImplementedError: {}.extract callback is not defined".format(self.__class__.__name__))
        raise NotImplementedError("{}.extract callback is not defined".format(self.__class__.__name__))


class AttributeExtractor(Extractor):

    def __init__(self, obj=None):
        self.obj = obj

    def extract(self, attr, default=None):
        if self.obj is not None:
            return self.obj[attr]
        else:
            return default


class NestedAttributeExtractor(Extractor):

    def __init__(self, root_obj=None, nested_obj=None):
        self.root_obj = root_obj
        self.nested_obj = nested_obj
        self.attr_extractor = None

    def extract(self, attr, default=None):
        if self.nested_obj in self.root_obj:
            self.attr_extractor = AttributeExtractor(self.root_obj[self.nested_obj])
            return self.attr_extractor.extract(attr, default)
        else:
            return default


class RetweetedStatusExtractor(Extractor):

    def __init__(self, status=None, retweeted_status=None):
        if retweeted_status is None:
            retweeted_status = retweeted_status_str
        self.nested_extractor = NestedAttributeExtractor(status, retweeted_status)

    def extract(self, attr, default=None):
        return self.nested_extractor.extract(attr, default)


class QuotedStatusExtractor(Extractor):

    def __init__(self, status=None, retweeted_status=None, quoted_status=None):
        if retweeted_status is None:
            retweeted_status = retweeted_status_str
        if quoted_status is None:
            quoted_status = quoted_status_str
        self.status = status
        self.retweeted_status = retweeted_status
        self.quoted_status = quoted_status
        self.nested_extractor = None

    def extract(self, attr, default=None):
        if self.retweeted_status in self.status:
            self.nested_extractor = NestedAttributeExtractor(self.status[self.retweeted_status], self.quoted_status)
            return self.nested_extractor.extract(attr, default)
        elif self.quoted_status in self.status:
            self.nested_extractor = NestedAttributeExtractor(self.status, self.quoted_status)
            return self.nested_extractor.extract(attr, default)
        else:
            return default


class EntitiesExtractor(Extractor):

    def __init__(self, entities=None):
        self.entities = entities

    def extract(self, attr, default=None):
        if self.entities is not None:
            return ', '.join(entity[attr] for entity in self.entities)
        else:
            return default


class EntitiesListExtractor(Extractor):

    def extract(self, entities_list, default=None):
        if entities_list is not None:
            result = ""
            for entity in entities_list:
                if entity:
                    result += entity + ", "
            return result
        else:
            return default
