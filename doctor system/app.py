from flask import Flask, render_template, request, jsonify
import threading
import time
import random
from queue import Queue

app = Flask(__name__)

# Shared resources
MAX_SLOTS = 5
available_slots = MAX_SLOTS
appointment_book = [0] * MAX_SLOTS

# Synchronization primitives
slots_semaphore = threading.Semaphore(MAX_SLOTS)
book_mutex = threading.Lock()
appointment_queue = Queue()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/book_appointment', methods=['POST'])
def book_appointment():
    patient_id = request.form.get('patient_id')
    
    if not patient_id:
        return jsonify({'error': 'Patient ID is required'}), 400
    
    # Create a new thread for each patient
    t = threading.Thread(target=process_appointment, args=(patient_id,))
    t.start()
    
    return jsonify({'message': 'Appointment request received'})

def process_appointment(patient_id):
    global available_slots
    
    print(f"Patient {patient_id} is trying to book an appointment...")
    
    # Wait for available slot
    slots_semaphore.acquire()
    
    # Critical section - access appointment book
    with book_mutex:
        # Book appointment
        for i in range(MAX_SLOTS):
            if appointment_book[i] == 0:
                appointment_book[i] = patient_id
                print(f"Patient {patient_id} booked slot {i+1}")
                break
    
    # Simulate consultation time
    consultation_time = random.randint(1, 3)
    time.sleep(consultation_time)
    
    # Release the slot after consultation
    with book_mutex:
        for i in range(MAX_SLOTS):
            if appointment_book[i] == patient_id:
                appointment_book[i] = 0
                print(f"Patient {patient_id} consultation completed. Slot {i+1} freed.")
                break
    
    slots_semaphore.release()

@app.route('/get_appointments')
def get_appointments():
    with book_mutex:
        return jsonify({'appointments': appointment_book})

if __name__ == '__main__':
    app.run(debug=True)