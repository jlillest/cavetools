#!/usr/bin/env python
import sys
from enum import Enum

STATE = Enum('state', 'Start Team Survey')

def cap(string, length):
    return string if len(string) <= length else string[0:length]

def comment(filename, remark):
    filename.write(";" + remark.strip() + "\n")

def process_compass_file(compass_file):
    State = STATE.Start
    with open(compass_file, 'r') as f:
        first_line = f.readline().strip()
        project_file = open("".join(first_line.split()) + ".wpj", 'w')
        comment(project_file, "WALLS Project file")
        project_file.write(".BOOK\t" + first_line + "\n")
  
        for line in f.readlines():
            short_line = line.strip()
            if State is STATE.Start:
                if line.startswith("SURVEY NAME"):
                    file_name = line.split()[-1]
                    survey_file = open(cap(file_name, 8) + ".srv", 'w')
                    comment(survey_file, file_name)
                    project_file.write(".SURVEY\t" + file_name + "\n")
                    project_file.write(".NAME\t" + cap(file_name, 8) + "\n")
                    project_file.write(".STATUS\t24\n")
                elif line.startswith("SURVEY DATE"):
                    dv = line.split()[2:5]
                    #grab comment 
                    survey_file.write("#DATE\t%s-%s-%s\n" % (dv[0], dv[1], dv[2]))
                elif line.startswith("SURVEY TEAM"):
                    State = STATE.Team
                elif line.startswith("DECLINATION"):
                    pass
                elif short_line.startswith("FROM"):
                    survey_file.write("#UNITS feet ORDER=DAV\n")
                    State = STATE.Survey

            elif State is STATE.Team:
                comment(survey_file, line)
                State = STATE.Start

            elif State is STATE.Survey:
                #compass uses this character to split surveys
                if line.startswith('\x0c'):
                    survey_file.close()
                    State = STATE.Start
                elif len(line.split()) >= 9:
                    sl = line.split()
                    try:
                        float(sl[3])
                        float(sl[5])
                        survey_format = "%s\t%s\t%s\t%s\t%s\t<%s,%s,%s,%s>\n"
                        survey_file.write(survey_format % (sl[0], sl[1], sl[2], sl[3], sl[4], sl[5], sl[6], sl[7], sl[8]))
                    except ValueError:
                        comment(survey_file, line)
                else:
                    pass

    project_file.write(".ENDBOOK\n")    
    project_file.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("ERROR: Missing compass data filename")
        sys.exit("    " + sys.argv[0] + " <compass.DAT>")

    compass_file = sys.argv[1]
    process_compass_file(compass_file)
