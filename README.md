# healthcare-operations-optimization

Web-based queue management system for healthcare facilities


## Project Overview  
This is a web-based prototype built to digitize appointment booking, queue tracking, and doctor availability in a local healthcare setup. The goal is to reduce manual operations and streamline patient experience.

Developed by: **Shubhangi Pulgurti**  
Degree: **BBA Business Analytics**  
Completion: **May 2025**

---

## Business Challenge  
The healthcare facility previously relied on manual appointment books and in-person queues. This caused:
- Long patient wait times
- No real-time queue updates
- Poor communication about doctor availability
- Inefficient rescheduling of conflicting appointments

---

## Solution Delivered  
- Patient-facing appointment booking web form  
- Live queue display that updates in real-time  
- Doctor dashboard with control panel to start, pause, or reset the queue  
- Status toggles like *start appointments*, *In Emergency*, *In Rounds*  
- Automatic rescheduling for duplicate bookings  
- Fully responsive (mobile, desktop compatibility)  
- Local file storage (CSV/JSON) for data management  
- Sunday-skip logic & dynamic next working day tracker  
- Motivational quote banner display  

---

## Tech Stack  
- **Frontend:** HTML, CSS, JavaScript  
- **Backend:** Python Flask  
- **Data Storage:** File-based (CSV, JSON, TXT)  
- **Hosting:** Localhost (for demo purposes)  
- **License:** MIT (Can be changed if needed)

---

## Key Features

| Feature | Description |
|--------|-------------|
| Appointment Booking | Patient form collects name, phone, department |
| Confirmation Page | Shows token and follow-up message |
| Doctor Dashboard | Live queue control, status toggles |
| Live Queue Display | Patients can track their position |
| Rescheduling Logic | Prevents booking conflicts |
| Device Compatibility | Responsive on all screen sizes |

---

## Business Impact  
- Eliminated manual appointment logs  
- Reduced patient confusion during peak hours  
- Improved doctor-patient communication  
- Increased trust via real-time updates  
- Reduced front-desk workload during emergencies

---

## Getting Started  

### Installation

```bash
git clone https://github.com/Shubhangi0831/healthcare-operations-optimization
cd healthcare-operations-optimization/src
pip install flask
python app.py
