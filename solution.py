#!/usr/bin/env python3
import os
import os.path
import platform
import subprocess
import time

class Solution:
    def __init__(self, source_file_name):
        self.source_file_name = source_file_name
    def compile(self):
        raise NotImplementedError
    def execute(self, input_file_path, output_file_path):
        start_time = time.time()
        p = subprocess.Popen(self.get_execute_command_line(),
                             stdin=open(input_file_path, 'r'),
                             stdout=open(output_file_path, 'w'),
                             env=self.get_execute_env())
        if p.wait() != 0:
            print('RuntimeError?')
            exit(-1)
        end_time = time.time()
        return end_time - start_time
    def get_execute_command_line(self):
        raise NotImplementedError
    def get_execute_env(self):
        return os.environ
    def get_a_out_name(self):
        if platform.system() == 'Windows':
            return 'a.exe'
        else:
            return 'a.out'


class SolutionC(Solution):
    def __init__(self, source_file_name):
        Solution.__init__(self, source_file_name)
    def compile(self):
        return subprocess.call(['gcc', '-O2', '-o', self.get_a_out_name(), '-Wno-deprecated', '-Wall', self.source_file_name]) == 0
    def get_execute_command_line(self):
        return ['./' + self.get_a_out_name()]


class SolutionCxx(Solution):
    def __init__(self, source_file_name):
        Solution.__init__(self, source_file_name)
    def compile(self):
        return subprocess.call(['g++', '-O2', '-o', self.get_a_out_name(), '-Wno-deprecated', '-Wall', '-std=c++11', self.source_file_name]) == 0
    def get_execute_command_line(self):
        return ['./' + self.get_a_out_name()]


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
    def get_execute_env(self):
        env=os.environ.copy()
        env['PYENV_VERSION']='2.7.9'
        return env
    def get_execute_command_line(self):
        return ['python', self.source_file_name]

class SolutionPyPy(Solution):
    def __init__(self, source_file_name):
        Solution.__init__(self, source_file_name)
    def compile(self):
        return True
    def get_execute_env(self):
        env=os.environ.copy()
        env['PYENV_VERSION']='pypy-2.5.0'
        return env
    def get_execute_command_line(self):
        return ['pypy', self.source_file_name]

class SolutionPython3(Solution):
    def __init__(self, source_file_name):
        Solution.__init__(self, source_file_name)
    def compile(self):
        return True
    def get_execute_env(self):
        env=os.environ.copy()
        env['PYENV_VERSION']='3.4.2'
        return env
    def get_execute_command_line(self):
        return ['python3', self.source_file_name]

class SolutionPyPy3(Solution):
    def __init__(self, source_file_name):
        Solution.__init__(self, source_file_name)
    def compile(self):
        return True
    def get_execute_env(self):
        env=os.environ.copy()
        env['PYENV_VERSION']='pypy3-2.4.0'
        return env
    def get_execute_command_line(self):
        return ['pypy3', self.source_file_name]


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
    def get_execute_env(self):
        env=os.environ.copy()
        env['RBENV_VERSION']='2.2.0'
        return env
    def get_execute_command_line(self):
        return ['ruby', self.source_file_name]

class SolutionRuby19(Solution):
    def __init__(self, source_file_name):
        Solution.__init__(self, source_file_name)
    def compile(self):
        return True
    def get_execute_env(self):
        env=os.environ.copy()
        env['RBENV_VERSION']='system'
        return env
    def get_execute_command_line(self):
        return ['ruby', self.source_file_name]

class SolutionRubyTopaz(Solution):
    def __init__(self, source_file_name):
        Solution.__init__(self, source_file_name)
    def compile(self):
        return True
    def get_execute_env(self):
        env=os.environ.copy()
        env['RBENV_VERSION']='topaz-dev'
    def get_execute_command_line(self):
        return ['topaz', self.source_file_name]


class SolutionHaskell(Solution):
    def __init__(self, source_file_name):
        Solution.__init__(self, source_file_name)
    def compile(self):
        return subprocess.call(['ghc', '-o', self.get_a_out_name(), self.source_file_name]) == 0
    def get_execute_command_line(self):
        return ['./' + self.get_a_out_name()]

class SolutionScala(Solution):
    def __init__(self, source_file_name):
        Solution.__init__(self, source_file_name)
    def get_execute_env(self):
        env=os.environ.copy()
        env['SCALAENV_VERSION']='scala-2.11.5'
    def compile(self):
        return subprocess.call(['scalac', self.source_file_name],env=self.get_execute_env()) == 0
    def get_execute_command_line(self):
        return ['scala',"-J-Xmx1024m","Main"]

class SolutionCs(Solution):
    def __init__(self, source_file_name):
        Solution.__init__(self, source_file_name)
    def compile(self):
        s=subprocess.check_output(['cygpath', '-w', self.source_file_name]).rstrip()
        return subprocess.call(['csc', '/out:a.exe', s]) == 0
    def get_execute_command_line(self):
        return ['./a.exe']

class SolutionGo(Solution):
    def __init__(self, source_file_name):
        Solution.__init__(self, source_file_name)
    def compile(self):
        return subprocess.call(['go', 'build', '-o', 'a.out', self.source_file_name]) == 0
    def get_execute_command_line(self):
        return ['./a.out']

class SolutionD(Solution):
    def __init__(self, source_file_name):
        Solution.__init__(self, source_file_name)
    def compile(self):
        return subprocess.call(['dmd', '-m64', '-w', '-wi', '-O', '-release', '-inline', '-ofa.out', self.source_file_name]) == 0
    def get_execute_command_line(self):
        return ['./a.out']

class SolutionOCaml(Solution):
    def __init__(self, source_file_name):
        Solution.__init__(self, source_file_name)
    def compile(self):
        return subprocess.call(['ocamlc', '-o', self.get_a_out_name(), self.source_file_name]) == 0
    def get_execute_command_line(self):
        return ['./' + self.get_a_out_name()]
