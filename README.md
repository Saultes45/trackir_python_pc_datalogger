# trackir_python_pc_datalogger
A python-based datalogger for the 6DOF pose data generated by TrackIR sofware


%% Ressources
% github: https://github.com/johnflux/python_trackir
% track IR:
% --> To be used with the python code from github:
% E:\Documents\08_Github Local Repo\python_trackir\TrackIR_to_log_file.py
%     [OLD](in pycharm to have automatic log saving)

% python uses the SDK: from trackir import TrackIRDLL, (TrackIR_6DOF_Data,
% logprint)
% but you need to have the trackIR app running in // as well !!!!
% the python code is heavily based on John Tapsell's work 

% [OLD] To save to a log, 2 options
%--> Do that in python
%--> Follow the instructions from Pycharm to save console logs
%automatically: https://stackoverflow.com/questions/46410577/intellij-idea-how-persist-console-output-to-file-programmatically


%% Matlab Post-process parser/plotter TODO
% --> Detect frame dropouts with variance
% --> Save as quaternion
% --> Filter using LERP/SLERP as quaternion ^


% -->  Pop up selection of the file to import ^
% -->  File name check, get runID
% -->  Detect all the good (LOG) files in a folder ^
