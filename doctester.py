#!/usr/bin/env python3
"""Runs doctests on snippets of code from books

   Copyright 2009, Vern Ceder, vceder@gmail.com
   
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import sys
import subprocess
import tempfile
import os
from tkinter import *

python_exe = sys.executable
ch_filename_template = "ch{0:0>2}_code.txt"
ch_header_template = "{0:0>2}.{1}\n\n"
template = """{0}\"\"\"\n{01}\n\"\"\"

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
        self.location_label = Label(self.top_frame, text="Header")
        self.location_label.grid(row=0, column=2)
        self.location = Entry(self.top_frame)
        self.location.grid(row=0, column=3)
        self.create_code_frame()
        self.create_test_frame()
        self.create_button_frame()
        
    def create_code_frame(self):
        self.code_frame = Frame(self)
        self.code_frame.grid(row=1, column=0, sticky="nsew")
        self.code_label = Label(self.code_frame, text="Shell code")
        self.code_label.grid(row=2, column=0, sticky="ew")
        self.doctest_vert_scroller = Scrollbar(self.code_frame, orient='vertical')
        self.doctest_vert_scroller.grid(row=3, column=1, sticky='nsew')
        self.doctest = Text(self.code_frame, yscrollcommand=self.doctest_vert_scroller.set, height=20)
        self.doctest.grid(row=3, column=0, sticky='nsew')
        self.doctest.bind_class("Text", "<Button-3><ButtonRelease-3>", self.show_menu)
        # if platform is not windows
        self.doctest.bind_class("Text","<Control-v>", self.paste)
        self.doctest.bind_class("Text","<Control-c>", self.copy)
        self.doctest.bind_class("Text","<Control-x>", self.cut)
        self.doctest_vert_scroller.config(command=self.doctest.yview)
        self.doctest_horz_scroller = Scrollbar(self.code_frame, orient='horizontal')
        self.doctest_horz_scroller.grid(row=4, column=0, sticky='ew')

        self.plain_code_label = Label(self.code_frame, text="Plain code")
        self.plain_code_label.grid(row=0, column=0, sticky="ew")
        self.plain_code_vert_scroller = Scrollbar(self.code_frame, orient='vertical')
        self.plain_code_vert_scroller.grid(row=1, column=1, sticky='ns')
        self.plain_code = Text(self.code_frame, yscrollcommand=self.plain_code_vert_scroller.set, height=15)
        self.plain_code.grid(row=1, column=0, sticky='nw')
        # if platform is not windows
        self.plain_code_vert_scroller.config(command=self.plain_code.yview)
        
    def create_test_frame(self):
        self.test_frame = Frame(self)
        self.test_frame.grid(row=1, column=1, sticky="nsew")

        self.results_label = Label(self.test_frame, text="Results")
        self.results_label.grid(row=0, column=0, sticky="ew")
        self.results_vert_scroller = Scrollbar(self.test_frame, orient='vertical')
        self.results_vert_scroller.grid(row=1, column=1, sticky='ns')
        self.results = Text(self.test_frame, yscrollcommand=self.results_vert_scroller.set, height=37)
        self.results.grid(row=1, column=0, sticky='nesw')
        self.results.config(state=DISABLED)
        self.results_vert_scroller.config(command=self.results.yview)
        self.results_horz_scroller = Scrollbar(self.test_frame, orient='horizontal')
        self.results_horz_scroller.grid(row=2, column=0, sticky='ew')

    def create_button_frame(self):
        self.button_frame = Frame(self)
        self.button_frame.grid(row=2, column=0, columnspan=4)
        self.test_button = Button(self.button_frame, text = "Test", command=self.test)
        self.test_button.grid(row=0, column = 0)
        self.full_button = Button(self.button_frame, text = "Full Test", command=self.full)
        self.full_button.grid(row=0, column = 1)
        self.clear_button = Button(self.button_frame, text = "Clear All", command=self.clear_all)
        self.clear_button.grid(row=0, column = 2)
        self.clear_button = Button(self.button_frame, text = "Clear Results", command=self.clear)
        self.clear_button.grid(row=0, column = 3)
        self.save_button = Button(self.button_frame, text = "Save", command=self.save)
        self.save_button.grid(row=0, column = 4)
        self.exit_button = Button(self.button_frame, text = "Exit", command=sys.exit)
        self.exit_button.grid(row=0, column = 5)

    def test(self, verbose=""):
        plaintext = self.plain_code.get(1.0, END)
        plaintext = plaintext.replace('"""', "\'\'\'")
        raw = "r"
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
        text = text.replace('"""', "\'\'\'")
        raw = "r"
        newlines = []
        for line in text.split("\n"):
            if not line.startswith(">>>"):
                pos =  line.find("#")
                # strip output lines of any trailing #'s (Manning code anno's)
                if pos > 0:
                    line = line[:pos].rstrip()
            if "\\" in line:
                raw = "r"
            newlines.append(line)
        text = "\n".join(newlines)
        text = plaintext + text

        # write to testfile, call with python_exe
        of_handle, testfile = tempfile.mkstemp(suffix=".py", text=True)
        outfile = os.fdopen(of_handle, "w")
        outfile.write(template.format(raw,text))
        outfile.close()

        output = subprocess.Popen([python_exe, testfile, verbose],
                                  stdout=subprocess.PIPE).communicate()[0]
        os.unlink(testfile)
        # capture output to results window...
        self.results.tag_config("out", foreground="red")
        self.results.config(state=NORMAL)
        self.results.insert(END, output, "out")
        self.results.config(state=DISABLED)

    def full(self):
        self.test(verbose="-v")

    def save(self):
        chap = self.chapter.get()
        savefile = open(ch_filename_template.format(chap), "a")
        outstring = ch_header_template.format(chap, self.location.get())
        plain_code_string = self.plain_code.get(1.0, END).strip()
        if plain_code_string:
            outstring += plain_code_string + "\n\n"
        doctest_string = self.doctest.get(1.0, END).strip()
        if doctest_string:
            outstring += doctest_string + "\n\n"
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

    def show_menu(self, e):
        w = e.widget
        w.focus()
        self.the_menu.entryconfigure("Cut", command=self.cut)
        self.the_menu.entryconfigure("Copy", command=self.copy)
        self.the_menu.entryconfigure("Paste", command=self.paste)
        self.the_menu.tk.call("tk_popup", self.the_menu, e.x_root, e.y_root)

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
