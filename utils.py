from pandas import read_csv
import os
import json
import discord
from datetime import datetime

#Holds a role and channel associated with a student
class Student:
    def __init__(self, _role, _channel):
        self.role = _role
        self.channel = _channel

class ScheduleDay:
    def __init__(self, open, close):
        self.open = open
        self.close = close
#Reads a raw csv file and returns it
def ReadFromFile(file_name):
    return read_csv(file_name)

#Reads a csv file and parses it into an array of strings for times
def ReadTimesFromFile(file_name):
    arr = []
    for i in ReadFromFile(file_name):
        arr.append(str(i)[0:5])
    return arr

#Writes to a file all elements in the string array, comma separated
def WriteToFile(file_name, *strings):
    with open(file_name, 'w') as file:
        for line in strings:
            file.write(line)
            file.write(',')
    
    with open(file_name, 'rb+') as file:
        file.seek(-1, os.SEEK_END)
        file.truncate()

#Converts a time "00:00" from EST time to UTC time
def ESTtoUTC(input_time, input_day) :
    adj_time = int(input_time[:2]) + 4
    output_day = input_day
    if adj_time >= 24:
        adj_time -= 24
        output_day = (output_day + 1) % 7

    if adj_time < 10:
        output_time = "0" + str(adj_time)
    else:
        output_time = str(adj_time)    
        
    output_time += input_time[2:5] #add the minutes back

    return output_time, output_day

#Converts a time "00:00" from UTC time to EST time
def UTCtoEST(input_time, input_day):
    adj_time = int(input_time[:2]) - 4
    output_day = input_day
    if adj_time < 0:
        adj_time += 24
        output_day = (output_day + 6) % 7

    if adj_time < 10:
        output_time = "0" + str(adj_time)
    else:
        output_time = str(adj_time)    
        
    output_time += input_time[2:5] #add the minutes back

    return output_time, output_day
#Takes a string "00:00" and converts it into an int for the number of seconds since midnight
def TimeToMinutes(input_time):
    hour = input_time[:2]
    return int(hour) * 60 + int(input_time[3:5])

#Save the settings with the globals object
def SaveSettings(_glob):
    
    settings = {
        "running": _glob.running },\
        {
        "o1-channel-name": "online-1",
        "o2-channel-name": "online-2",
        "o3-channel-name": "online-3",
        "o4-channel-name": "online-4",
        "of-channel-name": "overflow-room",
        "ge-channel-name": "gen-ed-courses"},\
        {"o1-role-name": "Student - Online - 1",
        "o2-role-name": "Student - Online - 2",
        "o3-role-name": "Student - Online - 3",
        "o4-role-name": "Student - Online - 4",
        "ov-role-name": "Student - Overflow Room",
        "ge-role-name": "Student - GenEd Course",
        "tutor-role-name": "CoPilot Tutor",
        "manager-role-name": "Manager"
        },\
        {
        "main-channel-name": "copilot-open-hours",
        "faq-channel-name": "todays-tutor-hours",
        "sched-channel-name": "frequently-asked-questions"
    }

    with open('settings.json', 'w') as file:
        json.dump(settings, file, indent=4)

#Load the settings into the globals object
def LoadSettings(_glob):
    
    pass

#Removes a role from a specific student
async def remove_role_from_users(student):
    
    for member in student.channel.members:

        if student.role in member.roles:
            await member.remove_roles(student.role)

            if member.voice is not None:
                await member.move_to(None)

            embed = discord.Embed(title="Your tutoring session has ended.", description="Thank you for coming to the CoPilot tutoring center today! Feel free to come back anytime during our online hours.", color = discord.Color.blue())

            embed.add_field(name="Find our schedule online!", value = "Open Door Hours are Monday - Friday (9am - 9pm EST), and Saturday's (10am - 2pm EST)  View our tutoring schedule for the week on FSO (https://one.fullsail.edu/connect/departments/copilot-tutoring-center/119/events)", inline = False)
            embed.set_thumbnail(url="https://simplybook.me/uploads/copilot/image_files/preview/7763022288eca6256d446459bb505b05.jpg")

            await member.send(embed=embed)
            
            return True

    return False

#Checks if the current time should be closed or opened
def CheckClosed(input_time, input_day, schedules):
    time = TimeToMinutes(input_time)

    return schedules[input_day].open > time or schedules[input_day].close <= time

    
#Gets the amount of time in seconds until the next closing time
def TimeUntilClose(input_time, input_day, closing_times):
    current_time = TimeToMinutes(input_time)
    close_time = TimeToMinutes(closing_times[input_day])

    return ((close_time - current_time - 1) * 60) + 60 - int(datetime.now().strftime("%S"))

#Gets the amount of time in seconds until the next opening time
def TimeUntilOpen(input_time, input_day, opening_times):
    current_time = TimeToMinutes(input_time)
    time_wait = 1440 - current_time
    while(opening_times[input_day] == "00:00" and time_wait < 10080):
        input_day = (input_day + 1) % 7
        time_wait += 1440

    time_wait += TimeToMinutes(opening_times[input_day])
    return time_wait

#Turns an array of strings into a single csv string
# def ArrayToString(*args):
#     output = ""
#     print(output)
#     for arg in args:        
#         output += str(arg[:-1]) + ","
    
#     print(output)
#     output = output[1:-2]
#     print(output)
#     return output