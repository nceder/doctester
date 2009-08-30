#!/usr/bin/env python3
"""Runs doctests on snippets of code from books

   Vern Ceder, 06-13-2009
"""

import sys, subprocess
from tkinter import *
template = """%s\"\"\"\n%s\n\"\"\"

import doctest

doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)
"""

class TesterGUI(PanedWindow):
    def __init__(self, master=None):

        PanedWindow.__init__(self, master)
        self.master.title("Python tester")
        self.make_menu(self)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.pack(fill=BOTH, expand=1)
        self.top_frame = Frame(self)
        self.top_frame.grid(row=0, column=0, sticky="nsew")
        self.chapter_label = Label(self.top_frame, text="Chapter")
        self.chapter_label.grid(row=0, column=0)
        self.chapter = Entry(self.top_frame)
        self.chapter.grid(row=0, column=1)
        self.location_label = Label(self.top_frame, text="location")
        self.location_label.grid(row=0, column=2)
        self.location = Entry(self.top_frame)
        self.location.grid(row=0, column=3)
        self.create_code_frame()
        self.create_test_frame()
        self.create_button_frame()
        
    def create_code_frame(self):
        self.code_frame = Frame(self)
        self.code_frame.pack(fill=BOTH, expand=1)
        self.code_frame.grid(row=1, column=0, sticky="nsew")
        self.doctest_vert_scroller = Scrollbar(self.code_frame, orient='vertical')
        self.doctest_vert_scroller.grid(row=2, column=1, sticky='nsew')
        self.doctest = Text(self.code_frame, yscrollcommand=self.doctest_vert_scroller.set, height=20)
        self.doctest.grid(row=2, column=0, sticky='nsew')
        self.doctest.bind_class("Text", "<Button-3><ButtonRelease-3>", self.show_menu)
        # if platform is not windows
        self.doctest.bind_class("Text","<Control-v>", self.paste)
        self.doctest.bind_class("Text","<Control-c>", self.copy)
        self.doctest.bind_class("Text","<Control-x>", self.cut)
        self.doctest_vert_scroller.config(command=self.doctest.yview)
        self.doctest_horz_scroller = Scrollbar(self.code_frame, orient='horizontal')
        self.doctest_horz_scroller.grid(row=3, column=0, sticky='ew')

        self.plain_code_vert_scroller = Scrollbar(self.code_frame, orient='vertical')
        self.plain_code_vert_scroller.grid(row=0, column=1, sticky='ns')
        self.plain_code = Text(self.code_frame, yscrollcommand=self.plain_code_vert_scroller.set, height=15)
        self.plain_code.grid(row=0, column=0, sticky='nw')
        # if platform is not windows
        self.plain_code_vert_scroller.config(command=self.plain_code.yview)
        
    def create_test_frame(self):
        self.test_frame = Frame(self)
        self.test_frame.grid(row=1, column=1, sticky="nsew")

        self.results_vert_scroller = Scrollbar(self.test_frame, orient='vertical')
        self.results_vert_scroller.grid(row=0, column=1, sticky='nesw')
        self.results = Text(self.test_frame, yscrollcommand=self.results_vert_scroller.set, height=35)
        self.results.grid(row=0, column=0, sticky='nesw')
        self.results.config(state=DISABLED)
        self.results_vert_scroller.config(command=self.results.yview)
        self.results_horz_scroller = Scrollbar(self.test_frame, orient='horizontal')
        self.results_horz_scroller.grid(row=5, column=0, sticky='nesw')

    def create_button_frame(self):
        self.button_frame = Frame(self)
        self.button_frame.grid(row=2, column=0, columnspan=4)
        self.test_button = Button(self.button_frame, text = "test", command=self.test)
        self.test_button.grid(row=2, column = 0)
        self.full_button = Button(self.button_frame, text = "full", command=self.full)
        self.full_button.grid(row=2, column = 1)
        self.clear_button = Button(self.button_frame, text = "clear all", command=self.clear_all)
        self.clear_button.grid(row=2, column = 2)
        self.clear_button = Button(self.button_frame, text = "clear results", command=self.clear)
        self.clear_button.grid(row=2, column = 3)
        self.save_button = Button(self.button_frame, text = "save", command=self.save)
        self.save_button.grid(row=2, column = 4)
        self.exit_button = Button(self.button_frame, text = "exit", command=sys.exit)
        self.exit_button.grid(row=2, column = 5)

    def test(self, verbose=""):
        plaintext = self.plain_code.get(1.0, END)
        raw = ""
        newlines = []
        if plaintext.strip():
            for line in plaintext.strip().split("\n"):
                if line.startswith(" "):
                    line = "... " + line
                else:
                    line = ">>> " + line
                newlines.append(line)
            if newlines[-1].startswith("..."):
                newlines.append("... ")
            plaintext = "\n".join(newlines)+ "\n"

        text = self.doctest.get(1.0, END)
        raw = ""
        newlines = []
        for line in text.split("\n"):
            if not line.startswith(">>>"):
                pos =  line.find("#")
                if pos > 0:
                    line = line[:pos].rstrip()
            if "\\" in line:
                raw = "r"
            newlines.append(line)
        text = "\n".join(newlines)
        text = plaintext + text

        outfile = open("test.py", "w")
        outfile.write(template % (raw,text))
        outfile.close()

        output = subprocess.Popen(["python3", "test.py", verbose],
                                  stdout=subprocess.PIPE).communicate()[0]

    #    print(output)
        # strip of any trailing #'s 
        # call with python3
        # capture output to new other window...
        self.results.tag_config("out", foreground="red")
        self.results.config(state=NORMAL)
        self.results.insert(END, output, "out")
        self.results.config(state=DISABLED)

    def full(self):
        self.test(verbose="-v")

    def save(self):
        chap = self.chapter.get()
        savefile = open("ch%s_code.txt" % chap, "a")
        outstring = "\n%s.%s\n\n" % (chap, self.location.get())
        outstring += (self.plain_code.get(1.0, END).rstrip()+"\n\n").lstrip()
        outstring += self.doctest.get(1.0, END)
        savefile.write(outstring)
        savefile.close()

    def clear_all(self):
        self.plain_code.delete(1.0, END)
        self.doctest.delete(1.0, END)
        self.results.config(state=NORMAL)
        self.results.delete(1.0, END)
        self.results.config(state=DISABLED)

    def clear(self):
        self.results.config(state=NORMAL)
        self.results.delete(1.0, END)
        self.results.config(state=DISABLED)

    def make_menu(self, w):
        self.the_menu = Menu(w, tearoff=0)
        self.the_menu.add_command(label="Cut")
        self.the_menu.add_command(label="Copy")
        self.the_menu.add_command(label="Paste")

    def show_menu(e):
        w = e.widget
        w.focus()
        self.the_menu.entryconfigure("Cut", command=cut)
        self.the_menu.entryconfigure("Copy", command=copy)
        self.the_menu.entryconfigure("Paste", command=paste)
        self.the_menu.tk.call("tk_popup", the_menu, e.x_root, e.y_root)

    def paste(self, e=None):
        if e:
            w=e.widget
        else:
            w = self.top_frame.focus_get()
        w.event_generate("<<Paste>>")
    def copy(self,e=None):
        if e:
            w=e.widget
        else:
            w = self.top_frame.focus_get()
        w.event_generate("<<Copy>>")
    def cut(self,e=None):
        if e:
            w=e.widget
        else:
            w = self.top_frame.focus_get()
        w.event_generate("<<Cut>>")



app = TesterGUI()
app.mainloop()
