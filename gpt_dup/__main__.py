import argparse
import pathlib
import re

from openai import OpenAI


def main():
    description = """ 
    Duplicates and refreshes a given math problem via chatGPT, updating 
    numbers and solutions as needed.  Results will vary, but this tool has been
    successful for many simple math problems from CS1800 given a well 
    formated latex template. 
    """
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('-f', '--file', type=str, help='Input File',
                        required=True)
    parser.add_argument('-k', '--key', type=str, help='openai api key')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='run in quiet mode')
    args = parser.parse_args()

    new_prob = duplicate(file=args.file)
    file_out = get_file_out_add_one(file=args.file)

    with open(file_out, 'w') as f:
        f.write(new_prob)

    if not args.quiet:
        print(new_prob)
        print(f'written to: {file_out}')


def duplicate(file=None, s=None, model='gpt-4o', api_key=None):
    assert (file is None) != (s is None), 'file xor s required'

    if s is None:
        s = open(file).read()

    if api_key is None:
        from gpt_dup.key import api_key
    if api_key is None:
        api_key = input('No OPENAI_API_KEY environment variable found, '
                        'enter here:')

    client = OpenAI(api_key=api_key)

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {'role': 'user',
             'content': f'Provide a file in a similar format, rewriting '
                        f'the math problem with new numbers and updating '
                        f'the solutions as needed to ensure correctness?\n'
                        f'"{s}"'}
        ]
    )
    return completion.choices[0].message.content


def get_file_out_add_one(file, z_fill_width=2):
    file = pathlib.Path(file)

    # get old idx (if present)
    match = re.search('\d+$', file.stem)
    if match is None:
        new_idx = 0
        stem_old = file.stem
    else:
        grp = match.group()
        new_idx = int(grp) + 1
        stem_old = file.stem[:-len(grp)]

    for _ in range(1000):
        file_out = file.with_stem(stem_old + str(new_idx).zfill(z_fill_width))
        if not file_out.exists():
            return file_out

    raise RuntimeError(f'no unique file out created: {file}')


if __name__ == '__main__':
    main()
