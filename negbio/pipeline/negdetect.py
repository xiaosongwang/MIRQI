import logging
import re

from negbio.neg.neg_detector import Detector
from negbio.neg import utils, semgraph, propagator


def neg_mesh(annotations):
    """
    Detect negative MeSH
    """
    for ann in annotations:
        if ann.infons.get('CUI', None) == 'C0332125':
            ann.infons[Detector.NEGATION] = 'True'


def uncertain_mesh(annotations):
    """
    Detect uncertain MeSH
    """
    for ann in annotations:
        if ann.infons.get('CUI', None) == 'C0332148':
            ann.infons[Detector.UNCERTAINTY] = 'True'


def is_neg_regex(text):
    if re.search(r'^(findings|impression): no ', text, re.I):
        return True
    return False


def _mark_anns(annotations, begin, end, type):
    """Mark all annotations in [begin:end] as type"""
    for ann in annotations:
        total_loc = ann.get_total_location()
        if begin <= total_loc.offset and total_loc.offset + total_loc.length <= end:
            ann.infons[type] = 'True'

def _mark_anns_attribute(annotations, begin, end, type, value):
    """Mark all annotations in [begin:end] as type"""
    for ann in annotations:
        total_loc = ann.get_total_location()
        if begin <= total_loc.offset and total_loc.offset + total_loc.length <= end:
            ann.infons[type] = value

def _extend(document, type):
    def _is_type(annotation):
        return annotation.infons.get(type, None) == 'True'

    neg_anns = []
    for passage in document.passages:
        for ann in passage.annotations:
            if _is_type(ann):
                neg_anns.append(ann)

    for passage in document.passages:
        for ann in passage.annotations:
            if not _is_type(ann):
                for nann in neg_anns:
                    if ann in nann:
                        ann.infons[type] = 'True'
                        break
                    if nann in ann and 'CUI' in ann and 'CUI' in nann and ann.infons['CUI'] == nann.infons['CUI']:
                        ann.infons[type] = 'True'
                        break


def detect(document, detector):
    """
    Args:
        document(BioCDocument):
        detector(Detector): detector. Define customized patterns in the detector
    """
    try:

        for passage in document.passages:
            neg_mesh(passage.annotations)
            uncertain_mesh(passage.annotations)

            locs = []
            for ann in passage.annotations:
                total_loc = ann.get_total_location()
                locs.append((total_loc.offset, total_loc.offset + total_loc.length))

            for sentence in passage.sentences:
                if is_neg_regex(sentence.text):
                    _mark_anns(passage.annotations, sentence.offset, sentence.offset + len(sentence.text),
                               Detector.NEGATION)
                    continue
                for name, matcher, loc in detector.detect(sentence, locs):
                    logging.debug('Find: %s, %s, %s', name, matcher.pattern, loc)
                    _mark_anns(passage.annotations, loc[0], loc[1], name)

        # _extend(document, Detector.NEGATION)
        # _extend(document, Detector.UNCERTAINTY)
    except:
        logging.exception("Cannot process %s", document.id)
    return document


def extractAttribute(document, detector):
    """
    Args:
        document(BioCDocument):
        detector(Detector): detector. Define customized patterns in the detector
    """
    try:

        for passage in document.passages:
            # neg_mesh(passage.annotations)
            # uncertain_mesh(passage.annotations)

            # locs = []
            for ann in passage.annotations:
                term = ann.text
                # total_loc = ann.get_total_location()
                # locs.append((total_loc.offset, total_loc.offset + total_loc.length))

                for sentence in passage.sentences:
                    sen_len = len(sentence.text)
                    in_range = 0
                    for location in ann.locations:
                        if location.offset >= sentence.offset and location.offset <= sentence.offset + sen_len:
                            in_range = 1
                    if not in_range:
                        continue

                    id_term = []
                    attribute_words = ''
                    attribute_word_id = []
                    for ann_in_sen in sentence.annotations:
                        if (ann_in_sen.text in term or term in ann_in_sen.text):# and ann_in_sen.infons['tag'] in ['NN','RB']:
                            id_term.append(ann_in_sen.id)

                    for relation in sentence.relations:
                        if relation.infons['dependency'] in ['amod','nsubj','dep','neg','dobj',
                                                             'conj:or','compound','nmod:within',
                                                             'advmod',]:
                            if relation.nodes[0].refid in id_term \
                                    and relation.nodes[1].refid not in id_term:
                                attribute_word_id.append(relation.nodes[1].refid)
                            elif relation.nodes[1].refid in id_term \
                                    and relation.nodes[0].refid not in id_term:
                                attribute_word_id.append(relation.nodes[0].refid)

                    for ann_in_sen in sentence.annotations:
                        if ann_in_sen.id in attribute_word_id  \
                                    and ann_in_sen.infons['tag'] not in ['LS', 'VB']:
                            if attribute_words == '':
                                attribute_words = attribute_words + ann_in_sen.text
                            else:
                                attribute_words = attribute_words + '/' + ann_in_sen.text

                    ann.infons['attributes'] = ann.infons['attributes'] + attribute_words
    except:
        logging.exception("Cannot process %s", document.id)
    return document