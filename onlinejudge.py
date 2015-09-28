#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import cookielib
import json
import os
import os.path
import re
import shutil
import subprocess
import time
import urllib
import urllib2
import zipfile

try:
    import colorama
    colorama.init()
    clr = colorama.Fore
except:
    class clr:
        RED   = ''
        GREEN = ''
        BLUE  = ''
        RESET = ''

from validator import *
from solution import *

class OnlineJudge:
    def __init__(self, options, problem_id):
        self.options = options
        self.problem_id = problem_id
        if options.titech_pubnet:
            self.proxies = {'http': 'http://proxy.noc.titech.ac.jp:3128'}
        else:
            self.proxies = None
        self.opener = None

    def get_url(self):
        raise NotImplementedError

    def get_input_file_path(self, index):
        return os.path.join(self.options.testcase_directory, self.get_input_file_name(index))
    def get_input_file_name(self, index):
        return self.__class__.__name__ + '.' + self.problem_id + '.' + str(index) + '.in.txt'

    def get_output_file_path(self, index):
        return os.path.join(self.options.testcase_directory, self.get_output_file_name(index))
    def get_output_file_name(self, index):
        return self.__class__.__name__ + '.' + self.problem_id + '.' + str(index) + '.out.txt'

    def get_source_file_name(self):
        if self.options.source_file_name:
            return self.options.source_file_name
        else:
            return self.problem_id + '.cpp'

    def format_pre(self, s):
        s = s.replace('<br />', '\n')
        s = s.replace('&lt;', '<')
        s = s.replace('&gt;', '>')
        s = s.replace('&quot;', '"')
        s = s.replace('\r', '')
        if not s.endswith('\n'):
            s += '\n'
        while s.endswith('\n\n'):
            s = s[0:len(s) - 1]
        while s.startswith('\n'):
            s = s[1:]
        return s

    def download_html(self):
        url = self.get_url()
        return self.get_opener().open(url).read()

    def download(self):
        raise NotImplementedError

    def get_opener(self):
        if self.opener == None:
            cj = cookielib.CookieJar()
            cjhdr = urllib2.HTTPCookieProcessor(cj)
            if self.proxies == None:
                self.opener = urllib2.build_opener(cjhdr)
            else:
                self.opener = urllib2.build_opener(cjhdr, urllib2.ProxyHandler(self.proxies))
        return self.opener

    def get_solution(self):
        source_file_name = self.get_source_file_name()
        ext = os.path.splitext(source_file_name)[1]
        if ext == '.c':
            return SolutionC(source_file_name)
        elif ext == '.cpp' or ext == '.cc':
            return SolutionCxx(source_file_name)
        elif ext == '.java':
            return SolutionJava(source_file_name)
        elif ext == '.io':
            return SolutionIo(source_file_name)
        elif ext == '.php':
            return SolutionPhp(source_file_name)
        elif ext == '.py':
            if self.options.py3:
                return SolutionPython3(source_file_name)
            elif self.options.pypy:
                return SolutionPyPy(source_file_name)
            elif self.options.pypy3:
                return SolutionPyPy3(source_file_name)
            else:
                return SolutionPython(source_file_name)
        elif ext == '.pl':
            return SolutionPerl(source_file_name)
        elif ext == '.rb':
            if self.options.r19:
                return SolutionRuby19(source_file_name)
            if self.options.topaz:
                return SolutionRubyTopaz(source_file_name)
            else:
                return SolutionRuby(source_file_name)
        elif ext == '.hs':
            return SolutionHaskell(source_file_name)
        elif ext == '.scala':
            return SolutionScala(source_file_name)
        elif ext == '.cs':
            return SolutionCs(source_file_name)
        elif ext == '.go':
            return SolutionGo(source_file_name)
        elif ext == '.d':
            return SolutionD(source_file_name)
        else:
            return Solution(source_file_name)

    def get_validator(self):
        if not self.options.floating_point:
            return DiffValidator()
        else:
            return FloatingPointValidator(self.options.floating_point)

    def check(self):
        print('compiling...')

        solution = self.get_solution()

        if not solution.compile():
            print('CompileError')
            exit(-1)

        if not os.path.exists(self.get_input_file_path(0)) or not os.path.exists(self.get_output_file_path(0)):
            print('downloading...')
            self.download()

        max_time = 0.0

        validator = self.get_validator()

        accept = 0
        total = 0
        no_input_files = True

        for index in range(100):
            input_file_path = self.get_input_file_path(index)
            output_file_path = self.get_output_file_path(index)

            if not os.path.exists(input_file_path):
                break

            no_input_files = False

            print(clr.GREEN + ('----- Case #%d -----' % index) + clr.RESET)

            execution_time = solution.execute(input_file_path, 'out.txt')

            if max_time < execution_time:
                max_time = execution_time

            if os.path.exists(output_file_path):
                result = validator.validate(output_file_path, 'out.txt')
                if result:
                    accept += 1
                    print(clr.BLUE + ('ok (%f sec)' % execution_time) + clr.RESET)
                else:
                    print(clr.RED + ('WA (%f sec)' % execution_time) + clr.RESET)
            else:
                subprocess.Popen(['cp', 'out.txt', output_file_path]).wait()
            total += 1

        if no_input_files:
            print(clr.GREEN + 'No input files...' + clr.RESET)
        elif accept == total:
            print(clr.BLUE + 'OK ({} cases) (max {} sec)'.format(total, max_time) + clr.RESET)
        else:
            print(clr.RED + 'WrongAnswer ({} WAs in {} cases) (max {} sec)'.format(total - accept, total, max_time) + clr.RESET)

    def add_test_case_template(self):
        for index in range(100):
            input_filepath = self.get_input_file_path(index)
            output_filepath = self.get_output_file_path(index)
            if os.path.isfile(input_filepath):
                continue
            open(input_filepath, 'w').close()
            open(output_filepath, 'w').close()
            print("Test case template file " + str(index) + " is created.")
            return

    def submit(self):
        raise NotImplementedError

    def create_solution_template_file(self):
        try:
            src = self.get_source_file_name()
            dst = self.get_source_file_name() + ".bak"
            shutil.copyfile(src, dst)
            print('Copied %s to %s' % (src, dst))
        except IOError, (errno, strerror):
            print("I/O error(%s): %s" % (errno, strerror))
        try:
            src = 'template.cpp'
            dst = self.get_source_file_name()
            shutil.copyfile(src, dst)
            print('Copied %s to %s' % (src, dst))
        except IOError, (errno, strerror):
            print("I/O error(%s): %s" % (errno, strerror))

    def get_language_id(self):
        source_file_name = self.get_source_file_name()
        root, ext = os.path.splitext(source_file_name)
        return self.get_language_id_from_extension()[ext.lower()]

    def get_language_id_from_extension(self):
        raise NotImplementedError


class POJ(OnlineJudge):
    def __init__(self, options, args):
        OnlineJudge.__init__(self, options, args[0])

    def get_url(self):
        return 'http://acm.pku.edu.cn/JudgeOnline/problem?id=' + self.problem_id

    def download(self):
        html = self.download_html()
        p = re.compile('<pre class="sio">(.+?)</pre>', re.M | re.S | re.I)
        result = p.findall(html)
        n = len(result) / 2;
        for index in range(n):
            input_file_name = self.get_input_file_path(index)
            output_file_name = self.get_output_file_path(index)
            open(input_file_name, 'w').write(self.format_pre(result[index * 2]))
            open(output_file_name, 'w').write(self.format_pre(result[index * 2 + 1]))
        return True

    def submit(self):
        opener = self.get_opener()

        setting = json.load(open(self.options.setting_file_path))['poj']
        postdata = dict()
        postdata['user_id1'] = setting['user_id']
        postdata['password1'] = setting['password']
        params = urllib.urlencode(postdata)
        p = opener.open('http://poj.org/login', params)
        print('Login ... ' + str(p.getcode()))

        postdata = dict()
        postdata['language'] = self.get_language_id()
        postdata['problem_id'] = self.problem_id
        postdata['source'] = open(self.get_source_file_name()).read()
        postdata['submit'] = 'Submit'
        params = urllib.urlencode(postdata)
        p = opener.open('http://poj.org/submit', params)
        print('Submit ... ' + str(p.getcode()))

        time.sleep(2.0)
        subprocess.call([setting['browser'], 'http://poj.org/status?problem_id=&user_id=' + setting['user_id'] + '&result=&language='])

    def get_language_id_from_extension(self):
        return {'.cpp':'4',
                '.cc':'4',
                '.c':'5',
                '.java':'2',}


class CodeForces(OnlineJudge):
    contest_id = None
    def __init__(self, options, args):
        OnlineJudge.__init__(self, options, args[1])
        self.contest_id = args[0]

    def get_input_file_name(self, index):
        return self.contest_id + self.problem_id + '.' + str(index) + '.in.txt'

    def get_output_file_name(self, index):
        return self.contest_id + self.problem_id + '.' + str(index) + '.out.txt'

    def get_url(self):
        return 'http://codeforces.com/contest/' + self.contest_id + '/problem/' + self.problem_id

    def download(self):
        html = self.download_html()
        p = re.compile('<pre>(.+?)</pre>', re.M | re.S | re.I)
        result = p.findall(html)
        n = len(result) / 2;
        for index in range(n):
            input_file_name = self.get_input_file_path(index)
            output_file_name = self.get_output_file_path(index)
            open(input_file_name, 'w').write(self.format_pre(result[index * 2 + 0]))
            open(output_file_name, 'w').write(self.format_pre(result[index * 2 + 1]))
        return True


class MJudge(OnlineJudge):
    def __init__(self, options, args):
        OnlineJudge.__init__(self, options, args[0])

    def get_url(self):
        return 'http://m-judge.maximum.vc/problem.cgi?pid=' + self.problem_id

    def download_html(self):
        opener = self.get_opener()

        setting = json.load(open(self.options.setting_file_path))['m_judge']
        postdata = dict()
        postdata['user'] = setting['user_id']
        postdata['pswd'] = setting['password']
        params = urllib.urlencode(postdata)
        p = opener.open('http://m-judge.maximum.vc/login.cgi', params)

        url = self.get_url()
        p = opener.open(url)
        return p.read()

    def download(self):
        html = self.download_html()
        index = html.rfind('Sample Input')
        html = html[index:]
        p = re.compile('<pre>(.+?)</pre>', re.M | re.S | re.I)
        result = p.findall(html)
        n = len(result) / 2;
        for index in range(n):
            input_file_name = self.get_input_file_path(index)
            output_file_name = self.get_output_file_path(index)
            open(input_file_name, 'w').write(self.format_pre(result[index * 2 + 0]))
            open(output_file_name, 'w').write(self.format_pre(result[index * 2 + 1]))
        return True

    def submit(self):
        opener = self.get_opener()

        setting = json.load(open(self.options.setting_file_path))['m_judge']
        postdata = dict()
        postdata['user'] = setting['user_id']
        postdata['pswd'] = setting['password']
        params = urllib.urlencode(postdata)
        p = opener.open('http://m-judge.maximum.vc/login.cgi', params)
        print('Login ... ' + str(p.getcode()))

        postdata = dict()
        postdata['m'] = '1'
        postdata['pid'] = self.problem_id
        postdata['lang'] = '1'
        postdata['code'] = open(self.get_source_file_name()).read()
        params = urllib.urlencode(postdata)
        p = opener.open('http://m-judge.maximum.vc/submit.cgi', params)
        print('Submit ... ' + str(p.getcode()))

        subprocess.call([setting['browser'], 'http://m-judge.maximum.vc/result.cgi'])


class AOJ(OnlineJudge):
    def __init__(self, options, args):
        OnlineJudge.__init__(self, options, args[0])

    def get_url(self):
        return 'http://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=' + self.problem_id

    def download(self):
        html = self.download_html()
        index = html.rfind('>Sample Input</')
        html = html[index:]
        p = re.compile('<pre>(.+?)</pre>', re.M | re.S | re.I)
        result = p.findall(html)
        n = len(result) / 2;
        for index in range(n):
            input_file_name = self.get_input_file_path(index)
            output_file_name = self.get_output_file_path(index)
            open(input_file_name, 'w').write(self.format_pre(result[index * 2]))
            open(output_file_name, 'w').write(self.format_pre(result[index * 2 + 1]))
        return True

    def submit(self):
        opener = self.get_opener()

        setting = json.load(open(self.options.setting_file_path))['aoj']

        postdata = dict()
        postdata['userID'] = setting['user_id']
        postdata['password'] = setting['password']
        postdata['problemNO'] = self.problem_id
        postdata['language'] = self.get_language_id()
        postdata['sourceCode'] = open(self.get_source_file_name()).read()
        postdata['submit'] = 'Send'
        params = urllib.urlencode(postdata)
        p = opener.open('http://judge.u-aizu.ac.jp/onlinejudge/servlet/Submit', params)
        print('Submit ... ' + str(p.getcode()))

        time.sleep(2.0)
        subprocess.call([setting['browser'], 'http://judge.u-aizu.ac.jp/onlinejudge/status.jsp'])
    
    def get_language_id_from_extension(self):
        return {'.cpp':'C++',
                '.cc':'C++',
                '.c':'C',
                '.java':'JAVA',
                '.cs':'C#',
                '.d':'D',
                '.rb':'Ruby',
                '.py':'Python',
                '.php':'PHP',}


class AOJ_test(OnlineJudge):
    def __init__(self, options, args):
        OnlineJudge.__init__(self, options, args[0])

    def get_url(self,index,inout):
        return 'http://analytic.u-aizu.ac.jp:8080/aoj/testcase.jsp?id=' + self.problem_id + '&case=' + str(index) + '&type=' + inout

    def download_html(self,index,inout):
        url = self.get_url(index,inout)
        return self.get_opener().open(url).read()

    def download(self):
        for index in range(100):
            try:
                input_data=self.download_html(index+1,"in")
                if input_data == "In preparation.\n":
                    print("testcase in preparation")
                    break
                output_data=self.download_html(index+1,"out")
                input_file_name = self.get_input_file_path(index)
                output_file_name = self.get_output_file_path(index)
                open(input_file_name, 'w').write(input_data)
                open(output_file_name, 'w').write(output_data)
            except:
                print("testcase notfound: index%d"%index)
                break
        return True


class CodeChef(OnlineJudge):
    contest_id = None
    def __init__(self, options, args):
        OnlineJudge.__init__(self, options, args[1])
        self.contest_id = args[0]

    def get_input_file_name(self, index):
        return self.contest_id + '.' + self.problem_id + '.' + str(index) + '.in.txt'

    def get_output_file_name(self, index):
        return self.contest_id + '.' + self.problem_id + '.' + str(index) + '.out.txt'

    def get_url(self):
        return 'http://www.codechef.com/' + self.contest_id + '/problems/' + self.problem_id

    def download(self):
        html = self.download_html()
        p = re.compile('put:</b>(.+?)<', re.M | re.S | re.I)
        result = p.findall(html)
        n = len(result) / 2;
        for index in range(n):
            input_file_name = self.get_input_file_path(index)
            output_file_name = self.get_output_file_path(index)
            open(input_file_name, 'w').write(self.format_pre(result[index * 2 + 0]))
            open(output_file_name, 'w').write(self.format_pre(result[index * 2 + 1]))
        return True


class ImoJudge(OnlineJudge):
    contest_id = None
    def __init__(self, options, args):
        OnlineJudge.__init__(self, options, args[1])
        self.contest_id = args[0]

    def get_input_file_name(self, index):
        return self.contest_id + '.' + self.problem_id + '.' + str(index) + '.in.txt'

    def get_output_file_name(self, index):
        return self.contest_id + '.' + self.problem_id + '.' + str(index) + '.out.txt'

    def get_url(self):
        return 'http://judge.imoz.jp/page.php?page=view_problem&pid=%s&cid=%s' % (self.problem_id, self.contest_id)

    def download(self):
        html = self.download_html()
        p = re.compile('<pre>(.+?)</pre>', re.M | re.S | re.I)
        result = p.findall(html)
        n = len(result) / 2;
        for index in range(n):
            input_file_name = self.get_input_file_path(index)
            output_file_name = self.get_output_file_path(index)
            open(input_file_name, 'w').write(self.format_pre(result[index * 2 + 0]))
            open(output_file_name, 'w').write(self.format_pre(result[index * 2 + 1]))
        return True


class AtCoder(OnlineJudge):
    contest_id = None
    def __init__(self, options, args):
        OnlineJudge.__init__(self, options, args[1])
        self.contest_id = args[0]

        self.problem_id = self.assume_correct_probrem_id()

    def assume_correct_probrem_id(self):
        result = re.match('(a[rb]c)(\d{3})', self.contest_id)
        if result and self.problem_id in list('1234ABCDabcd'):
            contest_type = result.group(1)
            contest_id_number = int(result.group(2))
            if self.problem_id in list('1234'):
                problem_id_number = int(self.problem_id)
            else:
                problem_id_number = list('abcd').index(self.problem_id.lower()) + 1
            if (contest_type == 'arc' and contest_id_number >= 35) or \
                    (contest_type == 'abc' and contest_id_number >= 20):
                return self.contest_id + '_' + list('abcd')[problem_id_number - 1]
            else:
                return self.contest_id + '_' + str(problem_id_number)
        elif self.problem_id.find('_') == -1:
            # is this really corrent?
            return self.contest_id.replace('-', '_') + '_' + self.problem_id
        else:
            return self.problem_id

    def get_url(self):
        return "http://%s.contest.atcoder.jp/tasks/%s" % (self.contest_id, self.problem_id)

    def get_opener(self):
        if self.opener == None:
            opener = OnlineJudge.get_opener(self)

            setting = json.load(open(self.options.setting_file_path))['atcoder']
            postdata = dict()
            postdata['name'] = setting['user_id']
            postdata['password'] = setting['password']
            postdata['submit'] = 'login'
            params = urllib.urlencode(postdata)
            p = opener.open('https://%s.contest.atcoder.jp/login' % self.contest_id, params)
            print('Login ... ' + str(p.getcode()))
        return self.opener

    def download(self):
        html = self.download_html()
        if '入力例' in html:
            html = html[html.find('入力例'):]
        if 'Sample Input' in html:
            html = html[html.find('Sample Input'):]
        p = re.compile('<pre.*?>(.+?)</pre>', re.M | re.S | re.I)
        result = p.findall(html)
        n = len(result) / 2
        for index in range(n):
            input_file_name = self.get_input_file_path(index)
            output_file_name = self.get_output_file_path(index)
            open(input_file_name, 'w').write(self.format_pre(result[index * 2 + 0]))
            open(output_file_name, 'w').write(self.format_pre(result[index * 2 + 1]))
        return True

    def submit(self):
        html = self.download_html()
        p = re.compile('"/submit\\?task_id=(.+?)"', re.M | re.S | re.I)
        result = p.findall(html)
        task_id = int(result[0])

        html = self.get_opener().open('http://%s.contest.atcoder.jp/submit?task_id=%d' % (self.contest_id, task_id)).read()
        p = re.compile('name="__session" value="([0-9a-f]+?)"', re.M | re.S | re.I)
        result = p.findall(html)
        session = result[0]

        opener = self.get_opener()

        postdata = dict()
        postdata['__session'] = session
        postdata['task_id'] = task_id
        postdata['language_id_%d' % task_id] = self.get_language_id()
        postdata['source_code'] = open(self.get_source_file_name()).read()
        postdata['submit'] = 'submit'
        params = urllib.urlencode(postdata)
        p = opener.open('http://%s.contest.atcoder.jp/submit?task_id=%d' % (self.contest_id, task_id), params)
        print('Submit ... ' + str(p.getcode()))

        time.sleep(2.0)
        setting = json.load(open(self.options.setting_file_path))['atcoder']
        subprocess.call([setting['browser'], 'http://%s.contest.atcoder.jp/submissions/me' % self.contest_id])

    def get_language_id_from_extension(self):
        return {'.cpp':'10',
                '.cc':'10',
                '.c':'1',
                '.java':'3',
                '.php':'5',
                '.py':'7',
                '.pl':'8',
                '.rb':'9',
                '.hs':'11'}


class ZOJContest(OnlineJudge):
    def __init__(self, options, args):
        OnlineJudge.__init__(self, options, args[0])

    def get_url(self):
        return 'http://acm.zju.edu.cn/onlinejudge/showContestProblem.do?problemId=%s' % self.problem_id

    def get_opener(self):
        if self.opener == None:
            opener = OnlineJudge.get_opener(self)

            setting = json.load(open(self.options.setting_file_path))['zoj']
            postdata = dict()
            postdata['handle'] = setting['user_id']
            postdata['password'] = setting['password']
            postdata['rememberMe'] = '1'
            postdata['submit'] = 'Login'
            params = urllib.urlencode(postdata)
            p = opener.open('http://acm.zju.edu.cn/onlinejudge/login.do', params)
            print('Login ... ' + str(p.getcode()))
        return self.opener

    def download(self):
        opener = self.get_opener()

        html = self.download_html()
        p = re.compile('<pre>(.+?)</pre>', re.M | re.S | re.I)
        result = p.findall(html)
        n = len(result) / 2;
        for index in range(n):
            input_file_name = self.get_input_file_path(index)
            output_file_name = self.get_output_file_path(index)
            open(input_file_name, 'w').write(self.format_pre(result[index * 2 + 0]))
            open(output_file_name, 'w').write(self.format_pre(result[index * 2 + 1]))
        return True

    def submit(self):
        opener = self.get_opener()

        postdata = dict()
        postdata['problemId'] = self.problem_id
        postdata['languageId'] = '2'
        postdata['source'] = open(self.get_source_file_name()).read()
        postdata['submit'] = 'Submit'
        params = urllib.urlencode(postdata)
        p = opener.open('http://acm.zju.edu.cn/onlinejudge/contestSubmit.do')
        print('Submit ... ' + str(p.getcode()))

    def get_language_id_from_extension(self):
        return {'.cpp':'2',
                '.cc':'2',
                '.c':'1',
                '.java':'4',
                '.py':'5',
                '.perl':'6',
                '.php':'8',}


class NPCA(OnlineJudge):
    def __init__(self, options, args):
        OnlineJudge.__init__(self, options, args[0])

    def get_url(self):
        return 'http://judge.npca.jp/problems/view/%s' % self.problem_id

    def get_opener(self):
        if self.opener == None:
            opener = OnlineJudge.get_opener(self)

            setting = json.load(open(self.options.setting_file_path))['npca']
            postdata = dict()
            postdata['_method'] = 'POST'
            postdata['data[User][username]'] = setting['user_id']
            postdata['data[User][password]'] = setting['password']
            postdata['data[User][active]'] = '1'
            postdata['submit'] = 'Login'
            params = urllib.urlencode(postdata)
            p = opener.open('http://judge.npca.jp/users/login', params)
            print('Login ... ' + str(p.getcode()))
        return self.opener

    def download(self):
        opener = self.get_opener()

        html = self.download_html()
        p = re.compile('<pre>(.+?)</pre>', re.M | re.S | re.I)
        result = p.findall(html)
        n = len(result) / 2;
        for index in range(n):
            input_file_name = self.get_input_file_path(index)
            output_file_name = self.get_output_file_path(index)
            open(input_file_name, 'w').write(self.format_pre(result[index * 2 + 0]))
            open(output_file_name, 'w').write(self.format_pre(result[index * 2 + 1]))
        return True

    def submit(self):
        opener = self.get_opener()

        postdata = dict()
        postdata['_method'] = 'POST'
        postdata['data[Submission][language_id]'] = self.get_language_id()
        postdata['data[Submission][source]'] = open(self.get_source_file_name()).read()
        postdata['submit'] = 'Submit'
        params = urllib.urlencode(postdata)
        p = opener.open('http://judge.npca.jp/submissions/submit/%s/' % self.problem_id)
        print('Submit ... ' + str(p.getcode()))

    def get_language_id_from_extension(self):
        return {'.cpp':'2',
                '.cc':'2',
                '.c':'1',
                '.java':'7',
                '.py':'11',
                '.perl':'9',
                '.php':'10'}


class KCS(OnlineJudge):
    contest_id = None
    def __init__(self, options, args):
        OnlineJudge.__init__(self, options, args[1])
        self.contest_id = args[0]

    def get_url(self):
        return "http://kcs.miz-miz.biz/contest/%s/view/%s" % (self.contest_id, self.problem_id)

    def get_opener(self):
        if self.opener == None:
            opener = OnlineJudge.get_opener(self)

            setting = json.load(open(self.options.setting_file_path))['kcs']
            postdata = dict()
            postdata['user_id'] = setting['user_id']
            postdata['password'] = setting['password']
            postdata['submit'] = '送信'
            params = urllib.urlencode(postdata)
            p = opener.open('http://kcs.miz-miz.biz/user/login', params)
            print('Login ... ' + str(p.getcode()))
        return self.opener

    def download(self):
        html = self.download_html()
        if '入出力例' in html:
            html = html[html.find('入出力例'):]
        p = re.compile('<pre>(.+?)</pre>', re.M | re.S | re.I)
        result = p.findall(html)
        n = len(result) / 2
        for index in range(n):
            input_file_name = self.get_input_file_path(index)
            output_file_name = self.get_output_file_path(index)
            open(input_file_name, 'w').write(self.format_pre(result[index * 2 + 0]))
            open(output_file_name, 'w').write(self.format_pre(result[index * 2 + 1]))
        return True

    def submit(self):
        opener = self.get_opener()

        postdata = dict()
        postdata['language'] = self.get_language_id()
        postdata['code'] = open(self.get_source_file_name()).read()
        postdata['submit'] = 'submit'
        params = urllib.urlencode(postdata)
        p = opener.open('http://kcs.miz-miz.biz/contest/%s/submit/%s' % (self.contest_id, self.problem_id), params)
        print('Submit ... ' + str(p.getcode()))

        time.sleep(2.0)
        setting = json.load(open(self.options.setting_file_path))['kcs']
        subprocess.call([setting['browser'], 'http://kcs.miz-miz.biz/contest/%s/submissions/page=1' % self.contest_id])

    def get_language_id_from_extension(self):
        return {'.c':'C',
                '.cc':'C++11',
                '.cpp':'C++11',
                '.cs':'C#',
                '.py':'Python',
                '.rb':'Ruby',
                '.java':'Java'}


class yukicoder(OnlineJudge):
    def __init__(self, options, args):
        OnlineJudge.__init__(self, options, args[0])

    def get_url(self):
        return "http://yukicoder.me/problems/no/%s" % self.problem_id

    def download(self):
        html = self.download_html()
        if 'class="sample"' in html:
            html = html[html.find('class="sample"'):]
        p = re.compile('<pre>(.+?)</pre>', re.M | re.S | re.I)
        result = p.findall(html)
        n = len(result) / 2
        for index in range(n):
            input_file_name = self.get_input_file_path(index)
            output_file_name = self.get_output_file_path(index)
            open(input_file_name, 'w').write(self.format_pre(result[index * 2 + 0]))
            open(output_file_name, 'w').write(self.format_pre(result[index * 2 + 1]))
        return True

    def get_source_file_name(self):
        if self.options.source_file_name:
            return self.options.source_file_name
        else:
            return '../yukicoder' + self.problem_id + '.rb'

class yukicoder_test(OnlineJudge):
    def __init__(self, options, args):
        OnlineJudge.__init__(self, options, args[0])
        self.testcase_names=[""]
        testfoldername = self.__class__.__name__ + '.' + self.problem_id + "/test_in"
        if os.path.exists(testfoldername):
            self.testcase_names = os.listdir(testfoldername)

    def get_input_file_name(self, index):
        if len(self.testcase_names) <= index:
            return "----invalid name" # とりあえずなさそうな名前を返す
        print(self.testcase_names[index])
        return self.__class__.__name__ + '.' + self.problem_id + '/test_in/' + self.testcase_names[index]

    def get_output_file_name(self, index):
        if len(self.testcase_names) <= index:
            return "----invalid name" # とりあえずなさそうな名前を返す
        return self.__class__.__name__ + '.' + self.problem_id + '/test_out/' + self.testcase_names[index]

    def get_url(self):
        return "http://yukicoder.me/problems/no/%s/testcase.zip" % self.problem_id

    def download(self):
        if self.problem_id == "9999":
            return True
        try:
            zipf = self.get_opener().open(self.get_url())
            zipname = self.__class__.__name__ + '.' + self.problem_id + ".zip"
            open(zipname, "w").write(zipf.read())
            with zipfile.ZipFile(zipname) as z:
                self.testcase_names = [os.path.basename(i) for i in z.namelist() if i[0:7]=="test_in"]
                z.extractall(self.__class__.__name__ + '.' + self.problem_id)
            return True
        except urllib2.HTTPError as error:
            print(error)
            return False

    def get_source_file_name(self):
        if self.options.source_file_name:
            return self.options.source_file_name
        else:
            return '../yukicoder' + self.problem_id + '.rb'
