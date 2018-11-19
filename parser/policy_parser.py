import re
import warnings
import _markupbase

from html import unescape
from html.parser import HTMLParser

__all__ = ['PolicyParser']

# Regular expressions used for parsing

interesting_normal = re.compile('[&<]')
incomplete = re.compile('&[a-zA-Z#]')

hans_one_to_ten = '\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u5341'
hans_one_to_ten = '\u4e00-\u5341'

startentity = re.compile('《[^\x00-\xff]*》')
endentity = re.compile('》')

hansfind_tolerant = re.compile('[^\x00-\xff]*?')

locatestarttagend_tolerant = re.compile('[^\x00-\xff]*?》')


class BasePolicyParser(_markupbase.ParserBase):
    """Find chinese 《》 pairs and call handler functions.

    Usage:
        p = BasePolicyParser()
        p.feed(data)
        ...
        p.close()

    """

    CDATA_CONTENT_ELEMENTS = ("script", "style")

    def __init__(self, *, convert_charrefs=True):
        """Initialize and reset this instance.

        If convert_charrefs is True (the default), all character references
        are automatically converted to the corresponding Unicode characters.
        """
        self.convert_charrefs = convert_charrefs
        self.reset()

    def reset(self):
        """Reset this instance.  Loses all unprocessed data."""
        self.rawdata = ''
        self.lasttag = '???'
        self.interesting = interesting_normal
        self.cdata_elem = None
        _markupbase.ParserBase.reset(self)

    def feed(self, data):
        r"""Feed data to the parser.

        Call this as often as you want, with as little or as much text
        as you want (may include '\n').
        """
        self.rawdata = self.rawdata + data
        self.goahead(0)

    def close(self):
        """Handle any buffered data."""
        self.goahead(1)

    __starttag_text = None

    def get_starttag_text(self):
        """Return full source of start tag: '<...>'."""
        return self.__starttag_text

    def set_cdata_mode(self, elem):
        self.cdata_elem = elem.lower()
        self.interesting = re.compile(r'</\s*%s\s*>' % self.cdata_elem, re.I)

    def clear_cdata_mode(self):
        self.interesting = interesting_normal
        self.cdata_elem = None

    # Internal -- handle data as far as reasonable.  May leave state
    # and data to be processed by a subsequent call.  If 'end' is
    # true, force handling all data as if followed by EOF marker.
    def goahead(self, end):
        rawdata = self.rawdata
        i = 0
        n = len(rawdata)
        while i < n:
            if self.convert_charrefs and not self.cdata_elem:
                j = rawdata.find('《', i)
                # print(f"Found parser, j : {j}, rawdata[j] : {rawdata[j]}")
                if j < 0:
                    # if we can't find the next <, either we are at the end
                    # or there's more text incoming.  If the latter is True,
                    # we can't pass the text to handle_data in case we have
                    # a charref cut in half at end.  Try to determine if
                    # this is the case before proceeding by looking for an
                    # & near the end and see if it's followed by a space or ;.
                    amppos = rawdata.rfind('&', max(i, n - 34))
                    if (amppos >= 0 and
                            not re.compile(r'[\s;]').search(rawdata, amppos)):
                        break  # wait till we get all the text
                    j = n
            else:
                match = self.interesting.search(rawdata, i)  # < or &
                if match:
                    j = match.start()
                else:
                    if self.cdata_elem:
                        break
                    j = n
            if i < j:
                if self.convert_charrefs and not self.cdata_elem:
                    self.handle_data(unescape(rawdata[i:j]))
                else:
                    self.handle_data(rawdata[i:j])
            i = self.updatepos(i, j)
            if i == n: break
            startswith = rawdata.startswith
            if startswith('《', i):
                if startentity.match(rawdata, i):  # < + letter
                    k = self.parse_policy_entity(i)
                elif startswith("（", i):
                    k = self.parse_policy_part(i)
                elif (i + 1) < n:
                    self.handle_data("《")
                    k = i + 1
                else:
                    break
                if k < 0:
                    if not end:
                        break
                    k = rawdata.find('》', i + 1)
                    if k < 0:
                        k = rawdata.find('《', i + 1)
                        if k < 0:
                            k = i + 1
                    else:
                        k += 1
                    if self.convert_charrefs and not self.cdata_elem:
                        self.handle_data(unescape(rawdata[i:k]))
                    else:
                        self.handle_data(rawdata[i:k])
                i = self.updatepos(i, k)
            elif startswith("&#", i):
                match = charref.match(rawdata, i)
                if match:
                    name = match.group()[2:-1]
                    self.handle_charref(name)
                    k = match.end()
                    if not startswith(';', k - 1):
                        k = k - 1
                    i = self.updatepos(i, k)
                    continue
                else:
                    if ";" in rawdata[i:]:  # bail by consuming &#
                        self.handle_data(rawdata[i:i + 2])
                        i = self.updatepos(i, i + 2)
                    break
            elif startswith('&', i):
                match = entityref.match(rawdata, i)
                if match:
                    name = match.group(1)
                    self.handle_entityref(name)
                    k = match.end()
                    if not startswith(';', k - 1):
                        k = k - 1
                    i = self.updatepos(i, k)
                    continue
                match = incomplete.match(rawdata, i)
                if match:
                    # match.group() will contain at least 2 chars
                    if end and match.group() == rawdata[i:]:
                        k = match.end()
                        if k <= i:
                            k = n
                        i = self.updatepos(i, i + 1)
                    # incomplete
                    break
                elif (i + 1) < n:
                    # not the end of the buffer, and can't be confused
                    # with some other construct
                    self.handle_data("&")
                    i = self.updatepos(i, i + 1)
                else:
                    break
            else:
                assert 0, "interesting.search() lied"
        # end while
        if end and i < n and not self.cdata_elem:
            if self.convert_charrefs and not self.cdata_elem:
                self.handle_data(unescape(rawdata[i:n]))
            else:
                self.handle_data(rawdata[i:n])
            i = self.updatepos(i, n)
        self.rawdata = rawdata[i:]

    # Internal -- handle starttag, return end or -1 if not terminated
    def parse_policy_entity(self, i):
        self.__starttag_text = None
        endpos = self.check_for_whole_start_tag(i)
        if endpos < 0:
            return endpos
        rawdata = self.rawdata

        self.__starttag_text = rawdata[i:endpos]

        # Now parse the data between i+1 and j into a tag and attrs
        attrs = []
        match = hansfind_tolerant.match(rawdata, i + 1)
        assert match, 'unexpected call to parse_starttag()'
        k = match.end()

        name = rawdata[i + 1:endpos - 2]

        end = rawdata[endpos - 2:endpos - 1].strip()
        if end not in ("》", '）'):
            lineno, offset = self.getpos()
            if "\n" in self.__starttag_text:
                lineno = lineno + self.__starttag_text.count("\n")
                offset = len(self.__starttag_text) \
                         - self.__starttag_text.rfind("\n")
            else:
                offset = offset + len(self.__starttag_text)
            self.handle_data(rawdata[i:endpos])
            return endpos
        if end.endswith('》'):
            # XHTML-style empty tag: <span attr="value" />
            self.handle_policy_entity(name)
        else:
            self.handle_policy_part(name)
        return endpos

    # Internal -- parse endtag, return end or -1 if incomplete
    def parse_policy_part(self, i):
        print(f"parse_policy_part, i : {i}")
        rawdata = self.rawdata
        assert rawdata[i:i + 1] == "》", "unexpected call to parse_endtag"
        match = endentity.search(rawdata, i + 1)  # >
        if not match:
            return -1
        gtpos = match.end()

        elem = match.group(1).lower()  # script or style
        if self.cdata_elem is not None:
            if elem != self.cdata_elem:
                self.handle_data(rawdata[i:gtpos])
                return gtpos

        self.handle_policy_part(elem.lower())
        self.clear_cdata_mode()
        return gtpos

    # Internal -- check to see if we have a complete starttag; return end
    # or -1 if incomplete.
    def check_for_whole_start_tag(self, i):
        rawdata = self.rawdata
        m = locatestarttagend_tolerant.match(rawdata, i)
        if m:
            j = m.end()
            next = rawdata[j-1]
            if next == "》":
                return j + 1
            if next == "":
                # end of input
                return -1
            if next in ("abcdefghijklmnopqrstuvwxyz=/"
                        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
                # end of input in or before attribute value, or we have the
                # '/' from a '/>' ending
                return -1
            if j > i:
                return j
            else:
                return i + 1
        raise AssertionError("we should not get here!")

    # Overridable -- handle start tag
    def handle_policy_entity(self, name):
        pass

    # Overridable -- handle end tag
    def handle_policy_part(self, tag):
        pass

    # Overridable -- handle character reference
    def handle_charref(self, name):
        pass

    # Overridable -- handle entity reference
    def handle_entityref(self, name):
        pass

    # Overridable -- handle data
    def handle_data(self, data):
        pass

    # Overridable -- handle comment
    def handle_comment(self, data):
        pass

    # Overridable -- handle declaration
    def handle_decl(self, decl):
        pass

    # Overridable -- handle processing instruction
    def handle_pi(self, data):
        pass

    def unknown_decl(self, data):
        pass

    # Internal -- helper to remove special character quoting
    def unescape(self, s):
        warnings.warn('The unescape method is deprecated and will be removed '
                      'in 3.5, use html.unescape() instead.',
                      DeprecationWarning, stacklevel=2)
        return unescape(s)


class PolicyParser(BasePolicyParser):
    def handle_policy_entity(self, name):
        print("Encountered a policy entity:", name)

    def handle_policy_part(self, tag):
        print("Encountered an end tag :", tag)

    def handle_data(self, data):
        print("Encountered some data  :", data)




if __name__ == '__main__':
    parser = PolicyParser()
    parser.feed('(一)有适应单位具体情况的内部治安保卫制度、措施和必要的治安防范设施； '
                '(二)单位范围内的治安保卫情况有人检查，重要部位得到重点保护，治安隐患及时得到排查；'
                '(三)单位范围内的治安隐患和问题及时得到处理，发生治安案件、涉嫌刑事犯罪的案件及时得到处置。'
                '(四)单位内部的消防、交通安全管理制度；'
                '中华人民共和国国务院令  第　635　号  《国务院关于修改〈中华人民共和国植物新品种保护条例〉的决定》'
                '已经2013年1月16日国务院第231次常务会议通过，现予公布，自2013年3月1日起施行。  总　理　温家宝 2013年1月31日 国务院关'
                '《中华人民共和国国民经济和社会发展第十一个五年规划纲要》和《国家“十一五”时期文化发展规划纲要》')