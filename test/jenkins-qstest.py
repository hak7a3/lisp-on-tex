#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import xml.etree.ElementTree as ET
# from enum import Enum # from 3.4...
import argparse
import subprocess
import os

_parse_result_pattern = re.compile(r'(?P<type>.*?): (?P<name>.*?)$')


# class Qstest(Enum):
class Qstest:
    passed = 1
    failed = 2


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
    >>> parse_qstest_result("Passed: hogehoge") == \
        [{'type': Qstest.passed, 'name': "hogehoge"}]
    True
    >>> parse_qstest_result(\
        "Failed: fugafuga\\n Except hogehoge\\n <hoge\\n >fuga") == \
        [{'type': Qstest.failed, 'name': "fugafuga",\
          'message': "Except hogehoge", \
          'left': "hoge", 'right': "fuga"}]
    True
    """
    result = []
    iter_line = iter(txt.splitlines())
    line = next(iter_line, None)
    while line:
        matched_result = _parse_result_pattern.match(line)
        if matched_result:
            if matched_result.group('type') == "Passed":
                result.append({'type': Qstest.passed,
                               'name': matched_result.group('name')})
                line = next(iter_line, None)
            elif matched_result.group('type') == "Failed":
                message_raw = next(iter_line, None)
                left_raw = next(iter_line, None)
                right_raw = next(iter_line, None)
                result.append({'type': Qstest.failed,
                               'name': matched_result.group('name'),
                               'message': message_raw[1:],
                               'left': left_raw[2:],
                               'right': right_raw[2:]})
                line = next(iter_line, None)
            else:
                raise QstestParseException(line)
        else:
            raise QstestParseException(line)
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
                        help='output XML file name (default:source file name + .xml)')
    args = parser.parse_args()
    perform_qstest_jenkins(args.engine, args.source,
                           args.option.split(), args.suffix, args.output)

if __name__ == "__main__":
    main()
