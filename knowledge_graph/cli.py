import click

from . import convert_csv, import_csv, post_process


@click.group(chain=True)
def main():
    pass


main.add_command(convert_csv.main)
main.add_command(import_csv.main)
main.add_command(post_process.main)


if __name__ == "__main__":
    main()
