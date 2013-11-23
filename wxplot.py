import wx
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure
from matplotlib.ticker import ScalarFormatter, LogFormatter
from os import path, remove


class _plot_data():
    """
    class to store plots appending or removing data as needed
    
    attributes:
    axes -- contains a matplotlib axes object
    lines -- all drawn matplotlib lines, not yet implemented.
        Maybe a wrapper to catch the line object or the input variables?
    selection -- line marking selection of plot area
    title -- title of sub-plot
    formatter -- a tuple containing the x- and y-axis formatter
    y2_axis -- the secondary y axis, if created, else None
    y2_label -- label of secondary axis
    """
    
    def __init__(self, parent, axes, title):
        """
        Keyword arguments:
        parent -- a _plot_list object, which will contains some globals
        axes -- a matplotlib axes component
        title -- title of the sub-plot
        """
        self.parent = parent
        self.axes = axes
        self.title = title
        self.formatter = parent.default_formatter
        self.lines = []
        self.selection = None
        
        # no reason to have two copies of the same code
        # active the formatting information
        self.reload()
        
        
        # check if a secondary y-axis should be created
        if parent.secondary_y_axis:
            self.create_y2_axis(parent.y2_label)
        else:
            self.y2_axis = None
            
    
    def create_y2_axis(self, y2_label):
        """
        Creates a secondary y-axis. Alternatively changes the label of said 
        axis.
        
        Keyword arguments:
        y2_label -- label of secondary y-axis
        """
        self.y2_label = y2_label
        if self.y2_axis == None:
            self.y2_axis = self.axes.twinx()
            self.y2_axis.set_ylabel(parent.y2_label)

#            # define a wrapper for the plot function
#            old_plot = self.y2_axis.plot
#            def plot_reload(self, *args, **kw):
#                old_plot(*args, **kw)
#                self.y2_axis.set_ylabel(self.y2_label)
#            self.y2_axis.plot = plot_reload
        
        else:
            self.y2_axis.set_ylabel(parent.y2_label)
    
                
    def reload(self):
        """
        Will reload things. Can be called when the axes has been changed to
        formatt the new axes according to th old formatting.
        
        Keyword arguments:
        """
        # recreate all the settings, as a new axes object has been set
        self.axes.grid(self.parent.grid)
        self.axes.set_title(self.title)
        self.axes.set_xlabel(self.parent.x_label)
        self.axes.set_ylabel(self.parent.y_label)
        self.axes.xaxis.set_major_formatter(self.formatter[0])
        self.axes.yaxis.set_major_formatter(self.formatter[1])
        if self.parent.secondary_y_axis:
            self.create_y2_axis(self.y2_label)
########This doesn't work########
#            #Redo lines
#            self.axes.cla()
#        for line in self.lines:
#            line.set_axes(self.axes)
#            self.axes.add_line(line)
        
        
    def remove_line(self, line):
        """
        Removes the specified line from the internal list and the axes object
        
        keyword arguments:
        line -- A matplotlib line
        """
        try:
            self.lines.remove(line)
        except ValueError:
            pass #silence
        self.axes.lines.remove(line)
        
    def set_formatter(self, formatter, axes = 'all'):
        """
        Sets the fomatter for the sub-plot
        
        Keyword arguments:
        formatter -- A matplotlib axis formatter
        axes -- Which axes should the formatter be used for, valid values are:
            'all', 'x', 'y' (default: 'all')
        """
        if not formatter == None:
            if axes == 'x':
                self.formatter = (formatter, self.formatter[1])
            elif axes == 'y':
                self.formatter = (self.formatter[0], formatter)
            else:
                self.formatter = (formatter,)*2
        
        # update formatter
        self.axes.xaxis.set_major_formatter(self.formatter[0])
        self.axes.yaxis.set_major_formatter(self.formatter[1])
        

class _plot_list():
    """
    A class for handiling lists of sub-plots and the associated data
    
    The canvas is never redrawn from this code.
    
    Attributes (should not be accesed directly):
    default_formatter
    figure
    grid -- (default: True)
    has_selection -- (default: False)
    secondary_y_axis -- (default: False)
    x_label -- (default: '')
    y_label -- (default: '')
    y2_label -- (default: '')
    """
    grid = True
    has_selection = False
    secondary_y_axis = False
    y2_label = ''
    
    def __init__(self, figure, x_label='', y_label=''):
        """
        Initializes a _plot_list, which contains plot_data.
        
        Keyword arguments:
        figure -- The matplotlib figure to which the plots are added.
        x_label -- The x-axis label to use for all plots (default: '')
        y_label -- The y-axis label to use for all plots (default: '')
        """
        self.x_label = x_label
        self.y_label = y_label
        self.figure = figure
        
        self.sub_plots = []
        # set default formatter for the time being
        frmt = ScalarFormatter(useOffset = True)   
        frmt.set_powerlimits((-3,3))
        frmt.set_scientific(True)
        self.default_formatter = (frmt, frmt)
    
    
    def __call__(self, index):
        """
        Returns the plot_data object at index
        
        Keyword arguments:
        index -- index of plot_data object to return
        """
        try:
            return self.sub_plots[index]
        except IndexError:
            raise IndexError, "No sub-plot exists at index:{0!s}".format(index)
    
    def append(self, sub_plot, title):
        """
        Appends another sub-plot to the _plot_list
        
        keyword arguments:
        sub_plot -- sub-plot to be appended to list, an axes object
        title -- title of sub-plot to append
        """
        self.sub_plots.append(_plot_data(self, sub_plot, title))
            
    def clear_axes(self):
        """
        Clears all axes from figure
        
        Currently also clears all lines and the selection as the reloading
        of lines doesn't seem to work
        """
        # Remove lines and selection as they can't be reloaded properly
        for plot in self.sub_plots:
            self.figure.delaxes(plot.axes)
            plot.axes=None
            plot.y2_axis = None
            plot.selection = None
            plot.lines = []
        self.figure.clear()
        # Set selction of view area to false as it was removed
        self.has_selection = False
        
    
    def remove(self):
        """
        Removes the last sub-plot
        """
        self.figure.delaxes(self.sub_plots[-1].axes)
        del self.sub_plots[-1]
    
    
    def set_axes(self, axes, index):
        """
        Sets the axes of the sub-plot at index
        
        Keyword arguments:
        axes -- The new axes for the sub-plot
        index -- Index of sub-plot
        """
        try:
            self.sub_plots[index].axes = axes
        except IndexError:
            raise IndexError, "No sub-plot exists at index:{0!s}".format(index)
        
        # Call the reload to load the proper settings to the new axes object
        self.sub_plots[index].reload()
            
    
    def set_default_formatter(self, formatter, axes='all'):
        ###TODO###
        ###Add possibilty of specifying a formatter without sending a object
        ###Although it might be better to change the Graph Class to enable
        ###setting the default formatter without sending it to all plots
        """
        Sets the default fomatter for new sub-plots
        
        Keyword arguments:
        formatter -- A matplotlib axis formatter
        axes -- Which axes should the formatter be used for, valid values are:
            'all', 'x', 'y' (default: 'all')
        """
        if axes == 'x':
            self.default_formatter = (formatter, self.default_formatter[1])
        elif axes == 'y':
            self.default_formatter = (self.default_formatter[0], formatter)
        else:
            self.default_formatter = (formatter,)*2
    
    
    def set_label(self, x_label, y_label, index):
        """
        Sets the x- and y-axis label of the sub-plot at the specified index.
        
        Keyword arguments:
        x_label -- The x-axis label to use for the specified sub-plot
        y_label -- The y-axis label to use for the specified sub-plot
        index -- Index of sub-plot
        """
        # Store the latest setting of labels as the default labels
        self.x_label = x_label
        self.y_label = y_label
        try:
            self.sub_plots[index].axes.set_xlabel(x_label)
            self.sub_plots[index].axes.set_ylabel(y_label)
        except IndexError:
            raise IndexError, "No sub-plot exists at index:{0!s}".format(index)
        
    def show_grid(self, show):
        self.grid = show
        
        #Set grid variable
        for sub_plot in self.sub_plots:
            sub_plot.axes.grid(show)
        
    
class Graph(wx.BoxSizer):
    """
    This holds a curve plot with associated toolbar
    keyword arguments:
    parent -- reference to the panel or context the plot should be created in.
    orientation -- (optional) wx.BoxSizer style. This also sets the deafult
        direction to expand when adding sub-plots (default: wx.VERTICAL)
    title -- (optional) sets the title of the plot window (default: '').
    dpi -- (optional) sets dots per inch of plot window.
    params -- (optional) set matplotlib rcParams, should be a dictionary.
    (default: sets font size of: ticks, legend, axes label, font)
    **kwargs -- any keyword argument to matplotlib.Figure
    """
    def __init__(self, parent,
                orientation= wx.VERTICAL,
                title='',
                dpi=None,
                params = None,
                **kwargs):
        
        super(Graph, self).__init__(orientation)
        #initialize some font settings for matplotlib
        if params == None:
            params = {'axes.labelsize': 16,
              'font.size': 14,
              'legend.fontsize': 14,
              'xtick.labelsize': 12,
              'ytick.labelsize': 12}
        matplotlib.rcParams.update(params)
        
        self.figure = Figure(dpi=dpi, figsize=(2,2), **kwargs)
        self.canvas = FigureCanvas(parent, wx.NewId(), self.figure)
        self.sub_plots = _plot_list(self.figure)
        self.sub_plots.append(self.figure.add_subplot(111), title)
        self.toolbar = NavigationToolbar2Wx(self.canvas)
        
        ###Create some extra controls for the toolbar###
        self.cb_grid = wx.CheckBox(self.toolbar, wx.NewId(), 'Show Grid')
        btn_mark = wx.Button(self.toolbar, wx.NewId(), 'Mark selection')
        #btn_rem = wx.Button(parent, wx.NewId(), 'Remove_graph')
        
        ####add extra controls to toolbar####
        self.toolbar.AddControl(self.cb_grid)
        self.toolbar.AddControl(btn_mark)
        ####create and set toolbar sizer####
        toolbar_sizer = wx.BoxSizer(wx.HORIZONTAL)
        toolbar_sizer.Add(self.toolbar, 0, wx.ALIGN_LEFT)
        toolbar_sizer.Add(self.cb_grid, 0, wx.LEFT | wx.ALIGN_CENTER,30)
        toolbar_sizer.Add(btn_mark, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 20)
        self.toolbar.SetSizer(toolbar_sizer)
        #needed to update the layout
        self.toolbar.Layout()

        
        #######Main layout#######
        v_sizer = wx.BoxSizer(wx.VERTICAL)
        v_sizer.Add(self.canvas, 1, wx.EXPAND)
        v_sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
        #Add to self
        self.Add(v_sizer, 1, wx.EXPAND)
        
        ###Set title and other things###
        self.orientation = orientation
        #layout of plots (height, width, count)
        self.layout = (1,1,1)
        self.cb_grid.SetValue(True)
        self.sub_plots.show_grid(True)
        
        #connect the buttons to event handlers
        self.cb_grid.Connect(-1, -1,
                            wx.wxEVT_COMMAND_CHECKBOX_CLICKED, 
                            self._on_cb_grid)
        btn_mark.Connect(-1, -1, wx.wxEVT_COMMAND_BUTTON_CLICKED, self._on_mark)
        #btn_rem.Connect(-1, -1, wx.wxEVT_COMMAND_BUTTON_CLICKED, self.on_rem)
        
    
    ############Event handlers############
    def _on_cb_grid(self, evt):
        """
        Toggles if grid should be shown on sub-plots
        """
        self.sub_plots.show_grid(self.cb_grid.IsChecked())
        #redraw plots
        self.canvas.draw()
        
    def _on_mark(self, evt):
        """
        Draws or removes a selection outline on current sub-plot selection
        """
        #TODO#
        if self.sub_plots.has_selection:
            #delete markers
            for sub_plot in self.sub_plots.sub_plots:
                for line in sub_plot.selection:
                    sub_plot.axes.lines.remove(line)
            self.canvas.draw()
        else:
            for i, sub_plot in enumerate(self.sub_plots.sub_plots):
                x1, x2, y1, y2 = sub_plot.axes.axis()
                x = [x1, x2, x2, x1, x1]
                y = [y1, y1, y2, y2, y1]
                sub_plot.selection = self.redraw(x,y, hold = True,
                                        limits = (x1,x2,y1,y2),
                                        index = i,
                                        color = 'k', linewidth = 2.0)
        self.sub_plots.has_selection = not self.sub_plots.has_selection
    
    ############Worker functions############
    def add_secondary_y_axis(self, label = '', index = None):
        """
        Creates a secondary y_axis on the specified sub-plots
        
        keyword arguments:
        label -- (optional) axis label of the second y-axis (default: '')
        index -- (optional) a integer or list of integers with the index of 
            sub-plots for which a secondary y-axis should be created. When 
            'None' the formatter is set for all sub-plots (default: None)
        """
        
        if type(index) == list:
            for i in index:
                self.sub_plots(i).create_y2_axis(label)
        elif type(index) == int:
            self.sub_plots(index).create_y2_axis(label)
        else:
            #do all
            count = self.layout[-1]
            for sub_plot in self.sub_plots.sub_plots:
                sub_plot.create_y2_axis(label)
        
    
    def add_subplot(self, title='', orientation=None):
        """
        Adds an additional subplot. If more than one row exists and it will
        not be filled, than the plots on the last row will be expanded to
        fill all horizontal space. All plots will be recreated
        
        keyword arguments:
        title -- (optional) title text of new subplot (default: '')
        orientation -- (optional) direction to add subplot, valid data is:
            wx.VERTICAL or wx.HORIZONTAL (default: Graph.orientation)
        
        return -- index of created plot
        """
        
        orientation = self.orientation if orientation == None else orientation
        count = self.layout[-1] + 1
        size = self.layout[0] * self.layout[1]
        #check if there is room for another subplot
        if size >= count:
            self.layout = self.layout[:2] + (count, )
        else:
            #expand layout
            if orientation == wx.VERTICAL:
                self.layout = (self.layout[0] + 1, self.layout[1], count)
            else:
                self.layout = (self.layout[0], self.layout[1] + 1, count)
            
        #Clear away old axes
        self.sub_plots.clear_axes()
        #recreate axes and add new one
        size = self.layout[0] * self.layout[1]
        for i in range(1,count+1):
            if count < size and i > self.layout[1] * (self.layout[0]-1):
                #expand graphs on last row
                exp_layout = (self.layout[0], self.layout[1] - (size-count))
                exp_i = exp_layout[0] * exp_layout[1] - (count - i)
                
                axes = self.figure.add_subplot(*exp_layout + (exp_i,))
                #check if to rebind axes or append new object
                if i == count:
                    self.sub_plots.append(axes, title)
                else:
                    self.sub_plots.set_axes(axes, i-1)
            else:
                axes = self.figure.add_subplot(*self.layout[:2] + (i, ))
                #check if to rebind axes or append new object
                if i == count:
                    self.sub_plots.append(axes, title)
                else:
                    self.sub_plots.set_axes(axes, i-1)
        
        self.canvas.draw()
        #return sub-plot index
        return count - 1
                
        
    def cleanse_fontcache(self):
        """
        Shouldn't be used. Can fix bug when using frozen programs under windows.
        Better to modify the setup script so that font files are left out of the
        matplotlib data files.
        """
        file_path = path.join(path.expanduser('~'), \
                    '.matplotlib', \
                    'fontList.cache')
        if path.exists(file_path):
            remove(file_path)
    
    
    def clear_lines(self, index = 0):
        """
        Removes all lines from the selected sub-plot
        
        keyword arguments:
        index -- (optional) index of subplot, which should be cleared from all
            lines (default: 0)
        """
        self.sub_plots(index).axes.cla()
        self.sub_plots(index).lines = []
        
    def get_lines(self, index = 0):
        """
        Retrieves all the lines of the specified sub-plot
        
        keyword arguments:
        index -- (optional) index of subplot from, which the lines should be
            retrieved from (default: 0)
        """
        return self.sub_plots(index).axes.get_lines()
        
        
    def redraw(self, x, y,
            index = 0,
            hold=False,
            xmin = None, ymin = None,
            limits=None,
            limit_selector = None,
            alpha = 1.0,
            draw = True,
            **kwarg):
        """
        Updates plot with new vectors
        keyword arguments:
        x -- the x-axis values
        y -- the y-axis values
        index -- (optional) index of subplot to plot the vector in (default: 0)
        hold -- (optional) should old vectors be kept (default: False)
        xmin -- (optional) set minimum value of x-axis (default: None)
        ymin -- (optional) set minimum value of y-axis (default: None)
        limits -- (optional) list to set the limits of x and y-axis. overrides
            the xmin and ymin arguments (default: None)
        limit_selector -- (optional) a fucntion which given the arguments:
            *(x1, x2, y1, y2) will return a list with the axis limits
            overrides the xmin, ymin and the limits argument (default: None)
            e.g. sel = lambda x1, x2, y1, y2: [x1, x2, min(y1, 0), y2]
        alpha -- (optional) sets the alpha of the line (default: 1.0)
        draw -- (optional) should the canvas be updated to show the new lines
        
        **kwarg -- all extra keyword arguments are sent to the plot function
        """
        #set plot to update
        try:
            plot = self.sub_plots(index)
        except IndexError:
            raise(IndexError,
                "The sub-plot of index:{0:d} doesn't exist".format(index))
            
        plot.axes.hold(hold)
        lines = plot.axes.plot(x,y, alpha = alpha, **kwarg)
        
        
        #Create a legend if label was given
        if not lines[0].get_label()[0] == "_":
            plot.axes.legend() #label must be sent through kwarg
        
        #if not ymin == None:
        x1, x2, y1, y2 = plot.axes.axis()
        ymin = y1 if ymin == None else ymin
        xmin = x1 if xmin == None else xmin
        plot.axes.axis([xmin, x2, ymin, y2])
        if not limits == None:
            plot.axes.axis(limits)
        if not limit_selector == None:
            plot.axes.axis(limit_selector(x1, x2, y1, y2))
        
        #plot it
        #plot.axes.grid(self.sub_plots.grid)
        plot.reload()
        if draw:
            self.canvas.draw()
        #store lines in a list
        #return line object
        #plot.lines.extend(lines)
        return lines
        
        
    def redraw_secondary_y(self, x, y, index = 0, **kwarg):
        """
        Update secondary y-axis with a new vector
        keyword arguments:
        x -- the x-axis values
        y -- the y-axis values
        index -- (optional) index of subplot to plot the vector in (default: 0)
        style -- (optional) line style (default: 'r.')
        **kwarg -- all extra keyword arguments are sent to the plot function
        """
        sub_plot = self.sub_plots(index)
        lines = sub_plot.y2_axis.plot(x, y, style, **kwarg)
        #show it
        self.canvas.draw()
        return lines
    
    def remove_lines(self, lines, index = 0):
        """
        Re
        
        keyword arguments:
        lines -- A list of matplotlib lines as given by the redraw function
        index -- (optional) index of subplot from, which the lines should be
            retrieved from (default: 0)
        """
        for line in lines:
            self.sub_plots(index).remove_line(line)
        self.canvas.draw()
        
    def remove_subplot(self):
        """
        Removes the last sub-plot.
        Note that plots in the last row aren't expanded to fill the entire row.
        """
        count = self.layout[-1] - 1
        if count < 0:
            raise ValueError, "There is no sub-plot to remove"
        
        self.layout = (self.layout[0], self.layout[1], count)
        
        if count > 0:
            layout_change = True
            #check if layout of plots can be decreased
            if self.layout[0] > 1 and self.layout[1] > 1:
                if self.layout[0] < self.layout[1]:
                    lrg = 1
                    sml = 0
                else:
                    lrg = 0
                    sml = 1
                #check if a decrease is possible on the major axis
                size = (self.layout[lrg] - 1) * (self.layout[sml])
                if size >= count:
                    if lrg == 0:
                        self.layout = (self.layout[0] - 1, self.layout[1], count)
                    else:
                        self.layout = (self.layout[0], self.layout[1] - 1, count)
                else:
                    #check the minor axis
                    size = (self.layout[lrg]) * (self.layout[sml] - 1)
                    if size >= count:
                        if sml == 0:
                            self.layout = (self.layout[0] - 1, self.layout[1], count)
                        else:
                            self.layout = (self.layout[0], self.layout[1] - 1, count)
                    else:
                        layout_change = False
            else:
                if self.layout[0] > self.layout[1]:
                    self.layout = (self.layout[0] - 1, self.layout[1], count)
                else:
                    self.layout = (self.layout[0], self.layout[1] - 1, count)
        else:
            layout_change = False
        
        #remove the last sub-plot
        self.sub_plots.remove()
        if layout_change:
            #clear figure and recreate plots
            self.sub_plots.clear_axes()
            
            for i in range(1,count+1):
                plot_index = i - 1
                self.sub_plots.set_axes(self.figure.add_subplot(*self.layout[:2] + (i, )), plot_index)
       
        #redraw screen
        self.canvas.draw()
    
    
    def set_formatter(self, frmt = 'sci', axes = 'all', useOffset = True,
            limits = (-3, 3), index=None):
        """
        Sets the formatter of the axes. Default is to set scientific notation
        for all axes of all subplots.
        
        keyword arguments:
        frmt -- Sets the type of formatter used, valid values are:
            'sci', 'log', 'plain' (default: 'sci')
        axes -- which axes should the formatter be used for, valid values are:
            'all', 'x', 'y' (default: 'all')
        useOffset -- Should offset be used to make the tickers more meaningful 
            (default: True)
        limits -- Limits for scientific notation as a tuple (default: (-3, 3))
        index -- a integer or list of integers with the index of sub-plots for
            which the formatter should set. When 'None' the formatter is set
            for all sub-plots (default: None)
        """
        
        frmt = frmt.lower()
        axes = axes.lower()
        
        if frmt == 'log':
            formatter = LogFormatter()
        else:
            sci = frmt == 'sci'
            formatter = ScalarFormatter(useOffset = useOffset)
            formatter.set_powerlimits(limits)
            formatter.set_scientific(sci)
            
        # format axes
        if type(index) == list:
            for i in index:
                self.sub_plots(i).set_formatter(formatter, axes)
        elif type(index) == int:
            self.sub_plots(index).set_formatter(formatter, axes)
        else:
            # do all
            for sub_plot in self.sub_plots.sub_plots:
                sub_plot.set_formatter(formatter, axes)
            #set default formatter
            self.sub_plots.set_default_formatter(formatter, axes)
        
        # redraw screen
        self.canvas.draw()
        
        
    def set_label(self, xlabel='', ylabel='', index = None):
        """
        Set labels of the specified plot axes
        
        keyword arguments:
        xlabel -- (optional) sets the label of the x-axis (default: '')
        ylabel -- (optional) sets the label of the y-axis (default: '')
        index -- (optional) a integer or list of integers with the index of 
            sub-plots for which a the labels should be set. When 'None' the
            labels is set for all sub-plots (default: None)
        """
        
        if type(index) == list:
            for i in index:
                self.sub_plots.set_label(xlabel, ylabel, i)
        elif type(index) == int:
            self.sub_plots.set_label(xlabel, ylabel, index)
        else:
            # do all
            count = self.layout[-1]
            for i in range(count):
                self.sub_plots.set_label(xlabel, ylabel, i)
        # Redraw screen
        self.canvas.draw()
        
        
    def set_limits(self, limits, index = 0):
        """
        Sets the axis limits of the specified sub-plot
        
        keyword arguments:
        limits -- A list to set the limits of x and y-axis: [x1, x2, y1, y2]
        index -- (optional) index of subplot to set axis limits (default: 0)
        """
        self.sub_plots(index).axes.axis(limits)
        self.canvas.draw()
        
        
    def set_title(self, titles = '', index = 0):
        """
        Set titles of the sub-plots
        
        keyword arguments:
        titles -- should be a list of title strings or a single
            string, in which case an index should be supplied (default: '')
        index -- (optional) Is only needed when titles is a single string
            specifies for which sub-plot to set the title
        """
        if type(titles) == list:
            for i, title in enumerate(titles):
                self.sub_plots(i).set_title(title)
        else:
            self.sub_plots(index).set_title(titles)
        
        self.canvas.draw()
        
        
    def update(self):
        """
        Will send a draw command to the canvas uppdating the graphs
        """
        self.canvas.draw()
        self.canvas.flush_events()
        
    def update_plot_only(self, lines, index=0):
        """
        Will redraw the background and plot lines only
        
        keyword arguments:
        lines -- a list of line objects for the plot
        index -- (optional) index of subplot to set axis limits (default: 0)
        """
        try:
            plot = self.sub_plots(index)
        except IndexError:
            raise(IndexError,
                "The sub-plot of index:{0:d} doesn't exist".format(index))
        ax = plot.axes
        #draw the background
        ax.draw_artist(ax.patch)
        #draw the lines
        for line in lines:
            ax.draw_artist(line)
        #draw the x grid
        for line in ax.get_xgridlines():
            ax.draw_artist(line)
        #draw the y grid
        for line in ax.get_ygridlines():
            ax.draw_artist(line)
        #redraw display selectively
        self.canvas.blit(ax.bbox)
        