from PyQt5 import uic, QtWidgets
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
import sys
import sqlite3
import pandas as pd
class EditDialog(QDialog):
    def __init__(self, parent=None):
        super(EditDialog, self).__init__(parent)
        self.setWindowTitle("Edit Record")

        self.layout = QVBoxLayout(self)

        # self.label5 = QLabel("id")
        # self.num_input = QLineEdit(self)
        # self.layout.addWidget(self.label5)
        # self.layout.addWidget(self.num_input)

        self.label1 = QLabel("Object")
        self.str1_input = QLineEdit(self)
        self.layout.addWidget(self.label1)
        self.layout.addWidget(self.str1_input)

        self.label2 = QLabel("DefaultValues")
        self.str2_input = QLineEdit(self)
        self.layout.addWidget(self.label2)
        self.layout.addWidget(self.str2_input)

        self.label3 = QLabel("WorksheetColumnName")
        self.str3_input = QLineEdit(self)
        self.layout.addWidget(self.label3)
        self.layout.addWidget(self.str3_input)

        self.save_button = QPushButton("Save", self)
        self.save_button.clicked.connect(self.accept)
        self.layout.addWidget(self.save_button)

    def set_values(self, str1, str2, str3):
       
        self.str1_input.setText(str1)
        self.str2_input.setText(str2)
        self.str3_input.setText(str3)

    def get_values(self):
        return (
            self.str1_input.text(),
            self.str2_input.text(),
            self.str3_input.text()
        )

class Ui(QtWidgets.QMainWindow):
    
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('Test2.ui', self)

        self.conn = sqlite3.connect('NEWDATA.db')
        self.cursor = self.conn.cursor()

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS input_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Objects TEXT,
                DefaultValues TEXT,
                WorksheetColumnName TEXT
            )
        ''')
        self.conn.commit()

        self.Button1.clicked.connect(self.data)
        self.Button1.clicked.connect(self.display_input_data)

        self.table_model = QStandardItemModel(self)
        self.tableView.setModel(self.table_model)

        self.deleteButton.clicked.connect(self.delete_record)
        self.editButton.clicked.connect(self.edit_record)
        self.showtableButton.clicked.connect(self.display_input_data)

        self.show()

    def create_table(self, table_name):
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS {} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Objects TEXT,
                DefaultValues TEXT,
                WorksheetColumnName TEXT
            )
        '''.format(table_name))
        self.conn.commit()
        self.show()

        # cnx = sqlite3.connect('NEWDATA.db')
        # df = pd.read_sql_query("SELECT * FROM {}".format(table_name), cnx)
        # print(df)


    def log_to_database(self, table_name, str1, str2, str3):
        table_name = self.Input5.currentText()

        # Create the table if it doesn't exist
        self.create_table(table_name)

        # Insert data into the specified table
        self.cursor.execute("INSERT INTO {} (Objects, DefaultValues, WorksheetColumnName) VALUES (?, ?, ?)".format(table_name),
                            (str1, str2, str3))
        self.conn.commit()



    def display_input_data(self, table_name):
        table_name = self.Input5.currentText()
        print(table_name)
        # Clear existing data in the QTableView
        self.table_model.clear()

        # Set table headers
        self.table_model.setHorizontalHeaderLabels(["id","Objects"," DefaultValues", "WorksheetColumnName"])

        # Fetch data from the database and display it
        self.cursor.execute("SELECT id, Objects, DefaultValues, WorksheetColumnName From {}".format(table_name))
        data = self.cursor.fetchall()
        
        for row_number, row_data in enumerate(data):
            for column_number, column_data in enumerate(row_data):
                item = QStandardItem(str(column_data))
                self.table_model.setItem(row_number, column_number, item)
        
        cnx = sqlite3.connect('NEWDATA.db')
        df = pd.read_sql_query("SELECT * FROM {}".format(table_name), cnx)
        print(df)
    def delete_record(self,table_name):
        table_name = self.Input5.currentText()
        # Get the ID to delete from the user input
        id_to_delete = self.Input4.text()

        try:
            table_name = table_name
            # Convert the ID to an integer
            id_to_delete = int(id_to_delete)

            # Delete the record from the database
            self.cursor.execute("DELETE FROM {} WHERE id=?".format(table_name), (id_to_delete,))
            self.conn.commit()

            # Refresh the table view
            self.display_input_data(table_name)

        except ValueError:
            print("Invalid ID input. Please enter a valid integer.")
    
    def edit_record(self,table_name):
        table_name = self.Input5.currentText()
        # Get the ID to edit from the user input
        id_to_edit = self.Input4.text()

        try:
            table_name = table_name
            # Convert the ID to an integer
            id_to_edit = int(id_to_edit)

            # Fetch the existing data for editing
            self.cursor.execute("SELECT Objects, DefaultValues, WorksheetColumnName FROM {} WHERE id=?".format(table_name), (id_to_edit,))
            existing_data = self.cursor.fetchone()

            # Open the edit dialog and set existing values
            edit_dialog = EditDialog(self)
            edit_dialog.set_values( existing_data[0], existing_data[1], existing_data[2])


            if edit_dialog.exec_() == QDialog.Accepted:
                # Get the edited values
                edited_values = edit_dialog.get_values()

                # Update the record in the database
                self.cursor.execute("UPDATE {} SET Objects=?, DefaultValues=?, WorksheetColumnName=? WHERE id=?".format(table_name),
                                    ( edited_values[0], edited_values[1], edited_values[2], id_to_edit))
                self.conn.commit()

                # Refresh the table view
                self.display_input_data(table_name)

        except ValueError:
            print("Invalid ID input. Please enter a valid integer.")
    def data(self):
        table_name = self.Input5.currentText()  # Replace this with your logic to get the table name
        str1 = self.Input1.text()
        str2 = self.Input2.text()
        str3 = self.Input3.text()

        self.log_to_database(table_name, str1, str2, str3)

    def get_table_name_somehow(self):
        # Replace this with your logic to get the table name dynamically
        return "input_data"
    def tableNameComboBoxChanged(self):
        # When the table name in the ComboBox changes, update the displayed data
        self.display_input_data()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    sys.exit(app.exec_())
