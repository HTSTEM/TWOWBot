import os
import shutil

from cogs.util.bot import TWOWBot


def main():
    bot = TWOWBot()

    if not os.path.exists('config.yml'):
        shutil.copy('config.example.yml', 'config.yml')

    bot.run()


if __name__ == '__main__':
    main()
