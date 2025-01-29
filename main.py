import atexit
import math
import random as rd
import threading
import time

import pyttsx3
from prettytable import PrettyTable


class StaticMethods:
    @staticmethod
    def process_player_input():
        player_input = input()
        player_input = player_input.lower()
        player_input = player_input.split()
        return player_input

    @staticmethod
    def print_help(commands_list):
        for command, description in commands_list:
            print(f"<{command}>: {description}")


class Player:
    def __init__(self):
        self.player_money = 67000000
        self.bought_countries = 0
        self.amount_of_countries = 0
        self.farms_class = self.Farms(self, False)
        self.countries_class = self.Farms(self, True)
        self.shop_class = None
        atexit.register(self.save_progress)

    def save_progress(self):
        import json

        def reformat_dict(dictionary):
            for a in dictionary.values():
                try:
                    a.pop()
                except:
                    pass
            return dictionary

        player_farms = reformat_dict(self.farms_class.player_farms)
        player_countries = reformat_dict(self.countries_class.player_countries)
        with open("save.json", 'w', encoding='utf-8') as file:
            json.dump({"player_money": self.player_money,
                       "bought_countries": self.bought_countries,
                       "amount_of_countries": self.amount_of_countries,
                       "player_farms": player_farms,
                       "player_countries": player_countries}, file, indent=2, ensure_ascii=False)

    def load_progress(self):
        import json
        with open("save.json", 'r', encoding='utf-8') as file:
            file_json = json.load(file)
            self.player_money = file_json["player_money"]
            self.bought_countries = file_json["bought_countries"]
            self.amount_of_countries = file_json["amount_of_countries"]
            countries = file_json["player_countries"]
            farms = file_json["player_farms"]
            # print(farms["0"])
            for i in countries:
                cost = int(self.shop_class.countries[int(i)].get_current_cost(1))
                print(f"cost {cost} name {self.shop_class.countries[int(i)].get_name()} i {int(i)}")
                self.countries_class.add_farm(int(i), self.shop_class.countries[int(i)].get_name(), 1,
                                              self.shop_class.countries[int(i)].get_item_production(), cost)
            for i in farms:
                amount = farms[i][1]
                cost = farms[i][3]

                print(f"cost {cost} name {self.shop_class.farms[int(i)].get_name()} i {i} amount {amount}")
                self.farms_class.add_farm(i, self.shop_class.farms[int(i)].get_name(), amount,
                                          self.shop_class.farms[int(i)].get_item_production(), cost)

    class Farms:
        def __init__(self, player_class, is_country):
            self.player_farms = {}  # farm_id: [farm_name, amount_of_farms, production, cost, passive_counter_class]
            self.player_countries = {}
            self.last_thread_id = 0
            self.is_country = is_country
            self.player_class = player_class

        def print_formatted_player_farms(self):
            table = PrettyTable()
            if not self.is_country:
                table.field_names = ["Farm Name", "Amount", "Total Production", "Total Cost"]
                for farm_id, data in self.player_farms.items():
                    # print(data)
                    table.add_row([data[0], data[1], data[2], data[3]])
            else:
                table.field_names = ["Country Name", "Total Production", "Total Cost"]
                for farm_id, data in self.player_countries.items():
                    table.add_row([data[0], data[1], data[2]])

            print(f"Player balance {self.player_class.player_money}")
            print("Player Property:")
            print(table)
            print('\n')

        def add_farm(self, farm_id, farm_name, amount, production, current_cost):
            if not self.is_country:
                if self.is_key_exists(farm_id):
                    self.player_farms[farm_id][1] = self.get_amount_of_farms(farm_id) + amount
                    self.player_farms[farm_id][2] = production * self.player_farms[farm_id][1]
                    print(production)
                    self.player_farms[farm_id][3] += current_cost
                    total_production = self.player_farms[farm_id][1] * self.player_farms[farm_id][2]
                    PassiveCounter_class = self.player_farms[farm_id][4]
                    PassiveCounter_class.update_earn(total_production)
                    # self.player_farms[farm_id][4] = PassiveCounter_class
                    # PassiveCounter_class.start()
                else:
                    PassiveCounter_class = PassiveCounter(amount * production, self.player_class, self.last_thread_id)
                    self.last_thread_id += 1
                    self.player_farms.setdefault(farm_id,
                                                 [farm_name, self.get_amount_of_farms(farm_id) + amount, production * amount,
                                                  current_cost, PassiveCounter_class])
                    PassiveCounter_class.start()
            else:
                if self.is_key_exists(farm_id):
                    self.player_countries[farm_id][1] = production
                    print(production)
                    self.player_countries[farm_id][2] += current_cost
                    total_production = self.player_countries[farm_id][1]
                    PassiveCounter_class = self.player_countries[farm_id][3]
                    PassiveCounter_class.update_earn(total_production)
                    # self.player_farms[farm_id][4] = PassiveCounter_class
                    # PassiveCounter_class.start()
                else:
                    PassiveCounter_class = PassiveCounter(production, self.player_class, self.last_thread_id)
                    self.last_thread_id += 1
                    self.player_countries.setdefault(farm_id,
                                                     [farm_name, production,
                                                      current_cost, PassiveCounter_class])
                    PassiveCounter_class.start()

            # print(self.player_farms)

        def get_amount_of_farms(self, farm_id):
            amount = 0
            try:
                amount = self.player_farms[farm_id][1]
            except KeyError:
                return 0
            return amount

        def get_current_total_cost(self, farm_id):
            cost = 0
            try:
                cost = self.player_farms[farm_id][2]
            except KeyError:
                return 0
            return cost

        def is_key_exists(self, farm_id):
            if not self.is_country:
                if farm_id in self.player_farms:
                    return True
            else:
                if farm_id in self.player_countries:
                    return True
            return False


class PassiveFarmer:
    def __init__(self, item_name: str, base_cost: int, earn_per_second: int, item_id: int):
        self.item_name = item_name
        self.cost = base_cost
        self.earn_per_second = earn_per_second
        self.item_id = item_id
        self.is_bought = False

    def get_item_id(self):
        return self.item_id

    def get_item_production(self):
        return self.earn_per_second

    def get_name(self):
        return self.item_name

    def get_is_bought(self):
        return self.is_bought

    def get_current_cost(self, item_amount):
        if item_amount > 2:
            return self.cost * item_amount * 0.5
        else:
            return self.cost


class Shop:
    def buy_farm(self, item_id, amount):
        cost = self.get_cost_for_multiple_buy(item_id, amount)
        if cost <= self.player_class.player_money:
            self.player_class.player_money -= cost
            self.player_class.farms_class.add_farm(item_id, self.farms[item_id].get_name(), amount,
                                                   self.farms[item_id].get_item_production(), cost)

    def buy_country(self, item_id):
        if self.countries[item_id].get_is_bought():
            return
        cost = int(self.countries[item_id].get_current_cost(1))

        if cost <= self.player_class.player_money:
            self.player_class.player_money -= cost
            self.player_class.countries_class.add_farm(item_id, self.countries[item_id].get_name(), 1,
                                                       self.countries[item_id].get_item_production(), cost)
        self.countries[item_id].is_bought = True
        self.player_class.bought_countries += 1

    def get_cost_for_multiple_buy(self, item_id, amount):
        cost = 0
        # print(self.player_class.farms_class.player_farms)
        bought_by_player_farms = self.player_class.farms_class.get_amount_of_farms(self.farms[item_id].get_item_id())
        for i in range(amount):
            cost += self.farms[item_id].get_current_cost(bought_by_player_farms + i)
        return cost

    def add_countries(self):
        import json
        with open("countries.json", 'r', encoding='utf-8') as file:
            countries = json.load(file)["countries"]
        for i in countries:
            self.countries.append(
                PassiveFarmer(i["country_name"], int(i["cost"]), int(i["earn_per_second"]), int(i["item_id"])))
        self.player_class.amount_of_countries = len(self.countries)

    def default_shop(self):
        self.farms.append(PassiveFarmer("Tea Farm", 100, 1, 0))
        self.farms.append(PassiveFarmer("Coffee Farm", 1000, 2, 1))
        self.farms.append(PassiveFarmer("Salt Farm", 3000, 3, 2))

    def default_buy(self):
        for j in range(3):
            for i in range(3):
                self.buy_farm(i, 1)
        self.player_class.farms_class.print_formatted_player_farms()

    def get_current_farm(self):
        table = PrettyTable()
        table.field_names = ["Farm ID", "Farm Name", "Cost", "Production"]
        counter = 0
        for i in self.farms:
            table.add_row(
                [counter, i.get_name(),
                 i.get_current_cost(self.player_class.farms_class.get_amount_of_farms(i.get_item_id())),
                 i.get_item_production()])
            counter += 1
        print(table)

    def get_current_countries(self):
        table = PrettyTable()
        table.field_names = ["Country ID", "Country Name", "Cost", "Production", "Is Bought?"]
        counter = 0
        for i in self.countries:
            table.add_row(
                [counter, i.get_name(),
                 i.get_current_cost(self.player_class.farms_class.get_amount_of_farms(i.get_item_id())),
                 i.get_item_production(), i.get_is_bought()])
            counter += 1
        print(table)

    def get_player_input(self):
        print('type <help> if you are newbie')
        while True:
            player_input = StaticMethods.process_player_input()
            # print(player_input)
            if player_input[0] == "buy" and player_input[1] == "farm":
                farm_id = int(player_input[2])
                amount = int(player_input[3])
                self.buy_farm(farm_id, amount)
                self.player_class.farms_class.print_formatted_player_farms()
            if player_input[0] == "buy" and player_input[1] == "country":
                country_id = int(player_input[2])
                self.buy_country(country_id)
                self.player_class.countries_class.print_formatted_player_farms()
            if player_input[0] == "get" and player_input[1] == "bal":
                print(f"Player balance: {self.player_class.player_money}")
            if player_input[0] == "farms":
                self.get_current_farm()
            if player_input[0] == "countries":
                self.get_current_countries()
            if player_input[0] == "get" and player_input[1] == "inventory":
                self.player_class.farms_class.print_formatted_player_farms()
                self.player_class.countries_class.print_formatted_player_farms()
            if player_input[0] == "help":
                StaticMethods.print_help(self.commands_list)
            if player_input[0] == "leave" and player_input[1] == "shop":
                break

    def __init__(self, player_class):
        self.player_class = player_class
        self.farms = []
        self.countries = []
        self.commands_list = [["buy {shop_id} {amount}", "buy a farm with a {shop_id} in quantity {amount}"],
                              ["get_bal", "Returns you the wallet"], ["farms", "Returns catalogue in the farm shop"],
                              ["countries", "Returns catalogue in the country shop"],
                              ["get_inventory", "Returns your property"], ["leave_shop", "Exit the shop"]]
        self.default_shop()
        self.add_countries()
        # self.default_buy()
        # self.get_player_input()


class PassiveCounter(threading.Thread):
    def start_earn(self):
        while self.not_stopped:
            self.player_class.player_money += self.earn_per_second

            # print(
            #     f"Passive counter id: {self.thread_id} earned: {self.earn_per_second}, total balance: {self.player_class.player_money}")
            time.sleep(self.earn_time)

    def get_current_earn(self):
        print(self.earn_per_second)

    def update_earn(self, earn_per_second):
        self.earn_per_second = earn_per_second

    def stop_earn(self):
        self.not_stopped = False

    def run(self):
        self.start_earn()

    def __init__(self, earn_per_second, player_class, thread_id):
        super().__init__()
        self.earn_per_second = earn_per_second

        self.earn_time = 1
        self.not_stopped = True
        self.player_class = player_class
        self.thread_id = thread_id


class Game:
    def __init__(self, player_class, money_per_guess):
        self.list_of_words = ["democracy", "influence", "enemy", "destroy", "eliminate", "kill"]
        self.list_of_questions = []
        self.player_class = player_class
        self.money_per_guess = money_per_guess
        self.parse_json()
        self.engine = pyttsx3.init()

    def parse_json(self):
        import json
        with open("questions.json", 'r', encoding="utf-8") as file:
            data = json.load(file)
        self.list_of_questions = data["questions"]

    def random_question(self):
        # print(len(self.list_of_questions))
        question_index = rd.randint(0, len(self.list_of_questions) - 1)
        return self.list_of_questions[question_index]

    def generate_word(self):

        word_index = rd.randint(0, len(self.list_of_words) - 1)
        return self.list_of_words[word_index]

    def player_input(self):
        while True:
            question = self.random_question()

            print(question["question"])
            correct_answer = question["correct_answer"]
            player_input = StaticMethods.process_player_input()
            if player_input[0] == "exit":
                break
            if player_input[0] == str(correct_answer):
                self.player_class.player_money += self.money_per_guess
                print(f"Received: {self.money_per_guess}, balance: {self.player_class.player_money}")
            else:
                print(f"Incorrect\ncorrect is: {str(correct_answer)}")


class Menu:
    def open_shop(self):
        self.shop_class.get_player_input()

    def show_world_progress(self):
        print(
            f"{math.ceil(self.player_class.bought_countries / self.player_class.amount_of_countries * 100)}%/100%({self.player_class.bought_countries}/{self.player_class.amount_of_countries})")

    def save_player_stats(self):
        self.player_class.save_progress()

    def load_player_stats(self):
        self.player_class.load_progress()

    def player_input(self):
        print('type <help> if you are a newbie')
        while True:
            player_input = StaticMethods.process_player_input()
            if player_input[0] == "open" and player_input[1] == "shop":
                self.open_shop()
            if player_input[0] == "save":
                self.save_player_stats()
            if player_input[0] == "load":
                self.load_player_stats()
            if player_input[0] == "world" and player_input[1] == "progress":
                self.show_world_progress()
            if player_input[0] == "work":
                self.game_class.player_input()
            if player_input[0] == "help":
                # self.print_help()
                StaticMethods.print_help(self.commands_list)

    def __init__(self):
        self.passive_threads = []
        self.player_class = Player()
        self.commands_list = [["open shop", "It opens shop"], ["work", "It starts work"],
                              ["world progress", "Shows your world democratisation progress"]]
        self.shop_class = Shop(self.player_class)
        self.game_class = Game(self.player_class, 50)
        self.player_class.shop_class = self.shop_class
        self.load_player_stats()
        self.player_input()
        # for i in range(2):
        #     passive = PassiveCounter(i + 1, self, i).start()
        #     self.passive_threads.append(passive)


test = Menu
test()
