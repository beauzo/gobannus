from .cli import cli


def main():
    cli(
        obj={},
        auto_envvar_prefix='GOBCLI'
    )


if __name__ == '__main__':
    main()
