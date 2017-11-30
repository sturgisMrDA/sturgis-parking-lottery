"""
# Parking Lottery Project
# (c) 2017 Sturgis Charter School, IB Computer Science class
# Manage and run the Sturgis West Parking Lottery.
"""
VERSION = 2.7
ANIMATION_DELAY = 3000 # ms to delay between displaying text for lottery results
# Import necessary libraries.
from tkinter import *
from tkinter import filedialog, ttk, messagebox
import csv, random, datetime, os 
def assignConstants(data):
    """
    Use column headers to find which column each question is in.
    These sometimes get moved when form is re-published,
    so can't be hard-coded in.
    Will raise a ValueError if an expected header is not found.
    This must be caught by the calling code.
    """
    # Mr. D.A.
    # Create global constants.
    global EMAIL_COL, GRADE_COL, NAME_COL, JOL_COL, CARPOOL_COL, \
           RIDER_NAME_COLS, RIDER_EMAIL_COLS
    # Get column headers (first row of array):
    headers = data[0]
    # These are the headers as assigned by google forms:
    # Use beginning of some questions because dates, etc., can change.
    questions = ['Email Address',
                 'Grade Level ',
                 'First and Last Name',
                 'Will you still be on your JOL ',
                 'Will you be carpooling? ']
    # Find columns for driver info:
    columns = []
    for q in questions:
        found = False
        for index,h in enumerate(headers):
            if h.startswith(q):
                columns.append(index)
                found = True
        if not found:
            raise ValueError
    EMAIL_COL, GRADE_COL, NAME_COL, JOL_COL, CARPOOL_COL = columns
    # Passengers are numbered 1-4.  These numbers will be tacked on later:
    rider_name_q = 'Name of Student Passenger '
    rider_email_q = 'Email of Student Passenger '
    # Assuming 4 passengers will be asked for,
    # find columns for passenger info:
    RIDER_NAME_COLS = []
    RIDER_EMAIL_COLS = []
    for n in range(1,5):
        RIDER_NAME_COLS.append(headers.index(rider_name_q+str(n)))
        RIDER_EMAIL_COLS.append(headers.index(rider_email_q+str(n)))
    #print(EMAIL_COL, GRADE_COL, NAME_COL, JOL_COL, CARPOOL_COL,
    #      RIDER_NAME_COLS, RIDER_EMAIL_COLS)
    return
def importToArray(filePath):
    """
    Read a CSV spreadsheet to a 2D array.
    Set each line in the file to an entry in a list.
    Set each entry in each line to a sublist.
    """
    # Alan, Justin, Dwight (well, mostly Alan)
    array = []
    with open(filePath, "rt", newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            array.append(row)
        file.close()
    return array
def JOL_drivers(data):
    """
    Check if anyone on JOL has signed up as carpooler (not allowed).
    JOL drivers ARE allowed to drive their siblings, so allow user to decide on a case-by-case basis
    whether to change these students to non-carpoolers.
    """
    #Theo Calianos, James Prygocki, Michael Bilodeau, Mr. D.A.
    JOL_flagged = [] # List of students with conflicting carpool/JOL answers.
    for i in range(len(data)):
        #Identify whether or not applicant is still on their JOL
        if data[i][JOL_COL] == "Yes" and data[i][CARPOOL_COL] == "Yes":
            name = data[i][NAME_COL]
            passengers = [data[i][x] for x in RIDER_NAME_COLS if (data[i][x] != '')]
            message = name + '\n\nis on JOL and has registered\n'
            message += 'as a carpooler with these passengers:\n\n'
            message += '\n'.join(passengers) + '\n\n'
            message += 'Would you like to remove this\n'
            message += 'driver from the carpooler list?'
            if messagebox.askyesno('JOL Check',message):
                data[i][CARPOOL_COL] = "No"
    return(data)
def gradYrs(cYOG):
    """ Return list of currently valid grad years as strings. """
    #Jack Wilson, William W. Smith, and significant editing by Mr. D.A.
    iCYOG=int(cYOG)
    posYrs=[]
    i=0
    while i<4:
            posYrs.append(str(iCYOG))
            iCYOG=iCYOG+1
            i=i+1
    return(posYrs)
def emailCheck(email, gradYrs):
    """
    Check if the email starts with a valid graduation year
    and ends in @sturgischarterschool.org
    """
    if '@' not in email:
        return False
    elif email.split('@')[1] != "sturgischarterschool.org":
        return False
    elif (email[:2] not in gradYrs):
        return False
    else:
        return True
def emailValidation(gradYear, data):
    """
    Check that the email addresses given for drivers and carpool passengers
    are valid student email addresses.  Allow user to change status of
    those that are not valid.
    """
    years = gradYrs(gradYear)
    numRows = len(data)
    for row in range(1,numRows): # Row 0 is headers, so start at row 1.
        # If driver email isn't valid...
        if not emailCheck(data[row][EMAIL_COL],years):
            message = data[row][NAME_COL] + '\n\nhas signed up as a driver with email address\n\n'
            message += data[row][EMAIL_COL]
            message += '\n\nwhich does not appear to be a valid student email.\n\n'
            message += 'Remove this applicant from the lottery?'
            # ... ask if we should remove the driver.
            if messagebox.askyesno('Invalid email',message):
                del data[row]
                continue # Move to next student driver.
        # If driver is a carpooler...
        if data[row][CARPOOL_COL] == 'Yes':
            # Get names and emails of passengers:
            rider_names = [data[row][x] for x in RIDER_NAME_COLS]
            rider_emails = [data[row][x].strip().lower() for x in RIDER_EMAIL_COLS]
            passengers = zip(rider_names, rider_emails)
            # Remove blank passengers:
            passengers = [x for x in passengers if x != ('', '')]
            # Now check whether passengers are students.
            valid_passengers = [emailCheck(x[1],years) for x in passengers]
            if not all(valid_passengers):
                message = data[row][NAME_COL] + ' has signed up\n'
                message += 'as a carpooler with the following passengers:\n\n'
                message += '\n'.join(
                    [x[0] + ', [no email given]' if x[1] == '' else ', '.join(x)
                                      for x in passengers])
                message += '\n\nSome of these passengers have invalid email\n'
                message += 'addresses.  Would you like to move this driver to\n'
                message += 'the non-carpooler list?'
                if messagebox.askyesno('Invalid passenger email',message):
                    data[row][CARPOOL_COL] = 'No'
    return data
def findGrade(data,gradYear):
    """
    This function allows the Lottery program to be able to determine what grade
    everybody is in. The function will first see what grade number the student
    put as their grade, then it will determine if the student told the truth.
    If they did not, the function will change the grade back to their actual
    grade.
    """
    # Ludjy, Klaire, Katie
    # data is the array that contains all the spreadsheet data.
    row = 1
    numOfRows = len(data)
    while row < numOfRows:   #creating a while loop - if row is less than the number of rows then...
        email = data[row][EMAIL_COL]   #email number might be made into an integer instead of a string
        #print(email)
        gradeNumber = data[row][GRADE_COL] #verifying that the gradenumber at begin of email is same, grade number is what they typed in/entered
        #print(gradeNumber)
        firstTwo = email[0:2]   #first two is the first two number in email which indicate year of grad (create var)
        #print(firstTwo)
        if int(firstTwo) == gradYear and gradeNumber == "11":   #if the first two numbers are the same as grad year, they r seniors
            data[row][GRADE_COL] = "12"   #we need to go into that row in the data and the GRADE_COL and change it to 12
        elif int(firstTwo) == gradYear + 1 and gradeNumber == "12": #corresponds with the year that it is
            data[row][GRADE_COL] = "11"   #changes that row and GRADE_COL to 11
            data [row][CARPOOL_COL] = "No"
        row = row +1 #then we go back to the next row and do the same things for the next thing
    return data
def quit_app():
    """Allows user to close the program."""
    root.withdraw()
    root.quit()
def validate():
    """
    This function checks to make sure the input for graduation year is a valid 2 digit number. Then
    it calls all the other validation functions.
    """
    # Set 'data' as a global variable.  This is the 2D array containing all spreadsheet values,
    # and will be used throughout the program:
    global data

    # Check that user entered a valid graduation year
    try:
        gradInput = int(gradEntry.get())
        if len(str(gradInput)) != 2:
            raise ValueError
    #alerts the user that a student's graduation year is invalid, then they will have a chance to enter a new graduation year
    except ValueError:
        messagebox.showinfo("Error", "The graduation year is not valid.")
        return False

    # Check that a file has been selected.
    if root.filepath == '':
        messagebox.showinfo("Error", "You need to select a file first.")
        return False
    data = emailValidation(gradInput, data)
    data = findGrade(data, gradInput)
    data = JOL_drivers(data)
    data = carpool_validate()
    message = "Validation finished. Changes will\nbe saved to the spreadsheet\n\n"
    message += root.filepath.split('/')[-1]
    message +="\n\nWould you like to view/edit this\nspreadsheet before running the lottery?"
    if messagebox.askyesno("Done",message):
        os.startfile(root.filepath)
        messagebox.showinfo("Close the spreadsheet.",
        "Make sure you save and close the spreadsheet before you continue running the lottery.")
    return data
def runLottery():
    """
    Running the Lottery
    This program takes the students' information located in a 2D array,
    prioritizes the students,
    randomly assigns parking spaces in order of priority,
    and writes the order to a new text file.
    """
    # by Justin Turbeville, with tweaks and error-handling by Mr. D.A.
    new_sheet = 'ParkingLotteryResults.csv'
    summary_file = 'ParkingSpaces.txt'
    if root.filepath == '':
        messagebox.showerror("Oops...",
        "You need to select a file first.")
        return
    else:
        try:
            dataArray = importToArray(root.filepath)
        except PermissionError:
            messagebox.showerror("Oops...",
            "Something's wrong.  Make sure the\nspreadsheet file is closed and try again.")
            return
        except FileNotFoundError:
            messagebox.showerror("Oops...",
            "That spreadsheet file seems to be missing.")
            return
    #these are the lists, based on priority, that will contain the students
    senCarpool = []
    sen = []
    junCarpool = []
    jun = []
    i = 1
    #this loop adds the students to the lists according to priority
    while i < len(dataArray):
        #this 'if' asks if the student is a junior
        if dataArray[i][GRADE_COL] == '11':
            #this code finds out if the junior is carpooling and adds them to a list accordingly
            if dataArray[i][CARPOOL_COL] == 'Yes':
                junCarpool.append(dataArray[i])
            else:
                jun.append(dataArray[i])
        #this 'else' just assumes the remaining students are seniors
        else:
            #this code finds out if the senior is carpooling and adds them to a list accordingly
            if dataArray[i][CARPOOL_COL] == 'Yes':
                senCarpool.append(dataArray[i])
            else:
                sen.append(dataArray[i])
        i = i + 1

    # The code below randomly orders each group of students,
    # and adds them to an array which shows the parking order.
    parkingSpots = []
    lotteryNum = 1
    #randomly orders seniors who carpool and adds them to the array
    while 0 < len(senCarpool):
        num = random.randint(0, len(senCarpool) - 1)
        student = senCarpool[num]
        del(senCarpool[num])
        parkingSpots.append([lotteryNum] + student)
        lotteryNum += 1
    #randomly orders remaining seniors and adds them to the array
    while 0 < len(sen):
        num = random.randint(0, len(sen) - 1)
        student = sen[num]
        del(sen[num])
        parkingSpots.append([lotteryNum] + student)
        lotteryNum += 1
    #randomly orders juniors who carpool and adds them to the array
    while 0 < len(junCarpool):
        num = random.randint(0, len(junCarpool) - 1)
        student = junCarpool[num]
        del(junCarpool[num])
        parkingSpots.append([lotteryNum] + student)
        lotteryNum += 1
    #randomly orders remaining juniors and adds them to the array
    while 0 < len(jun):
        num = random.randint(0, len(jun) - 1)
        student = jun[num]
        del(jun[num])
        parkingSpots.append([lotteryNum] + student)
        lotteryNum += 1
    # This code writes the data to a new CSV file
    with open(new_sheet, 'w+', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Parking space']+dataArray[0])
        for row in parkingSpots:
            writer.writerow(row)
        file.close()
    message = "Lottery results will be saved\nto a new spreadsheet:\n\n"
    message += new_sheet
    message += "\n\nA summary of names and parking\nspaces will be in:\n\n"
    message += summary_file
    messagebox.showinfo("Here we go!", message)
    # Save summary to text file:
    with open(summary_file, 'w') as file:
        # All columns are +1 because we added the parking space column.
        for row in parkingSpots:
            display_text = '...'.join([str(row[x]) for x in [0, NAME_COL + 1, EMAIL_COL + 1]])
            file.write(display_text + '\n')
        file.close()
    # Display results on the screen.
    # We need this hinky recursive callback nonsense to avoid locking up on button press.
    # See http://stupidpythonideas.blogspot.com/2013/10/why-your-gui-app-freezes.html for details.
    row = 0
    def advance_text():
        nonlocal row, parkingSpots
        # All columns are +1 because we added the parking space column.
        display_text = ': '.join([str(parkingSpots[row][x]) for x in [0, NAME_COL + 1]])
        lottery_text1.set(lottery_text2.get())
        lottery_text2.set(display_text)
        row += 1
        if row < len(parkingSpots):
            root.after(ANIMATION_DELAY)
            root.after_idle(advance_text)
        else:
            lottery_text1.set(lottery_text2.get())
            lottery_text2.set("Lottery is finished.")
        return
    root.after_idle(advance_text)
    return 
def file_choose():
    """ Create a 'file open' dialog and set the chosen filepath in the main window. """
    # D.A.
    root.filepath =  filedialog.askopenfilename(
        initialdir = "/",title = "Select a spreadsheet file",filetypes =
        (("Comma-Separated Values (CSV)","*.csv"), ("all files","*.*")))
    # Open the spreadsheet and get data
    global data
    data = importToArray(root.filepath)
    # Run the validation functions
    try:
        assignConstants(data)
    except ValueError:
        root.filepath = ""
        file_text.set("No file chosen.")
        message = "This doesn't look like the file you want.\n"
        message += "It doesn't have the expected column headers.\n"
        messagebox.showinfo("Error", message)          
        return False
    if len(root.filepath) < 50:
        file_text.set(root.filepath)
    else:
        root.filename = root.filepath.rsplit('/',1)[1]
        abbreviated = root.filepath[:10] + ".../" + root.filename
        file_text.set(abbreviated)
    return data
def carpool_validate():
    """
    Check whether any carpool passengers are also listed as drivers.
    If so, flag both driver and passenger for potential correction.
    """
    # Carpool validation by D.A.
    # Huge apologies to Ryan Melehan, whose object-oriented approach was clever,
    # but I needed to simplify things for the sake of auto-correcting the "cheaters."
    global data
    # For each row of the spreadsheet (start at 1 to skip header row):
    for row in range(1,len(data)):
        # Get list of passenger emails for that driver.
        passenger_emails = [data[row][col] for col in RIDER_EMAIL_COLS if data[row][col] != ''] \
                            if data[row][CARPOOL_COL] == 'Yes' else []
        # Make a list of passengers who are also drivers:
        driver_passengers = []
        for rider_mail in passenger_emails:
            rider_index = is_driver(rider_mail)
            if rider_index:
                driver_passengers.append((rider_index,rider_mail,data[rider_index][NAME_COL]))
        # Do something about it
        if driver_passengers:
            driver_name = data[row][NAME_COL]
            message = '{} has listed the\nfollowing carpool passengers who\nare also listed as drivers:\n\n'
            message += '\n'.join([x[2] for x in driver_passengers]) + '\n\n'
            question = 'Would you like to change\n\n{}\n\nto non-carpooler status?'
            prompt = message.format(driver_name) + question.format(driver_name)
            if messagebox.askyesno('Carpool Issue',prompt):
                data[row][CARPOOL_COL] = 'No'
            for rider_index,rider_email,rider_name in driver_passengers:
                prompt = message.format(driver_name) + question.format(rider_name)
                if messagebox.askyesno('Carpool Issue',prompt):
                    data[rider_index][CARPOOL_COL] = 'No'
    return data
def is_driver(email):
    """
    If email is in the driver email column, return its row index;
    else return False.
    """
    global data
    driver_emails = [data_row[EMAIL_COL] for data_row in data]
    try:
        driver_index = driver_emails.index(email)
        return driver_index
    except ValueError:
        return False
    return
def set_grad_year():
    """ Return the current grad year based on current date """
    now = datetime.date.today()
    year = now.year
    # Get last two digits of year.
    # Okay, I could just subtract 2000 but this is more thorough, in case this program
    # is still used 83 years from now:
    year -= (year // 100) * 100
    month = now.month
    # If after March, assume we are running the fall lottery.  
    # Therefore, return next year as the grad year.  
    if month > 3:
        return year + 1
    else:
        return year
def get_help():
    try:
        os.startfile('help.txt')
    except FileNotFoundError:
        messagebox.showerror('Helpless',"Can't find the help file.\nSearch your google docs for instructions.")
def show_credits():
    try:
        os.startfile('credits.txt')
    except FileNotFoundError:
        messagebox.showerror('No credits',"Can't find the credits file.")
def main():
    """ Parking Lottery GUI """
    #By: Matt, Mark, Madison, Alan, Justin, MR. D.A.
    # global variables used by other functions
    global root, file_text, gradEntry, lottery_text1, lottery_text2
    #the code below creates the user interface
    root = Tk()
    root.title('Sturgis Parking Lottery')

    #the code below creates a menu bar with 'File' and 'Help' menus.
    menubar = Menu(root)
    file_menu = Menu(menubar, tearoff=0)
    file_menu.add_command(label='Quit', command=quit_app)
    menubar.add_cascade(label='File', menu=file_menu)
    help_menu = Menu(menubar, tearoff=0)
    help_menu.add_command(label='Help',command=get_help)
    help_menu.add_command(label='Credits',command=show_credits)
    menubar.add_cascade(label='Help', menu=help_menu)
    root.config(menu=menubar)

    # Label an entry box to get current graduation year,
    # used to determine if students' input for grad year is invalid.
    grad_text = "Current Senior Graduation Year (last two digits):"
    gradLabel = Label(root, text=grad_text)
    gradLabel.grid(row=1, column=1, columnspan=3)
    gradEntry = Entry(root, width=2)
    gradEntry.insert(0,set_grad_year()) # Set a default value based on current date.
    gradEntry.grid(row=1, column=4, sticky=W, padx=10, pady=10)

    # Button to choose spreadsheet file
    file_button = Button(root, text='Choose a file...', command=file_choose)
    file_button.grid(row=2, column=1, padx=10, pady=10, sticky=W)
    # Display name of chosen file.
    root.filepath = ''
    file_text = StringVar()
    file_text.set("No file chosen.")
    file_label = Label(root, textvariable=file_text)
    file_label.grid(row=2, column=2, columnspan=5, padx=10, pady=10, sticky=W)

    # Create button that will validate the students' graduation years
    validatebutton = Button(root, text='Validate', command=validate)
    validatebutton.grid(row=9, column=1, padx=10, pady=10)

    # Create a button that will run the lottery
    lotterybutton= Button(root, text='Run Lottery', command=runLottery)
    lotterybutton.grid(row=9, column=2, padx=10, pady=10)

    # Create labels that will be used to display lottery results as they are run.
    lottery_text1 = StringVar()
    lottery_text2 = StringVar()
    lottery_text1.set("Choose a file")
    lottery_text2.set("and then click Validate...")
    lottery_label1 = Label(root, textvariable=lottery_text1, anchor=W, width=35)
    lottery_label2 = Label(root, textvariable=lottery_text2, anchor=W, width=35)
    lottery_label1.grid(row=20, column=1, columnspan = 6, sticky=W)
    lottery_label2.grid(row=22, column=1, columnspan = 6, sticky=W)

    # Run the whole thing
    root.mainloop()
if __name__ == '__main__':
    main()