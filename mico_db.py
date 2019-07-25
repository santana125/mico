import sqlite3
import os

class DataBase():

    def __init__(self):
        if not os.path.isdir('/var/lib/mico'):
            os.mkdir('/var/lib/mico')
        try:
            self.conn = sqlite3.connect('/var/lib/mico/mazon_packages.db')
            self.cursor = self.conn.cursor()
        except sqlite3.OperationalError:
            print("Impossível ler arquivo.")
            exit()

    def create_table(self):
        try:
            self.cursor.execute("""
                DROP TABLE packages;
                                """)
        except Exception as e:
            print(e)
        try:
            self.cursor.execute("""
                CREATE TABLE packages(
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                version TEXT NOT NULL,
                directory text NOT NULL,
                link TEXT NOT NULL);
                """)
            self.conn.commit()
        except sqlite3.Error as e:
            pass
        except Exception as ee:
            print(ee)

    def post_pkg(self, name, version, repo, link):
        self.cursor.execute("""
                INSERT INTO packages(name, version, directory, link)
                VALUES(?,?,?,?);
            """, (name, version, repo, link))
        self.conn.commit()

    def search_pkg(self, name):
        self.cursor.execute("""
                                SELECT * FROM packages
                                WHERE name LIKE ?
                            """, ('%'+name+'%',))
        response = self.cursor.fetchall()
        pkgs = []
        for item in response:
            pkg = {'name': item[1], 'version': item[2],
                   'directory': item[3], 'link': item[4]
                   }
            pkgs.append(pkg)
        return pkgs


    def close_conn(self):
        self.conn.close()
