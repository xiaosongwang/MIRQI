"""Entry-point script to label radiology reports."""
import pandas as pd

from utils import ArgParser
from utils import Loader
from processors import Extractor, Classifier, Aggregator
from predefined.constants import *
from pathlib import Path


def write(reports, labels, output_path, verbose=False):
    """Write labeled reports to specified path."""
    labeled_reports = pd.DataFrame({REPORTS: reports})
    # for index, category in enumerate(CATEGORIES):
    #     labeled_reports[category] = labels[:, index]
    labeled_reports['attributes'] = labels

    if verbose:
        print(f"Writing reports and labels to {output_path}.")
    labeled_reports[[REPORTS] + ['attributes']].to_csv(output_path,
                                                   index=False)

class Labelor(object):
    def __init__(self, ref_path, verbose=False):
        self.extractor = Extractor(ref_path['mention_phrases_dir'],
                              ref_path['unmention_phrases_dir'],
                              verbose=verbose)
        self.classifier = Classifier(ref_path['pre_negation_uncertainty_path'],
                                ref_path['negation_path'],
                                ref_path['post_negation_uncertainty_path'],
                                verbose=verbose)
        self.aggregator = Aggregator(CATEGORIES,
                                verbose=verbose)


    def label(self, report_pairs, reports_path, extract_impression):
        """Label the provided report(s)."""
        # Load reports in place.
        loader = Loader(report_pairs, reports_path, extract_impression)
        loader.load()
        # Extract observation mentions in place.
        self.extractor.extract(loader.collection)
        # Classify mentions in place.
        self.classifier.classify(loader.collection)
        # output mentions/categories/negation/attributes
        attributes = self.aggregator.getAttributeOutput(loader.collection)
        # # Aggregate mentions to obtain one set of labels for each report.
        # labels = aggregator.aggregate(loader.collection)

        return loader.reports, attributes

# Medical Image Reporting Quality Indexing
def MIRQI(gt_list, cand_list, pos_weight=0.8, attribute_weight=0.3, verbose=False):
    """Compute the score of matching keyword and associated attributes between gt list and candidate list.
       It returns two scores:   MIRQI-r (recall: hits in gt)
                                MIRQI-p (precision: correct ratio of all candidates)
    """

    MIRQI_r = []
    MIRQI_p = []
    MIRQI_f = []

    for gt_report_entry, cand_report_entry in zip(gt_list, cand_list):
        attribute_cand_all = []

        pos_count_in_gt = 0
        pos_count_in_cand = 0
        tp = 0.0
        fp = 0.0
        tn = 0.0
        fn = 0.0

        for gt_entity in gt_report_entry:
            if gt_entity[2] == 'NEGATIVE':
                continue
            pos_count_in_gt = pos_count_in_gt + 1
        neg_count_in_gt = len(gt_report_entry) - pos_count_in_gt

        for entity_index, cand_entity in enumerate(cand_report_entry):
            if cand_entity[2] == 'NEGATIVE':
                for entity_index, gt_entity in enumerate(gt_report_entry):
                    if  gt_entity[1] == cand_entity[1]:
                        if gt_entity[2] == 'NEGATIVE':
                            tn = tn + 1     # true negative hits
                            break
                        else:
                            fn = fn + 1     # false negative hits
                            break
            else:
                pos_count_in_cand = pos_count_in_cand + 1
                for entity_index, gt_entity in enumerate(gt_report_entry):
                    if gt_entity[1] == cand_entity[1]:
                        if gt_entity[2] == 'NEGATIVE':
                            fp = fp + 1     # false positive hits
                            break
                        else:
                            tp = tp + 1.0 - attribute_weight    # true positive hits (key words part)
                            # count attribute hits
                            if gt_entity[3] == '':
                                break
                            attributes_all_gt = gt_entity[3].split('/')
                            attribute_hit_count = 0
                            for attribute in attributes_all_gt:
                                if attribute in cand_entity[3]:
                                    attribute_hit_count = attribute_hit_count + 1
                            # true positive hits (attributes part)
                            tp = tp + attribute_hit_count/len(attributes_all_gt)*attribute_weight
                            break
        neg_count_in_cand = len(cand_report_entry) - pos_count_in_cand
        #
        # calculate score for positive/uncertain mentions
        if pos_count_in_gt == 0 and pos_count_in_cand == 0:
            score_r = 1.0
            score_p = 1.0
        elif pos_count_in_gt == 0 and pos_count_in_cand != 0:
            score_r = 0.0
            score_p = 0.0
        elif pos_count_in_gt != 0 and pos_count_in_cand == 0:
            score_r = 0.0
            score_p = 0.0
        else:
            score_r = tp / (tp + fn + 0.000001)
            score_p = tp / (tp + fp + 0.000001)

        # calculate score for negative mentions
        # if neg_count_in_cand != 0 and neg_count_in_gt != 0:
        if tn != 0:
            score_r = score_r * pos_weight + tn / (tn + fp + 0.000001) * (1.0 - pos_weight)
            score_p = score_p * pos_weight + tn / (tn + fn + 0.000001) * (1.0 - pos_weight)

        MIRQI_r.append(score_r)
        MIRQI_p.append(score_p)
        MIRQI_f.append(2*(score_r * score_p) / (score_r + score_p) if (score_r + score_p) != 0.0 else 0.0)

    return MIRQI_r, MIRQI_p, MIRQI_f







if __name__ == "__main__":
    parser = ArgParser()
    args = parser.parse_args()
    ref_path = dict.fromkeys(['mention_phrases_dir',
                              'unmention_phrases_dir',
                              'pre_negation_uncertainty_path',
                              'negation_path',
                              'post_negation_uncertainty_path'])
    ref_path['mention_phrases_dir'] = Path('predefined/phrases/mention')
    ref_path['unmention_phrases_dir'] = Path('predefined/phrases/unmention')
    ref_path['pre_negation_uncertainty_path'] = 'predefined/patterns/pre_negation_uncertainty.txt'
    ref_path['negation_path'] = 'predefined/patterns/negation.txt'
    ref_path['post_negation_uncertainty_path'] = 'predefined/patterns/post_negation_uncertainty.txt'

    labelor = Labelor(ref_path, args.verbose)
    reports, labels = labelor.label(args.report_gt, args.reports_path_gt, args.extract_impression)
    reports_cand, labels_cand = labelor.label(args.report_cand, args.reports_path_cand, args.extract_impression)
    score_r, score_p, score_f = MIRQI(labels, labels_cand)
    print(score_r, score_p, score_f)

    # write(reports, labels, args.output_path, args.verbose)
