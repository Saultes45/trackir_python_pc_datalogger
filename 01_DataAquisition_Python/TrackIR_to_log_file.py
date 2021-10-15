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
#

# ---------------------- imports -----------------------------------------

# from previous code
from trackir import TrackIRDLL                    ## for getting the data from trackIR
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
aquisitionLoopTargetFrequency  = 300.0  # in [Hz], sampling at ~240hz, for the ~120hz signal
nbrLogFiles                    = 10
logFileNameDateFormat          = '%Y-%m-%d--%H-%M-%S'
timeStampDateFormat            = '%Y-%m-%d_%H-%M-%S'
dataFolderName                 = 'Data'

# Source: scroll down: https://docs.python.org/3/library/time.html#time.strftime
# %H :Hour (24-hour clock) as a decimal number [00,23].
# %I :Hour (12-hour clock) as a decimal number [01,12].


# data print format (cannot be implemented as is)

lineLogFormat   = '%(asctime)s.%(msecs)03d%(message)s'  # comma without space is not supported

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
    # Logging

    # create a reference number which is shared for all the data generated for this particular execution
    # this reference is just the date time
    testRef = time.strftime(logFileNameDateFormat)

    # Create a data folder in root/CWD
    if not (os.path.isdir(os.getcwd() + '/' + dataFolderName)):
        os.mkdir(os.getcwd() + '/' + dataFolderName)

    # In this data folder, create a subfolder for this execution
    if not (os.path.isdir(os.getcwd() + '/' + dataFolderName + '/' + testRef)):
        os.mkdir(os.getcwd() + '/' + dataFolderName + '/' + testRef)

    LOG_FILENAME = os.getcwd() + '/' + dataFolderName + '/' + testRef + '/' + testRef + '-Data.log'
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    # logFileHandler = logging.FileHandler(filename=LOG_FILENAME)
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
        log.info(" Started")
        log.info(" Local directory is: " + os.getcwd())
        log.info(" Version: {}".format(thisCodeVersion))
    except Exception as e:
        print("Error while logging header")
        print(e)

    app = tkinter.Tk()
    app.title("TrackIR Logging: " + testRef)
    app.update_idletasks()
    app.update()
    tkinter.Label(app, text="Currently saving values to a log file.  Close to stop").grid(column=0, row=0)

    try:
        trackrIr = TrackIRDLL(app.wm_frame())
    except Exception as e:
        # logprint("Crash!\n  (This usually means you need to restart the TrackIR GUI)\n")
        print("Crash!\n  (This usually means you need to restart the TrackIR GUI)\n")
        raise e

    # statistics variables initialisation
    previous_frame = -1
    num_logged_frames = 0
    num_missed_frames = 0
    start_time = time.time()

    ## Tells what happens when the stop button of the tkinter GUI is pressed
    def signal_handler(sig, frame):
        trackrIr.stop()
        print("Number of frames logged (num_logged_frames): {}".format(num_logged_frames))
        print("Number of missed frames (num_missed_frames): {}".format(num_missed_frames))
        end_time = time.time()
        print("Total time (computer clock): {} s".format(round(end_time - start_time)))
        print(
            "Overall Frame Rate (computer clock): {} Hz".format(round(num_logged_frames / (end_time - start_time))))
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    log.info(
        " Timestamp[ms], Frame Number, Roll[deg], Pitch[deg], Yaw[deg], X[m], Y[m], Z[m]")  # show the order of the data columns

    ## Aquisition loop
    while (True):

        trackIRData = trackrIr.NP_GetData()  # get the data from TrackIR
        if trackIRData.frame != previous_frame:  # check the data are fresh using the frame number variable, reported by TrackIR

            num_logged_frames += 1  # increment our own variable
            if previous_frame != -1:
                num_missed_frames += trackIRData.frame - previous_frame - 1  # TODO: this doesn't work well

            previous_frame = trackIRData.frame
            time_ms = round((time.time() - start_time) * 1000)  # conversion from [s] to [ms]
            try:
                # Source: "Method: Nested Replacement Fields"   https://realpython.com/python-formatted-output/
                # "The string modulo operator only allows <width> and <prec>"
                log.info(",{:07d},{:011d},{:{}},{:+.5f},{:+.5f},{:+.5f},{:+.5f},{:+.5f}".format(
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


if __name__ == "__main__":
    main()
