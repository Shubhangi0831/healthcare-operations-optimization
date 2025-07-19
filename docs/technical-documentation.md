# Technical Documentation

## System Overview

Flask-based web application to manage hospital appointments and real-time patient queues. Frontend and backend logic were developed using AI assistance and deployed locally as a prototype.

## Components

### Patient Interface
- Book appointments
- Track queue position
- Receive confirmation

### Doctor Dashboard
- View appointments
- Mark queue as started
- Set status (In Surgery, Rounds, Available)
- Reset queue

## Architecture

- **Frontend**: HTML, CSS, JS (Patient + Doctor)
- **Backend**: Python Flask
- **Data Layer**: CSV + JSON file storage

## File Structure

- `app.py` — Main Flask app
- `templates/` — All HTML pages
- `static/` — Images and CSS
- `appointments.csv` — Booking data
- `status.json` — Doctor status
- `queue_status.txt`, `last_reset.txt`, etc. — Queue control logic

## Key Logic

- Validates phone number length
- Detects duplicate bookings
- Tracks current vs next batch
- Updates doctor status and resets queue

## Features Implemented

- Real-time queue display
- Emergency status control
- Reschedule flow with pre-filled data
- Mobile-compatible responsive UI

## Limitations

- File-based (not scalable for large systems)
- No SMS/email notifications yet
- No login/authentication in prototype

## Future Enhancements

- Cloud database integration
- SMS alert system
- Admin portal for reports
