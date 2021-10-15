#!/usr/bin/env python3

# -------------------Metadata----------------------
# Creator: Nathanael ESNAULT

# nathanael.esnault@gmail.com
# or
# nesn277@aucklanduni.ac.nz

# Creation date 2021-10-10
# Version	0.1

# Version Control: https://github.com/Saultes45/

# -------------------VERY important notes----------------------
# Clear console
# os.system('printf "\033c"')


# TODO list:
# compare xlsxwriter speed vs logging
# import parameters from INI file
# Compile to .exe

# ---------------------- imports -----------------------------------------

# from previous code
from trackir import TrackIRDLL                    ## for getting the data from trackIR (you need the file called )
#, TrackIR_6DOF_Data, logprint
import time
import signal                                     ## for quitting the GUI
import sys                                        ## for signal_handler
import tkinter                                    ## for the GUI

# added by myself
import logging                                    ## for logging both data and debug log
from logging.handlers import RotatingFileHandler  ## for limiting the file size
import os                                         ## for folder creation and get current working directory

##------------------Warning------------------------
# warnings.filterwarnings("ignore")
# InitialisationIsDone = False


##------------------ Tunable parameters ------------------------
thisCodeVersion = 1.0

maxLogFileMegaBytesSize        = 1  # in [MB]
aquisitionLoopTargetFrequency  = 300.0  # in [Hz], checking for new values at ~300hz, for the ~120hz report rate from TrackIR
nbrLogFiles                    = 10 # We use circular logs with replacement
logFileNameDateFormat          = '%Y-%m-%d--%H-%M-%S'
timeStampDateFormat            = '%Y-%m-%d_%H-%M-%S'
dataFolderName                 = 'Data'

# Source: scroll down: https://docs.python.org/3/library/time.html#time.strftime
# %H :Hour (24-hour clock) as a decimal number [00,23].
# %I :Hour (12-hour clock) as a decimal number [01,12].


# data print format (cannot be implemented as is)

lineLogFormat   = '%(asctime)s.%(msecs)03d%(message)s'  # Comma without space between timestamp field and message field is not supported

# time_msLogFormat   = '.010d'  # integer, no sign, 0 padding for a total field width of 10
# frameLogFormat     = '.010d'  # integer, no sign, 0 padding for a total field width of 10
# rollLogFormat      = '+.5f'  # float, always display sign, NO 0 padding, 5 digits after decimal place
# pitchLogFormat     = '+.5f'  # float, always display sign, NO 0 padding, 5 digits after decimal place
# yawLogFormat       = '+.5f'  # float, always display sign, NO 0 padding, 5 digits after decimal place
# xLogFormat         = '+.5f'  # float, always display sign, NO 0 padding, 5 digits after decimal place
# yLogFormat         = '+.5f'  # float, always display sign, NO 0 padding, 5 digits after decimal place
# zLogFormat         = '+.5f'  # float, always display sign, NO 0 padding, 5 digits after decimal place


##------------------ Main ------------------------
def main():

    # Create a reference number which is shared for all the data generated for this particular execution
    # This reference is just the date time
    testRef = time.strftime(logFileNameDateFormat)

    # Create a data folder in root/CWD
    if not (os.path.isdir(os.getcwd() + '/' + dataFolderName)):
        os.mkdir(os.getcwd() + '/' + dataFolderName)

    # In this data folder, create a subfolder for this execution
    if not (os.path.isdir(os.getcwd() + '/' + dataFolderName + '/' + testRef)):
        os.mkdir(os.getcwd() + '/' + dataFolderName + '/' + testRef)

    # Generate a log file name
    LOG_FILENAME = os.getcwd() + '/' + dataFolderName + '/' + testRef + '/' + testRef + '-Data.log'

    # Prepare the logger
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    # noinspection PyTypeChecker
    logFileHandler = RotatingFileHandler(filename=LOG_FILENAME,
                                         mode='a',
                                         backupCount=nbrLogFiles - 1,
                                         maxBytes=maxLogFileMegaBytesSize * 1024 * 1024,
                                         encoding=None,
                                         delay=0)
    logFileHandler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        fmt=lineLogFormat,
        datefmt=timeStampDateFormat
    )

    logFileHandler.setFormatter(formatter)
    log.addHandler(logFileHandler)

    # Write some stuff at the top of the log file (header), before the data
    try:
        log.info(" Started")  # Notice the space before the message
        log.info(" Local directory is: " + os.getcwd())  # Notice the space before the message
        log.info(" Version: {}".format(thisCodeVersion))  # Notice the space before the message
    except Exception as e:
        print("Error while logging header")
        print(e)

    # Create the simplest GUI with Tkinter
    app = tkinter.Tk()
    app.title("TrackIR Logging: " + testRef)
    app.update_idletasks()
    app.update()
    tkinter.Label(app, text="Currently saving values to a log file.  Close to stop").grid(column=0, row=0)

    try:
        trackrIr = TrackIRDLL(app.wm_frame())
    except Exception as e:
        print("--------- /!\ CRASH /!\ ---------")
        print("This usually means you need to (re-)start the TrackIR GUI")
        print("Note that this only works on Windows, since it requires the TrackIR.dll.")
        print("The TrackIR software must be running, and use the 1:1 mapping if you want real values")
        raise e

    # Statistics variables initialisation (to display in the console when user close the GUI)
    previous_frame = -1
    num_logged_frames = 0
    num_missed_frames = 0
    start_time = time.time()

    # Tell what happens when the stop button of the tkinter GUI is pressed
    def signal_handler(sig, frame):
        trackrIr.stop()
        print("Number of frames logged (num_logged_frames): {}".format(num_logged_frames))
        print("Number of missed frames (num_missed_frames): {}".format(num_missed_frames))
        end_time = time.time()
        print("Total time (computer clock): {} s".format(round(end_time - start_time)))
        print(
            "Overall Frame Rate (computer clock): {} Hz".format(round(num_logged_frames / (end_time - start_time))))
        sys.exit(0)

    # Link the function we just created "signal_handler" to the signal generated by the GUI when closing
    signal.signal(signal.SIGINT, signal_handler)

    # show the order of the data columns
    log.info(
        " Timestamp[ms], Frame Number[N/A], Roll[deg], Pitch[deg], Yaw[deg], X[mm], Y[mm], Z[mm]")  # Notice the space at the start

    # Acquisition loop
    while True:

        # Get the data from TrackIR
        trackIRData = trackrIr.NP_GetData()

        # Check the data are fresh using the frame number variable, reported by TrackIR
        if trackIRData.frame != previous_frame:

            num_logged_frames += 1  # increment our own variable
            if previous_frame != -1:
                num_missed_frames += trackIRData.frame - previous_frame - 1  # TODO: this doesn't work well

            previous_frame = trackIRData.frame
            time_ms = round((time.time() - start_time) * 1000)  # conversion from [s] to [ms]
            try:
                # Source: "Method: Nested Replacement Fields"   https://realpython.com/python-formatted-output/
                # "The string modulo operator only allows <width> and <prec>"
                log.info(",{:07d},{:011d},{:+.5f},{:+.5f},{:+.5f},{:+.5f},{:+.5f},{:+.5f}".format(
                    time_ms,
                    trackIRData.frame,
                    trackIRData.roll,
                    trackIRData.pitch,
                    trackIRData.yaw,
                    trackIRData.x,
                    trackIRData.y,
                    trackIRData.z)
                )

            except Exception as e:
                print("Error while logging data")
                print(e)

        try:
            app.update_idletasks()
            app.update()
        except Exception:
            signal_handler(0, 0)

        time.sleep(1 / aquisitionLoopTargetFrequency)  # wait time before cheching new data available


# This is where we execute the main
if __name__ == "__main__":
    main()
