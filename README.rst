.. _digitail_rain: https://en.wikipedia.org/wiki/Digital_rain
.. _curses: https://docs.python.org/3/howto/curses.html

######################
  Matrix Digital Rain
######################

****************
  Introduction
****************

From `Wikipedia <https://en.wikipedia.org/wiki/Digital_rain>`_:

    Matrix digital rain, or Matrix code, is the computer code featured in the Ghost in the Shell series and the Matrix series. The falling green code is a way of representing the activity of the simulated reality environment of the Matrix on screen by kinetic typography.

The classic green body with a white head.

.. image:: ./media/matrix_run_green.png

The script has options to control the color of head, body, and background.
Here it is blue body and red head.

.. image:: ./media/matrix_run_blue.png

This project demonstrates use of the `curses <https://docs.python.org/3/howto/curses.html>`_ module.
I was inpired by 
`Making the Matrix Screensaver in C on a PDP-11/83 <https://youtu.be/-foAV_zU2as?si=1GcCSSo1SPAo0Llh>`_
and had long wanted to learn how to write an application using `curses <https://docs.python.org/3/howto/curses.html>`_.

****************
  About Curses
****************

* Colors are numbered, and `start_color()` initializes 8 basic colors when it activates color mode.
* Color pair 0 is hard-wired to white on black, and cannot be changed.
* Coordinates are always passed in the order y,x, and the top-left corner of a window is coordinate (0,0)
* Writing to lower right corner will move cursor to new and non-existing(!) line thus raising exception

*******************
  Getting Started
*******************

Dependencies
============

Installing
==========

Executing
=========

********
  Help
********

********
  TODO
********

* Code breaks after resize when following writing to lower right corner.  
* What to do with Windows
* Version due to type hints

