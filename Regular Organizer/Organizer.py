import datetime
import json
import time

class ReminderEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Reminder):
            return obj.serialize()
        return super().default(obj)

class Reminder:
    def __init__(self, title, start_time, end_time, repetitions=None, bank_holiday_adjustment=False, permanent_offset=False):
        self.title = title
        self.start_time = start_time
        self.end_time = end_time
        self.done = False
        self.triggered = False
        self.trigger_count = 0
        self.done_count = 0
        self.repetitions = repetitions or []
        self.bank_holiday_adjustment = bank_holiday_adjustment
        self.permanent_offset = permanent_offset

    def check_notification(self):
        current_time = datetime.datetime.now().time()
        if not self.triggered and self.start_time.time() <= current_time <= self.end_time.time():
            print(f"Reminder: {self.title} - It's time!")
            self.triggered = True
            self.trigger_count += 1
            if self.done:
                self.done_count += 1

    def mark_as_done(self):
        self.done = True

    def serialize(self):
        return {
            'title': self.title,
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M'),
            'end_time': self.end_time.strftime('%Y-%m-%d %H:%M'),
            'repetitions': self.repetitions,
            'bank_holiday_adjustment': self.bank_holiday_adjustment,
            'permanent_offset': self.permanent_offset
        }

    @classmethod
    def deserialize(cls, data):
        start_time = datetime.datetime.strptime(data['start_time'], '%Y-%m-%d %H:%M')
        end_time = datetime.datetime.strptime(data['end_time'], '%Y-%m-%d %H:%M')
        return cls(
            data['title'],
            start_time,
            end_time,
            repetitions=data['repetitions'],
            bank_holiday_adjustment=data['bank_holiday_adjustment'],
            permanent_offset=data['permanent_offset']
        )

class Calendar:
    def __init__(self):
        self.reminders = []
        self.completed_tasks = []

    def add_reminder(self, reminder):
        self.reminders.append(reminder)

    def remove_reminder(self, reminder):
        self.reminders.remove(reminder)
    
    def mark_reminder_as_done(self, reminder):
        reminder.mark_as_done()
        self.completed_tasks.append({
            "title": reminder.title,
            "date": datetime.date.today().strftime("%Y-%m-%d")
        })
        print("Reminder marked as done.")
        return

    def save_completion_data(self):
        today = datetime.date.today().strftime("%Y-%m-%d")
        completion_data = []
        for reminder in self.reminders:
            completion_data.append({
                "title": reminder.title,
                "date": today,
                "trigger_count": reminder.trigger_count,
                "done_count": reminder.done_count
            })
            reminder.triggered = False
        with open(f"completion_data_{today}.json", "w") as file:
            json.dump(completion_data, file, indent=4)
        print("Completion data saved.")

    def serialize(self):
        reminders_data = [reminder.serialize() for reminder in self.reminders]
        return {'reminders': reminders_data, 'completed_tasks': self.completed_tasks}

    def save_reminders_to_file(self, filename):
        data = self.serialize()
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)

    @classmethod
    def load_reminders_from_file(cls, filename):
        with open(filename, 'r') as file:
            data = json.load(file)
        calendar = cls.deserialize(data)
        return calendar

    def start_clock(self):
        while True:
            current_time = datetime.datetime.now().time()
            for reminder in self.reminders:
                if reminder.start_time.time() <= current_time <= reminder.end_time.time():
                    reminder.check_notification()
            time.sleep(60)  # Check every minute

    # Add a reminder via a user input. TODO: Extend to button when GUI prepared.
    def add_reminder(self):
        print("Adding a new reminder:")
        title = input("Enter the title: ")
        start_time_str = input("Enter the start time (HH:MM): ")
        start_time = datetime.datetime.strptime(start_time_str, "%H:%M").time()
        end_time_str = input("Enter the end time (HH:MM): ")
        end_time = datetime.datetime.strptime(end_time_str, "%H:%M").time()

        reminder = Reminder(title, start_time, end_time)
        self.reminders.append(reminder)
        print("Reminder added successfully!")


# Helper function to display a weekly calendar view. TODO: Set static to Mon:Sun vs 1 week from view date?
def display_weekly_calendar(calendar):
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=today.weekday())  # Get the start of the current week
    end_date = start_date + datetime.timedelta(days=6)  # Get the end of the current week

    current_date = start_date
    while current_date <= end_date:
        print(current_date.strftime('%A, %B %d, %Y'))
        events = [reminder.title for reminder in calendar.reminders if reminder.start_time.date() == current_date]
        print('\t', ', '.join(events))
        print()
        current_date += datetime.timedelta(days=1)

# Helper function to display the breakdown of a specific day
def display_day_breakdown(calendar, day):
    events = [reminder for reminder in calendar.reminders if reminder.start_time.date() == day]
    events.sort(key=lambda r: r.start_time)
    for reminder in events:
        print('Title:', reminder.title)
        print('Start Time:', reminder.start_time.strftime('%H:%M'))
        print('End Time:', reminder.end_time.strftime('%H:%M'))
        print('Repetitions:', ', '.join(reminder.repetitions))
        print('Bank Holiday Adjustment:', reminder.bank_holiday_adjustment)
        print('Permanent Offset:', reminder.permanent_offset)
        print()

# Example usage
def main():
    calendar = Calendar()

    # Start the clock and check for reminders
    calendar.start_clock()

    # For now, reminders go here. When you run it, it will display these reminders. Intent is to have these feed into graphic display of calendar; more here for data format.
    reminder1 = Reminder('Meeting', datetime.datetime(2023, 6, 7, 14, 0), datetime.datetime(2023, 6, 7, 15, 0))
    reminder2 = Reminder('Exercise', datetime.datetime(2023, 6, 8, 8, 0), datetime.datetime(2023, 6, 8, 9, 0), repetitions=['Monday', 'Wednesday', 'Friday'])
    reminder3 = Reminder('Bin Collection', datetime.datetime(2023, 6, 9, 9, 0), datetime.datetime(2023, 6, 9, 10, 0), bank_holiday_adjustment=True, permanent_offset=True)

    calendar.add_reminder(reminder1)
    calendar.add_reminder(reminder2)
    calendar.add_reminder(reminder3)

    # Save reminders to a file
    calendar.save_reminders_to_file('reminders.json')

    # Load reminders from a file
    loaded_calendar = Calendar.load_reminders_from_file('reminders.json')
    display_weekly_calendar(loaded_calendar)

    # Display breakdown of a specific day
    selected_day = datetime.date(2023, 6, 7)
    display_day_breakdown(calendar, selected_day)

    # Mark a reminder as done
    calendar.mark_reminder_as_done()

    # Save completion data
    calendar.save_completion_data()

    # Serialize the calendar to JSON
    data = calendar.serialize()
    json_data = json.dumps(data, indent=4, cls=ReminderEncoder)
    print('\nSerialized Calendar:\n', json_data)

    # Deserialize the calendar from JSON
    deserialized_calendar = Calendar.deserialize(data)

if __name__ == '__main__':
    main()
