from flask import Flask, render_template, request, redirect, flash, session
import csv
import os
import json
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'sudha_hospital_secure_123!'

STATUS_FILE = 'status.json'
CSV_FILE = 'appointments.csv'


def get_next_working_day(current_date_str):
    current_date = datetime.strptime(current_date_str, '%Y-%m-%d')
    next_day = current_date + timedelta(days=1)
    while next_day.weekday() == 6:  # Sunday = 6
        next_day += timedelta(days=1)
    return next_day.strftime('%Y-%m-%d')



def read_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, 'r') as f:
            return json.load(f)
    return {"emergency": False, "rounds": False, "weekend": False}

def update_status(mode, value):
    status = read_status()
    status[mode] = value
    with open(STATUS_FILE, 'w') as f:
        json.dump(status, f)

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/doctor')
def doctor_dashboard():
    current_status = read_status()
    status_message = ""
    if current_status.get("emergency"):
        status_message += "🚨 Emergency mode is active. "
    if current_status.get("rounds"):
        status_message += "🔄 Rounds mode is active. "
    if current_status.get("weekend"):
        status_message += "💤 Sunday mode is active."

    try:
        with open('last_reset.txt', 'r') as f:
            last_reset = f.read()
    except FileNotFoundError:
        last_reset = "Never"

    return render_template('doctor.html', status=current_status, status_message=status_message, last_reset=last_reset)

@app.route('/activate/<mode>', methods=['POST'])
def activate_mode(mode):
    if mode in ["emergency", "rounds", "weekend"]:
        current_status = read_status()
        update_status(mode, not current_status.get(mode, False))
    return redirect('/doctor')

@app.route('/reset-queue', methods=['POST'])
def reset_queue():
    # 1. Clear current batch (appointments in progress)
    with open('current_batch.txt', 'w') as f:
        f.write('')

    # 2. Reset token status to empty or 1
    with open('queue_status.txt', 'w') as f:
        f.write('1')  # or '' if you want it empty

    # 3. Reset status.json if needed (live mode or queue progress)
    with open('status.json', 'w') as f:
        json.dump({"status": "not_started", "current_token": ""}, f)

    # 4. Update reset time
    with open('reset_timestamp.txt', 'w') as f:
        f.write(datetime.now().strftime('%Y-%m-%d %I:%M %p'))

    flash("✅ Queue reset successfully.", "success")
    return redirect('/doctor')


@app.route('/appointment', methods=['GET', 'POST'])
def appointment():
    if request.method == 'POST':
        name = request.form['name'].strip()
        age = request.form['age'].strip()
        phone = request.form['phone'].strip()
        if not phone.isdigit() or len(phone) != 10:
            return render_template('error.html', message="❌ Please enter a valid 10-digit phone number.")
        reason = request.form['reason'].strip()

        appt_date = datetime.now() + timedelta(days=1)
        while appt_date.weekday() == 6:
            appt_date += timedelta(days=1)
        appt_date = appt_date.strftime('%Y-%m-%d')

        try:
            with open('current_batch.txt', 'r') as f:
                batch_id = f.read().strip()
        except FileNotFoundError:
            batch_id = "default"

        try:
            with open('appointments.csv', newline='') as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) >= 8 and row[1] == name and row[3] == phone and row[6] == appt_date and row[7] == batch_id:
                        return render_template('confirmation.html', name=name, token=None, timeslot=None, appointment_date=appt_date, duplicate=True)
        except FileNotFoundError:
            pass

        token = 1
        try:
            with open('appointments.csv', newline='') as file:
                rows = [row for row in csv.reader(file) if len(row) >= 8 and row[6] == appt_date and row[7] == batch_id]
                token = len(rows) + 1
        except FileNotFoundError:
            pass

        base_time = datetime(2025, 1, 1, 9, 0)
        slot_start = base_time + timedelta(minutes=(token - 1) * 15)
        slot_end = slot_start + timedelta(minutes=15)
        timeslot = f"{slot_start.strftime('%I:%M %p')} - {slot_end.strftime('%I:%M %p')}"

        with open('appointments.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([token, name, age, phone, reason, timeslot, appt_date, batch_id])

        return render_template('confirmation.html', name=name, token=token, phone=phone, timeslot=timeslot, appointment_date=appt_date, duplicate=False)

    return render_template('appointment.html')

@app.route('/next-patient', methods=['POST'])
def next_patient():
    # Read current batch ID
    try:
        with open('current_batch.txt', 'r') as f:
            current_batch = f.read().strip()
    except FileNotFoundError:
        current_batch = "default"

    # Get appointments for the current batch only (ignore date)
    try:
        with open('appointments.csv', newline='') as file:
            reader = csv.reader(file)
            appointments = [row for row in reader if len(row) >= 8 and row[7].strip() == current_batch]
    except FileNotFoundError:
        appointments = []

    # Get current token position
    try:
        with open('queue_status.txt', 'r') as file:
            current = int(file.read())
    except:
        current = 0

    # Check if we reached end
    if current >= len(appointments):
        return render_template('current_patient.html', current=current, message="There is no patient next.")
    else:
        current += 1
        with open('queue_status.txt', 'w') as file:
            file.write(str(current))
        return redirect('/current-patient')

@app.route('/current-patient')
def current_patient():
    # Read current batch ID
    try:
        with open('current_batch.txt', 'r') as f:
            current_batch = f.read().strip()
    except FileNotFoundError:
        current_batch = "default"

    # Get appointments for the current batch
    try:
        with open('appointments.csv', newline='') as file:
            reader = csv.reader(file)
            appointments = [row for row in reader if len(row) >= 8 and row[7].strip() == current_batch]
    except FileNotFoundError:
        appointments = []

    # Get current token
    try:
        with open('queue_status.txt', 'r') as file:
            current = int(file.read())
    except:
        current = 0

    if 0 < current <= len(appointments):
        patient = appointments[current - 1]
        name = patient[1]
        age = patient[2]
        phone = patient[3]
        reason = patient[4]
        time = patient[5]
        message = ""
    else:
        name = age = phone = reason = time = ""
        message = "There is no patient next."

    return render_template('current_patient.html', current=current, name=name, age=age, reason=reason, time=time, message=message)

@app.route('/view-appointments') 
def view_appointments():
    try:
        with open('current_batch.txt', 'r') as f:
            current_batch = f.read().strip()
    except FileNotFoundError:
        current_batch = "default"

    appointments_by_date = {}
    legacy_appointments_by_date = {}

    try:
        with open('appointments.csv', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                print("ROW:", row)  # 🟡 For debugging
                if len(row) >= 8:
                    date = row[6].strip()
                    batch = row[7].strip()
                    if batch == current_batch:
                        appointments_by_date.setdefault(date, []).append(row)
                    else:
                        legacy_appointments_by_date.setdefault(date, []).append(row)
    except FileNotFoundError:
        appointments_by_date = {}
        legacy_appointments_by_date = {}

    # Sort both sections (most recent date first)
    appointments_by_date = dict(sorted(appointments_by_date.items(), reverse=True))
    legacy_appointments_by_date = dict(sorted(legacy_appointments_by_date.items(), reverse=True))

    return render_template(
        'view_appointments.html',
        appointments=appointments_by_date,
        legacy_appointments=legacy_appointments_by_date
    )

@app.route('/track-token', methods=['GET', 'POST'])
def track_token():
    status_message = ""
    message = ""
    estimated_time = ""

    try:
        with open('queue_status.txt', 'r') as f:
            current = int(f.read())
    except:
        current = 0

    today = datetime.now().strftime('%Y-%m-%d')

    try:
        with open('current_batch.txt', 'r') as f:
            current_batch = f.read().strip()
    except FileNotFoundError:
        current_batch = "default"

    try:
        with open('appointments.csv', newline='') as file:
            appointments = [
                row for row in csv.reader(file)
                if len(row) >= 8 and row[7] == current_batch
            ]
    except:
        appointments = []

    status = read_status()

    # 🔢 FORM PROCESSING
    if request.method == 'POST':
        token = request.form.get('token').strip()  # Strip spaces
        found = False

        for idx, row in enumerate(appointments):
            if row[0] == token:
                found = True
                appointment_date = row[6]

                if appointment_date > today:
                    message = f"📅 Your appointment is on {appointment_date}. Please check back that day to track your token."
                elif appointment_date == today:
                    if idx < current:
                        message = "✅ Your turn is already over."
                    elif idx == current:
                        message = "🎉 It's your turn now!"
                    else:
                        message = f"⏳ There are {idx - current} patient(s) ahead of you."
                        estimated_time = f"⏱️ Estimated wait time: {(idx - current) * 15} minutes."
                else:
                    message = "⚠️ This token is from a past appointment."
                break

        if not found:
            status_message = "⚠️ Invalid token number. Please check your confirmation or try again."

    # 🔁 Show estimated queue wait time
    estimated_wait_time = ""
    if not any(status.values()):  # not emergency/rounds/weekend
        # Show only today's appointments for wait time estimation
        today_appointments = [row for row in appointments if row[6] == today]
        remaining = len(today_appointments) - current
        if remaining > 0:
            estimated_wait_time = f"⏱️ Estimated wait: {remaining * 15} minutes."
        else:
            estimated_wait_time = "✅ No one in queue right now."

    # 💬 Motivational quote for live queue section
    quotes = [
        "Patience is also a form of action.",
        "Healing takes time — and you’re on your way!",
        "Good things come to those who wait.",
        "Take a deep breath. You’re doing great.",
        "You're one step closer to getting better!"
    ]
    import random
    quote = random.choice(quotes)

    return render_template('track_token.html',
                           message=message,
                           estimated_time=estimated_time,
                           status_message=status_message,
                           current=current,
                           status=status,
                           estimated_wait_time=estimated_wait_time,
                           quote=quote)



@app.route('/live-queue')
def live_queue():
    try:
        with open('queue_status.txt', 'r') as f:
            current = int(f.read())
    except:
        current = 0

    today = datetime.now().strftime('%Y-%m-%d')

    try:
        with open('current_batch.txt', 'r') as f:
            current_batch = f.read().strip()
    except FileNotFoundError:
        current_batch = "default"

    try:
        with open('appointments.csv', newline='') as file:
            appointments = [
                row for row in csv.reader(file)
                if len(row) >= 8 and row[6] == today and row[7] == current_batch
            ]
    except:
        appointments = []

    status = read_status()

    # Estimate wait time dynamically
    estimated_wait_time = ""
    if not any(status.values()):  # If doctor is not in emergency/rounds/weekend
        remaining = len(appointments) - current
        if remaining > 0:
            estimated_wait_time = f"⏱️ Estimated wait: {remaining * 15} minutes (subject to delay)."
        else:
            estimated_wait_time = "✅ No one in queue right now."

    quotes = [
        "Patience is also a form of action.",
        "Healing takes time — and you’re on your way!",
        "Good things come to those who wait.",
        "Take a deep breath. You’re doing great.",
        "You're one step closer to getting better!"
    ]
    import random
    quote = random.choice(quotes)
    print("Selected Quote:", quote)

    return render_template('live_queue.html',
                           appointments=appointments,
                           current=current,
                           status=status,
                           estimated_wait_time=estimated_wait_time,
                           quote=quote)


@app.route('/clear-appointments', methods=['POST'])
def clear_appointments():
    with open('appointments.csv', 'w') as file:
        file.truncate()
    return redirect('/view-appointments')

@app.route('/reschedule', methods=['GET', 'POST']) 
def reschedule():
    if request.method == 'GET':
        token = request.args.get('token')
        phone = request.args.get('phone')

        #use appointment date directly from query string
        appointment_date = request.args.get('appt_date')

        if not token or not phone or not appointment_date:
            return render_template('error.html', message="❌ Missing required data to reschedule.")

        return render_template('reschedule.html',
                               token=token,
                               phone=phone,
                               appointment_date=appointment_date)
    
    # --- POST: Reschedule logic ---
    token = request.form['token']
    phone = request.form['phone']

    updated = False
    updated_rows = []

    next_day = datetime.now() + timedelta(days=1)
    while next_day.weekday() == 6:
        next_day += timedelta(days=1)
    appt_date = next_day.strftime('%Y-%m-%d')

    try:
        with open('current_batch.txt', 'r') as f:
            batch_id = f.read().strip()
    except FileNotFoundError:
        batch_id = "default"

    try:
        with open('appointments.csv', newline='') as file:
            reader = csv.reader(file)
            all_rows = list(reader)
    except FileNotFoundError:
        all_rows = []

    new_token = 1 + sum(1 for row in all_rows if len(row) >= 8 and row[6] == appt_date and row[7] == batch_id)

    for row in all_rows:
        if len(row) >= 8 and row[0] == token and row[3] == phone:
            row[6] = appt_date
            row[0] = str(new_token)
            base_time = datetime(2025, 1, 1, 9, 0)
            slot_start = base_time + timedelta(minutes=(new_token - 1) * 15)
            slot_end = slot_start + timedelta(minutes=15)
            row[5] = f"{slot_start.strftime('%I:%M %p')} - {slot_end.strftime('%I:%M %p')}"
            updated = True
        updated_rows.append(row)

    if updated:
        with open('appointments.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(updated_rows)

        return render_template('confirmation.html', name="Patient", token=new_token,
                               timeslot=row[5], appointment_date=appt_date, duplicate=False)
    else:
        return render_template('error.html', message="❌ Error: Could not find a matching appointment to reschedule. please try again or contact the hospital.")


@app.route('/view-confirmation', methods=['POST'])
def view_confirmation():
    phone = request.form.get('phone')
    if not phone:
        return "Error: Phone number is required"

    appointment = None
    with open('appointments.csv', newline='') as file:
        reader = csv.reader(file)
        for row in reversed(list(reader)):
            if len(row) >= 4 and row[3] == phone:
                appointment = row
                break

    if not appointment:
        return "Error: Could not find matching appointment."

    name = appointment[1]
    token = appointment[0]
    timeslot = appointment[5]
    appt_date = appointment[6]

    return render_template(
        'confirmation.html',
        name=name,
        token=token,
        phone=phone,
        timeslot=timeslot,
        appointment_date=appt_date,
        duplicate=False
    )

from flask import flash, redirect, url_for

@app.route('/confirm-reschedule', methods=['POST'])
def confirm_reschedule():
    token = request.form['token'].strip()
    phone = request.form['phone'].strip()
    date = request.form['date'].strip()

    print("📥 Received from form:")
    print("Token:", repr(token))
    print("Phone:", repr(phone))
    print("Date:", repr(date))

    updated_rows = []
    match_found = False

    with open('appointments.csv', 'r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) >= 7:
                row_token = row[0].strip()
                row_name = row[1].strip()
                row_phone = row[3].strip()
                row_date = row[6].strip()

                print("🔍 Checking row:")
                print("→ Token:", repr(row_token))
                print("→ Phone:", repr(row_phone))
                print("→ Date :", repr(row_date))

                if row_token == token and row_phone == phone and row_date == date:
                    match_found = True
                    new_token = row_token
                    name = row_name
                    new_phone = row_phone
                    new_timeslot = row[5].strip()
                    new_date = get_next_working_day(date)

                    row[6] = new_date
                    row[5] = new_timeslot  # update if timeslot changes

            updated_rows.append(row)

    if match_found:
        with open('appointments.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(updated_rows)

        return render_template('confirmation.html',
                               name=name,
                               token=new_token,
                               phone=new_phone,
                               timeslot=new_timeslot,
                               appointment_date=new_date,
                               duplicate=False)
    else:
        return render_template('error.html',
                               message="❌ Error: Could not find matching appointment.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

