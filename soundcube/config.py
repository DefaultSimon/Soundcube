# coding=utf-8
import configparser

config = configparser.ConfigParser()
config.read("data/settings.ini")


def get_config(section, key):
    return config.get(section, key)
