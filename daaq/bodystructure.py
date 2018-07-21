'''Parses IMAP fetch BODYSTRUCTURE results and displays message partnumbers
Reference RFC3501 for additional information.
'''
__version__ = '''IMAP BODYSTRUCTURE parser v 0.2

Copyright (C) 2010 Brian Peterson
This is free software; see LICENSE file for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
'''
import re, sys
from PyQt4.QtXml import QDomDocument

SUBTYPES = ['MIXED', 'MESSAGE', 'DIGEST', 'ALTERNATIVE', 'RELATED',
            'REPORT','SIGNED','ENCRYPTED','FORM DATA']

BODYSTRUCTURE_RE = re.compile('.*\(BODY\w{0,9} (.*)\)')
CONTENT_TYPE_RE = re.compile(r'\s*"(TEXT|APPLICATION|IMAGE|VIDEO|AUDIO)"', re.I)
MULTIPART_SUBTYPE_RE = re.compile('\s*"({0})"'.format('|'.join(SUBTYPES)), re.I)

def parse_bodystructure(string):
    '''Parses IMAP fetch "BODY" or "BODYSTRUCTURE" results
    returns a list of tuples in the format (multipart subtype, depth, text)'''
    match = BODYSTRUCTURE_RE.search(string)
    if not match: 
        mesg = 'WARNING: BODYSTRUCTURE text does not match expected pattern.'
        sys.stderr.write(mesg + '\n')
        return
    body, parts = (match.group(1), [])
    for multipart_subtype, depth, text in parse_parts(string):
        if multipart_subtype:
            i = len(parts) - 1
            while (i >= 0) and (depth < parts[i]): i -= 1
            parts.insert(i + 1, (depth - 1, multipart_subtype))
        if CONTENT_TYPE_RE.match(text):
            parts.append((depth, text))
    return add_part_nums(parts)


def parse_parts(string):
    '''Nested parenthese text generator, yields (depth, text)'''
    open_paren_pos = []
    for ch_pos, char in enumerate(string):
        if char == '(':
            open_paren_pos.append(ch_pos)
        elif char == ')':
            start_pos = open_paren_pos.pop()
            text = string[ start_pos + 1: ch_pos]
            depth = len(open_paren_pos)
            match = MULTIPART_SUBTYPE_RE.match(string[ch_pos + 1:])
            multipart_subtype = match.group(1) if match else ''
            yield (multipart_subtype, depth, text)

def add_part_nums(parts):
    result = []
    partnums = [0] * max(parts)[0]
    #get_part_str = lambda x, y, z: '{0}{1}{2}'.format(
    #    y, ' '*(y!=''), z)
    for depth, text in parts:
        partnum, is_multipart = ('', (text.upper() in SUBTYPES))
        if depth > 1:
            partnums[depth - 2] += 1
            partnum = '.'.join([ str(i) for i in partnums[:depth - 1] ])
        if is_multipart: text = 'MULTIPART/' + text.upper()
        result.append((partnum, text))
    return result

def parse_nonmultipart(text):
    # create bracket dict
    bracket_dict = {}
    open_paren_pos = []
    for ch_pos, char in enumerate(text):
        if char == '(':
            open_paren_pos.append(ch_pos)
        elif char == ')':
            start_pos = open_paren_pos.pop()
            bracket_dict[start_pos] = ch_pos
    # split text
    frags = []
    quote, part = None, ''
    pos, length = 0, len(text)
    while pos < length:
        char = text[pos]
        if quote == None: # chars are not inside quote
            if char == ' ':
                if part != '' :
                    frags.append(part)
                    part = ''
            elif char == '"':
                quote = pos
            elif char == '(':
                end_pos = bracket_dict[pos]
                frag = text[pos+1:end_pos]
                frags.append(frag)
                pos = end_pos
            else:       # a number or NIL
                part += char
        elif char == '"':
            frag = text[quote+1:pos]
            frags.append(frag)
            quote = None
        pos += 1
    if part != '' : frags.append(part)
    #print frags
    part_type = frags[0].lower() + '/' + frags[1].lower()
    encoding = frags[5]
    size = frags[6]
    filename = 'Unknown'
    p = re.compile('"NAME" "([^"]+)"', re.I)
    m = p.search(frags[2])
    if m:
        filename = m.group(1)
    if len(frags) >= 9:
        p = re.compile('"FILENAME" "([^"]+)"', re.I)
        m = p.search(frags[8])
        if m:
            filename = m.group(1)
    return part_type, encoding, size, filename

def bodystructureToXml(bodystructure):
    parts = parse_bodystructure(bodystructure)
    alt_partnum = '.'
    doc = QDomDocument()
    root = doc.createElement('body')
    doc.appendChild(root)
    for part_num, text in parts:
        if text.startswith('MULTIPART/'):
            if text == 'MULTIPART/ALTERNATIVE':
                alt_part = doc.createElement('alternative')
                root.appendChild(alt_part)
                alt_partnum = part_num
        else:
            part_type, encoding, size, filename = parse_nonmultipart(text)
            item = doc.createElement('part')
            item.setAttribute('PartNum', part_num)
            item.setAttribute('type', part_type)
            item.setAttribute('encoding', encoding)
            if part_num.startswith(alt_partnum) and part_type.startswith('text/'):
                alt_part.appendChild(item)
            else:
                item.setAttribute('filename', filename)
                item.setAttribute('size', size)
                root.appendChild(item)
    return doc

if __name__ == '__main__':
    # Sample Usage
    body = '3 (BODY (((("TEXT" "PLAIN"  ("charset" "US-ASCII") NIL NIL "QUOTED-PRINTABLE" 2210 76)("TEXT" "HTML"  ("charset" "US-ASCII") NIL NIL "QUOTED-PRINTABLE"3732 99) "ALTERNATIVE")("IMAGE" "GIF"  ("name" "pic00041.gif") "<2__=07BBFD03DDC66BF58f9e8a93@domain.org>" NIL "BASE64" 1722)("IMAGE" "GIF"  ("name" "ecblank.gif") "<3__=07BBFD43DFC66BF58f9e8a93@domain.org>" NIL "BASE64" 64) "RELATED")("APPLICATION" "PDF"  ("name" "Quote_VLQ5069.pdf") "<1__=07BBED03DFC66BF58f9e8a93@domain.org>" NIL "BASE64" 59802) "MIXED"))'
    doc = bodystructureToXml(body)
    with open('out.txt', 'w') as doc_file:
        doc_file.write(doc.toString())

    #parts = parse_bodystructure(body)
    #for part_num, text in parts:
    #    #print part_num, text
    #    if not text.startswith('MULTIPART/'): parse_nonmultipart(text)

"""Sample Output:
MULTIPART/MIXED
        1 MULTIPART/RELATED
                1.1 MULTIPART/ALTERNATIVE
                        1.1.1 "TEXT" "PLAIN"  ("charset" "US-ASCII") NIL NIL "QUOTED-PRINTABLE" 2210 76
                        1.1.2 "TEXT" "HTML"  ("charset" "US-ASCII") NIL NIL "QUOTED-PRINTABLE" 3732 99
                1.2 "IMAGE" "GIF"  ("name" "pic00041.gif") "<2__=07BBFD03DDC66BF58f9e8a93@domain.org>" NIL "BASE64" 1722
                1.3 "IMAGE" "GIF"  ("name" "ecblank.gif") "<3__=07BBFD43DFC66BF58f9e8a93@domain.org>" NIL "BASE64" 64
        2 "APPLICATION" "PDF"  ("name" "Quote_VLQ5069.pdf") "<1__=07BBED03DFC66BF58f9e8a93@domain.org>" NIL "BASE64" 59802
"""
