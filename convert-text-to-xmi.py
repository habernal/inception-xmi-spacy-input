# python -m spacy download en_core_web_sm-3.0.0 --direct
from pathlib import Path
from typing import List

import cassis
import spacy
from cassis import Cas
from cassis.typesystem import Type
from spacy.tokens import Token, Doc

# init spacy
nlp: spacy.Language = spacy.load("en_core_web_sm")


def convert_single_file(input_paragraph_list: List[str], output_xmi_file: str) -> None:
    document_text = '\n'.join(input_paragraph_list)

    cas = Cas(typesystem=cassis.load_dkpro_core_typesystem())
    cas.sofa_string = document_text

    print("----")
    print(document_text)
    print("----")

    token_type: Type = cas.typesystem.get_type(
        'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token')
    paragraph_type: Type = cas.typesystem.get_type(
        'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Paragraph')
    sentence_type: Type = cas.typesystem.get_type(
        'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence')

    total_doc_offset: int = 0
    for paragraph_str in input_paragraph_list:
        this_paragraph_total_offset = total_doc_offset

        doc: Doc = nlp(paragraph_str)

        for token in doc:
            assert isinstance(token, Token)
            # print(token.text, token.idx, len(token), token.idx + len(token), token.is_space)
            begin: int = total_doc_offset + token.idx
            end: int = total_doc_offset + token.idx + len(token)
            # annotate token -- only if it is not a space!
            if not token.is_space:
                cas.add_annotation(token_type.__call__(begin=begin, end=end))

        total_doc_offset += len(paragraph_str)

        # annotate paragraph
        this_paragraph_annotation = paragraph_type.__call__(
            begin=this_paragraph_total_offset, end=total_doc_offset)
        cas.add_annotation(this_paragraph_annotation)
        # and for paragraph too; but how about the '\n' char? maybe +1?
        total_doc_offset += 1

        # add sentences aligned exactly to paragraphs
        cas.add_annotation(sentence_type.__call__(
            begin=this_paragraph_annotation.begin,
            end=this_paragraph_annotation.end))

    print([x.get_covered_text() for x in cas.select(paragraph_type.name)])
    print([x.get_covered_text() for x in cas.select(sentence_type.name)])
    print([x.get_covered_text() for x in cas.select(token_type.name)])

    # create parent folder if not exists
    Path(output_xmi_file).parent.mkdir(parents=True, exist_ok=True)

    cas.to_xmi(output_xmi_file)


if __name__ == '__main__':
    input_paragraphs = ['This is the first paragraph. It contains two sentences.',
                        'This seems to be the second paragraph with only one sentence.']
    convert_single_file(input_paragraphs, '/tmp/output-uima-cas-xmi-xml-1.1.xmi')
