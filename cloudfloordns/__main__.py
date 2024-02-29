import click


# Keep it as the main entry point
@click.group()
def cli():
    pass


# Add here your subcommands if needed
# cli.add_command(main)

if __name__ == "__main__":
    cli()
