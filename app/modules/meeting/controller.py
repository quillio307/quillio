from flask import Blueprint, render_template, flash, request, redirect, \
    url_for, jsonify
from flask_security import current_user, login_required

from app.modules.auth.model import User
from app.modules.meeting.model import MeetingForm
from app.modules.meeting.model import Meeting

meeting = Blueprint('meeting', __name__)


@meeting.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    form = MeetingForm(request.form)
    if request.method == 'GET':
        return render_template('meeting/new.html', form=form)

    if form.validate():
        try:
            # generate list of users that will be in the meeting
            emails = form.emails.data.split(" ")
            emails.append(current_user.email)

            # grab the list of valid users
            query = User.objects(email__in=emails)
            query_emails = [u.email for u in query]

            # validate that all the members exist
            if len(emails) == len(query):
                Meeting(name=form.name.data, members=query, active=True).save()
                flash('New meeting created with member(s): {}'
                      .format(query_emails))
                return redirect(url_for('dash.home'))
            # show the invalid users
            else:
                invalid = list(set(emails) - set(query_emails))
                flash('Could not find user(s): {}'.format(invalid))
                return redirect(url_for('meeting.new'))
        except Exception as e:
            flash('A problem has occurred, please try again! {}'.format(e))
            return redirect(url_for('meeting.new'))
    flash('Please list a meeting name between 3 and 50 characters in length!')
    return redirect(url_for('meeting.new'))
