import os
import logging
import time
import smtplib
import datetime
from os import walk
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from os import path
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

APP_HOME = "/home/rishav/work/pycharmProjects/social_studio_app_automation"
SCRIPTS_DIR = path.join(APP_HOME, "automater_scripts")

# constants start
DOWNLOAD_DIR = "csv"
LOGS_DIR = "logs"
DRIVER = 'chromedriver'
# constants end


# logging setup start
def create_dir_if_not_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)


create_dir_if_not_exists(LOGS_DIR)
todays_date = str(datetime.datetime.today().strftime('%Y-%m-%d'))

logger = logging.getLogger("automater")
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler(os.path.join(LOGS_DIR, todays_date + '.log'))
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s")

fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(ch)
logger.addHandler(fh)


# logging setup finished

class Parser:
    attr_instruction = "instruction"
    attr_command = "command"
    attr_message = "message"
    attr_identifier = "identifier"
    attr_identifier_value = "identifier_value"
    attr_field_input = "field_input"

    command_open = "open"
    command_mode = "mode"
    command_refresh = "refresh"
    command_click = "click"
    command_set = "set"
    command_run = "run"
    command_sleep = "sleep"
    command_log = "log"
    commands = [command_run, command_open, command_mode, command_click, command_set, command_sleep, command_log]

    separator_with = "with"
    separator_http = "http"

    identifier_xpath = "xpath"
    identifier_class = "class"
    identifier_id = "id"

    identifier_variable = "var"
    identifier_date = "current_date"
    identifier_format = "format"

    time_unit_day = "day"

    def __init__(self, path):
        self.script_path = path
        self.commands = []
        self.variables = {}
        self.parse()

    def parse(self):
        for instruction in open(self.script_path).readlines():
            if self.is_valid(instruction):
                instruction = instruction.strip().replace("  ", " ")
                if Parser.identifier_variable in instruction:
                    variable_name, value = self.parse_variables(instruction)
                    self.variables[variable_name] = value
                else:
                    command, message, identifier, identifier_value, field_input = self.parse_instruction(instruction)
                    self.commands.append({
                        Parser.attr_instruction: instruction,
                        Parser.attr_command: command,
                        Parser.attr_message: message,
                        Parser.attr_identifier: identifier,
                        Parser.attr_identifier_value: self.replace_with_variable(identifier_value, self.variables),
                        Parser.attr_field_input: field_input
                    })

    def parse_instruction(self, instruction):
        command, instruction = self.parse_command(instruction)
        message, instruction = self.parse_message(command, instruction)
        identifier, identifier_value, instruction = self.parse_identifier(command, instruction)
        field_input = self.parse_field_input(command, instruction)
        return command, message, identifier, identifier_value, field_input

    def is_valid(self, instruction):
        # todo add validation
        return instruction.strip() != ""

    def parse_command(self, instruction):
        first_position = 0
        if ' ' in instruction:
            first_position = instruction.index(' ')
        else:
            first_position = len(instruction)
        command = instruction[:first_position]
        instruction = instruction[first_position + 1:]
        return command.strip(), instruction.strip()

    def parse_message(self, command, instruction):
        message = ''
        if Parser.command_open == command:
            message = instruction[: instruction.index(Parser.separator_http)]
            instruction = instruction.replace(message, '', 1)
        elif Parser.command_click == command:
            message = instruction[: instruction.index(Parser.separator_with)]
            instruction = instruction.replace(message, '', 1).replace(Parser.separator_with, '', 1)
        elif Parser.command_set == command:
            message = instruction[: instruction.index("\"")]
            instruction = instruction.replace(message, '', 1).replace(Parser.separator_with, '', 1)
        elif Parser.command_log == command:
            message = instruction
            instruction = ''

        return message.strip(), instruction.strip()

    def parse_identifier(self, command, instruction):
        identifier = ''

        if Parser.identifier_xpath in instruction:
            identifier = Parser.identifier_xpath
        elif Parser.identifier_class in command:
            identifier = Parser.identifier_class
        elif Parser.identifier_id == command:
            identifier = Parser.identifier_id

        identifier_value = instruction[instruction.index(identifier) + len(identifier):]
        instruction = instruction.replace(identifier, '', 1).replace(identifier_value, '', 1)
        return identifier.strip(), identifier_value.strip(), instruction.strip()

    def parse_field_input(self, command, instruction):
        if (Parser.command_set == command):
            return instruction.replace("\"", "").strip()
        elif instruction != '':
            logger.error("Unexpected instruction : " + instruction)
        return ''

    def parse_variables(self, instruction):
        variable = instruction[instruction.index(Parser.identifier_variable) + len(Parser.identifier_variable)
                               : instruction.index("=")]
        instruction = instruction[instruction.index("=") + 1:].strip()
        if (Parser.identifier_date in instruction):
            date = self.parse_date(instruction)
            return variable.strip(), date
        else:
            return variable.strip(), instruction

    def parse_date(self, instruction):
        format = instruction[instruction.index(Parser.identifier_format) + len(Parser.identifier_format):].strip()
        integral_part = [int(s) for s in instruction.split() if s.isdigit()][0]
        if '-' in instruction:
            return str(int((datetime.datetime.today() - datetime.timedelta(integral_part)).strftime(format)))
        elif '+' in instruction:
            return str(int((datetime.datetime.today() + datetime.timedelta(integral_part)).strftime(format)))

    def replace_with_variable(self, identifier_value, variables):
        if (identifier_value != ''):
            for variable, value in variables.items():
                item_to_replace = "'\"+" + variable + "+\"'"
                if item_to_replace in identifier_value:
                    identifier_value = identifier_value.replace(item_to_replace, "'" + value + "'")
        return identifier_value


class Automater:

    def __init__(self):
        self.scripts = {}
        self.driver = None
        self.load_scripts()

    def load_scripts(self):
        for dirpath, dirnames, filenames in walk(SCRIPTS_DIR):
            for filename in filenames:
                script_path = path.join(dirpath, filename)
                logger.info("Parsing script at path : " + script_path)
                parser = Parser(script_path)
                self.scripts[script_path] = parser

    def execute_scripts(self):
        for script_path, parser in self.scripts.items():
            for command in parser.commands:
                if self.driver == None:
                    self.initialize_chrome_driver(command[Parser.attr_identifier_value])
                logger.info(command[Parser.attr_instruction])
                self.execute_command(command)

    def execute_command(self, command):
        if Parser.command_refresh == command[Parser.attr_command]:
            return self.driver.refresh()
        if Parser.command_click == command[Parser.attr_command]:
            self.perform_click(command)
        elif Parser.command_open == command[Parser.attr_command]:
            self.driver.get(command[Parser.attr_identifier_value])
        elif Parser.command_set == command[Parser.attr_command]:
            self.set_input_field(command)
        elif Parser.command_sleep == command[Parser.attr_command]:
            time.sleep(int(command[Parser.attr_identifier_value]))

    def initialize_chrome_driver(self, mode):
        chrome_options = Options()
        if "headless" in mode:
            chrome_options.add_argument("--headless")
        csv_download_dir = os.path.join(DOWNLOAD_DIR, todays_date)
        create_dir_if_not_exists(csv_download_dir)
        prefs = {'download.default_directory': csv_download_dir}
        chrome_options.add_experimental_option('prefs', prefs)
        self.driver = webdriver.Chrome(DRIVER, options=chrome_options)
        self.enable_download_in_headless_chrome(self.driver, csv_download_dir)
        self.driver.implicitly_wait(60)

    def get_element_if_exists(self, xpaths):
        for xpath in xpaths.split("~or~"):
            try:
                return self.driver.find_element_by_xpath(xpath.strip())
            except:
                logger.error("Element not found, xpath : " + xpath)

    def enable_download_in_headless_chrome(self, driver, download_dir):
        driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')

        params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
        command_result = driver.execute("send_command", params)

    def perform_click(self, command):
        if Parser.identifier_xpath == command[Parser.attr_identifier]:
            self.get_element_if_exists(command[Parser.attr_identifier_value]).click()
        elif Parser.identifier_id == command[Parser.attr_identifier]:
            self.driver.find_element_by_id(command[Parser.attr_identifier_value]).click()
        elif Parser.identifier_class == command[Parser.attr_identifier]:
            self.driver.find_elements_by_class_name(command[Parser.attr_identifier_value]).click()

    def set_input_field(self, command):
        if Parser.identifier_xpath == command[Parser.attr_identifier]:
            self.get_element_if_exists(command[Parser.attr_identifier_value]) \
                .send_keys(command[Parser.attr_field_input])
        elif Parser.identifier_id == command[Parser.attr_identifier]:
            self.driver.find_element_by_id(command[Parser.attr_identifier_value]) \
                .send_keys(command[Parser.attr_field_input])
        elif Parser.identifier_class == command[Parser.attr_identifier]:
            self.driver.find_elements_by_class_name(command[Parser.attr_identifier_value]) \
                .send_keys(command[Parser.attr_field_input])

if __name__ == "__main__":
    try:
        automater = Automater()
        automater.execute_scripts()
    except Exception as e:
        logger.error(e)
