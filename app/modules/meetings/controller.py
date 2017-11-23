import json
import string
import re

from rake_nltk import Rake
from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer


from app.modules.auth.model import User
from app.modules.meetings.model import Meeting, MeetingCreateForm, \
    MeetingUpdateForm, MeetingDeleteForm

from flask import Blueprint, render_template, flash, request, redirect, \
    url_for, jsonify
from flask_security import current_user, login_required

meetings = Blueprint('meetings', __name__)


def filter_form(form):
    """ Router for CRUD Forms that were Recieved on the Meeting Dashboard """

    if form['submit'] == 'create':
        return create_meeting(form)
    elif form['submit'] == 'update':
        return update_meeting(form)
    elif form['submit'] == 'delete':
        return delete_meeting(form)

    flash('Could not Fulfill Request. Please Try Again.')
    return redirect(url_for('meetings.home'))


@meetings.route('/', methods=['GET', 'POST'])
@login_required
def home():
    """ Displays All of the Current Users Meetings on the Meeting Dashboard """
    if request.method == 'POST':
        return filter_form(request.form)

    user = current_user._get_current_object()
    return render_template('meeting/dashboard.html', meetings=user.meetings)


@meetings.route('/create', methods=['POST'])
@login_required
def create_meeting(form=None):
    """ Creates a new Meeting. """

    if form is None:
        flash('error Invalid Request to Create Meeting.')
        return redirect(request.args.get('next') or url_for('meetings.home'))

    create_form = MeetingCreateForm(form)

    if not create_form.validate():
        flash('error Could not Create New Meeting, Please Try Again.')
        return redirect(request.args.get('next') or url_for('meetings.home'))

    try:
        user = current_user._get_current_object()

        # generate the list of users that will be in the meeting
        emails = create_form.emails.data.split(" ")
        emails.append(user.email)

        # generate the list of valid emails
        query = User.objects(email__in=emails)
        valid_emails = [u.email for u in query]

        # display the invalid emails, cancel the creation request
        if len(emails) != len(emails):
            invalid_emails = list(set(emails) - set(valid_emails))
            flash('error We Were Unable to Find User(s): {}'.format(
                invalid_emails))
            return redirect(url_for('meetings.home'))

        # validate and create the meeting
        m = Meeting(name=create_form.name.data,
                    members=query, owner=user, active=False).save()

        # insert the meeting in each user's list of meetings
        for u in query:
            u.meetings.append(m)
            u.meeting_count = u.meeting_count + 1
            u.save()

        flash('success New Meeting Created with Member(s): {}'.format(
            ", ".join(valid_emails)))
    except Exception as e:
        flash('error An Error has occurred, Please Try Again. {}'.format(e))

    return redirect(request.args.get('next') or url_for('meetings.home'))


@meetings.route('/update', methods=['PUT'])
@login_required
def update_meeting(form=None):
    """ Updates an Existing Meeting """

    if form is None:
        flash('error Invalid Request to Create New Meeting.')
        return redirect(request.args.get('next') or url_for('meetings.home'))

    update_form = MeetingUpdateForm(form)

    if not update_form.validate():
        flash('error Could not Update Meeting, Please Try Again.')
        return redirect(request.args.get('next') or url_for('meetings.home'))

    try:
        # extract the form data
        name = update_form.name.data
        emails_to_add_str = update_form.emails_to_add.data
        emails_to_remove_str = update_form.emails_to_remove.data

        # search for the meeting
        meeting = Meeting.objects.get(id=update_form.meeting_id.data)

        members = meeting.members

        # remove the undesired members
        if len(emails_to_remove_str) != 0:
            emails_to_remove = emails_to_remove_str.split(" ")
            members_to_remove = User.objects(email__in=emails_to_remove)

            # remove the meeting from each members list of meetings
            for member in members_to_remove:
                if meeting in member.meetings:
                    member.meeting_count = member.meeting_count - 1
                    member.meetings.remove(meeting)
                    member.save()

            # remove the members from the list
            members = list(filter(
                lambda x: x not in members_to_remove, members))

        # add the new members
        if len(emails_to_add_str) != 0:
            emails_to_add = emails_to_add_str.split(" ")
            members_to_add = User.objects(email__in=emails_to_add)

            for member in members_to_add:
                # add member to the meeting's list of members
                if member not in members:
                    members.append(member)

                # add meeting to the member's list of meetings
                if meeting not in member.meetings:
                    member.meetings.append(meeting)
                    member.save()

        # save the changes
        meeting.name = name
        meeting.members = members
        meeting.save()

        flash('success Meeting has been Successfully Updated.')
    except Exception as e:
        flash('error An Error has Occurred, Please Try Again. {}'.format(e))

    return redirect(request.args.get('next') or url_for('meetings.home'))


@meetings.route('/delete', methods=['POST'])
@login_required
def delete_meeting(form=None):
    """ Deletes an Existing Meeting """

    if form is None:
        flash('error Invalid Request to Delete Meeting.')
        return redirect(request.args.get('next') or url_for('meetings.home'))

    delete_form = MeetingDeleteForm(form)

    if not delete_form.validate():
        flash('error Could not Delete Meeting, Please Try Again.')
        return redirect(request.args.get('next') or url_for('meetings.home'))

    try:
        user = current_user._get_current_object()
        meeting = Meeting.objects.get(id=delete_form.meeting_id.data)

        members = meeting.members
        owner = meeting.owner

        # user is not the owner of the group and cannot delete
        if user != owner:
            flash('error You do not have Permission to Delete this Meeting.')
            return redirect(url_for('meetings.home'))

        # remove the meeting from each member's list of meeting
        for member in members:
            if meeting in member.meetings:
                member.meetings.remove(meeting)
                member.meeting_count = member.meeting_count - 1
                member.save()

        # remove meeting from owner's list of meetings
        if meeting in owner.meetings:
            owner.meetings.remove(meeting)
            owner.save()

        for group in user.groups:
            if meeting in group.meetings:
                group.meetings.remove(meeting)
                group.save();

        meeting.delete()
        flash('success Meeting Successfully Deleted.')

    except Exception as e:
        flash('error An Error has Occured, Please Try Again.'
              '{}'.format(str(e)))

    return redirect(request.args.get('next') or url_for('meetings.home'))


@meetings.route('/edit/<id>', methods=['GET', 'POST'])
@login_required
def edit_meeting(id):
    if len(id) != 24 or not all(c in string.hexdigits for c in id):
        flash('error Invalid Meeting Id.')
        return redirect(request.args.get('next') or url_for('meetings.home'))

    try:
        meeting = Meeting.objects.get(id=id)
        user = current_user._get_current_object()

        if user not in meeting.members:
            flash('error You are not a member of that meeting.')
            return redirect(url_for('meetings.meetings_page'))

        return render_template('transcripts/transcripts.html', meeting=meeting)
    except Exception as e:
        flash('error An Error Occured. {}'.format(str(e)))
        return redirect(request.args.get('next') or url_for('meetings.home'))


@meetings.route('/search=<string:query>', methods=['GET', 'POST'])
@login_required
def search_meetings(query):
    """ Displays the Meetings to the User's Dashboard that match the given
        criteria """

    if request.method == 'POST':
        return filter_form(request.form)

    meetings = current_user._get_current_object().meetings
    search = query.split(" ")

    # search is too expensive
    if len(search) > 20:
        flash('error Could not fulfill search request.')
        return redirect(request.args.get('next') or url_for('meetings.home'))

    # get the list of users to search for
    users = list(filter(lambda x: "@" in x, search))

    # get the list of tags to search for
    tags = list(filter(lambda x: "#" in x, search))

    # get the other search criteria
    search = list(set(search) - set(users) - set(tags))

    # filter the meetings to only contain meetings with desired tags
    for t in tags:
        try:
            t = t.lower()
            meetings = list(filter(lambda x: t[1:] in
                                   " ".join(x.tags).split(" "), meetings))

        except Exception as e:
            return render_template('meetings.home', meetings=[])

    # filter the meetings to only contain meetings with desired members
    for u in users:
        try:
            user = User.objects.get(email=u[1:])
            meetings = list(filter(lambda x: user in x.members, meetings))
        except Exception as e:
            return render_template('meetings.home', meetings=[])

    # filter the meetings to only contain meetings with the desired text
    for c in search:
        meetings = list(filter(
            lambda x: c.lower() in x.name.lower(), meetings))

    # reset the page and only show the desired meetings
    return render_template('meeting/dashboard.html', meetings=meetings)


@meetings.route('/info/<string:meeting_id>', methods=['GET'])
@login_required
def meeting_info(meeting_id):
    if len(meeting_id) != 24 or \
       not all(c in string.hexdigits for c in meeting_id):
        flash('error Invalid Meeting Id.')
        return redirect(request.args.get('next') or
                        url_for('meeting.meetings_page'))

    try:
        meeting = Meeting.objects.get(id=meeting_id)
        user = current_user._get_current_object()

        if user not in meeting.members:
            flash('error You Are Not a Member of That Meeting.')
            return redirect(url_for('meetings.meetings_page'))

        return jsonify(meeting)
    except Exception as e:
        flash('error An Error Occured')
        return redirect(request.args.get('next') or url_for('meetings.home'))


@meetings.route('/<meeting_id>/tags', methods=['GET'])
@login_required
def get_tags(meeting_id):
    """ generates topics for the meeting with the given id """
    meeting = Meeting.objects.with_id(meeting_id)
    string = meeting.transcriptText.replace("\n", " ")
    r = Rake()  # initializes Rake with English (all punc) as default lang
    r.extract_keywords_from_text(string)

    topic_data = r.get_ranked_phrases_with_scores()
    count = 0
    data = []
    for topic in topic_data:
        if topic[0] < 5 or count == 10:
            break
        else:
            data.append(str(topic[1]))
            count = count + 1

    return_data = " ".join(data).split(" ")
    meeting.topics = return_data
    meeting.tags = return_data
    meeting.save()
    return redirect(url_for('meetings.edit_meeting', id=meeting_id))

@meetings.route('/<meeting_id>/updateTranscript', methods=['POST'])
def update_transcript(meeting_id):
    if request.form is None:
        print('Form is invalid')

    transcript = request.form['transcript']

    if transcript is None:
        return json.dumps({'error': 'invalid transcript'})

    meeting = Meeting.objects.get(id=meeting_id)
    meeting.transcriptText = transcript
    meeting.save()

    return json.dumps({'status': 'success'})


@meetings.route('/<meeting_id>/updateTags', methods=['POST'])
def update_tags(meeting_id):
    if request.form is None:
        print('Form is invalid')

    tags = request.form['tags']

    if tags is None:
        return json.dumps({'error': 'invalid tags'})

    meeting = Meeting.objects.get(id=meeting_id)
    meeting.tags = tags.split(" ")
    meeting.save()

    return json.dumps({'status': 'success'})

@meetings.route('/<meeting_id>/updateTranscriptGrammar', methods=['GET'])
@login_required
def update_grammar(meeting_id):
    meeting = Meeting.objects.with_id(meeting_id)
    string = meeting.transcriptText.replace("\n", " ")

    #punctuation = re.compile(r'[-,":;()\']')
    punctuation = ["'","’","!","?",".",",","—","\""]
    exclude = set(punctuation)
    tokens =word_tokenize(string)
    tokens = [w.lower() for w in tokens]
    #print(tokens)
    #tokens = "".join(ch+" " for ch in tokens if ch not in punctuation)
    retStr = ""

    for tok in tokens:
        if tok not in punctuation: # != "’" || tok != "'":
            retStr += (tok)
            retStr += " "
        else:
            if tok == "'" or tok == "\"" or tok == "’":
                #print(tok)
                retStr = retStr[:-1]


    meeting.transcriptText = retStr
    meeting.save()

    return redirect(url_for('meetings.edit_meeting', id=meeting_id))
