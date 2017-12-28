#!/usr/bin/python
import sys,wx

if len(sys.argv)>1:
	task=" ".join(sys.argv[1:])
else:
	task="Task"
task=task.title()
str=task+" is Done."


app=wx.PySimpleApp()
frame=wx.Frame(None,-1,'')
frame.SetTitle('Notice me , please! ')
frame.Center()
text=wx.StaticText(frame,-1,str,pos=(10,10))
font=wx.Font(18,wx.DECORATIVE,wx.BOLD,wx.NORMAL)
text.SetFont(font)
frame.Show()
app.MainLoop()

