from functools import wraps
from address_book import AddressBook, Record, Phone, ValidationError


def input_error(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            return str(e)
        except ValueError:
            return "Give me name and phone please."
        except IndexError:
            return "Enter user name."
        except KeyError:
            return "Contact not found."

    return inner


def parse_input(user_input):
    cmd, *args = user_input.split()
    return cmd.lower(), *args


def normalize_name(name: str) -> str:
    return name.capitalize()


def check_args(args, count, usage):
    if len(args) != count:
        raise ValidationError(f"Invalid arguments. Usage: {usage}")


@input_error
def add_contact(args, book: AddressBook):
    check_args(args, 2, "add [name] [phone]")
    name, phone = args
    name = normalize_name(name)
    record = book.find(name)
    message = "Contact updated."
    # перевірка до створення запису
    Phone(phone)
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    check_args(args, 3, "change [name] [old phone] [new phone]")
    name, old_phone, new_phone = args
    name = normalize_name(name)
    record = book.find(name)
    if record is None:
        raise KeyError

    record.edit_phone(old_phone, new_phone)
    return "Contact updated."


@input_error
def show_phone(args, book: AddressBook):
    check_args(args, 1, "phone [name]")
    name = normalize_name(args[0])
    record = book.find(name)
    if record is None:
        raise KeyError
    phones = (
        "; ".join(p.value for p in record.phones)
        if record.phones
        else "No phones saved."
    )
    return phones


@input_error
def show_all(args, book: AddressBook):
    check_args(args, 0, "all")
    if not book.data:
        return "No contacts saved."
    return "\n".join(str(record) for record in book.data.values())


@input_error
def add_birthday(args, book: AddressBook):
    check_args(args, 2, "add-birthday [name] [DD.MM.YYYY]")
    name, birthday = args
    name = normalize_name(name)
    record = book.find(name)
    if record is None:
        raise KeyError
    record.add_birthday(birthday)
    return "Birthday has been added"


@input_error
def show_birthday(args, book: AddressBook):
    check_args(args, 1, "show-birthday [name]")
    name = normalize_name(args[0])
    record = book.find(name)
    if record is None:
        raise KeyError

    return str(record.birthday) if record.birthday else "No birthday saved."


@input_error
def birthdays(args, book: AddressBook):
    check_args(args, 0, "birthdays")
    if not book.data:
        return "No contacts saved."
    upcoming_birthdays = book.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return "No birthdays next 7 days"

    return "\n".join(
        f"{upcoming_birthday['name']}: {upcoming_birthday['congratulation_date']}"
        for upcoming_birthday in upcoming_birthdays
    )


COMMANDS = {
    "add": add_contact,
    "change": change_contact,
    "phone": show_phone,
    "all": show_all,
    "add-birthday": add_birthday,
    "show-birthday": show_birthday,
    "birthdays": birthdays,
}


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        if not user_input.strip():
            continue
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command in COMMANDS:
            print(COMMANDS[command](args, book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()