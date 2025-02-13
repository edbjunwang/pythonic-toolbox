from collections import deque
from inspect import getmembers, isfunction, getsource
from operator import itemgetter
from pathlib import Path
import subprocess
from typing import List, Optional, Dict, DefaultDict
import re

import funcy

NEW_LINE = '\n'
SPACE = ' '
SHARP = '#'
THREE_BACKTICKS = '```'

URL_PREFIX = "https://github.com/albertmenglongli/pythonic-toolbox/actions/workflows"
BADGE_SUFFIX = "badge.svg?branch=master"

WORKFLOW_CODEQL_LINK = f"{URL_PREFIX}/codeql-analysis.yml"
WORKFLOW_TEST_PY36_LINK = f"{URL_PREFIX}/tests-python36.yml"
WORKFLOW_TEST_PY37_LINK = f"{URL_PREFIX}/tests-python37.yml"
WORKFLOW_TEST_PY38_LINK = f"{URL_PREFIX}/tests-python38.yml"
WORKFLOW_TEST_PY39_LINK = f"{URL_PREFIX}/tests-python39.yml"
WORKFLOW_TEST_PY310_LINK = f"{URL_PREFIX}/tests-python310.yml"
WORKFLOW_TEST_PY311_LINK = f"{URL_PREFIX}/tests-python311.yml"
WEBSITE_SNYK_LINK = "https://snyk.io/test/github/albertmenglongli/pythonic-toolbox"

BADGE_CODEQL_LINK = f"{WORKFLOW_CODEQL_LINK}/{BADGE_SUFFIX}"
BADGE_TEST_PY36_LINK = f"{WORKFLOW_TEST_PY36_LINK}/{BADGE_SUFFIX}"
BADGE_TEST_PY37_LINK = f"{WORKFLOW_TEST_PY37_LINK}/{BADGE_SUFFIX}"
BADGE_TEST_PY38_LINK = f"{WORKFLOW_TEST_PY38_LINK}/{BADGE_SUFFIX}"
BADGE_TEST_PY39_LINK = f"{WORKFLOW_TEST_PY39_LINK}/{BADGE_SUFFIX}"
BADGE_TEST_PY310_LINK = f"{WORKFLOW_TEST_PY310_LINK}/{BADGE_SUFFIX}"
BADGE_TEST_PY311_LINK = f"{WORKFLOW_TEST_PY311_LINK}/{BADGE_SUFFIX}"
BADGE_SNYK_LINK = "https://snyk.io/test/github/albertmenglongli/pythonic-toolbox/badge.svg"

TITLE = (f"""# Pythonic toolbox

> README.md is auto generated by the script **tests/generate_readme_markdown.py** from testing files,
>
> **DO NOT EDIT DIRECTLY!**   ;)

```bash
python3 tests/generate_readme_markdown.py
```


## Introduction

A python3.6+ toolbox with multi useful utils, functions, decorators in pythonic way, and is fully tested from python3.6 to python3.11 .

## Installation

```bash
pip3 install pythonic-toolbox --upgrade
```""")

BADGES = (f"""
[![PyPI version](https://badge.fury.io/py/pythonic-toolbox.svg)](https://badge.fury.io/py/pythonic-toolbox)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/pythonic-toolbox.svg?style=flat&logo=python&logoColor=yellow&labelColor=5c5c5c)](https://pypi.org/project/pythonic-toolbox)
[![Stability](https://img.shields.io/pypi/status/pythonic-toolbox.svg?style=flat)](https://badge.fury.io/py/pythonic-toolbox)
[![CodeQL Status]({BADGE_CODEQL_LINK})]({WORKFLOW_CODEQL_LINK})
[![Python3.6 Test Status]({BADGE_TEST_PY36_LINK})]({WORKFLOW_TEST_PY36_LINK})
[![Python3.7 Test Status]({BADGE_TEST_PY37_LINK})]({WORKFLOW_TEST_PY37_LINK})
[![Python3.8 Test Status]({BADGE_TEST_PY38_LINK})]({WORKFLOW_TEST_PY38_LINK})
[![Python3.9 Test Status]({BADGE_TEST_PY39_LINK})]({WORKFLOW_TEST_PY39_LINK})
[![Python3.10 Test Status]({BADGE_TEST_PY310_LINK})]({WORKFLOW_TEST_PY310_LINK})
[![Python3.11 Test Status]({BADGE_TEST_PY311_LINK})]({WORKFLOW_TEST_PY311_LINK})
[![SNYK Status]({BADGE_SNYK_LINK})]({WEBSITE_SNYK_LINK})

""")

DIR_PATH = Path(__file__).resolve().parent
README_PATH = DIR_PATH.parent / 'README.md'

begin_block_pattern = re.compile(r'(?<=begin-block-of-content\[)(.*?)(?=])', re.IGNORECASE)
end_block_pattern = re.compile(r'(?<=end-block-of-content\[)(.*?)(?=])', re.IGNORECASE)
insert_block_pattern = re.compile(r'(?<=insert-block-of-content\[)(.*?)(?=])', re.IGNORECASE)


def get_testing_file_paths_under_current_module() -> List[Path]:
    global DIR_PATH
    file_paths = [x for x in DIR_PATH.iterdir() if not x.is_dir()]
    testing_file_paths = [x for x in file_paths if x.name.startswith('test_')]
    return testing_file_paths


def get_functions_in_pkg(pkg):
    return getmembers(pkg, isfunction)


# remove_prefix is introduced after Python 3.9
def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


def extract_block_of_contents(file_path) -> DefaultDict[str, List[str]]:
    from collections import defaultdict
    cur_block_content_key: Optional[str] = None
    res = defaultdict(list)
    with open(file_path) as f:
        all_lines = f.readlines()
        all_lines = list(map(lambda s: s.replace('\n', ''), all_lines))

    # validation for block of content' begin end pairs
    stack = []
    for line in all_lines:
        begin_match = funcy.first(begin_block_pattern.findall(line))
        end_match = funcy.first(end_block_pattern.findall(line))

        if not begin_match and not end_match:
            continue

        if begin_match:
            stack.append(begin_match)
            continue

        # for end_match case
        if len(stack) == 1 and stack[-1] == end_match:
            stack.pop()
        else:
            raise RuntimeError(f'begin-block-of-content[{end_match}]/end-block-of-content[{end_match}] not match')

    for line in all_lines:
        begin_match = funcy.first(begin_block_pattern.findall(line))
        end_match = funcy.first(end_block_pattern.findall(line))

        if end_match:
            cur_block_content_key = None
            continue

        if cur_block_content_key is None:
            if begin_match:
                cur_block_content_key = begin_match
                continue
        else:
            res[cur_block_content_key].append(line)

    return res


def main():
    test_file_paths: List[Path] = get_testing_file_paths_under_current_module()
    contents: List[str] = [TITLE, '## Usage']
    title_level = 3
    for testing_file_path in sorted(test_file_paths, key=lambda x: x.name):
        block_of_contents_map: DefaultDict[str, List[str]] = extract_block_of_contents(testing_file_path)
        pkg_name = testing_file_path.stem
        pkg_name_without_test_ = remove_prefix(pkg_name, 'test_')
        contents.append(SHARP * title_level + SPACE + pkg_name_without_test_)
        pkg = __import__(pkg_name)
        name_func_pairs = get_functions_in_pkg(pkg)
        for func_name, func in sorted(name_func_pairs, key=itemgetter(0)):
            if not func_name.startswith('test_'):
                continue
            title_level += 1
            func_name_without_test_ = remove_prefix(func_name, 'test_')
            contents.append(SHARP * title_level + SPACE + func_name_without_test_)

            source_code_str = getsource(func)
            source_codes_lines = deque(source_code_str.split('\n'))
            source_codes_lines.popleft()  # remove first line for def function
            source_codes_lines.appendleft(THREE_BACKTICKS + 'python3')
            source_codes_lines.append(THREE_BACKTICKS)
            # de-indent the codes
            source_codes_lines = [remove_prefix(line, SPACE * 4) for line in source_codes_lines]

            final_source_code_lines = []
            for line in source_codes_lines:
                insert_match = funcy.first(insert_block_pattern.findall(line))
                if insert_match:
                    lines_to_insert = block_of_contents_map[insert_match]
                    if not lines_to_insert:
                        raise RuntimeError(f'"{insert_match}" block of content not found '
                                           f'in current file: {testing_file_path}')
                    final_source_code_lines.extend(lines_to_insert)
                else:
                    final_source_code_lines.append(line)

            reformatted_source_code_str = '\n'.join(final_source_code_lines)
            contents.append(reformatted_source_code_str)
            title_level -= 1
    readme_content = (NEW_LINE * 2).join(contents)
    with open(README_PATH, 'w') as f:
        f.write(readme_content)

    try:
        curl_cmd_str = 'markdown-toc  -h 4 -t github -toc "## Table of Contents" README.md'
        subprocess.run(curl_cmd_str, shell=True, universal_newlines=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       cwd=README_PATH.parent, check=True)
    except subprocess.CalledProcessError:
        print(('Failed to generate TOC, please run `markdown-toc` manually. \n'
               'To install markdown-toc, run: \n'
               '\tpip3 install markdown-toc --upgrade'))
        print('README.md is generated without TOC!')
    else:
        print('README.md is generated successfully with TOC!')

    # insert badges

    with open(README_PATH, 'r+') as f:
        lines = f.readlines()
        if len(lines) >= 1:
            lines.insert(1, BADGES)

        # Reset the reader's location (in bytes)
        f.seek(0)

        f.writelines(lines)


if __name__ == '__main__':
    main()
