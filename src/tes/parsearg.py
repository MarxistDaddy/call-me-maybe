import argparse

class p():
    def __init__(self):
        self.name = None
        self.age = None
        self.msg = None


    def parse(self):
        ps = argparse.ArgumentParser(
            usage="py main.py <name> <age> <msg>"
        )

#        ps.print_help()
        
        ps.add_argument("name")
        ps.add_argument("age")
        ps.add_argument("msg")
        
        ps.parse_args()

x = p()
x.parse()
