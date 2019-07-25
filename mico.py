#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import sqlite3
from db import DataBase
import sys
import getopt
import os
import hashlib

CBOLD = '\33[1m'
CGREEN = '\33[32m'
CYELLOW = '\33[33m'
CBLUE = '\33[34m'
CPURPLE = '\33[35m'
ENDC = '\033[0m'



REPOS_NAMES = ['dev',
               'base',
               'extra',
               'games',
               'lib',
               'net',
               'sec',
               'theme',
               'x',
               'xapp']
PKGS_URL = 'http://www.mazonos.com/packages/'
class Mico():
    def __init__(self):
        pass

    def get_pkgs(self, repo):
        repo_url = PKGS_URL + repo + '/'
        req = requests.get(repo_url)
        content = req.content
        soup = BeautifulSoup(content, 'html.parser')
        links = soup('a')
        black_list = ('.desc', '.sha256', '.sig')
        links = links[5:]
        pkgs = []
        for link in links:
            if not any(x in link.get('href') for x in black_list):
                pkgs.append(link.get('href'))
        for link in pkgs:
            pkg = link
            pkg_url = pkg
            pkg = pkg.replace('.mz', '')
            pkg = pkg.split('-', 1)
            parsed_pkg = {'name': pkg[0], 'version': pkg[1]}
            self.DB.post_pkg(parsed_pkg['name'],
                        parsed_pkg['version'],
                        repo,
                        repo_url + pkg_url)

    def check_db(self):
        if os.path.isfile('/var/lib/mico/mazon_packages.db'):
            self.DB = DataBase()
        else:
            print("Data base was not created, please run mico -u.")
            sys.exit(4)

    def update_db(self):
        self.DB.create_table()
        for repo in REPOS_NAMES:
            print("Atualizando repositorio: " + repo)
            self.get_pkgs(repo)


    def search_pkg(self, name):
        packages = self.DB.search_pkg(name)
        for pkg in packages:
            if pkg['directory'] == "base":
                pkg['directory'] = CBOLD + CYELLOW + "base" + ENDC
            elif pkg['directory'] == "dev":
                pkg['directory'] = CBOLD + CYELLOW + "dev" + ENDC
            elif pkg['directory'] == "extra":
                pkg['directory'] = CBOLD + CGREEN + "extra" + ENDC
            elif pkg['directory'] == "games":
                pkg['directory'] = CBOLD + CGREEN + "games" + ENDC
            elif pkg['directory'] == "theme":
                pkg['directory'] = CBOLD + CGREEN + "theme" + ENDC
            elif pkg['directory'] == "lib":
                pkg['directory'] = CBOLD + CBLUE + "lib" + ENDC
            elif pkg['directory'] == "net":
                pkg['directory'] = CBOLD + CBLUE + "net" + ENDC
            elif pkg['directory'] == "sec":
                pkg['directory'] = CBOLD + CBLUE + "sec" + ENDC
            elif pkg['directory'] == "x":
                pkg['directory'] = CBOLD + CPURPLE + "x" + ENDC
            elif pkg['directory'] == "xapp":
                pkg['directory'] = CBOLD + CPURPLE + "xapp" + ENDC
            print(f"{pkg['directory']}/{CBOLD}{pkg['name']}{ENDC}" +
                  f" {CBLUE}{pkg['version']}{ENDC}")

    def get_pkg(self, name):
        packages = self.DB.search_pkg(name)
        if len(packages) > 1 or len(packages) <= 0:
            print("Pacote não encontrado.")
            return None
        else:
            package = packages[0]
            return f"{package['directory']}/{package['name']}-{package['version']}.mz"


    def install(self, name):
        path = "/var/lib/mico/pkgs_cache/"
        if not os.path.isdir(path):
            os.mkdir(path)
        package = self.get_pkg(name)
        if package:
            answer = input("Do you want to install " + name + "? [Y/n] ")
            if answer != 'y' and answer != 'Y' and answer != '':
                print("Can't continue installation.")
                sys.exit(0)
            pkg_name = package.split('/')[1]
            if os.path.isfile(path+pkg_name):
                os.remove(path+pkg_name)
            print("#-------- Downloading --------#")
            os.system('wget -q --show-progress ' + PKGS_URL +
                      package + ' -P ' + path)
            origin_hash = requests.get(PKGS_URL + package +
                                       '.sha256').content.decode('UTF-8')
            origin_hash = origin_hash.split(' ')[0]
            with open(path+pkg_name, 'rb') as file:
                contents = file.read()
                file_hash = hashlib.sha256(contents).hexdigest()
            if file_hash == origin_hash:
                print("Hash [OK]")
                print("Installing...")
                os.system('banana -i ' + path+pkg_name)
                os.remove(path+pkg_name)
            else:
                print("Hash [ERROR] \n Exiting...")
                sys.exit(3)

    def show_help(self):
        print('mico -i <pkg_name> to install a package.' +
            '\nmico -s <pkg_name> to search.' +
            '\nmico -u to upgrade packages DataBase.' +
            '\nmico -r to remove a package.')

    def run(self, argv):
        pkg_name = ''
        try:
            opts, args = getopt.getopt(argv, "hui:s:",
                                       ["help", "update", "download=", "search="])
        except getopt.GetoptError:
            self.show_help()
            sys.exit(2)
        for opt, arg in opts:
            if opt == '-h':
                self.show_help()
                sys.exit(0)
            elif opt in ("-s", "--search"):
                self.check_db()
                pkg_name = arg
                self.search_pkg(pkg_name)
            elif opt in ("-i", "--install"):
                self.check_db()
                if os.getuid() == 0:
                    pkg_name = arg
                    self.install(pkg_name)
                else:
                    print('You need super user privileges to perform this.')
            elif opt in ("-u", "--update"):
                if os.getuid() == 0:
                    self.check_db()
                    self.update_db()
                else:
                    print('You need super user privileges to perform this.')
        try:
            self.DB.close_conn()
        except:
            pass

if __name__ == "__main__":
    mico = Mico()
    mico.run(sys.argv[1:])
