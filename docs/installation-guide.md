# Installation & Setup Guide

## Prerequisites

- Python 3.7+
- Flask installed (`pip install flask`)
- Local machine with internet browser

## Steps

1. Clone the repo:
- git clone https://github.com/Shubhangi0831/healthcare-operations-optimization

2. Navigate to `src/`:
- cd healthcare-operations-optimization/src

3. Run the app:
- python app.py

4. Access the patient portal:
- http://127.0.0.1:5000/

5. Access the doctor dashboard:
- http://127.0.0.1:5000/doctor

## For Patients

- Fill appointment form
- Note token/confirmation
- Track queue status

## For Doctors

- View all appointments
- Click “Start Queue”
- Advance to next patient
- Update doctor status

## Troubleshooting

- Ensure `appointments.csv`, `status.json`, etc. are present
- Avoid booking with invalid phone numbers
- Keep JSON/CSV structure consistent

## Notes

- This is a local prototype, not deployed online
- Designed for demonstration purposes
