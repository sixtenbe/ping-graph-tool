#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import traceback

def excepthook(etype, value, tb):
    message = '\nUncaught exception:\n'
    message += ''.join(traceback.format_exception(etype, value, tb))
    with open('error.log', 'a') as log:
        log.write(message)
sys.excepthook = excepthook

from numpy import nan
import numpy as np
from pipe import ping
from time import time, sleep
from threading import Thread, Event
import re
import wx
from wx.lib.agw.floatspin import FloatSpin as FS, EVT_FLOATSPIN

from wxplot import Graph

class MyForm(wx.Frame):


    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "ping graphing program",
                                   size=(750,600))
        sys.excepthook = self.excepthook
        #used to start stop the ping operation
        self.stoprequest = Event()
        #variables with ping data for graph
        self.ping_ms = []   #y-axis
        self.ping_date = [] #x-axis

        # Add a panel so it looks the correct on all platforms
        panel = wx.Panel(self, wx.ID_ANY)
        self.plot = Graph(panel)
        self.plot.set_label(xlabel='Time (s)', ylabel='ping [ms]')
        self.plot.set_formatter('plain', useOffset = False)

        ###stats###
        self.ping_avg = wx.StaticText(panel, wx.ID_ANY, 'Ping average: xxx±xx ms')
        self.packet_loss = wx.StaticText(panel, wx.ID_ANY, 'Packet loss: x %')
        
        self.ping_avg_latest = wx.StaticText(panel, wx.ID_ANY, 'Last 10 avg: xxx±xx ms')
        self.packet_loss_latest = wx.StaticText(panel, wx.ID_ANY, 'Last 10 loss: x %')
        
        
        ###settings###
        # start stop button
        self.start_stop = wx.Button(panel, wx.ID_ANY, "&Start")

        # ping parameters
        host_lbl = wx.StaticText(panel, wx.ID_ANY, 'Se&rver')
        self.host = wx.TextCtrl(panel, wx.ID_ANY,
                                value = 'ping.sunet.se', size = (200,-1))
        timeout_lbl = wx.StaticText(panel, wx.ID_ANY, '&Timeout')
        self.timeout = FS(panel, wx.ID_ANY, size = (60, -1), value = 200,
                            min_val = 100, max_val = 10000,
                            increment = 10, digits = 0)
        #field for setting limit line in graph
        limit_lbl = wx.StaticText(panel, wx.ID_ANY, 'Limi&t lvl')
        self.limit = FS(panel, wx.ID_ANY, size = (50, -1), value = 70,
                            min_val = 1, max_val = 1000,
                            increment = 1, digits = 0)
        #how many point should show on the graph
        history_lbl = wx.StaticText(panel, wx.ID_ANY, 'history (s)')
        self.history = FS(panel, wx.ID_ANY, size = (60, -1), value = 100,
                            min_val = 100, max_val = 10000,
                            increment = 10, digits = 0)

        #------ Bindings ------#
        self.start_stop.Bind(wx.EVT_BUTTON, self.onStart_Stop)
        self.Bind(wx.EVT_CLOSE, self.onClose)

        #------ Layout ------#
        vsizer = wx.BoxSizer(wx.VERTICAL) #main sizer
        hsizer_stats = wx.BoxSizer(wx.HORIZONTAL)
        hsizer_stats_latest = wx.BoxSizer(wx.HORIZONTAL)
        hsizer_settings = wx.BoxSizer(wx.HORIZONTAL)
        vsizer_host = wx.BoxSizer(wx.VERTICAL)
        vsizer_timeout = wx.BoxSizer(wx.VERTICAL)
        vsizer_limit = wx.BoxSizer(wx.VERTICAL)
        vsizer_history = wx.BoxSizer(wx.VERTICAL)

        #build text input sizers
        vsizer_host.Add(host_lbl, 0, wx.ALIGN_LEFT)
        vsizer_host.Add(self.host, 0, wx.ALIGN_LEFT)

        vsizer_timeout.Add(timeout_lbl, 0, wx.ALIGN_LEFT)
        vsizer_timeout.Add(self.timeout, 0, wx.ALIGN_LEFT)

        vsizer_limit.Add(limit_lbl, 0, wx.ALIGN_LEFT)
        vsizer_limit.Add(self.limit, 0, wx.ALIGN_LEFT)

        vsizer_history.Add(history_lbl, 0, wx.ALIGN_LEFT)
        vsizer_history.Add(self.history, 0, wx.ALIGN_LEFT)
        
        #sizer with status information
        hsizer_stats.Add(self.ping_avg, 0,
                            wx.RIGHT | wx.LEFT | wx.ALIGN_CENTER,
                            10)
        hsizer_stats.Add(self.packet_loss, 0,
                            wx.RIGHT | wx.LEFT | wx.ALIGN_CENTER,
                            10)
        #sizer with latest stats (last 10 pings)
        hsizer_stats_latest.Add(self.ping_avg_latest, 0,
                            wx.RIGHT | wx.LEFT | wx.ALIGN_CENTER,
                            10)
        hsizer_stats_latest.Add(self.packet_loss_latest, 0,
                            wx.RIGHT | wx.LEFT | wx.ALIGN_CENTER,
                            10)
        
        #sizer with controls for settings
        hsizer_settings.Add(self.start_stop, 0,
                            wx.RIGHT | wx.LEFT | wx.ALIGN_BOTTOM,
                            10)
        hsizer_settings.Add(vsizer_host, 0,
                            wx.RIGHT | wx.LEFT | wx.ALIGN_CENTER,
                            10)
        hsizer_settings.Add(vsizer_timeout, 0,
                            wx.RIGHT | wx.LEFT | wx.ALIGN_CENTER,
                            10)
        hsizer_settings.Add(vsizer_limit, 0,
                            wx.RIGHT | wx.LEFT | wx.ALIGN_CENTER,
                            10)
        hsizer_settings.Add(vsizer_history, 0,
                            wx.RIGHT | wx.LEFT | wx.ALIGN_CENTER,
                            10)

        #main layout
        vsizer.Add(self.plot, 1, wx.EXPAND)
        vsizer.Add(hsizer_stats, 0, wx.ALIGN_CENTER | wx.TOP, 5)
        vsizer.Add(hsizer_stats_latest, 0, wx.ALIGN_CENTER | wx.BOTTOM, 5)
        vsizer.Add(hsizer_settings, 0, wx.ALIGN_CENTER | wx.TOP, 0)

        #finalize
        panel.SetSizerAndFit(vsizer)
        #self.SetMinSize(vsizer.GetMinSize())
        self.GetBestSize()
        self.Show(True)
        self.stoprequest.set()


    ###-----Events bound to specific buttons-----###
    def onClose(self, event):
        """
        Should ensure that a proper exit is done
        """
        if not self.stoprequest.isSet():
            self.stop_ping()
            #sleep to let the thread have time to halt
            sleep(max(1, self.timeout.GetValue() // 1000))
        #death to everything
        self.Destroy()

    def onStart_Stop(self, event):
        """
        Starts or stops the pinging of the server
        """
        if self.stoprequest.isSet():
            self.start_ping()
        else:
            self.stop_ping()


    def excepthook(self, etype, value, tb):
        """
        exception hook to log error and display a message dialog.
        """
        message = '\nUncaught exception:\n'
        message += ''.join(traceback.format_exception(etype, value, tb))
        with open('error.log', 'a') as log:
            log.write(message)

        d = wx.MessageDialog(self, "{0}: {1}".format(etype.__name__, value),
                            "Unhandled exception", wx.OK | wx.ICON_ERROR)
        d.ShowModal()
        d.Destroy()


    def ping_it(self):
        """
        will perform the pinging and plot to the graph
        """
        #reset the ping data
        self.ping_ms = []   #y-axis
        self.ping_date = [] #x-axis
        #the data length to use when calling the fill_axis function
        hist_max = self.history.GetMax()
        
        with ping(self.host.GetValue(), self.timeout.GetValue()) as pinger:
            x_limit = [-100, 0]
            #intialize the first line
            y_limit = [self.limit.GetValue()]*2
            plot_lim = axis_limit(x_limit, self.limit.GetValue(), [0])
            #set initial limits
            self.plot.set_limits(plot_lim)
            line_limit = self.plot.redraw(x_limit, y_limit, color='r',
                                draw=False)[0]
            line_ping = self.plot.redraw(*([0,0],)*2, draw=False, color='b',
                                        hold=True, marker='x')[0]
            line_timeout = self.plot.redraw(*([0,0],)*2, draw=False, color='r',
                                        hold=True, marker='', linestyle='--')[0]
            self.plot.set_limits(plot_lim)

            while not self.stoprequest.isSet():
                ping_ms, ping_date = pinger.next()
                hist_len = int(self.history.GetValue())
                #trim lists using the maximum length
                self.ping_ms = fill_axis(self.ping_ms, ping_ms, hist_max)
                self.ping_date = fill_axis(self.ping_date, ping_date, hist_max)
                #create truncated lists for temp usage
                trunc_ping_ms =          self.ping_ms[-hist_len:]
                trunc_ping_date = self.ping_date[-hist_len:]
                
                #convert ping time to relative time from current time
                was_pinged = get_time_diff(trunc_ping_date, time())
               
                #genereate plot limits
                x_limit = [-hist_len, 0]
                plot_lim_new = axis_limit(x_limit, self.limit.GetValue(), trunc_ping_ms)

                #update the y_limit line
                y_limit = [self.limit.GetValue()]*2

                #efficient plotting
                line_limit.set_data(x_limit, y_limit)
                line_ping.set_data(was_pinged, trunc_ping_ms)
                line_timeout.set_data(*nan_line_creator(was_pinged, trunc_ping_ms))
                #only redo the plot limits and grid if needed
                if not plot_lim == plot_lim_new:
                    plot_lim = plot_lim_new
                    self.plot.set_limits(plot_lim)
                else:
                    self.plot.update_plot_only([line_limit, line_ping,
                                                line_timeout])
                #update status texts
                self.set_packet_loss_status(trunc_ping_ms)
                self.set_ping_avg_status(trunc_ping_ms)
                #explicit wait instead of implicit from the generator
                sleep(0.2)
            #cleanup remove the line objects
            self.plot.clear_lines()
            #self.plot.sub_plots().axes.lines.remove(line)


    def set_ping_avg_status(self, ping_ms):
        """
        Updates the average ping text
        """
        average = np.nanmean(ping_ms)
        std = np.nanstd(ping_ms)
        lbl = 'Ping average: {0:.0f}±{1:.0f} ms'.format(average, std)
        self.ping_avg.SetLabel(lbl)
        #get stats for the last 10 ping packets
        ping_latest = ping_ms[-10:]
        average = np.nanmean(ping_latest)
        std = np.nanstd(ping_latest)
        lbl = 'Last 10 avg: {0:.0f}±{1:.0f} ms'.format(average, std)
        self.ping_avg_latest.SetLabel(lbl)
        
    def set_packet_loss_status(self, ping_ms):
        """
        Updates the packet loss rate text
        """
        loss_rate = list(np.isnan(ping_ms)).count(True)
        loss_rate /= float(len(ping_ms))
        lbl = 'Packet loss: {0:.0f} %'.format(loss_rate * 100)
        self.packet_loss.SetLabel(lbl)
        #get stats for the last 10 ping packets
        ping_latest = ping_ms[-10:]
        loss_rate = list(np.isnan(ping_latest)).count(True)
        loss_rate /= float(len(ping_latest))
        lbl = 'Packet loss: {0:.0f} %'.format(loss_rate * 100)
        self.packet_loss_latest.SetLabel(lbl)
        
    
    def start_ping(self):
        self.stoprequest.clear()
        thread = Thread(target=self.ping_it)
        thread.setDaemon(True)
        thread.start()
        self.start_stop.SetLabel("&Stop")
    def stop_ping(self):
        self.stoprequest.set()
        self.start_stop.SetLabel("&Start")



def axis_limit(x_limit, min_y, y_data):
    """
    Will return the axis limits for a plot to fit the all the y_data within view.
    Shows the highest y-value + 5

    keyword arguments:
    x_limit -- a list with 2 integers defining the limits for the x_axis
    min_y -- the minimum value of the y-axis
    y_data -- points plotted on the y axis
    """
    output = x_limit + [0, np.nanmax([min_y] + y_data) + 5]

    return output


def get_time_diff(time_list, ref_time):
    """
    Calaculates the time difference between all dates in a list and a
    reference date

    Keyword arguments:
    time_list -- a list with dates to calculate the time difference for
    ref_time -- The reference date to subtract from the time_list
    """

    return [element - ref_time for element in time_list]


def fill_axis(axis, value, length=100):
    """
    Will append the value to the list untill it reaches the length 100
    When at full length the oldest value will be popped.

    Keyword arguments:
    axis -- a list to which the value should be added
    value -- value to add to the list
    length -- (optional) how long should the list be (default: 100)
    """
    #force it to integer
    length = int(length)
    #pop the oldest value if length has been reached
    if len(axis) == length:
        axis.pop(0)
    elif len(axis) > length:
        for i in range(len(axis) - length):
            axis.pop(0)
    #add the new value
    axis.append(value)

    return axis


def list_nan(elements):
    """
    Finds all the nan elements in a list and return their indices

    keyword arguments:
    elements -- a list that is to be checked for nan elements
    """
    output = []
    for i, element in enumerate(np.isnan(elements)):
        if element:
            #add the indice of the current nan element
            output.append(i)
    return output


def nan_insert(data):
    """
    inserts a nan element every two elements

    keyword arguments:
    data -- a list of values
    """
    #if len(data) > 2:
    for index in reversed(xrange(len(data) // 2)):
        if index != 0:
            data.insert(index * 2, nan)

    return data

def nan_line_creator(x_axis, y_axis):
    """
    Returns an x- and y-axis that can draw lines to span over nan elements
    in the given y-axis

    keyword arguments:
    x_axis -- a list that contain the x-axis values
    y_axis -- a list that contain the y-axis values
    """
    nan_elements = list_nan(y_axis)

    x_out = []
    y_out = []

    #if length of axis vars =1 just exit right here
    if len(y_axis) <= 1:
        return (x_out, y_out)
    #trimming out nan elements that precede each other
    nan_elements = nan_trim(nan_elements)


    #produces one pair of x and y values per iteration
    for indice in nan_elements:
        prev_indice = indice - 1
        next_indice = indice + 1
        #find first preceeding resp. succeding non-nan element
        while prev_indice > 0 and np.isnan(y_axis[prev_indice]):
            prev_indice -= 1
        while next_indice > len(y_axis) and np.isnan(y_axis[next_indice]):
            next_indice += 1

        #check if the element is the first element of the axes
        if indice == 0:
            #indice is first element
            x_out.append(x_axis[indice])
            y_out.append(y_axis[next_indice])
        else:
            #standard case
            x_out.append(x_axis[prev_indice])
            #check if the prev_indice value is a nan value
            if np.isnan(y_axis[prev_indice]):
                #bug when ping starts with 2 timeouts
                try: y_out.append(y_axis[next_indice])
                except IndexError: x_out.pop(-1) #trim lists to equal length
            else:
                y_out.append(y_axis[prev_indice])


        #add the second value for the x and y axes
        #check if indice is at end of y_axis
        if indice == len(y_axis)-1:
            #use last value in x-axis
            x_out.append(x_axis[indice])
            #since last value in axis reuse previous non-nan y_value
            y_out.append(y_axis[prev_indice])
        else:
            x_out.append(x_axis[next_indice])
            y_out.append(y_axis[next_indice])

    #add nan values if more than one line is to be drawn
    x_out = nan_insert(x_out)
    y_out = nan_insert(y_out)
    #return data
    return (x_out, y_out)


def nan_trim(data):
    """
    Removes elements whose difference to the next element == 1

    keyword arguments:
    data -- a list of values
    """
    data_diff = np.diff(data)

    for i, diff in reversed(list(enumerate(data_diff))):
        if diff == 1:
            data.pop(i)

    return data




def installThreadExcepthook():
    """
    Workaround for sys.excepthook thread bug
    From
http://spyced.blogspot.com/2007/06/workaround-for-sysexcepthook-bug.html

(https://sourceforge.net/tracker/?func=detail&atid=105470&aid=1230540&
group_id=5470).
    Call once from __main__ before creating any threads.
    If using psyco, call psyco.cannotcompile(threading.Thread.run)
    since this replaces a new-style class method.
    """
    init_old = Thread.__init__
    def init(self, *args, **kwargs):
        init_old(self, *args, **kwargs)
        run_old = self.run
        def run_with_except_hook(*args, **kw):
            try:
                run_old(*args, **kw)
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                sys.excepthook(*sys.exc_info())
        self.run = run_with_except_hook
    Thread.__init__ = init


# Run the program
if __name__ == "__main__":
    installThreadExcepthook()

    app = wx.PySimpleApp()
    frame = MyForm()
    app.MainLoop()


