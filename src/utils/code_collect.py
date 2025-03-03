import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def collect_codebase(output_file='codebase.txt', modules=None):
    if modules is None:
        modules = [
            'main.py',
            'handlers/message_handler.py',
            'handlers/task_handler.py',
            'handlers/start_handler.py',
            'handlers/stop_handler.py',
            'handlers/delete_handler.py',
            'handlers/model_handler.py',
            'handlers/error_handler.py',
            'utils/ssh_utils.py',
            'utils/state_utils.py',
            'utils/logging_config.py',
            'constants.py',
        ]

    output_path = os.path.join(BASE_DIR, output_file)
    with open(output_path, 'w', encoding='utf-8') as outfile:
        for module in modules:
            module_path = os.path.join(BASE_DIR, 'src', module)
            try:
                with open(module_path, 'r', encoding='utf-8') as infile:
                    contents = infile.read()
                outfile.write(f'{module}:\n')
                outfile.write('```\n')
                outfile.write(contents)
                if not contents.endswith('\n'):
                    outfile.write('\n')
                outfile.write('```\n')

            except FileNotFoundError:
                outfile.write(f'{module}:\n')
                outfile.write('```\n')
                outfile.write(f'# File not found: {module_path}\n')
                outfile.write('```\n')
        outfile.write(
            '\n---\n'
            'dont forget about max length 79 characters, pep 8, single quotes and '
            'double blank lines between classes and functions. please refactor if not so.\n'
            '---\n'
        )


if __name__ == '__main__':
    collect_codebase()