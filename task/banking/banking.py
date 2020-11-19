import random
import sqlite3
conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='card';")
if cur.fetchone():
    pass
else:
    cur.execute("""CREATE TABLE card(
                id INTEGER,
                number TEXT,
                pin TEXT,
                balance INTEGER DEFAULT 0
                );""")
conn.commit()


class CreditCard:
    def __init__(self):
        self.card_number = None
        self.pin = None
        self.balance = None

    def new_data(self, data):
        self.card_number = data[1]
        self.pin = data[2]
        self.balance = data[3]

    def do_add_money(self):
        print("Enter income:")
        value = int(input())
        self.balance += value
        cur.execute("UPDATE card SET balance = {} WHERE number = '{}'".
                                format(self.balance, self.card_number))
        conn.commit()
        print("Income was added!")

    def luhn_algoritm(self, string):
        summary = 0
        numbers = []
        numbers[:0] = string
        numbers = list(map(int, string))

        for i in range(len(numbers)):
            if (i + 1) % 2 == 1:
                numbers[i] *= 2
            if numbers[i] > 9:
                numbers[i] -= 9
            summary += numbers[i]

        return summary % 10 == 0

    def do_transfer(self):
        print("Enter receiver card number:")
        receiver_card_number = input()
        if self.card_number == receiver_card_number:
            print("You can't transer money to the same account!")
        elif not self.luhn_algoritm(receiver_card_number):
            print("Probably you made a mistake in the card number. Please try again!")
        else:
            cur.execute("SELECT * FROM card WHERE number = '{}'".format(receiver_card_number))
            result = cur.fetchone()
            if result:
                print("Enter how much money you want to transfer:")
                transfer = int(input())
                if self.balance < transfer:
                    print("Not enough money!")
                else:
                    cur.execute("UPDATE card SET balance = {} WHERE number = '{}'".
                                format(result[3] + transfer, receiver_card_number))
                    cur.execute("UPDATE card SET balance = {} WHERE number = '{}'".
                                format(self.balance - transfer, self.card_number))
                    self.balance -= transfer
                    conn.commit()
            else:
                 print("Such a card does not exist.")

    def generate_new_card(self):
        self.pin = self.new_pin()
        self.balance = 0
        self.card_number = self.generate_card_number()
        self.update_dictionary()

    def generate_card_number(self):
        bank_identification_number = "400000"
        customer_account_number = self.generate_customer_AN()
        check_sum = self.generate_check_sum(bank_identification_number
                                                + customer_account_number)
        return bank_identification_number + customer_account_number + check_sum

    def generate_customer_AN(self):
        while True:
            new_customer_AN = ''
            for i in range(9):
                new_customer_AN += str(random.randrange(0, 9, 1))
            # Checking if there is same id in database
            cur.execute('SELECT id FROM card WHERE id = {}'.format(int(new_customer_AN)))
            customer_id = cur.fetchone()
            if customer_id:
                continue
            else:
                break
        return new_customer_AN

    def generate_check_sum(self, card_numbers):
        summary = 0
        numbers = []
        numbers[:0] = card_numbers
        numbers = list(map(int, card_numbers))

        for i in range(15):
            if (i + 1) % 2 == 1:
                numbers[i] *= 2
            if numbers[i] > 9:
                numbers[i] -= 9
            summary += numbers[i]
        return str((10 - (summary % 10)) % 10)

    def new_pin(self):
        string = ''
        for i in range(4):
            string += str(random.randrange(0, 9, 1))
        return string

    def update_dictionary(self):
        cur.execute("INSERT INTO card (id, number, pin, balance) VALUES ({}, '{}', '{}', {});".
                    format(int(self.card_number[6:15]), self.card_number, self.pin, self.balance))
        conn.commit()

    def close_card(self):
        print(self.card_number)
        cur.execute("DELETE FROM card WHERE number = '{}'".format(self.card_number))
        conn.commit()


def menu_text():
    print("1. Create an account")
    print("2. Log into account")
    print("0. Exit")


def menu_logged_text():
    print("1. Balance")
    print("2. Add income")
    print("3. Do transfer")
    print("4. Close account")
    print("5. Log out")
    print("0. Exit")


def menu_logged(result):
    print("You have successfully logged in!")
    logged_card = CreditCard()
    logged_card.new_data(result)

    menu_logged_text()
    new_input = input()
    while new_input != '0':  # Exit condition from terminal
        if new_input == '1':  # Balance
            print("Balance: ", logged_card.balance)
        elif new_input == '2':  # Add income
            logged_card.do_add_money()
        elif new_input == '3':  # Do transfer
            logged_card.do_transfer()
        elif new_input == '4':  # Close account
            logged_card.close_card()
            print("The account has been closed!")
            break
        elif new_input == '5':  # Log out
            print("You have successfully logged out!")
            break
        menu_logged_text()
        new_input = input()
        print()
    return new_input


def menu():
    new_input = '-1'

    while new_input != '0':
        menu_text()
        new_input = input()
        if new_input == '1':  # Create card and pin
            new_credit_card = CreditCard()
            new_credit_card.generate_new_card()
            print("Your card had been created")
            print("Your card number:")
            print(new_credit_card.card_number)
            print("Your card PIN:")
            print(new_credit_card.pin)
        elif new_input == '2':  # Log in if valid
            print("Enter your card number:")
            input_card_number = input()
            print("Enter your PIN:")
            input_pin = input()
            cur.execute("SELECT * FROM card WHERE number = '{}' AND pin = '{}'".format(input_card_number, input_pin))
            result = cur.fetchone()
            if result:
                new_input = menu_logged(result)
            else:
                print("Wrong card number or PIN!")
    else:
        print("Bye!")
        pass


menu()
