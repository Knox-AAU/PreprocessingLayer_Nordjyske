import argparse
import json
import codecs

from knox_source_data_io.io_handler import IOHandler, Generator

from nitf_parser.parser import NitfParser

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # defines input and output path
    parser.add_argument('input_file', help='The XML file to read. Must be NITF')

    # defines toDate argument
    parser.add_argument('-o', '--output_dest', dest="output_dest", default=None,
                        help='Save JSON to this location. If not specified, the module will output to stdout.')

    args = parser.parse_args()

    nitf_parser = NitfParser()
    publication = nitf_parser.parse(args.input_file)

    if args.output_dest is not None:
        handler = IOHandler(Generator(app="NITF Parser", version=1.0), "https://repos.knox.cs.aau.dk/schema/publication.schema.json")
        with codecs.open(args.output_dest, 'w', encoding="utf-8") as outfile:
            handler.write_json(publication, outfile)
    else:
        print(publication)
