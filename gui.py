#!/usr/bin/python

import sys
import wx
import wx.lib.agw.ultimatelistctrl as ULC
from wx.lib.mixins.listctrl import ColumnSorterMixin
import sqlite3
from DBbuilder import out_dir, db_name, images_folder
import os
from textwrap import wrap


class MyFrame(wx.Frame, ColumnSorterMixin):

    def connect_to_db(self):
        self.conn = sqlite3.connect(os.path.join(out_dir, db_name))
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def __init__(self, parent):

        wx.Frame.__init__(self, parent, -1, "MDB")
        self.connect_to_db()

        # Build the list
        self.itemDataMap = {}

        self.lst = ULC.UltimateListCtrl(self, wx.ID_ANY,
                agwStyle=wx.LC_REPORT | wx.LC_VRULES | wx.LC_HRULES |
                wx.LC_SINGLE_SEL | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick, self.lst)
        ColumnSorterMixin.__init__(self, 5)

        self.lst.InsertColumn(0, "Title")
        self.lst.InsertColumn(1, "Rating")
        self.lst.InsertColumn(2, "Year")
        self.lst.InsertColumn(3, "Genre")
        self.lst.InsertColumn(4, "Runtime")
        self.lst.InsertColumn(5, "Details")

        self.lst.SetColumnWidth(5, -3)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.lst, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.Layout()

    def GetListCtrl(self):
        return self.lst

    def OnColClick(self, event):
        event.Skip()
        self.Refresh()

    def add_row(self, filename):
        # get info from db, build info panel, add to list, update
        # itemdatamap
        data = self.get_from_db(filename)

        index = self.lst.InsertStringItem(sys.maxint, data['title'])

        self.lst.SetItemData(index, index)
        self.itemDataMap[index] = (data['title'], data['rating'], data['year'],
                data['genre'], data['runtime'])

        self.lst.SetStringItem(index, 1, unicode(data["rating"]))
        self.lst.SetStringItem(index, 2, unicode(data["year"]))
        self.lst.SetStringItem(index, 3, unicode(data["genre"]))
        self.lst.SetStringItem(index, 4, unicode(data["runtime"]))
        self.lst.SetItemWindow(index, 5, self.build_info_panel(data), expand=True)

    def ascii_str(self, item):
        return unicode(item)#.encode('ascii', 'ignore')

    def get_from_db(self, filename):
        res = self.cursor.execute('SELECT * FROM movies WHERE filename=?',
                (filename,)).fetchall()
        return res[0]

    def build_info_panel(self, data):
        panel_3 = wx.Panel(self.lst, -1)
        bitmap_1 = wx.StaticBitmap(panel_3, -1, wx.Bitmap(os.path.join(
            out_dir, images_folder, data['filename'] + '.jpg'),
            wx.BITMAP_TYPE_ANY))
        label_1 = wx.StaticText(panel_3, -1, self.generate_label_text(data))
        font = wx.Font(11, wx.MODERN, wx.NORMAL, wx.NORMAL)
        label_1.SetFont(font)

        self.label_1 = label_1

        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(bitmap_1, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        sizer_3.Add(label_1, 0, 0, 0)
        sizer_2.Add(sizer_3, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        panel_3.SetSizer(sizer_2)

        return panel_3

    def generate_label_text(self, data):
        heading_width = 10
        total_width = 70
        sep = ':  '

        data2 = [('Title', unicode(data['title'])),
                ('Filename', unicode(data['filename'])),
                ('Director', unicode(data['director'])),
                ('Actors', unicode(data['actors'])),
                ('Plot', unicode(data['plot'])),
                ]

        res = ""
        for item in data2:
            item_1_lines = wrap(item[1], total_width-heading_width-len(sep))
            line1 = u"{0:<{w1}}{2}{1:<{w2}}\n".format(item[0], item_1_lines[0],
                    sep, w1=heading_width, w2=total_width-heading_width-3)
            res += line1

            for line in item_1_lines[1:]:
                out = (' '*(heading_width+len(sep))) + line + '\n'
                res += out

        print ''
        print res
        return res