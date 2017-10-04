from flask import Blueprint, render_template, flash, request, redirect, \
    url_for, jsonify

from app.modules.meeting.model import MeetingForm
from app.modules.meeting.model import Meeting

meeting = Blueprint('meeting', __name__)

@meeting.route('/new', methods=['GET', 'POST'])
def new():
    form = MeetingForm(request.form)
    if request.method == 'GET':
        return render_template('meeting/new.html', form=form)

    if form.validate():
        try: 
            return str(request.form['emails'])
        except Exception as e:
            flash('A problem has occurred, please try again! {}'.format(e))
            return redirect(url_for('meeting.new'))
    flash('Please list a meeting name between 3 and 50 characters in length!')
    return redirect(url_for('meeting.new'))
