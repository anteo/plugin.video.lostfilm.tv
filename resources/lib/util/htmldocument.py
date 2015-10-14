# -*- coding: utf-8 -*-

import re
import HTMLParser


htmlParser = HTMLParser.HTMLParser()
# Init unescape immediately, because in multi-threaded environment it may fail
htmlParser.unescape("&nbsp;")


class HtmlElement:
    def __init__(self, tag=None, html="", attrs=None):
        self.tag = tag
        self.html = html
        self.attrs = attrs or {}

    def attr(self, name, default=None):
        return self.attrs[name].strip() if name in self.attrs else default

    def has_attr(self, name):
        return name in self.attrs

    @property
    def classes(self):
        return self.attr('class', '').split(' ')

    def __len__(self):
        return len(self.html.strip())

    @property
    def text(self):
        text = re.sub('<[^>]*>', '', self.html)
        text = htmlParser.unescape(text)
        return text.strip()

    @property
    def before_text(self):
        pos = self.html.find("<")
        text = self.html[:pos] if pos >= 0 else self.html
        text = htmlParser.unescape(text)
        return text.strip()

    @property
    def after_text(self):
        pos = self.html.rfind(">")
        text = self.html[pos+1:] if pos >= 0 else self.html
        text = htmlParser.unescape(text)
        return text.strip()

    @staticmethod
    def _get_contents(html, elem, tag):
        endstr = "</" + tag

        start = html.find(elem)
        end = html.find(endstr, start)
        pos = html.find("<" + tag, start + 1)

        while end > pos >= 0:  # Ignore too early </endstr> return
            tend = html.find(endstr, end + len(endstr))
            if tend >= 0:
                end = tend
            pos = html.find("<" + tag, pos + 1)

        result = ""
        if start <= 0 and end <= 0:
            pass
        elif start >= 0 and end >= 0:
            result = html[start + len(elem):end]
        elif end >= 0:
            result = html[:end]
        elif start >= 0:
            result = html[start + len(elem):]
        return result

    @staticmethod
    def _get_attributes(elem):
        res = re.findall('([\w\-.:]+)\s*=\s*("[^"]*"|\'[^\']*\'|[\w\-.:]+)', elem)
        attrs = {}
        for key, val in res:
            if val[0] == '"' or val[0] == '\'':
                val = val[1:-1]
            attrs[key] = htmlParser.unescape(val)
        return attrs

    def find(self, tag, attrs=None):
        if attrs:
            res = []
            for key, val in attrs.iteritems():
                res2 = list(re.finditer('(<(%s)[^>]*?(?:%s=[\'"]%s[\'"].*?>))(?ms)' % (tag, key, val), self.html))
                if not res2 and val.find(" ") == -1:  # Try matching without quotation marks
                    res2 = list(re.finditer('(<(%s)[^>]*?(?:%s=%s(?:\s+.*?>|>)))(?ms)' % (tag, key, val), self.html))
                groups = set([item.group() for item in res2])
                res = [item for item in res if item.group() in groups] if res else res2
        else:
            res = list(re.finditer('(<(%s)(?:>|\s+[^>]*?>))(?ms)' % tag, self.html))

        elements = HtmlElements()
        for match in res:
            elem = match.group()
            tag = match.group(2)
            start_pos = match.start()
            tag_attrs = self._get_attributes(elem)
            tag_contents = self._get_contents(self.html[start_pos:], elem, tag)
            element = HtmlElement(tag, tag_contents, tag_attrs)
            elements.append(element)
        return elements

    def __str__(self):
        return self.html.encode('utf-8')

    def __unicode__(self):
        return self.html


class HtmlElements(list):

    def find(self, tag, attrs=None):
        result = HtmlElements()
        for element in self:
            elements = element.find(tag, attrs)
            result += elements
        return result

    def attr(self, name, default=None):
        for element in self:
            if name in element.attrs:
                return element.attrs[name]
        return default

    def attrs(self, name, default=None):
        return [element.attr(name, default) for element in self]

    @property
    def first(self):
        return self[0]

    @property
    def last(self):
        return self[-1]

    @property
    def strings(self):
        return [e.text for e in self]

    @property
    def text(self):
        return "".join(self.strings)

    @property
    def after_text(self):
        return "".join([e.after_text for e in self])

    @property
    def before_text(self):
        return "".join([e.before_text for e in self])

    def __unicode__(self):
        return u"".join([unicode(e) for e in self])

    def __str__(self):
        return "".join([str(e) for e in self])

    @property
    def html(self):
        return "".join([e.html for e in self])


class HtmlDocument(HtmlElements):
    @classmethod
    def from_string(cls, html, encoding='utf-8'):
        """
        :type cls: type
        :rtype: HtmlDocument
        """
        if not isinstance(html, basestring):
            raise ValueError("Accept only string value")
        if isinstance(html, str):
            html = html.decode(encoding)
        return cls([HtmlElement(html=html)])
