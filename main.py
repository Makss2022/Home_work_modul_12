from collections import UserDict
from datetime import datetime
import re
from pickle import dump, load
from pathlib import Path
from decorators import input_error

handlers: dict[str, list[str]] = {
    "hello": ["hello_hendler", "hello_show_exit_parser"],
    "good bye": ["exit_hendler", "hello_show_exit_parser"],
    "close": ["exit_hendler", "hello_show_exit_parser"],
    "exit": ["exit_hendler", "hello_show_exit_parser"],
    "add": ["add_handler", "add_change_parser"],
    "change": ["change_hendler", "add_change_parser"],
    "find": ["find_hendler", "find_parser"],
    "show all": ["show_all_handler", "hello_show_exit_parser"]
}


class Field:
    def __init__(self, value: str) -> None:
        self.__value = None
        self.value = value

    def __repr__(self) -> str:
        return self.value

    @property
    def value(self) -> str:
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value: str) -> None:
        super().__init__(value)

    @Field.value.setter
    def value(self, value):
        phone = "".join(re.findall(r"\d+", value))
        if len(phone) == 10:
            phone = "+38" + phone
        elif len(phone) == 12:
            phone = "+" + phone
        else:
            raise ValueError(f"Phone number '{value}' entered incorrectly")
        Field.value.fset(self, phone)


class Birthday(Field):
    def __init__(self, value: str) -> None:
        super().__init__(value)

    @Field.value.setter
    def value(self, value):
        if value != "":
            try:
                datetime.strptime(value, "%d.%m.%Y")
                Field.value.fset(self, value)
            except ValueError:
                raise ValueError(
                    f"The date '{value}' does not match the format 'DD .MM .YYYY'")


class Record:
    def __init__(self, name: Name, phone: Phone = None, birthday: Birthday = None) -> None:
        self.name: Name = name
        self.phone: list[Phone] = [phone] if phone else []
        self.birthday: Birthday = birthday

    def __repr__(self) -> str:
        return f"\tcontact name : {self.name}:\n\tphones : {', '.join(phone.value for phone in self.phone)}\
        \n\tbirthday : {self.birthday}"

    def days_to_birthday(self):
        if self.birthday == None:
            return "Birthday not specified."
        birthday: datetime = datetime.strptime(self.birthday.value, "%d.%m.%Y")
        day_now = datetime.now().date()
        day_birthday = birthday.replace(year=datetime.now().year).date()
        if day_birthday < day_now:
            day_birthday = birthday.replace(
                year=(datetime.now().year+1)).date()
        return f"{self.name.value}: {(day_birthday - day_now).days} days until next birthday"

    def add_phone(self, *phone: Phone) -> None:
        self.phone.extend(phone)

    def change_phone(self, old_phone: Phone, new_phone: Phone) -> None:
        for phone in self.phone:
            if phone.value == old_phone.value:
                phone.value = new_phone.value
                return f"{self.name.value}'s phone has been replaced with a new phone {new_phone.value}"
        return f"Phone number '{old_phone.value}' does not exist!"

    def remuve_phone(self, phone_remuve: Phone) -> None:
        for phone in self.phone:
            if phone.value == phone_remuve.value:
                self.phone.remove(phone)
                return
        print(f"Phone number '{phone_remuve.value}' does not exist!")


class AddressBook(UserDict):
    data: dict[str, Record] = {}
    book_name = "address_book.dat"
    quantity = 4
    count = 0
    index_count = 0

    def __enter__(self):
        if not Path(self.book_name).exists():
            with open(self.book_name, "wb") as file:
                dump(self.data, file)
        with open(self.book_name, "rb") as file:
            book = load(file)
            self.data.update(book)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with open(self.book_name, "wb") as file:
            dump(self.data, file)

    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find_fragment(self, fragment: str) -> str:
        data_find = {}
        for name, record in self.data.items():
            if fragment.lower() in name.lower():
                data_find.update({name: record})
            elif True in [fragment in phone.value for phone in record.phone]:
                data_find.update({name: record})
        if data_find == {}:
            return f"\nContacts with fragment '{fragment}' not found.\n"
        return f"\nFound contacts for fragment '{fragment}' :\n" + "\n".join(
            [f"{name} : \n{record}" for name, record in data_find.items()]
        ) + "\n"

    def __iter__(self):
        return self

    def __next__(self):
        self.count += 1
        len_data = len(self.data)
        max_count = (len_data // self.quantity + 1) \
            if (len_data % self.quantity) else (len_data // self.quantity)
        if self.count > max_count:
            raise StopIteration
        else:
            data_list = list(self.data.items())
            start_index = self.index_count
            end_index = start_index + self.quantity
            if (len_data - end_index) > 0:
                to_return = data_list[start_index:(end_index)]
            else:
                to_return = data_list[start_index:]
        self.index_count = end_index
        return "\n".join(
            [f"{contact[0]} : \n{contact[1]}\n" for contact in to_return]
        )


class InputParser():
    def __init__(self) -> None:
        self.parser_handler_dict = None

    @input_error
    def hello_show_exit_parser(self, list_input_user: list[str]) -> str:
        return ["", ""]

    @input_error
    def add_change_parser(self, list_input_user: list[str]) -> str:
        if list_input_user[1] == "" or list_input_user[2] == "" or list_input_user[1].isdigit():
            return [""]
        return [list_input_user[1], list_input_user[2], list_input_user[3]]

    @input_error
    def find_parser(self, list_input_user: list[str]) -> str:
        return [list_input_user[1], ""]

    @input_error
    def unknown_command(self, list_input_user: list[str]) -> str:
        return [""]

    @input_error
    def parser_user_input(self, imput_user: str) -> tuple[str, list]:
        input_user_split = imput_user.split()
        command = input_user_split[0].lower()
        input_user_split.extend([""])
        if input_user_split[0].lower() == "show" and input_user_split[1].lower() == "all" or input_user_split[0].lower() == "good" and input_user_split[1].lower() == "bye":
            command = " ".join(input_user_split[0:2]).lower()
        arguments_func = handlers.get(
            command, "unknown_command")[1]
        arguments = getattr(self, arguments_func)(input_user_split)
        return command, arguments


class CLI():
    def __init__(self) -> None:
        self.book: AddressBook = None
        self.parser = InputParser()

    @input_error
    def hello_hendler(self, *args) -> str:
        return "How can I help you?"

    @input_error
    def exit_hendler(self, *args) -> str:
        return "Good bye!"

    @input_error
    def add_handler(self, name_phone: list[str]) -> str:
        name = name_phone[0]
        phone = name_phone[1]
        if name in self.book.keys():
            record: Record = self.book.data[name]
            record.add_phone(Phone(phone))
            return f"The phone number '{phone}' has been added to the '{name}' contact."
        record = Record(Name(name), Phone(phone))
        self.book.data[name] = record
        return "New contact saved!"

    @input_error
    def find_hendler(self, fragment_list: list[str]) -> str:
        fragment = fragment_list[0]
        if fragment == "":
            return "Please enter a fragment of the name or phone number to search!"
        return self.book.find_fragment(fragment)

    @input_error
    def change_hendler(self, name_phone: list[str]) -> str:
        name = name_phone[0]
        old_phone = name_phone[1]
        new_phone = name_phone[2]
        record = self.book.data[name]
        return record.change_phone(Phone(old_phone), Phone(new_phone))

    @input_error
    def show_all_handler(self, *args: str) -> str:
        header = "\nContacts book:\n"
        contacts_format = "\n".join(
            [f"{name} : \n{record}" for name,
                record in self.book.data.items()]
        ) + "\n"
        contacts_format = "Phone numbers do not exist yet!" if self.book.data == {} else contacts_format
        return header + contacts_format

    def run(self):
        with AddressBook() as book:
            self.book = book

            while True:
                try:
                    user_input = input("Command: ")
                    command, arguments = self.parser.parser_user_input(
                        user_input)
                    command_handler = handlers.get(command)[0]
                    command_response = getattr(
                        self, command_handler)(arguments)
                    print(command_response)
                    if command_response == "Good bye!":
                        break
                except ValueError:
                    print("Сommand entered incorrectly!")


if __name__ == "__main__":
    cli = CLI()
    cli.run()
