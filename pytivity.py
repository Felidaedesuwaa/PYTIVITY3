import sqlite3

from PyQt5.QtWidgets import QDialog, QApplication, QListWidgetItem, QMessageBox 
from PyQt5.uic import loadUi
import sys

from PyQt5.QtCore import Qt

# Define a class for the main window
class Window(QDialog):
    def __init__(self):
        # Initialize the window
        super(Window, self).__init__()
        # Load the UI file into the window
        loadUi("pytivity.ui", self)
        # Connect the calendar date changed signal to the calendarDateChanged method
        self.calendarWidget.selectionChanged.connect(self.calendarDateChanged)
        # Call the calendarDateChanged method initially
        self.calendarDateChanged()
         # Connect the save button's clicked signal to the saveChanges method
        self.saveButton.clicked.connect(self.saveChanges)
        # Connect the add button's clicked signal to the addNewTask method
        self.addButton.clicked.connect(self.addNewTask)
        # Connect the clear button's clicked signal to the deleteTask method
        self.clearButton.clicked.connect(self.deleteTask)

# Method to handle calendar date changes
    def calendarDateChanged(self):
         # Get the selected date from the calendar
        print("The calendar date was changed.")
        dateSelected = self.calendarWidget.selectedDate().toPyDate()
        # Update the task list with the selected date
        print("Date selected:", dateSelected)
        self.updateTaskList(dateSelected)

# Method to update the task list with the selected date
    def updateTaskList(self, date):
        # Clear the task list
        self.tasksListWidget.clear()
        # Connect to the database
        db = sqlite3.connect("data.db")
        cursor = db.cursor()

 # Create a query to select tasks for the selected date
        query = "SELECT task, completed FROM tasks WHERE date = ?"
         # Execute the query with the selected date
        row = (date,)
        results = cursor.execute(query, row).fetchall()
         # Iterate over the results
        for result in results:
             # Create a new list item
            item = QListWidgetItem(str(result[0]))
            # Set the item's flags to allow checking
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            # Check the item if the task is completed
            if result[1] == "YES":
                item.setCheckState(Qt.Checked)
            elif result[1] == "NO":
                item.setCheckState(Qt.Unchecked)
                # Add the item to the task list
            self.tasksListWidget.addItem(item)

     # Method to save changes
    def saveChanges(self):
        # Connect to the database
        db = sqlite3.connect("data.db")
        cursor = db.cursor()
        # Get the selected date
        date = self.calendarWidget.selectedDate().toPyDate()

# Iterate over the items in the task list
        for i in range(self.tasksListWidget.count()):
            # Get the item
            item = self.tasksListWidget.item(i)
             # Get the task text
            task = item.text()
             # Check if the item is checked
            if item.checkState() == Qt.Checked:
                 # Update the task as completed
                query = "UPDATE tasks SET completed = 'YES' WHERE task = ? AND date = ?"
            else:
                # Update the task as not completed
                query = "UPDATE tasks SET completed = 'NO' WHERE task = ? AND date = ?"
                # Execute the query with the task and date
            row = (task, date)
            cursor.execute(query, row)
            # Commit the changes
        db.commit()

# Show a message box to indicate that changes were saved
        messageBox = QMessageBox()
        messageBox.setText("Changes saved.")
        messageBox.setStandardButtons(QMessageBox.Ok)
        messageBox.exec()

   
    # Method to delete a task
    def deleteTask(self):
        # Get the selected item
        item = self.tasksListWidget.currentItem()
        if item is not None:
            # Get the task text
            task = item.text()
            # Get the selected date
            date = self.calendarWidget.selectedDate().toPyDate()
            # Connect to the database
            db = sqlite3.connect("data.db")
            cursor = db.cursor()
            # Create a query to delete the task
            query = "DELETE FROM tasks WHERE task = ? AND date = ?"
            # Show a confirmation dialog box
            messageBox = QMessageBox()
            messageBox.setText("Are you sure you want to delete the task '{}'?".format(task))
            messageBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            messageBox.setDefaultButton(QMessageBox.No)
            result = messageBox.exec()
            if result == QMessageBox.Yes:
                # Execute the query with the task and date
                row = (task, date)
                cursor.execute(query, row)
                # Commit the changes
                db.commit()
                # Remove the item from the task list
                self.tasksListWidget.takeItem(self.tasksListWidget.row(item))
                # Show a message box to indicate that the task was deleted
                messageBox = QMessageBox()
                messageBox.setText("Task deleted.")
                messageBox.setStandardButtons(QMessageBox.Ok)
                messageBox.exec()
            else:
                # Show a message box to indicate that the task was not deleted
                messageBox = QMessageBox()
                messageBox.setText("Task not deleted.")
                messageBox.setStandardButtons(QMessageBox.Ok)
                messageBox.exec()
        else:
            messageBox = QMessageBox()
            messageBox.setText("No task selected.")
            messageBox.setStandardButtons(QMessageBox.Ok)
            messageBox.exec()

# Method to add a new task
    def addNewTask(self):
        # Connect to the database
        db = sqlite3.connect("data.db")
        cursor = db.cursor()

 # Get the new task text
        newTask = str(self.taskLineEdit.text())
        # Get the selected date
        date = self.calendarWidget.selectedDate().toPyDate()

# Create a query to insert the new task
        query = "INSERT INTO tasks(task, completed, date) VALUES (?,?,?)"
        # Execute the query with the new task, date, and not completed
        row = (newTask, "NO", date,)

        cursor.execute(query, row)
        # Commit the changes
        db.commit()
        # Update the task list with the new task
        self.updateTaskList(date)
        # Clear the task line edit
        self.taskLineEdit.clear()

# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
