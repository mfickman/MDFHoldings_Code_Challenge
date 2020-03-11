import flask
from flask import Flask, render_template, url_for, request, redirect, flash, Response
from flask_sqlalchemy import SQLAlchemy
import datetime
import sqlite3


##### INITIALIZATIONS #####
## create flask application
app = Flask(__name__)


## create sqlite local dabase LogHistory.db
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///LogHistory.db'
db = SQLAlchemy(app)
sqlite_conn = sqlite3.connect('LogHistory.db', check_same_thread=False)


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
## create error handeling
@app.errorhandler(404)
def page_not_found(error):
    error_message = "404 Status Received, this page does not exist"
    return render_template("error.html", error_message=error_message)

## create index/home method
@app.route("/", methods=['GET', 'POST'])
def index():
    flash_bool = False
    flash_message = ""
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
            #flash("bad data flash custom")
            print("IN BAD DATA")
            flash_bool = True
            flash_message = "Invalid phone numbers entered"
            # get all pending calls
            pending_log = CallLog.query.filter_by(is_active=0).filter_by(deleted=0).order_by(CallLog.id).all()

            # get all active calls
            active_log = CallLog.query.filter_by(is_active=1).filter_by(deleted=0).order_by(CallLog.id).all()
            print(active_log)
            return render_template("index.html", flash_bool=flash_bool, flash_message=flash_message, pending_log=pending_log, active_log=active_log)
        else:
            new_call_log = CallLog(ani_number=ani_log, callto_number=callto_log, date_created=datetime.datetime.now(), is_active=0, deleted=0)
            #push content to dabase
            try:
                db.session.add(new_call_log)
                db.session.commit()
                return redirect('/')
            except Exception as e:
                return redirect('page_not_found')
    else:
        #get all pending calls
        pending_log = CallLog.query.filter_by(is_active=0).filter_by(deleted=0).order_by(CallLog.id).all()
        print(pending_log)

        #get all active calls
        active_log = CallLog.query.filter_by(is_active=1).filter_by(deleted=0).order_by(CallLog.id).all()
        print(active_log)
        return render_template("index.html", pending_log=pending_log, active_log=active_log, flash_bool=flash_bool, flash_message=flash_message)

## create route to mock delete content, but actual just hang up, is_active=0, deleted=1, date_deleted=datetime.datetime.now()
@app.route("/hangup/<int:id>/", methods=['GET', 'POST'])
def hang_up(id):
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
        return redirect('page_not_found')

## create route to answer phone, mock PUT method, update data, set is_active=1
@app.route("/answer/<int:id>/", methods=['GET', 'POST'])
def answer(id):
    ans_call_log = CallLog.query.get_or_404(id)
    try:
        print(ans_call_log)
        ans_call_log.is_active = 1
        ans_call_log.time_active = datetime.datetime.now()
        db.session.commit()
        return redirect('/')
    except Exception as e:
        return redirect('page_not_found')

## create manual post method with 3 distinct fields, mimics index/home
@app.route("/<int:ani>/<int:callto>/<string:action>/")
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
        print("BAD DATA for manual post")
        redirect(url_for('.index', flash_bool=True, flash_message="BAD DATA FOR MNA"))
    #if action is answer, check that numbers exist in pending log database
    if action_log.lower() == 'answer':
        try:
            pending_log_match = CallLog.query.filter_by(is_active=0).filter_by(deleted=0).filter_by(ani_number=ani_log).filter_by(callto_number=callto_log).order_by(CallLog.id).all()
            answer(pending_log_match[0].id)
            return redirect('/')
        except Exception as e:
            return redirect('page_not_found')
    #action is hangup
    elif action_log.lower() == 'hangup':
        try:
            log_match = CallLog.query.filter_by(deleted=0).filter_by(ani_number=ani_log).filter_by(callto_number=callto_log).order_by(CallLog.id).all()
            hang_up(log_match[0].id)
            return redirect('/')
        except Exception as e:
            return redirect('page_not_found')
    else:
        ## bad action
        return redirect('page_not_found')

## create full log page with button to redirect to home page
@app.route("/history_page/")
def history_page():
    full_log = CallLog.query.all()
    return render_template("history.html", full_log=full_log)


##### HOUSEKEEPING #####
if __name__ == "__main__":
    app.run(debug=True)



