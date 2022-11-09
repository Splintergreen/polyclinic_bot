from dataclasses import dataclass
# from datetime import datetime


@dataclass
class RequestData:
    first_name: str = ''
    last_name: str = ''
    patient_birthday: str = ''
    patient_id: str = ''
    speciality_id: str = ''
    clinic_id: str = '403'
    doctor_id: str = ''
    selected_time: str = ''
    # date_list:list[datetime] = []

    def patient_data(self):
        patient_data = {
            "patient_form-first_name": self.first_name,
            "patient_form-last_name": self.last_name,
            "patient_form-birthday": self.patient_birthday,
            "patient_form-clinic_id": self.clinic_id
        }
        return patient_data

    def speciality_data(self):
        speciality_data = {
            "clinic_form-clinic_id": self.clinic_id,
            "clinic_form-patient_id": self.patient_id
        }
        return speciality_data
    def doctor_data(self):
        doctor_data = {
            "speciality_form-speciality_id": self.speciality_id,
            "speciality_form-clinic_id": self.clinic_id,
            "speciality_form-patient_id": self.patient_id
        }
        return doctor_data
    def appointment_data(self):
        appointment_data = {
            "doctor_form-doctor_id": self.doctor_id,
            "doctor_form-clinic_id": self.clinic_id,
            "doctor_form-patient_id": self.patient_id
        }
        return appointment_data