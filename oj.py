#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os
import os.path

from onlinejudge import *

def main():
    usage = "usage: %(prog)s [options] ... [contest_id] problem_id"
    parser = argparse.ArgumentParser(usage=usage)

    parser.add_argument('contest_id', nargs='?')
    parser.add_argument('problem_id')

    # command
    # command = parser.add_mutually_exclusive_group()
    # for title
    # > Note that currently mutually exclusive argument groups do not support the title and description arguments of add_argument_group().
    command = parser.add_argument_group(title="command")
    command.add_argument("--check", action="store_const",
                      const="check", dest="command", default="check",
                      help="(default)")
    command.add_argument("-c", "--create-solution-template-file", action="store_const",
                      const="create_solution_template_file", dest="command",
                      help="Build and check the solution")
    command.add_argument("-s", "--submit", action="store_const",
                      const="submit", dest="command",
                      help="Submit the solution")
    command.add_argument('-d', '--download', action="store_const",
                      const='download', dest="command",
                      help="Only download the test cases")

    # switch online judge
    # contest = parser.add_mutually_exclusive_group()
    contest = parser.add_argument_group(title="contest")
    contest.add_argument("--poj", action="store_const",
                      const="poj", dest="contest",
                      help="PKU JudgeOnline")
    contest.add_argument("--codeforces", action="store_const",
                      const="codeforces", dest="contest",
                      help="CodeForces")
    contest.add_argument("--mjudge", action="store_const",
                      const="m_judge", dest="contest",
                      help="M-Judge")
    contest.add_argument("--aoj", action="store_const",
                      const="aoj", dest="contest",
                      help="Aizu Online Judge")
    contest.add_argument("--codechef", action="store_const",
                      const="codechef", dest="contest",
                      help="CodeChef")
    contest.add_argument("--imojudge", action="store_const",
                      const="imojudge", dest="contest",
                      help="Imo Judge")
    contest.add_argument("--atcoder", action="store_const",
                      const="atcoder", dest="contest",
                      help="AtCoder")
    contest.add_argument("--zojcontest", action="store_const",
                      const="zoj_contest", dest="contest",
                      help="ZOJ Contest")
    contest.add_argument("--npca", action="store_const",
                      const="npca", dest="contest",
                      help="NPCA (Nada Personal Computer users' Association) Judge")
    contest.add_argument("--kcs", action="store_const",
                      const="kcs", dest="contest",
                      help="KCS (Kagamiz Contest System)")
    contest.add_argument("--yukicoder", action="store_const",
                      const="yukicoder", dest="contest",
                      help="yukicoder sample case")
    contest.add_argument("--yukicoder-test", action="store_const",
                      const="yukicoder_test", dest="contest",
                      help="yukicoder all test case")

    # misc
    parser.add_argument('-i', '--source-file-name', action='store',
                      dest='source_file_name', default=None,
                      help='Specify the source file name')
    parser.add_argument('--setting-file-path', action='store',
                      dest='setting_file_path', default=None,
                      help='Specify the setting file path')
    parser.add_argument('--testcase-directory', action='store',
                      dest='testcase_directory', default=None,
                      help='Specify the directory for testcases')

    parser.add_argument("-t", "--titech-pubnet", action="store_true",
                      dest="titech_pubnet", default=False,
                      help="Use titech pubnet proxy",)
    parser.add_argument("-e", action="store",
                      dest="floating_point", default=None,
                      help="Use floating point validator and set max error")

    parser.add_argument('--r19', action="store_true",
                      dest='r19', default=False,
                      help="use Ruby1.9 for test")
    parser.add_argument('--topaz', action="store_true",
                      dest='topaz', default=False,
                      help="use Topaz for test")
    parser.add_argument('--py3', action="store_true",
                      dest='py3', default=False,
                      help="use Python3 for test")
    parser.add_argument('--pypy', action="store_true",
                      dest='pypy', default=False,
                      help="use PyPy for test")
    parser.add_argument('--pypy3', action="store_true",
                      dest='pypy3', default=False,
                      help="use PyPy3 for test")

    options = parser.parse_args()
    args = [options.contest_id, options.problem_id]
    try:
        while True:
            args.remove(None)
    except ValueError:
        pass

    if options.setting_file_path is None:
        if os.path.exists('setting.json'):
            options.setting_file_path = 'setting.json'
        elif os.path.exists(os.path.join(os.environ['HOME'], '.onlinejudgehelper.setting.json')):
            options.setting_file_path = os.path.join(os.environ['HOME'], '.onlinejudgehelper.setting.json')
        else:
            parser.error("setting.json is not found")
    setting = json.load(open(options.setting_file_path))

    if options.source_file_name is None:
        if 'source_file_name' in setting:
            options.source_file_name = setting['source_file_name']

    online_judge = None
    if options.contest == "zoj_contest":
        online_judge = ZOJContest(options, args)
    elif options.contest == "atcoder":
        online_judge = AtCoder(options, args)
    elif options.contest == "imojudge":
        online_judge = ImoJudge(options, args)
    elif options.contest == "codechef":
        online_judge = CodeChef(options, args)
    elif options.contest == "codeforces":
        online_judge = CodeForces(options, args)
    elif options.contest == "m_judge":
        online_judge = MJudge(options, args)
    elif options.contest == "aoj":
        online_judge = AOJ(options, args)
    elif options.contest == "npca":
        online_judge = NPCA(options, args)
    elif options.contest == "kcs":
        online_judge = KCS(options, args)
    elif options.contest == "yukicoder":
        online_judge = yukicoder(options, args)
    elif options.contest == "yukicoder_test":
        online_judge = yukicoder_test(options, args)
    elif options.contest == "poj":
        online_judge = POJ(options, args)
    else:
        parser.error("contest is not given")

    if options.testcase_directory is None:
        if 'testcase_directory' in setting:
            options.testcase_directory = setting['testcase_directory']
        else:
            options.testcase_directory = os.curdir
    if not os.path.exists(options.testcase_directory):
        os.makedirs(options.testcase_directory)

    if options.command == "submit":
        online_judge.submit()
    elif options.command == "create_solution_template_file":
        online_judge.create_solution_template_file()
    elif options.command == "download":
        online_judge.download()
    elif options.command == "check":
        online_judge.check()
    else:
        assert False

if __name__ == '__main__':
    main()
