#!/usr/bin/python
# -*- coding: UTF-8 -*-
import numpy as np
from numpy import nan
import unittest
import pipe
import ping_gui
from time import time, sleep

class TestPing(unittest.TestCase):
    def test_output(self):
        host = 'ping.sunet.se'
        timeout = 200
        with pipe.ping(host, timeout) as pinger:
            ms, date = pinger.next()

        #check that the date is about correct
        self.assertAlmostEqual(date, time(), 0,
                                msg="invalid date:{}".format(date))
        #check that the time is expressed in either int or nan
        self.assertTrue(isinstance(ms, int) or np.isnan(ms))



class TestMain(unittest.TestCase):
    def test_axis_limit(self):
        """
        Tests the axis limit function
        """
        arg1 = [-100, 0]
        arg2 = 70
        arg3 = [nan, 30, 10, 90]
        arg4 = [nan, 30, 10, 50]
        result1 = [-100, 0, 0, 95]
        result2 = [-100, 0, 0, 75]
        output1 = ping_gui.axis_limit(arg1, arg2, arg3)
        output2 = ping_gui.axis_limit(arg1, arg2, arg4)

        self.assertListEqual(output1, result1)
        self.assertListEqual(output2, result2)


    def test_fill_axis(self):
        """
        Tests the fill axis function
        extending, appending and truncating lists
        """
        f = ping_gui.fill_axis
        data = range(99)
        result = range(100)
        output = f(data, 99)

        self.assertListEqual(output, result, msg='problem with appending')
        #check that default length is set to 100
        self.assertEqual(len(f(range(100), 5)), 100, msg='def length != 100')
        #check that first element is removed when maximum length is reached
        data = range(50)
        result = range(1, 51)
        self.assertListEqual(f(data, 50, 50), result, msg='list poping problem')
        #check that it can truncate list
        data = range(50)
        output = f(data, 50, 25)
        result = range(25,51)
        self.assertListEqual(output, result)


    def test_list_nan(self):
        """
        Tests the list_nan function
        finding all the nan values in a list
        """
        data = [3, nan, 1, 2, nan, 78, nan]
        result = [1, 4, 6]
        output = ping_gui.list_nan(data)
        #check that the output returns the indices of all the nan elements
        self.assertIsInstance(output, list, msg='Must return a list')
        self.assertEqual(output, result, 'faulty indices')


    def test_time_diff(self):
        """
        Tests the time diff function.
        Subtracts a value from a list of values
        """
        data = [1.0, 2.0, 3.0]
        result = [0.0, 1.0, 2.0]
        diff = ping_gui.get_time_diff(data, 1.0)
        #check that the value 1.0 has been subtracted from each element
        self.assertListEqual(diff, result)


    def test_nan_insert(self):
        """
        Test nan_insert function
        Should insert a nan value every 2 elements in a list
        """
        data = range(10)
        result = [0, 1, nan, 2, 3, nan, 4,5, nan, 6,7, nan, 8,9]
        output = ping_gui.nan_insert(data)

        self.assertListEqual(output, result)


    def test_nan_line_creator(self):
        """
        test nan_line_creator
        """
        x_data = range(5)
        y_data = [1, nan, 3, 1, 2]
        x_res = [0, 2]
        y_res = [1, 3]

        #short name for the function under test
        f = ping_gui.nan_line_creator
        #first simple test
        x_out, y_out = f(x_data, y_data)

        self.assertListEqual(x_out, x_res)
        self.assertListEqual(y_out, y_res)

        #a nan element in the as the first and last element
        x_data = range(5)
        y_data = [nan, 4, 3, 1, nan]
        x_res = [0, 1, nan, 3, 4]
        y_res = [4, 4, nan, 1, 1]

        x_out, y_out = f(x_data, y_data)
        self.assertListEqual(x_out, x_res)
        self.assertListEqual(y_out, y_res)

        #test handling of multiple consecutive nan elements
        x_data = range(8)
        y_data = [3, nan, nan, nan, 2, nan, nan, 5]
        x_res = [0, 4, nan, 4, 7]
        y_res = [3, 2, nan, 2, 5]

        x_out, y_out = f(x_data, y_data)
        self.assertListEqual(x_out, x_res)
        self.assertListEqual(y_out, y_res)


        #test handling of multiple consecutive nan elements at start
        x_data = range(10)
        y_data = [nan, nan, nan, nan, 2, nan, nan, 5, nan, nan]
        x_res = [0, 4, nan, 4, 7, nan, 7, 9]
        y_res = [2, 2, nan, 2, 5, nan, 5, 5]

        x_out, y_out = f(x_data, y_data)
        self.assertListEqual(x_out, x_res)
        self.assertListEqual(y_out, y_res)

        #test that a single nan element causes no error
        x_data = [0]
        y_data = [nan]
        x_out, y_out = f(x_data, y_data)

    def test_nan_trim(self):
        """
        Tests nan_trim
        Removes adjacent nan values
        """
        data = [1, 2, 3, 5, 6, 9]
        result = [3, 6, 9]

        output = ping_gui.nan_trim(data)
        self.assertListEqual(output, result)




if __name__ == '__main__' or True:
    #unittest.main()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPing)
    suite2 = unittest.TestLoader().loadTestsFromTestCase(TestMain)
    unittest.TextTestRunner(verbosity=2).run(suite2)

    #sleep(3)






