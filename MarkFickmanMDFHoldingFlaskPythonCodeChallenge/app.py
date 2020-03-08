from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
import datetime
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import sqlite3
import os


##### INITIALIZATIONS #####
## create flask application
app = Flask(__name__)

## create sqlite local dabase LogHistory.db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///LogHistory.db'
db = SQLAlchemy(app)
sqlite_conn = sqlite3.connect('LogHistory.db', check_same_thread=False)


##### EXTRA FUNCTIONS #####
## method/function to quickly create dataframe from numpy converted output of sql query for easy debugging
def create_DataFrame(data, colnames):
    col_arr = np.array(colnames)
    df = pd.DataFrame(data, columns=col_arr[:, 0])
    return df

def dataframe_download(data, colnames, report_name):

    #create dataframe from column names and db values
    # df_database = create_DataFrame(dbvalue, dbdescriptionlist)
    data_arr = np.array(data)
    #print(data_arr)
    df_database = pd.DataFrame(data_arr, columns=colnames)


    # Create a Pandas Excel writer using XlsxWriter as the engine.
    df_save_dir = os.path.join(app.root_path, app.config['TEMP_PATH'])
    df_save_name = report_name
    writer = pd.ExcelWriter(df_save_dir + df_save_name, engine='xlsxwriter')
    workbook = writer.book # create an xlsxwriter so later on we can add new worksheets utilizing xlswriter instead of pandas

    # Convert the dataframe to an XlsxWriter Excel object.
    df_database.to_excel(writer, sheet_name='Sheet1')

    #set column length
    worksheet = writer.sheets['Sheet1']  # pull worksheet object
    for idx, col in enumerate(df_database):  # loop through all columns
        series = df_database[col]
        max_len = max((
            series.astype(str).map(len).max(),  # len of largest item
            len(str(series.name))  # len of column name/header
            )) + 1  # adding a little extra space
        worksheet.set_column(idx+1, idx+1, max_len)  # set column width

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()

    return df_save_name

def download_history_log():
    log_output = CallLog.query.all()
    df = pd.read_sql_table(table_name="call_log", con="sqlite:///LogHistory.db")
    df_download = dataframe_download(df.values, list(df.columns.get_values()), 'Full_History_Log_' + datetime.datetime.now().strftime("%Y_%m_%D_%H_%M_%S") + ".xlsx")
    return df_download



##### MODELS #####
##create the model for the call log class
class CallLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ani_number = db.Column(db.String(12), nullable=False)
    callto_number = db.Column(db.String(12), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Integer, nullable=False)
    time_active = db.Column(db.DateTime, nullable=True)
    deleted = db.Column(db.Integer, nullable=True)
    date_deleted = db.Column(db.DateTime, nullable=True)

    ## function to return string when we create new entry
    def __repr__(self):
        return '<Log_x %r>' % self.id


##### ROUTES #####
## create index/home method
@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        bad_ani = False
        bad_callto = False

        ani_log = request.form['ani_number']
        callto_log = request.form['callto_number']

        #validate number input
        if len(str(ani_log)) != 11:
            bad_ani = True
        elif str(ani_log)[0] != '1':
            bad_ani = True

        if len(str(callto_log)) != 11:
            bad_callto = True
        elif str(callto_log)[0] != '1':
            bad_callto = True

        if True in [bad_ani, bad_callto]:
            ##dont create calllog obejct, mock 400 status
            return redirect('/')

        else:
            new_call_log = CallLog(ani_number=ani_log, callto_number=callto_log, date_created=datetime.datetime.now(), is_active=0, deleted=0)

            #push content to dabase
            try:
                db.session.add(new_call_log)
                db.session.commit()
                return redirect('/')
            except Exception as e:
                error_message = "Error in POST Method" + "\n" + "Exception: " + str(e)
                return error_message
    else:
        #get all pending calls
        pending_log = CallLog.query.filter_by(is_active=0).filter_by(deleted=0).order_by(CallLog.id).all()

        print(pending_log)

        #get all active calls
        # active_log_query = """SELECT id, ani_number, callto_numer, date_created from call_log WHERE is_active = 1 AND deleted = 0"""
        # active_log = sqlite_conn.execute(active_log_query).fetchall()
        active_log = CallLog.query.filter_by(is_active=1).filter_by(deleted=0).order_by(CallLog.id).all()
        print(active_log)

        return render_template("index.html", pending_log=pending_log, active_log=active_log)

## create route to mock delete content, but actual just hang up, is_active=0, deleted=1, date_deleted=datetime.datetime.now()
@app.route("/hangup/<int:id>/", methods=['GET', 'POST'])
def hang_up(id):
    # del_call_log = CallLog.query.filter_by(id=id).all()
    del_call_log = CallLog.query.get_or_404(id)
    try:
        print(del_call_log)
        del_call_log.is_active = 0
        del_call_log.deleted = 1
        del_call_log.date_deleted = datetime.datetime.now()
        db.session.commit()
        return redirect('/')
    except Exception as e:
        error_message = "Error in hangup Method" + "\n" + "Exception: " + str(e)
        return error_message

## create route to answer phone, mock PUT method, update data, set is_active=1
@app.route("/answer/<int:id>/", methods=['GET', 'POST'])
def answer(id):
    # del_call_log = CallLog.query.filter_by(id=id).all()
    ans_call_log = CallLog.query.get_or_404(id)
    try:
        print(ans_call_log)
        ans_call_log.is_active = 1
        ans_call_log.time_active = datetime.datetime.now()
        db.session.commit()
        return redirect('/')
    except Exception as e:
        error_message = "Error in Answer Method" + "\n" + "Exception: " + str(e)
        return error_message

## create manual post method with 3 distinct fields, mimics index/home
@app.route("/post_x/<int:ani>/<int:callto>/<string:action>/")
def index_manual_post(ani, callto, action):
    bad_ani = False
    bad_callto = False
    bad_action = False

    ani_log = ani
    callto_log = callto
    action_log = action

    #validate number input
    if len(str(ani_log)) != 11:
        bad_ani = True
    elif str(ani_log)[0] != '1':
        bad_ani = True

    if len(str(callto_log)) != 11:
        bad_callto = True
    elif str(callto_log)[0] != '1':
        bad_callto = True

    #valid action input
    if action_log.lower() not in ['answer', 'hangup']:
        bad_action = True

    if True in [bad_ani, bad_callto, bad_action]:
        ##dont create calllog obejct, mock 400 status
        return redirect('/')

    #if action is answer, check that numbers exist in pending log database
    if action_log.lower() == 'answer':
        try:
            pending_log_match = CallLog.query.filter_by(is_active=0).filter_by(deleted=0).filter_by(ani_number=ani_log).filter_by(callto_number=callto_log).order_by(CallLog.id).all()
            # print("pending_log_match[0].id: {}".format(pending_log_match[0].id))
            answer(pending_log_match[0].id)
            return redirect('/')
        except Exception as e:
            error_message = "Error in manual method to answer phone" + "\n" + "Exception: " + str(e)
            return redirect('/')
    #action is hangup
    elif action_log.lower() == 'hangup':
        try:
            log_match = CallLog.query.filter_by(deleted=0).filter_by(ani_number=ani_log).filter_by(callto_number=callto_log).order_by(CallLog.id).all()
            hang_up(log_match[0].id)
            return redirect('/')
        except Exception as e:
            error_message = "Error in manual method to hang up phone" + "\n" + "Exception: " + str(e)
            return redirect('/')
    else:
        ## bad action
        return redirect('/')

## create full log page with button to redirect to home page
@app.route("/history_page/")
def history_page():
    full_log = CallLog.query.all()
    return render_template("history.html", full_log=full_log)


##### HOUSEKEEPING #####
if __name__ == "__main__":
    app.run(debug=True)



