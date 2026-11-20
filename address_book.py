from collections import UserDict
from datetime import datetime, date, timedelta

DAYS_AHEAD = 7


def _birthday_in_year(birthday: date, year: int) -> date:
    try:
        return birthday.replace(year=year)
    except ValueError:
        return birthday.replace(year=year, day=28)


class ValidationError(ValueError):
    pass


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not (len(value) == 10 and value.isdigit()):
            raise ValidationError(f"Phone must contain exactly 10 digits, got: {value}")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            date = datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(date)
        except ValueError:
            raise ValidationError("Invalid date format. Use DD.MM.YYYY")

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def edit_phone(self, old_phone, new_phone):
        for i, phone in enumerate(self.phones):
            if phone.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return
        raise ValidationError(f"Phone {old_phone} not found")

    def remove_phone(self, phone):
        found = self.find_phone(phone)
        if found is None:
            raise ValidationError(f"Phone {phone} not found")
        self.phones.remove(found)

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        if not self.birthday:
            self.birthday = Birthday(birthday)
        else:
            raise ValidationError("Birthday is already set!")

    def __str__(self):
        phones = "; ".join(p.value for p in self.phones) or "—"
        birthday = self.birthday if self.birthday else "—"
        return (
            f"Contact name: {self.name.value}, phones: {phones}, birthday: {birthday}"
        )


class AddressBook(UserDict):

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming = []

        for record in self.data.values():
            if record.birthday is None:
                continue

            birthday = record.birthday.value

            next_birthday = _birthday_in_year(birthday, today.year)
            if next_birthday < today:
                next_birthday = _birthday_in_year(birthday, today.year + 1)

            days_until = (next_birthday - today).days
            if days_until >= DAYS_AHEAD:
                continue

            congratulation_date = next_birthday
            weekday = congratulation_date.weekday()
            if weekday >= 5:
                congratulation_date += timedelta(days=7 - weekday)

            upcoming.append(
                {
                    "name": record.name.value,
                    "congratulation_date": congratulation_date.strftime("%d.%m.%Y"),
                }
            )

        return upcoming


if __name__ == "__main__":
    book = AddressBook()

    # Створення запису для John
    john_record = Record("John")
    john_record.add_phone("1234567890")
    john_record.add_phone("5555555555")

    # Додавання запису John до адресної книги
    book.add_record(john_record)

    # Створення та додавання нового запису для Jane
    jane_record = Record("Jane")
    jane_record.add_phone("9876543210")
    book.add_record(jane_record)

    # Виведення всіх записів у книзі
    for name, record in book.data.items():
        print(record)

    # Знаходження та редагування телефону для John
    john = book.find("John")
    john.edit_phone("1234567890", "1112223333")

    print(john)  # Виведення: Contact name: John, phones: 1112223333; 5555555555

    # Пошук конкретного телефону в записі John
    found_phone = john.find_phone("5555555555")
    print(f"{john.name}: {found_phone}")  # Виведення: 5555555555

    # Видалення запису Jane
    book.delete("Jane")

    birth = Birthday("12.12.2026")
    print(birth)
    print(Birthday("25.12.1990"))
