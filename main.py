import json
import os
from datetime import datetime

import kivy
from kivy.metrics import sp
kivy.require("2.1.0")

# For testing on a portrait mobile device (optional)
from kivy.core.window import Window
Window.size = (360, 640)

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.core.text import Label as CoreLabel

# ---------- THEME COLORS ----------
PRIMARY_COLOR = (0.2, 0.6, 0.8, 1)       # Blue for buttons/highlights
BACKGROUND_COLOR = (0.95, 0.95, 0.95, 1)  # Light grey background
TEXT_COLOR = (0.1, 0.1, 0.1, 1)           # Dark text

# ---------- Responsive Label ----------
BASELINE_WIDTH = 900.0  # Baseline for scaling text

class ResponsiveLabel(Label):
    def __init__(self, base_font_size=16, **kwargs):
        super().__init__(**kwargs)
        self.base_font_size = base_font_size
        Clock.schedule_once(lambda dt: self.update_font(), 0)
        Window.bind(size=self.on_window_resize)
    def on_window_resize(self, window, size):
        self.update_font()
    def update_font(self, *args):
        self.font_size = sp(self.base_font_size * Window.width / BASELINE_WIDTH)

# ---------- Responsive Spinner ----------
class ResponsiveSpinner(Spinner):
    def __init__(self, base_font_size=16, **kwargs):
        super().__init__(**kwargs)
        self.base_font_size = base_font_size
        Clock.schedule_once(lambda dt: self.update_font(), 0)
        Window.bind(size=self.on_window_resize)
    def on_window_resize(self, window, size):
        self.update_font()
    def update_font(self, *args):
        self.font_size = sp(self.base_font_size * Window.width / BASELINE_WIDTH)

# ---------- STYLED BOX ----------
class StyledBox(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*BACKGROUND_COLOR)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)
    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos

# ---------- AUTO-EXPANDING TEXTINPUT ----------
class AutoExpandingTextInput(TextInput):
    def __init__(self, min_height=100, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("multiline", True)
        self.min_height = min_height
        super().__init__(**kwargs)
        Clock.schedule_once(lambda dt: self.update_height(), 0)
        self.bind(text=self.update_height, width=self.update_height)
    def update_height(self, *args):
        core_label = CoreLabel(text=self.text or " ", font_size=self.font_size, width=self.width, multiline=True)
        core_label.refresh()
        if core_label.texture:
            new_height = core_label.texture.size[1] + 20
        else:
            new_height = self.min_height
        self.height = max(self.min_height, new_height)

# ---------- SINGLE FIELD ----------
class SingleField(BoxLayout):
    """
    Displays a field with a label on top and an input widget (TextInput or Spinner) below.
    The parameter 'readonly' (default False) makes the input unchangeable.
    """
    def __init__(self, label_text, multiline=False, input_filter=None, spinner_values=None,
                 height_for_multiline=None, readonly=False, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = 5
        self.size_hint_y = None
        self.bind(minimum_height=self.setter("height"))
        label = ResponsiveLabel(text=label_text, base_font_size=18, color=TEXT_COLOR,
                                size_hint_y=None, height=30)
        self.add_widget(label)
        if spinner_values:
            self.input_widget = Spinner(text=spinner_values[0], values=spinner_values,
                                        size_hint_y=None, height=40)
            if readonly:
                self.input_widget.disabled = True
        else:
            if multiline:
                self.input_widget = AutoExpandingTextInput(min_height=height_for_multiline if height_for_multiline else 100)
            else:
                self.input_widget = TextInput(multiline=False, size_hint_y=None, height=40)
            if input_filter:
                self.input_widget.input_filter = input_filter
            if readonly:
                self.input_widget.readonly = True
        self.add_widget(self.input_widget)

# ---------- FORM CARD ----------
class FormCard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 20
        self.spacing = 20
        self.size_hint_x = 1
        self.size_hint_y = None
        self.bind(minimum_height=self.setter("height"))
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)
    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos

# ---------- PATIENT MEDICAL FORM (Add Patient) ----------
class PatientMedicalForm(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = 15
        self.size_hint_y = None
        self.bind(minimum_height=self.setter("height"))
        # 1. Name
        self.field_name = SingleField("Name:", multiline=False)
        self.add_widget(self.field_name)
        # 2. Mobile No (only numbers)
        self.field_mobile = SingleField("Mobile No:", multiline=False, input_filter='int')
        self.add_widget(self.field_mobile)
        # 3. Date (auto-filled, read-only)
        self.field_date = SingleField("Date:", multiline=False)
        self.field_date.input_widget.text = datetime.now().strftime("%Y-%m-%d")
        self.field_date.input_widget.readonly = True
        self.add_widget(self.field_date)
        # 4. Adress
        self.field_adress = SingleField("Adress:", multiline=True, height_for_multiline=100)
        self.add_widget(self.field_adress)
        # 5. Gender (dropdown)
        self.field_gender = SingleField("Gender:", spinner_values=["Male", "Female", "Other"])
        self.add_widget(self.field_gender)
        # 6. Weight
        self.field_weight = SingleField("Weight:", multiline=False, input_filter='float')
        self.add_widget(self.field_weight)
        # 7. Systolic BP
        self.field_systolic = SingleField("Systolic BP:", multiline=False, input_filter='int')
        self.add_widget(self.field_systolic)
        # 8. Diastolic BP
        self.field_diastolic = SingleField("Diastolic BP:", multiline=False, input_filter='int')
        self.add_widget(self.field_diastolic)
        # 9. Pulse Rate
        self.field_pulse = SingleField("Pulse Rate:", multiline=False, input_filter='int')
        self.add_widget(self.field_pulse)
        # 10. Surgery (dropdown, default "No")
        self.field_surgery = SingleField("Surgery:", spinner_values=["No", "Yes"])
        self.field_surgery.input_widget.text = "No"
        self.add_widget(self.field_surgery)
        # 11. Surgery Description (always visible)
        self.field_surgery_desc = SingleField("Surgery Description:", multiline=True, height_for_multiline=100)
        # Bind surgery spinner changes
        self.field_surgery.input_widget.bind(text=self.on_surgery_change)
        # Call once to set initial state (default "No" makes it read-only and clears text)
        self.on_surgery_change(self.field_surgery.input_widget, self.field_surgery.input_widget.text)
        self.add_widget(self.field_surgery_desc)
        # 12. Medical History
        self.field_medical_history = SingleField("Medical History:", multiline=True, height_for_multiline=200)
        self.add_widget(self.field_medical_history)
        # 13. Diseases
        self.field_diseases = SingleField("Diseases:", multiline=True, height_for_multiline=100)
        self.add_widget(self.field_diseases)
        # 14. Medicines
        self.field_medicines = SingleField("Medicines:", multiline=True, height_for_multiline=100)
        self.add_widget(self.field_medicines)
        # 15. Extra
        self.field_extra = SingleField("Extra:", multiline=True, height_for_multiline=200)
        self.add_widget(self.field_extra)
        # 16. Other Illnesses
        self.field_other_illnesses = SingleField("Other Illnesses:", multiline=False)
        self.add_widget(self.field_other_illnesses)
        # 17. Other Medicines
        self.field_other_medicines = SingleField("Other Medicines:", multiline=True, height_for_multiline=100)
        self.add_widget(self.field_other_medicines)
        # 18. Next Appointment Date
        self.field_next_appointment = SingleField("Next Appointment Date:", multiline=False)
        self.add_widget(self.field_next_appointment)

    def on_surgery_change(self, instance, value):
        if value.strip().lower() == "yes":
            self.field_surgery_desc.input_widget.readonly = False
        else:
            self.field_surgery_desc.input_widget.text = ""
            self.field_surgery_desc.input_widget.readonly = True
        if self.field_surgery_desc.parent:
            self.field_surgery_desc.parent.do_layout()

    def clear_fields(self):
        self.field_name.input_widget.text = ""
        self.field_mobile.input_widget.text = ""
        self.field_date.input_widget.text = datetime.now().strftime("%Y-%m-%d")
        self.field_adress.input_widget.text = ""
        self.field_gender.input_widget.text = "Male"
        self.field_weight.input_widget.text = ""
        self.field_systolic.input_widget.text = ""
        self.field_diastolic.input_widget.text = ""
        self.field_pulse.input_widget.text = ""
        self.field_surgery.input_widget.text = "No"
        self.field_surgery_desc.input_widget.text = ""
        self.field_surgery_desc.input_widget.readonly = True
        self.field_medical_history.input_widget.text = ""
        self.field_diseases.input_widget.text = ""
        self.field_medicines.input_widget.text = ""
        self.field_extra.input_widget.text = ""
        self.field_other_illnesses.input_widget.text = ""
        self.field_other_medicines.input_widget.text = ""
        self.field_next_appointment.input_widget.text = ""

    def get_patient_data(self):
        return {
            "name": self.field_name.input_widget.text,
            "mobile_no": self.field_mobile.input_widget.text,
            "date": self.field_date.input_widget.text,
            "adress": self.field_adress.input_widget.text,
            "gender": self.field_gender.input_widget.text,
            "weight": self.field_weight.input_widget.text,
            "systolic_bp": self.field_systolic.input_widget.text,
            "diastolic_bp": self.field_diastolic.input_widget.text,
            "pulse_rate": self.field_pulse.input_widget.text,
            "surgery": self.field_surgery.input_widget.text,
            "surgery_description": self.field_surgery_desc.input_widget.text,
            "medical_history": self.field_medical_history.input_widget.text,
            "diseases": self.field_diseases.input_widget.text,
            "medicines": self.field_medicines.input_widget.text,
            "extra": self.field_extra.input_widget.text,
            "other_illnesses": self.field_other_illnesses.input_widget.text,
            "other_medicines": self.field_other_medicines.input_widget.text,
            "next_appointment_date": self.field_next_appointment.input_widget.text
        }

# ---------- PATIENT MEDICAL FORM VIEW (Read-only) ----------
class PatientMedicalFormView(BoxLayout):
    def __init__(self, patient_data, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = 15
        self.size_hint_y = None
        self.bind(minimum_height=self.setter("height"))
        self.field_name = SingleField("Name:", multiline=False, readonly=True)
        self.field_name.input_widget.text = patient_data.get("name", "")
        self.add_widget(self.field_name)
        self.field_mobile = SingleField("Mobile No:", multiline=False, input_filter='int', readonly=True)
        self.field_mobile.input_widget.text = patient_data.get("mobile_no", "")
        self.add_widget(self.field_mobile)
        self.field_date = SingleField("Date:", multiline=False, readonly=True)
        self.field_date.input_widget.text = patient_data.get("date", "")
        self.add_widget(self.field_date)
        self.field_adress = SingleField("Adress:", multiline=True, height_for_multiline=100, readonly=True)
        self.field_adress.input_widget.text = patient_data.get("adress", "")
        self.add_widget(self.field_adress)
        self.field_gender = SingleField("Gender:", spinner_values=["Male", "Female", "Other"], readonly=True)
        self.field_gender.input_widget.text = patient_data.get("gender", "")
        self.add_widget(self.field_gender)
        self.field_weight = SingleField("Weight:", multiline=False, input_filter='float', readonly=True)
        self.field_weight.input_widget.text = patient_data.get("weight", "")
        self.add_widget(self.field_weight)
        self.field_systolic = SingleField("Systolic BP:", multiline=False, input_filter='int', readonly=True)
        self.field_systolic.input_widget.text = patient_data.get("systolic_bp", "")
        self.add_widget(self.field_systolic)
        self.field_diastolic = SingleField("Diastolic BP:", multiline=False, input_filter='int', readonly=True)
        self.field_diastolic.input_widget.text = patient_data.get("diastolic_bp", "")
        self.add_widget(self.field_diastolic)
        self.field_pulse = SingleField("Pulse Rate:", multiline=False, input_filter='int', readonly=True)
        self.field_pulse.input_widget.text = patient_data.get("pulse_rate", "")
        self.add_widget(self.field_pulse)
        self.field_surgery = SingleField("Surgery:", spinner_values=["No", "Yes"], readonly=True)
        self.field_surgery.input_widget.text = patient_data.get("surgery", "")
        self.add_widget(self.field_surgery)
        self.field_surgery_desc = SingleField("Surgery Description:", multiline=True, height_for_multiline=100, readonly=True)
        self.field_surgery_desc.input_widget.text = patient_data.get("surgery_description", "")
        self.add_widget(self.field_surgery_desc)
        self.field_medical_history = SingleField("Medical History:", multiline=True, height_for_multiline=200, readonly=True)
        self.field_medical_history.input_widget.text = patient_data.get("medical_history", "")
        self.add_widget(self.field_medical_history)
        self.field_diseases = SingleField("Diseases:", multiline=True, height_for_multiline=100, readonly=True)
        self.field_diseases.input_widget.text = patient_data.get("diseases", "")
        self.add_widget(self.field_diseases)
        self.field_medicines = SingleField("Medicines:", multiline=True, height_for_multiline=100, readonly=True)
        self.field_medicines.input_widget.text = patient_data.get("medicines", "")
        self.add_widget(self.field_medicines)
        self.field_extra = SingleField("Extra:", multiline=True, height_for_multiline=200, readonly=True)
        self.field_extra.input_widget.text = patient_data.get("extra", "")
        self.add_widget(self.field_extra)
        self.field_other_illnesses = SingleField("Other Illnesses:", multiline=False, readonly=True)
        self.field_other_illnesses.input_widget.text = patient_data.get("other_illnesses", "")
        self.add_widget(self.field_other_illnesses)
        self.field_other_medicines = SingleField("Other Medicines:", multiline=True, height_for_multiline=100, readonly=True)
        self.field_other_medicines.input_widget.text = patient_data.get("other_medicines", "")
        self.add_widget(self.field_other_medicines)
        self.field_next_appointment = SingleField("Next Appointment Date:", multiline=False, readonly=True)
        self.field_next_appointment.input_widget.text = patient_data.get("next_appointment_date", "")
        self.add_widget(self.field_next_appointment)

# ---------- HOME SCREEN ----------
class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)
        root_layout = BoxLayout(orientation="vertical")
        title_anchor = AnchorLayout(anchor_x="center", anchor_y="top", size_hint_y=None, height=80)
        title = ResponsiveLabel(text="Clinic Manager", base_font_size=28, color=PRIMARY_COLOR)
        title.bold = True
        title_anchor.add_widget(title)
        root_layout.add_widget(title_anchor)
        button_anchor = AnchorLayout(anchor_x="center", anchor_y="center")
        btn_layout = BoxLayout(orientation="vertical", spacing=10, size_hint=(None, None))
        btn_layout.size = (200, 120)
        btn1 = Button(text="Add Patient", size_hint=(1, None), height=40,
                      background_normal="", background_color=PRIMARY_COLOR,
                      color=(1,1,1,1), font_size=sp(18))
        btn1.bind(on_press=self.go_to_add_patient)
        btn2 = Button(text="View Records", size_hint=(1, None), height=40,
                      background_normal="", background_color=PRIMARY_COLOR,
                      color=(1,1,1,1), font_size=sp(18))
        btn2.bind(on_press=self.go_to_records)
        btn_layout.add_widget(btn1)
        btn_layout.add_widget(btn2)
        button_anchor.add_widget(btn_layout)
        root_layout.add_widget(button_anchor)
        self.add_widget(root_layout)
    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos
    def go_to_add_patient(self, instance):
        self.manager.current = "main"
    def go_to_records(self, instance):
        self.manager.current = "records"

# ---------- MAIN SCREEN (Add Patient) ----------
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = StyledBox(orientation="vertical", padding=10, spacing=10)
        top_bar = BoxLayout(orientation="horizontal", size_hint_y=None, height=50)
        exit_btn = Button(text="Exit", size_hint_x=None, width=80,
                          background_normal="", background_color=PRIMARY_COLOR,
                          color=(1,1,1,1), font_size=sp(16))
        exit_btn.bind(on_press=self.exit_to_home)
        top_bar.add_widget(exit_btn)
        title = ResponsiveLabel(text="Patient Form", base_font_size=20, color=PRIMARY_COLOR)
        title.bold = True
        top_bar.add_widget(title)
        layout.add_widget(top_bar)
        form_card = FormCard()
        self.form = PatientMedicalForm()
        form_card.add_widget(self.form)
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True)
        scroll.add_widget(form_card)
        layout.add_widget(scroll)
        buttons_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=40, spacing=5)
        save_btn = Button(text="Save", background_normal="", background_color=PRIMARY_COLOR,
                          color=(1,1,1,1), font_size=sp(16))
        save_btn.bind(on_press=self.save_patient)
        clear_btn = Button(text="Clear", background_normal="", background_color=PRIMARY_COLOR,
                           color=(1,1,1,1), font_size=sp(16))
        clear_btn.bind(on_press=lambda x: self.form.clear_fields())
        view_records_btn = Button(text="Records", background_normal="", background_color=PRIMARY_COLOR,
                                  color=(1,1,1,1), font_size=sp(16))
        view_records_btn.bind(on_press=self.go_to_records)
        buttons_layout.add_widget(save_btn)
        buttons_layout.add_widget(clear_btn)
        buttons_layout.add_widget(view_records_btn)
        layout.add_widget(buttons_layout)
        self.add_widget(layout)
    def save_patient(self, instance):
        app = App.get_running_app()
        data = self.form.get_patient_data()
        if not data["name"]:
            app.show_error("Patient name is required")
            return
        data["id"] = str(len(app.patients) + 1)
        app.patients.append(data)
        app.save_patients_to_file()
        app.update_patient_list()
        self.form.clear_fields()
        app.show_message("Patient information saved successfully!")
    def go_to_records(self, instance):
        self.manager.current = "records"
    def exit_to_home(self, instance):
        self.manager.current = "home"

# ---------- RECORDS SCREEN ----------
class RecordsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = StyledBox(orientation="vertical", padding=10, spacing=10)
        title = ResponsiveLabel(text="Patient Records", base_font_size=20, size_hint_y=None, height=40, color=PRIMARY_COLOR)
        layout.add_widget(title)
        search_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=40, spacing=5, padding=5)
        search_layout.add_widget(Label(text="Search:", size_hint_x=0.3, color=TEXT_COLOR, font_size=sp(16)))
        self.search_input = TextInput(multiline=False, font_size=sp(16))
        self.search_input.bind(text=self.on_search)
        search_layout.add_widget(self.search_input)
        self.search_type = ResponsiveSpinner(text="Name", values=("Name", "Date", "Disease", "Mob No."), size_hint_x=0.3, base_font_size=16)
        search_layout.add_widget(self.search_type)
        layout.add_widget(search_layout)
        self.records_container = BoxLayout(orientation="vertical", spacing=5, size_hint_y=None)
        self.records_container.bind(minimum_height=self.records_container.setter("height"))
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(self.records_container)
        layout.add_widget(scroll_view)
        bottom_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=40, spacing=5, padding=5)
        back_btn = Button(text="Back", background_normal="", background_color=(1,0,0,1),
                          color=(1,1,1,1), font_size=sp(16))
        back_btn.bind(on_press=self.go_back)
        add_patient_btn = Button(text="Add Patient", background_normal="", background_color=PRIMARY_COLOR,
                                 color=(1,1,1,1), font_size=sp(16))
        add_patient_btn.bind(on_press=self.go_to_add_patient)
        bottom_layout.add_widget(back_btn)
        bottom_layout.add_widget(add_patient_btn)
        layout.add_widget(bottom_layout)
        self.add_widget(layout)
    def on_pre_enter(self):
        App.get_running_app().update_patient_list()
    def on_search(self, instance, value):
        App.get_running_app().update_patient_list()
    def go_to_add_patient(self, instance):
        self.manager.current = "main"
    def go_back(self, instance):
        self.manager.current = "home"

# ---------- PATIENT RECORD ----------
class PatientRecord(BoxLayout):
    def __init__(self, patient_data, delete_callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = 40
        self.patient_data = patient_data
        info = f"{patient_data.get('name', 'No Name')} - {patient_data.get('date', '')}"
        self.add_widget(ResponsiveLabel(text=info, base_font_size=16, size_hint_x=0.7, color=(0,0,0,1)))
        view_btn = Button(text="View", size_hint_x=0.15,
                          background_normal="", background_color=PRIMARY_COLOR,
                          color=(1,1,1,1), font_size=sp(16))
        view_btn.bind(on_press=self.view_details)
        self.add_widget(view_btn)
        del_btn = Button(text="Delete", size_hint_x=0.15,
                         background_normal="", background_color=(0.8,0.2,0.2,1),
                         color=(1,1,1,1), font_size=sp(16))
        del_btn.bind(on_press=lambda x: delete_callback(patient_data))
        self.add_widget(del_btn)
    def view_details(self, instance):
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        form_card = FormCard()
        view_form = PatientMedicalFormView(self.patient_data)
        form_card.add_widget(view_form)
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True)
        scroll.add_widget(form_card)
        content.add_widget(scroll)
        close_btn = Button(text="Close", size_hint_y=None, height=40,
                           background_normal="", background_color=PRIMARY_COLOR,
                           color=(1,1,1,1), font_size=sp(16))
        content.add_widget(close_btn)
        popup = Popup(title=f"Patient: {self.patient_data.get('name', '')}",
                      content=content, size_hint=(0.9, 0.9))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

# ---------- MAIN APP ----------
class PatientManagementApp(App):
    def build(self):
        self.patients = []
        self.load_patients()
        sm = ScreenManager()
        self.home_screen = HomeScreen(name="home")
        self.main_screen = MainScreen(name="main")
        self.records_screen = RecordsScreen(name="records")
        sm.add_widget(self.home_screen)
        sm.add_widget(self.main_screen)
        sm.add_widget(self.records_screen)
        sm.current = "home"
        return sm
    def update_patient_list(self):
        container = self.records_screen.records_container
        container.clear_widgets()
        if not self.patients:
            container.add_widget(ResponsiveLabel(
                text="No patients found.", base_font_size=16,
                size_hint_y=None, height=40
            ))
            return
        search_text = self.records_screen.search_input.text.lower()
        filtered = self.patients
        if search_text:
            field = self.records_screen.search_type.text.lower()
            if field == "name":
                filtered = [p for p in self.patients if search_text in p.get("name", "").lower()]
            elif field == "date":
                filtered = [p for p in self.patients if search_text in p.get("date", "").lower()]
            elif field == "disease":
                filtered = [p for p in self.patients if search_text in p.get("diseases", "").lower()]
            elif field == "mob no.":
                filtered = [p for p in self.patients if search_text in p.get("mobile_no", "").lower()]
        filtered = sorted(filtered, key=lambda x: x.get("date", ""), reverse=True)
        for p in filtered:
            rec = PatientRecord(p, self.confirm_delete_patient, size_hint_y=None, height=40)
            container.add_widget(rec)
    def confirm_delete_patient(self, patient_data):
        content = BoxLayout(orientation="vertical", padding=10, spacing=10)
        content.add_widget(ResponsiveLabel(
            text="Are you sure you want to delete this patient record?",
            base_font_size=16
        ))
        btns = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=40)
        yes_btn = Button(text="Yes", background_normal="", background_color=(0.8,0.2,0.2,1),
                         color=(1,1,1,1), font_size=sp(16))
        no_btn = Button(text="No", background_normal="", background_color=PRIMARY_COLOR,
                        color=(1,1,1,1), font_size=sp(16))
        btns.add_widget(yes_btn)
        btns.add_widget(no_btn)
        content.add_widget(btns)
        popup = Popup(title="Confirm Deletion", content=content, size_hint=(0.8, 0.3))
        yes_btn.bind(on_press=lambda instance: self.delete_patient(patient_data, popup))
        no_btn.bind(on_press=popup.dismiss)
        popup.open()
    def delete_patient(self, patient_data, popup=None):
        if popup:
            popup.dismiss()
        for i, p in enumerate(self.patients):
            if p.get("id") == patient_data.get("id"):
                self.patients.pop(i)
                break
        self.save_patients_to_file()
        self.update_patient_list()
        self.show_message("Patient record deleted.")
    def save_patients_to_file(self):
        with open("patients.json", "w") as f:
            json.dump(self.patients, f)
    def load_patients(self):
        try:
            if os.path.exists("patients.json"):
                with open("patients.json", "r") as f:
                    self.patients = json.load(f)
        except Exception as e:
            print(f"Error loading patients: {e}")
            self.patients = []
    def show_message(self, message):
        content = BoxLayout(orientation="vertical", padding=10, spacing=10)
        content.add_widget(ResponsiveLabel(text=message, base_font_size=16))
        btn = Button(text="OK", size_hint_y=None, height=40,
                     background_normal="", background_color=PRIMARY_COLOR,
                     color=(1,1,1,1), font_size=sp(16))
        content.add_widget(btn)
        popup = Popup(title="Information", content=content, size_hint=(0.8, 0.3))
        btn.bind(on_press=popup.dismiss)
        popup.open()
    def show_error(self, message):
        content = BoxLayout(orientation="vertical", padding=10, spacing=10)
        col = (1,0,0,1) if message=="Patient name is required" else TEXT_COLOR
        content.add_widget(ResponsiveLabel(text=message, base_font_size=16, color=col))
        btn = Button(text="OK", size_hint_y=None, height=40,
                     background_normal="", background_color=(0.8,0,0,1),
                     color=(1,1,1,1), font_size=sp(16))
        content.add_widget(btn)
        popup = Popup(title="Error", content=content, size_hint=(0.8, 0.3))
        btn.bind(on_press=popup.dismiss)
        popup.open()

if __name__ == "__main__":
    PatientManagementApp().run()
