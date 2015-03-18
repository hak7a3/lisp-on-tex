#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import xml.etree.ElementTree as ET
# from enum import Enum # from 3.4...
import argparse
import subprocess
import os


# class Qstest(Enum):
class Qstest:
    passed = 1
    failed = 2
    no_message_failed = 3


class QstestParseException(Exception):
    def __init__(self, value):
        self.line = value

    def __str__(self):
        return "qstest logfile parse error: " + self.line


def parse_qstest_result(txt):
    """
    parse qstest.sty's test result to a Python's list of dicts.
    >>> parse_qstest_result("") == \
        []
    True
    >>> parse_qstest_result("Passed: hogehoge\\n")  == \
        [{'type': Qstest.passed, 'name': "hogehoge"}]
    True
    >>> parse_qstest_result(\
        "Failed: fugafuga\\n Except hogehoge\\n <hoge\\n >fuga\\n") == \
        [{'type': Qstest.failed, 'name': "fugafuga",\
          'message': "Except hogehoge", \
          'left': "hoge", 'right': "fuga"}]
    True
    >>> parse_qstest_result("Failed: fugafuga\\n") == \
        [{'type': Qstest.no_message_failed, 'name': "fugafuga", 'message': "", \
          'left': "", 'right': ""}]
    True
    """
    result = []
    parse_regexp = r'|'.join(
        [r'(?P<{0}>{1}\n)'.format(*x) for x in [
             ('Passed', r'Passed: (?P<name_p>.*)'),
             ('Failed', r'Failed: (?P<name_f>.*)\n (?P<message_f>.*)\n' +
              r' <(?P<left_f>.*)\n >(?P<right_f>.*)'),
             ('NoMessageFailed', r'Failed: (?P<name_nf>.*)'),
             ('Error', r'.*')]])
    parse_compiled = re.compile(parse_regexp, re.M)
    for token in re.finditer(parse_compiled, txt):
        typ = token.lastgroup
        if typ == 'Passed':
            result.append({'type': Qstest.passed,
                           'name': token.group('name_p')})
        elif typ == 'Failed':
            result.append({'type': Qstest.failed,
                           'name': token.group('name_f'),
                           'message': token.group('message_f'),
                           'left': token.group('left_f'),
                           'right': token.group('right_f')})
        elif typ == 'NoMessageFailed':
            result.append({'type': Qstest.no_message_failed,
                           'name': token.group('name_nf'),
                           'message': '',
                           'left': '',
                           'right': ''})
        else:
            raise QstestParseException(token.group('Error'))
    return result


def create_jenkins_xml(test_name, qstest_result, stdout_txt, stderr_txt):
    # create toplevel element
    fails = len([x for x in qstest_result if x['type'] == Qstest.failed])
    xml_root = ET.Element("testsuite",
                          {'name': test_name,
                           'tests': str(len(qstest_result)),
                           'failures': str(fails),
                           'errors': "0"})
    # create qstest result elements
    for result in qstest_result:
        add_node = ET.SubElement(xml_root,
                                 "testcase",
                                 {'name': result['name'],
                                  'classname': test_name})
        if result['type'] == Qstest.failed:
            fail_node = ET.SubElement(add_node,
                                      "failure",
                                      {'type': "LaTeX qstest failure",
                                       'message': result['message']})
            fail_node.text = "expected:" + result['left'] + "\n" + \
                             "got:" + result['right'] + "\n"
        elif result['type'] == Qstest.no_message_failed:
            fail_node = ET.SubElement(add_node,
                                      "failure",
                                      {'type': "LaTeX qstest failure",
                                       'message': '--NO MESSAGE--'})
            fail_node.text = "###no test####"
    # add stdout and stderr
    stdout_node = ET.SubElement(xml_root, "system-out")
    stdout_node.text = stdout_txt
    stderr_node = ET.SubElement(xml_root, "system-err")
    stderr_node.text = stderr_txt
    return xml_root


def perform_qstest_jenkins(engine, source, option, suffix, output):
    proc = subprocess.Popen([engine] + option + [source],
                            shell=(os.name == 'nt'),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    out_raw, err_raw = proc.communicate()
    filename_body = re.sub(r'\.tex$', "", source)
    qstest_file = open(filename_body + '.' + suffix)
    log_file = open(filename_body + '.log')
    xml = create_jenkins_xml(filename_body,
                             parse_qstest_result(qstest_file.read()),
                             out_raw.decode() + "\n===logfile===\n" + log_file.read(),
                             err_raw.decode())
    qstest_file.close()
    log_file.close()
    if not(output):
        output = filename_body + '.xml'
    output_file = open(output, mode='wb')
    ET.ElementTree(element=xml).write(output_file,
                                      xml_declaration=True,
                                      encoding="utf-8")
    output_file.close()


def main():
    parser = argparse.ArgumentParser(
        description="LaTeX qstest wrapper for Jenkins")
    parser.add_argument('source', help="source file")
    parser.add_argument('-e, --engine', dest='engine',
                        default="latex", help='TeX engine (default:latex)')
    parser.add_argument('-q, --qstest', dest='suffix',
                        default="lgout", help='suffix of the qstest logfile')
    parser.add_argument('--option', default="-interaction=batchmode",
                        help='options of TeX engine')
    parser.add_argument('-o, --output', dest='output', default=None,
                        help='output XML file (default:source file + .xml)')
    args = parser.parse_args()
    perform_qstest_jenkins(args.engine, args.source,
                           args.option.split(), args.suffix, args.output)

if __name__ == "__main__":
    main()
