#!/usr/bin/python
from optparse import OptionParser
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

class Validator:
    def validate(self, answer_path, output_path):
        raise NotImplementedError


class DiffValidator(Validator):
    def validate(self, answer_path, output_path):
        return subprocess.call(['diff', answer_path, output_path, '-y', '--strip-trailing-cr', '-W', '79', '-a', '-d']) == 0
    
    
class FloatingPointValidator(Validator):
    absolute_error = None
    def __init__(self, absolute_error):
        self.absolute_error = float(absolute_error)

    def validate(self, answer_path, output_path):
        answer_file = open(answer_path)
        output_file = open(output_path)
        result = True
        print '%-25s %-25s   %s' % ('answer', 'output', 'diff')
        while True:
            answer_line = answer_file.readline()
            output_line = output_file.readline()
            
            if answer_line == '' and output_line == '':
                break
            
            answer_line = answer_line.strip()
            output_line = output_line.strip()
            
            answer_value = float(answer_line)
            output_value = float(output_line)
            ok = False
            diff = output_value - answer_value
            
            if abs(diff) < self.absolute_error:
                ok = True

#            if abs(answer_value) > absolute_error:
#                if abs((answer_value - output_value) / answer_value) < relative_error:
#                    ok = True
            
            separator = ' '

            if not ok:
                separator = '|'
                result = False

            print '%-25s %-25s %s %e' % (answer_line, output_line, separator, diff)
        return result


class Solution:
    def __init__(self, source_file_name):
        self.source_file_name = source_file_name
    def compile(self):
        raise NotImplementedError
    def execute(self, input_file_path, output_file_path):
        start_time = time.time()
        p = subprocess.Popen(self.get_execute_command_line(),
                             stdin=open(input_file_path, 'r'),
                             stdout=open(output_file_path, 'w'))
        if p.wait() != 0:
            print 'RuntimeError?'
            exit(-1)
        end_time = time.time()
        return end_time - start_time
    def get_execute_command_line(self):
        raise NotImplementedError


class SolutionC(Solution):
    def __init__(self, source_file_name):
        Solution.__init__(self, source_file_name)
    def compile(self):
        return subprocess.call(['gcc', '-O2', '-o', 'a.exe', '-Wno-deprecated', '-Wall', self.source_file_name]) == 0
    def get_execute_command_line(self):
        return ['./a.exe']


class SolutionCxx(Solution):
    def __init__(self, source_file_name):
        Solution.__init__(self, source_file_name)
    def compile(self):
        return subprocess.call(['g++', '-O2', '-o', 'a.exe', '-Wno-deprecated', '-Wall', self.source_file_name]) == 0
    def get_execute_command_line(self):
        return ['./a.exe']


class SolutionJava(Solution):
    def __init__(self, source_file_name):
        Solution.__init__(self, source_file_name)
    def compile(self):
        return subprocess.call(['javac', self.source_file_name]) == 0
    def get_execute_command_line(self):
        class_name = self.source_file_name.split('.')[0]
        return ['java', '-Xmx256m', class_name]


class SolutionIo(Solution):
    def __init__(self, source_file_name):
        Solution.__init__(self, source_file_name)
    def compile(self):
        return True
    def get_execute_command_line(self):
        return ['io', self.source_file_name]


class SolutionPhp(Solution):
    def __init__(self, source_file_name):
        Solution.__init__(self, source_file_name)
    def compile(self):
        return True
    def get_execute_command_line(self):
        return ['php', self.source_file_name]


class SolutionPython(Solution):
    def __init__(self, source_file_name):
        Solution.__init__(self, source_file_name)
    def compile(self):
        return True
    def get_execute_command_line(self):
        return ['python', self.source_file_name]


class SolutionPerl(Solution):
    def __init__(self, source_file_name):
        Solution.__init__(self, source_file_name)
    def compile(self):
        return True
    def get_execute_command_line(self):
        return ['perl', self.source_file_name]


class SolutionRuby(Solution):
    def __init__(self, source_file_name):
        Solution.__init__(self, source_file_name)
    def compile(self):
        return True
    def get_execute_command_line(self):
        return ['ruby', self.source_file_name]


class SolutionHaskell(Solution):
    def __init__(self, source_file_name):
        Solution.__init__(self, source_file_name)
    def compile(self):
        return subprocess.call(['ghc', '-o', 'a.exe', self.source_file_name]) == 0
    def get_execute_command_line(self):
        return ['./a.exe']


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
    
    def get_input_file_name(self, index):
        return self.problem_id + '.' + str(index) + '.in.txt'
    
    def get_output_file_name(self, index):
        return self.problem_id + '.' + str(index) + '.out.txt'
    
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
        if source_file_name.endswith('.c'):
            return SolutionC(source_file_name)
        elif source_file_name.endswith('.cpp') or source_file_name.endswith('.cc'):
            return SolutionCxx(source_file_name)
        elif source_file_name.endswith('.java'):
            return SolutionJava(source_file_name)
        elif source_file_name.endswith('.io'):
            return SolutionIo(source_file_name)
        elif source_file_name.endswith('.php'):
            return SolutionPhp(source_file_name)
        elif source_file_name.endswith('.py'):
            return SolutionPython(source_file_name)
        elif source_file_name.endswith('.pl'):
            return SolutionPerl(source_file_name)
        elif source_file_name.endswith('.rb'):
            return SolutionRuby(source_file_name)
        elif source_file_name.endswith('.hs'):
            return SolutionHaskell(source_file_name)
        else:
            return Solution(source_file_name)
    
    def get_validator(self):
        if not self.options.floating_point:
            return DiffValidator()
        else:
            return FloatingPointValidator(self.options.floating_point)

    def check(self):
        print 'compiling...'

        solution = self.get_solution()
        
        if not solution.compile():
            print 'CompileError'
            exit(-1)
        
        if not os.path.exists(self.get_input_file_name(0)) or not os.path.exists(self.get_output_file_name(0)):
            print 'downloading...'
            self.download()
        
        max_time = 0.0
        
        validator = self.get_validator()

        ok = True
        no_input_files = True

        for index in range(100):
            input_file_path = self.get_input_file_name(index)
            output_file_path = self.get_output_file_name(index)
        
            if not os.path.exists(input_file_path):
                break

            no_input_files = False

            print 'Case #' + str(index) + ':'
                        
            execution_time = solution.execute(input_file_path, 'out.txt')

            if max_time < execution_time:
                max_time = execution_time
    
            if os.path.exists(output_file_path):
                ok = validator.validate(output_file_path, 'out.txt') and ok
            else:
                subprocess.Popen(['cat', 'out.txt']).wait()
            
        if no_input_files:
            print 'No input files...'
        elif ok:
            print 'OK (max ' + str(max_time) + "s)"
        else:
            print 'WrongAnswer (max ' + str(max_time) + "s)"
    
    def add_test_case_template(self):
        for index in range(100):
            input_filepath = self.get_input_file_name(index)
            output_filepath = self.get_output_file_name(index)
            if os.path.isfile(input_filepath):
                continue
            open(input_filepath, 'w').close()
            open(output_filepath, 'w').close()
            print "Test case template file " + str(index) + " is created."
            return

    def submit(self):
        raise NotImplementedError
    
    def create_solution_template_file(self):
        try:
            src = self.get_source_file_name()
            dst = self.get_source_file_name() + ".bak"
            shutil.copyfile(src, dst)
            print 'Copied %s to %s' % (src, dst)
        except IOError, (errno, strerror):
            print "I/O error(%s): %s" % (errno, strerror)
        try:
            src = 'template.cpp'
            dst = self.get_source_file_name()
            shutil.copyfile(src, dst)
            print 'Copied %s to %s' % (src, dst)
        except IOError, (errno, strerror):
            print "I/O error(%s): %s" % (errno, strerror)

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
            input_file_name = self.get_input_file_name(index)
            output_file_name = self.get_output_file_name(index)
            open(input_file_name, 'w').write(self.format_pre(result[index * 2]))
            open(output_file_name, 'w').write(self.format_pre(result[index * 2 + 1]))
        return True

    def submit(self):
        opener = self.get_opener()
    
        setting = json.load(open('setting.json'))['poj']
        postdata = dict()
        postdata['user_id1'] = setting['user_id']
        postdata['password1'] = setting['password']
        params = urllib.urlencode(postdata)
        p = opener.open('http://poj.org/login', params)
        print 'Login ... ' + str(p.getcode())
        
        postdata = dict()
        postdata['language'] = self.get_language_id()
        postdata['problem_id'] = self.problem_id
        postdata['source'] = open(self.get_source_file_name()).read()
        postdata['submit'] = 'Submit'
        params = urllib.urlencode(postdata)
        p = opener.open('http://poj.org/submit', params)
        print 'Submit ... ' + str(p.getcode())
        
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
            input_file_name = self.get_input_file_name(index)
            output_file_name = self.get_output_file_name(index)
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
    
        setting = json.load(open('setting.json'))['m_judge']
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
            input_file_name = self.get_input_file_name(index)
            output_file_name = self.get_output_file_name(index)
            open(input_file_name, 'w').write(self.format_pre(result[index * 2 + 0]))
            open(output_file_name, 'w').write(self.format_pre(result[index * 2 + 1]))
        return True

    def submit(self):
        opener = self.get_opener()
    
        setting = json.load(open('setting.json'))['m_judge']
        postdata = dict()
        postdata['user'] = setting['user_id']
        postdata['pswd'] = setting['password']
        params = urllib.urlencode(postdata)
        p = opener.open('http://m-judge.maximum.vc/login.cgi', params)
        print 'Login ... ' + str(p.getcode())

        postdata = dict()
        postdata['m'] = '1'
        postdata['pid'] = self.problem_id
        postdata['lang'] = '1'
        postdata['code'] = open(self.get_source_file_name()).read()
        params = urllib.urlencode(postdata)
        p = opener.open('http://m-judge.maximum.vc/submit.cgi', params)
        print 'Submit ... ' + str(p.getcode())
    
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
            input_file_name = self.get_input_file_name(index)
            output_file_name = self.get_output_file_name(index)
            open(input_file_name, 'w').write(self.format_pre(result[index * 2]))
            open(output_file_name, 'w').write(self.format_pre(result[index * 2 + 1]))
        return True

    def submit(self):
        opener = self.get_opener()
    
        setting = json.load(open('setting.json'))['aoj']
        
        postdata = dict()
        postdata['userID'] = setting['user_id'] 
        postdata['password'] = setting['password']
        postdata['problemNO'] = self.problem_id
        postdata['language'] = self.get_language_id()
        postdata['sourceCode'] = open(self.get_source_file_name()).read()
        postdata['submit'] = 'Send'
        params = urllib.urlencode(postdata)
        p = opener.open('http://judge.u-aizu.ac.jp/onlinejudge/servlet/Submit', params)
        print 'Submit ... ' + str(p.getcode())
    
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
            input_file_name = self.get_input_file_name(index)
            output_file_name = self.get_output_file_name(index)
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
            input_file_name = self.get_input_file_name(index)
            output_file_name = self.get_output_file_name(index)
            open(input_file_name, 'w').write(self.format_pre(result[index * 2 + 0]))
            open(output_file_name, 'w').write(self.format_pre(result[index * 2 + 1]))
        return True


class AtCoder(OnlineJudge):
    contest_id = None
    def __init__(self, options, args):
        OnlineJudge.__init__(self, options, args[1])
        self.contest_id = int(args[0])
        
    def get_url(self):
        return "http://arc%03d.contest.atcoder.jp/tasks/arc%03d_%d" % (self.contest_id, self.contest_id, int(self.problem_id))
    
    def get_opener(self):
        if self.opener == None:
            opener = OnlineJudge.get_opener(self)
            
            setting = json.load(open('setting.json'))['atcoder']
            postdata = dict()
            postdata['name'] = setting['user_id']
            postdata['password'] = setting['password']
            postdata['submit'] = 'login'
            params = urllib.urlencode(postdata)
            p = opener.open('http://arc%03d.contest.atcoder.jp/login' % self.contest_id, params)
            print 'Login ... ' + str(p.getcode())
        return self.opener

    def download(self):
        html = self.download_html()
        p = re.compile('<pre>(.+?)</pre>', re.M | re.S | re.I)
        result = p.findall(html)
        n = len(result) / 2
        for index in range(n):
            input_file_name = self.get_input_file_name(index)
            output_file_name = self.get_output_file_name(index)
            open(input_file_name, 'w').write(self.format_pre(result[index * 2 + 1]))
            open(output_file_name, 'w').write(self.format_pre(result[index * 2 + 2]))
        return True

    def submit(self):
        html = self.download_html()
        p = re.compile('"/submit\\?task_id=(.+?)"', re.M | re.S | re.I)
        result = p.findall(html)
        task_id = int(result[0])
        
        html = self.get_opener().open('http://arc%03d.contest.atcoder.jp/submit?task_id=%d' % (self.contest_id, task_id)).read()
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
        p = opener.open('http://arc%03d.contest.atcoder.jp/submit?task_id=%d' % (self.contest_id, task_id), params)
        print 'Submit ... ' + str(p.getcode())
        
        time.sleep(2.0)
        setting = json.load(open('setting.json'))['atcoder']
        subprocess.call([setting['browser'], 'http://arc%03d.contest.atcoder.jp/submissions/me' % self.contest_id])    
    
    def get_language_id_from_extension(self):
        return {'.cpp':'2',
                '.cc':'2',
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
            
            setting = json.load(open('setting.json'))['zoj']
            postdata = dict()
            postdata['handle'] = setting['user_id']
            postdata['password'] = setting['password']
            postdata['rememberMe'] = '1'
            postdata['submit'] = 'Login'
            params = urllib.urlencode(postdata)
            p = opener.open('http://acm.zju.edu.cn/onlinejudge/login.do', params)
            print 'Login ... ' + str(p.getcode())
        return self.opener

    def download(self):
        opener = self.get_opener()
        
        html = self.download_html()
        p = re.compile('<pre>(.+?)</pre>', re.M | re.S | re.I)
        result = p.findall(html)
        n = len(result) / 2;
        for index in range(n):
            input_file_name = self.get_input_file_name(index)
            output_file_name = self.get_output_file_name(index)
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
        print 'Submit ... ' + str(p.getcode())
    
    def get_language_id_from_extension(self):
        return {'.cpp':'2',
                '.cc':'2',
                '.c':'1',
                '.java':'4',
                '.py':'5',
                '.perl':'6',
                '.php':'8',}


def main():
    parser = OptionParser()
    # function
    parser.add_option("-c", "--create-solution-template-file", action="store_true",
                      dest="create_solution_template_file", default=False,
                      help="Build and check the solution")
    parser.add_option("-s", "--submit", action="store_true",
                      dest="submit", default=False,
                      help="Submit the solution")
    parser.add_option("-a", "--add-test-case-template", action="store_true",
                      dest="add_test_case", default=False,
                      help="Add a test case template file")
    parser.add_option('-i', '--source-file-name', action='store',
                      dest='source_file_name', default=None,
                      help='Specify the source file name')

    # switch online judge
    parser.add_option("--poj", action="store_true",
                      dest="poj", default=True,
                      help="PKU JudgeOnline")
    parser.add_option("--codeforces", action="store_true",
                      dest="codeforces", default=False,
                      help="CodeForces")
    parser.add_option("--mjudge", action="store_true",
                      dest="m_judge", default=False,
                      help="M-Judge")
    parser.add_option("--aoj", action="store_true",
                      dest="aoj", default=False,
                      help="Aizu Online Judge")
    parser.add_option("--codechef", action="store_true",
                      dest="codechef", default=False,
                      help="CodeChef")
    parser.add_option("--imojudge", action="store_true",
                      dest="imojudge", default=False,
                      help="Imo Judge")
    parser.add_option("--atcoder", action="store_true",
                      dest="atcoder", default=False,
                      help="AtCoder")
    parser.add_option("--zojcontest", action="store_true",
                      dest="zoj_contest", default=False,
                      help="ZOJ Contest")
    
    # misc
    parser.add_option("-t", "--titech-pubnet", action="store_true",
                      dest="titech_pubnet", default=False,
                      help="Use titech pubnet proxy",)
    parser.add_option("-e", action="store",
                      dest="floating_point", default=None,
                      help="Use floating point validator and set max error")
    parser.add_option('-d', '--download', action="store_true",
                      dest='download', default=False,
                      help="Only download the test cases")

    (options, args) = parser.parse_args()
    
    if len(args) == 0:
        print "Select problem id."
        parser.print_help()
        return
    
    online_judge = None
    if options.zoj_contest:
        online_judge = ZOJContest(options, args)
    elif options.atcoder:
        online_judge = AtCoder(options, args)
    elif options.imojudge:
        online_judge = ImoJudge(options, args)
    elif options.codechef:
        online_judge = CodeChef(options, args)
    elif options.codeforces:
        online_judge = CodeForces(options, args)
    elif options.m_judge:
        online_judge = MJudge(options, args)
    elif options.aoj:
        online_judge = AOJ(options, args)
    elif options.poj:
        online_judge = POJ(options, args)
    else:
        print 'Select an online judge!!!'
        parser.print_help()
        return
    
    if options.add_test_case:
        online_judge.add_test_case_template()
    elif options.submit:
        online_judge.submit()
    elif options.create_solution_template_file:
        online_judge.create_solution_template_file()
    elif options.download:
        online_judge.download()
    else:
        online_judge.check()
    
if __name__ == '__main__':
    main()


