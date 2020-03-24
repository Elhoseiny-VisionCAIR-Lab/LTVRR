
# coding: utf-8

# ## Analyze the behavior of various networks predicting S,O,P triplets; while paying attention to their comparative perfomance at the long-tail of the training distribution.

# In[5]:

import numpy as np
import pandas as pd
import os.path as osp
# import seaborn as sns # not critical.
import matplotlib.pylab as plt


# In[9]:

import os
import re


def files_in_subdirs(top_dir, search_pattern):  # TODO: organize project as proper
    join = os.path.join                         # python module (e.g. see https://docs.python-guide.org/writing/structure/) then move this function
    regex = re.compile(search_pattern)          # e.g. in the helper.py
    for path, _, files in os.walk(top_dir):
        for name in files:
            full_name = join(path, name)
            if regex.search(full_name):
                yield full_name


def keep_only_heavy_tail_observations(dataframe, prediction_type, threshold_of_tail):
    df = dataframe.copy()
    freqs = df[[gt_prefix + '_' + prediction_type, prediction_type + '_freq_gt']]
    unique_freqs = freqs.groupby(gt_prefix + '_' + prediction_type).mean() # assumes same
    unique_freqs = unique_freqs.sort_values(prediction_type + '_freq_gt', ascending=False)
    n_total_occurences = unique_freqs.sum()
    unique_freqs[prediction_type + '_freq_gt'] /= float(n_total_occurences)
    valid = unique_freqs[unique_freqs.cumsum()[prediction_type + '_freq_gt'] > threshold_of_tail].index
    df = df[df[gt_prefix + '_' + prediction_type].isin(valid)]
    return df

def get_many_medium_few_scores(csv_path, cutoffs, syn):
    df = pd.read_csv(csv_path)
    # df = df.groupby(['gt_sbj', 'gt_rel', 'gt_obj']).mea)
    df['box_id'] = df.groupby('image_id').cumcount()
    metric_type = 'top1'
    all_prediction_types = ['rel', 'obj', 'sbj']
    if syn:
        syn_obj = pd.read_csv('./data/gvqa/objects_synsets.csv')
        syn_obj = syn_obj[['object_name', 'synset']]
        syn_obj.set_index('object_name', inplace=True)

        syn_prd = pd.read_csv('./data/gvqa/predicates_synsets.csv')
        syn_prd = syn_prd[['predicate_name', 'synset']]
        syn_prd.set_index('predicate_name', inplace=True)

    for prediction_type in all_prediction_types:
        df[prediction_type + '_' + metric_type] = df[prediction_type + '_rank'] < int(metric_type[3:])

    if syn:
        for prediction_type in ['sbj', 'obj']:
            df['gt_' + prediction_type + '_syn'] = syn_obj.loc[df['gt_' + prediction_type], 'synset'].to_list()
            df['det_' + prediction_type + '_syn'] = syn_obj.loc[df['det_' + prediction_type], 'synset'].to_list()
            df[prediction_type + '_top1_syn'] = df['gt_' + prediction_type + '_syn'] == df['det_' + prediction_type + '_syn']

        for prediction_type in ['rel']:
            df['gt_' + prediction_type + '_syn'] = syn_prd.loc[df['gt_' + prediction_type], 'synset'].to_list()
            df['det_' + prediction_type + '_syn'] = syn_prd.loc[df['det_' + prediction_type], 'synset'].to_list()
            df[prediction_type + '_top1_syn'] = df['gt_' + prediction_type + '_syn'] == df['det_' + prediction_type + '_syn']

    df['triplet_top1'] = df['rel_top1'] & df['sbj_top1'] & df['obj_top1']
    if syn:
        df['triplet_top1_syn'] = df['rel_top1_syn'] & df['sbj_top1_syn'] & df['obj_top1_syn']

    cutoff, cutoff_medium = cutoffs

    a = df.groupby('gt_rel').mean()
    classes_rel = (list(a.sort_values('rel_freq_gt').index))
    freqs_rel = (list(a.sort_values('rel_freq_gt')['rel_freq_gt']))
    classes_rel_few = classes_rel[:int(len(classes_rel)*cutoff)]
    classes_rel_medium = classes_rel[int(len(classes_rel)*cutoff):int(len(classes_rel)*cutoff_medium)]
    classes_rel_many = classes_rel[int(len(classes_rel)*cutoff_medium):]
    # freqs_rel = freqs_rel[:int(len(classes_rel)*cutoff)]

    a = df.groupby('gt_sbj').mean()
    classes_sbj = (list(a.sort_values('sbj_freq_gt').index))
    freqs_sbj = (list(a.sort_values('sbj_freq_gt')['sbj_freq_gt']))
    classes_sbj_few = classes_sbj[:int(len(classes_sbj)*cutoff)]
    classes_sbj_medium = classes_sbj[int(len(classes_sbj)*cutoff):int(len(classes_sbj)*cutoff_medium)]
    classes_sbj_many = classes_sbj[int(len(classes_sbj)*cutoff_medium):]
    # freqs_sbj = freqs_sbj[:int(len(classes_sbj)*cutoff)]

    a = df.groupby('gt_obj').mean()
    classes_obj = (list(a.sort_values('obj_freq_gt').index))
    freqs_obj = (list(a.sort_values('obj_freq_gt')['obj_freq_gt']))
    classes_obj_few = classes_obj[:int(len(classes_obj)*cutoff)]
    classes_obj_medium = classes_obj[int(len(classes_obj)*cutoff):int(len(classes_obj)*cutoff_medium)]
    classes_obj_many = classes_obj[int(len(classes_obj)*cutoff_medium):]
    # freqs_obj = freqs_obj[:int(len(classes_obj)*cutoff)]

    df_few_rel = df[df['gt_rel'].isin(classes_rel_few)]
    df_medium_rel = df[df['gt_rel'].isin(classes_rel_medium)]
    df_many_rel = df[df['gt_rel'].isin(classes_rel_many)]

    df_few_sbj = df[df['gt_sbj'].isin(classes_sbj_few)]
    df_medium_sbj = df[df['gt_sbj'].isin(classes_sbj_medium)]
    df_many_sbj = df[df['gt_sbj'].isin(classes_sbj_many)]

    df_few_obj = df[df['gt_obj'].isin(classes_obj_few)]
    df_medium_obj = df[df['gt_obj'].isin(classes_obj_medium)]
    df_many_obj = df[df['gt_obj'].isin(classes_obj_many)]


    # print('sbj_overall_top1', num(df_['sbj_top1'].mean() * 100.))
    # print('obj_overall_top1', num(df['obj_top1'].mean() * 100.))
    # print('rel few:', len(df_few_rel))
    # print('rel medium:',len(df_medium_rel))
    # print('rel many:', len(df_many_rel))
    #
    # print('sbj few:', len(df_few_sbj))
    # print('sbj medium:',len(df_medium_sbj))
    # print('sbj many:', len(df_many_sbj))
    #
    # print('obj few:', len(df_few_obj))
    # print('obj medium:',len(df_medium_obj))
    # print('obj many:', len(df_many_obj))
    # print('all:', len(df))
    # print()
    print('Many, Medium, Few accuracy scores using exact matching:')

    print('rel many:', df_many_rel['rel_top1'].mean() * 100.)
    print('rel med:', df_medium_rel['rel_top1'].mean() * 100.)
    print('rel few:', df_few_rel['rel_top1'].mean() * 100.)
    print('rel all:', df['rel_top1'].mean() * 100.)
    print()
    print('sbj many:', df_many_sbj['sbj_top1'].mean() * 100.)
    print('sbj med:', df_medium_sbj['sbj_top1'].mean() * 100.)
    print('sbj few:', df_few_sbj['sbj_top1'].mean() * 100.)
    print('sbj all:', df['sbj_top1'].mean() * 100.)
    print()
    print('obj man:', df_many_obj['obj_top1'].mean() * 100.)
    print('obj med:', df_medium_obj['obj_top1'].mean() * 100.)
    print('obj few:', df_few_obj['obj_top1'].mean() * 100.)
    print('obj all:', df['obj_top1'].mean() * 100.)
    print()
    # print('triplet accuracy few:', df_few_rel['triplet_top1'].mean() * 100.)
    # print('triplet accuracy med:', df_medium_rel['triplet_top1'].mean() * 100.)
    # print('triplet accuracy man:', df_many_rel['triplet_top1'].mean() * 100.)
    # print('triplet accuracy all:', df['triplet_top1'].mean() * 100.)
    # print('=========================================================')
    if syn:
        print('Many, Medium, Few accuracy scores using synset matching:')
        print('rel syn many:', df_many_rel['rel_top1_syn'].mean() * 100.)
        print('rel syn med:', df_medium_rel['rel_top1_syn'].mean() * 100.)
        print('rel syn few:', df_few_rel['rel_top1_syn'].mean() * 100.)
        print('rel syn all:', df['rel_top1_syn'].mean() * 100.)
        print()
        print('sbj syn many:', df_many_sbj['sbj_top1_syn'].mean() * 100.)
        print('sbj syn med:', df_medium_sbj['sbj_top1_syn'].mean() * 100.)
        print('sbj syn few:', df_few_sbj['sbj_top1_syn'].mean() * 100.)
        print('sbj syn all:', df['sbj_top1_syn'].mean() * 100.)
        print()
        print('obj syn many:', df_many_obj['obj_top1_syn'].mean() * 100.)
        print('obj syn med:', df_medium_obj['obj_top1_syn'].mean() * 100.)
        print('obj syn few:', df_few_obj['obj_top1_syn'].mean() * 100.)
        print('obj syn all:', df['obj_top1_syn'].mean() * 100.)
        print()

    # print('triplet accuracy few:', df_few_rel['triplet_top1_syn'].mean() * 100.)
    # print('triplet accuracy med:', df_medium_rel['triplet_top1_syn'].mean() * 100.)
    # print('triplet accuracy man:', df_many_rel['triplet_top1_syn'].mean() * 100.)
    # print('triplet accuracy all:', df['triplet_top1_syn'].mean() * 100.)
    # print('=========================================================')

def get_wordsim_metrics_from_csv(csv_file):
    verbose = True
    collected_simple_means = dict()
    collected_per_class_means = dict()
    print('Reading csv file')
    df = pd.read_csv(csv_file)
    print('Done')
    # wordnet_metrics = ['lch', 'wup', 'res', 'jcn', 'lin', 'path']
    wordnet_metrics = ['lch', 'wup', 'lin', 'path']
    word2vec_metrics = ['w2v_gn']
    gt_prefix = 'gt'

    for prediction_type in ['sbj']:
        for metric_type in wordnet_metrics + word2vec_metrics:
            mu = df[prediction_type + '_' + metric_type].mean()

            if verbose:
                print('overall', prediction_type, metric_type, '{:2.2f}'.format(mu))

            collected_simple_means[(csv_file, prediction_type, metric_type)] = mu

    for prediction_type in ['rel']:
        for metric_type in  word2vec_metrics:
            mu = df[prediction_type + '_' + metric_type].mean()

            if verbose:
                print('overall', prediction_type, metric_type, '{:2.2f}'.format(mu))

            collected_simple_means[(csv_file, prediction_type, metric_type)] = mu

    for prediction_type in ['sbj', 'obj']:
        for metric_type in wordnet_metrics + word2vec_metrics:
            mu = df.groupby(gt_prefix + '_' + prediction_type)[prediction_type + '_' + metric_type].mean().mean()

            if verbose:
                print('per-class', prediction_type, metric_type, '{:2.2f}'.format(mu))

            collected_per_class_means[(csv_file, prediction_type, metric_type)] = mu

    for prediction_type in ['rel']:
        for metric_type in word2vec_metrics:
            mu = df.groupby(gt_prefix + '_' + prediction_type)[prediction_type + '_' + metric_type].mean().mean()

            if verbose:
                print('per-class', prediction_type, metric_type, '{:2.2f}'.format(mu))

            collected_per_class_means[(csv_file, prediction_type, metric_type)] = mu
    return collected_simple_means, collected_per_class_means


def get_metrics_from_csv(csv_file, get_mr=False):
    verbose = True
    collected_simple_means = dict()
    collected_per_class_means = dict()
    print('Reading csv file')
    df = pd.read_csv(csv_file)
    print('Done')
    # df['rel_top1'] = df['rel_rank'] < 1
    metric_type = 'top1'
    all_prediction_types = ['rel', 'obj', 'sbj']
    gt_prefix = 'gt'
    for prediction_type in all_prediction_types:
        df[prediction_type + '_' + metric_type] = df[prediction_type + '_rank'] < int(metric_type[3:])

    df['triplet_top1'] = df['rel_top1'] & df['sbj_top1'] & df['obj_top1']

    if verbose:
        print('------', metric_type, '------')

    # Overall Accuracy
    for prediction_type in all_prediction_types:
        mu = (len(df[df[prediction_type + '_rank'] < int(metric_type[3:])]) / len(df)) * 100.0
        # mu = df[prediction_type + '_' + metric_type].mean() * 100

        if verbose:
            print('simple-average', prediction_type, '{:2.2f}'.format(mu))

        collected_simple_means[(csv_file, prediction_type, metric_type)] = mu
    print()
    if get_mr:
        # Overall Mean Rank
        for prediction_type in all_prediction_types:
            mu = df[prediction_type + '_rank'].mean() * 100.0 / 250.0
            # mu = df.groupby(gt_prefix + '_' + prediction_type)[prediction_type + '_rank'].mean()
            # print(mu)

            if verbose:
                print('overall-mr', prediction_type, '{:2.2f}'.format(mu))

            # collected_per_class_means[(csv_file, prediction_type, metric_type)] = mu
    print()
    # Per-class Accuracy
    for prediction_type in all_prediction_types:
        mu = df.groupby(gt_prefix + '_' + prediction_type)[prediction_type + '_' + metric_type].mean().mean() * 100
        # mu = df.groupby(gt_prefix + '_' + prediction_type)[prediction_type + '_rank'].mean()
        # print(mu)

        if verbose:
            print('per-class-average', prediction_type, '{:2.2f}'.format(mu))

        collected_per_class_means[(csv_file, prediction_type, metric_type)] = mu
    print()
    if get_mr:
        # Per-class Mean Rank
        for prediction_type in all_prediction_types:
            mu = df.groupby(gt_prefix + '_' + prediction_type)[prediction_type + '_rank'].mean().mean() * 100.0 / 250.0
            # mu = df.groupby(gt_prefix + '_' + prediction_type)[prediction_type + '_rank'].mean()
            # print(mu)

            if verbose:
                print('per-class-mr', prediction_type, '{:2.2f}'.format(mu))

            # collected_per_class_means[(csv_file, prediction_type, metric_type)] = mu
    print()

    mu = df['triplet_top1'].mean() * 100.0
    if verbose:
        print('simple-average', 'triplet', '{:2.2f}'.format(mu))

    for prediction_type in all_prediction_types:
        mu = df.groupby(gt_prefix + '_' + prediction_type)['triplet_top1'].mean().mean() * 100
        if verbose:
            print('per-class-average', 'triplet_' + prediction_type, '{:2.2f}'.format(mu))

    print()

    return collected_simple_means, collected_per_class_means


if __name__ == '__main__':
    top_data_dir = '/home/x_abdelks/c2044/Large_Scale_VRD_pytorch/Outputs/'

    dataset = 'gvqa'
    # # dataset = 'vg_wiki_and_relco'
    #
    # split = 'test'
    # top_data_dir = osp.join(top_data_dir, 'ltvrd/reports/{}/{}'.format(dataset, split))

    # In[11]:

    # if split == 'val' and dataset == 'gvqa':
    #     top_data_dir = osp.join(top_data_dir, '_baseline_hubness_hubness10k_hubness50k_focal_loss_g025_focal_loss_g1_focal_loss_g2_focal_loss_g5_focal_loss_g10_focal_loss_g50')

    # In[12]:

    all_csvs = np.array([f for f in files_in_subdirs(top_data_dir, 'prdcls.csv$')])
    # method_names = np.array([osp.basename(f)[1:-len('.csv')] for f in all_csvs])
    # sids = np.argsort(method_names)
    sids = np.argsort(all_csvs)
    all_csvs = all_csvs[sids]
    # method_names = method_names[sids]

    print('Found {} methods.'.format(len(all_csvs)))

    # In[13]:

    apply_mask = True

    # methods_to_keep = ['baseline', 'focal_loss_g025', 'focal_loss_g1', 'focal_loss_g10',
    #                   'focal_loss_g2', 'focal_loss_g5', 'focal_loss_g50', 'hubness',
    #                   'hubness10k', 'hubness50k']
    methods_to_keep = ['baseline', 'focal_025', 'focal_1', 'focal_10',
                       'focal_2', 'focal_5', 'focal_50', 'hubness',
                       'hubness10k', 'hubness50k']
    data_name = 'gvqa10k'
    if apply_mask:
        keep_mask = np.zeros(len(all_csvs), dtype=np.bool)
        # for i, m in enumerate(method_names):
        for i, m in enumerate(all_csvs):
            # if m in methods_to_keep:
            if np.any([x in m for x in methods_to_keep]) and (data_name in m):
                keep_mask[i] = True
        all_csvs = all_csvs[keep_mask]
        method_names = np.array([None for _ in all_csvs])
        for i, csv_path in enumerate(all_csvs):
            for method in methods_to_keep:
                if method in csv_path:
                    method_names[i] = method

        # method_names = method_names[keep_mask]

        print('Kept methods', len(method_names))
        print(method_names)
        print(all_csvs)
    # In[14]:

    # Load meta-information (integer to "human" readable names)
    if dataset == 'gvqa':
        meta_file_name = 'GVQA'
    else:
        meta_file_name = 'Visual_Genome'

    obj_names = '/ibex/scratch/x_abdelks/Large-Scale-VRD/datasets/large_scale_VRD/{}/object_categories_spo_joined_and_merged.txt'.format(
        meta_file_name)
    rel_names = '/ibex/scratch/x_abdelks/Large-Scale-VRD/datasets/large_scale_VRD/{}/predicate_categories_spo_joined_and_merged.txt'.format(
        meta_file_name)

    with open(obj_names) as fin:
        ids_to_obj_names = fin.readlines()
        ids_to_obj_names = {i: idx.rstrip() for i, idx in enumerate(ids_to_obj_names)}

    with open(rel_names) as fin:
        ids_to_rel_names = fin.readlines()
        ids_to_rel_names = {i: idx.rstrip() for i, idx in enumerate(ids_to_rel_names)}

        # In[15]:

    ## Expected columns names of .csv
    relation_prefix = 'rel'
    object_prefix = 'obj'
    subject_prefix = 'sbj'
    gt_prefix = 'gt'
    all_prediction_types = [relation_prefix, object_prefix, subject_prefix]
    raw_metrics = ['top1']

    # Print basic statistics (ignore tail behavior, just overall average.)
    verbose = True
    collected_simple_means = dict()
    collected_per_class_means = dict()
    drop_left_right = False
    #all_csvs = ['/home/x_abdelks/scratch/freq_bias_files/evaluator/reports/gvqa/test/_weighted_ce_s0/csv_files/_weighted_ce_s0.csv',
    #            '/home/x_abdelks/scratch/freq_bias_files/evaluator/reports/gvqa/test/_retrain_s0/csv_files/_retrain_s0.csv',
    #            '/home/x_abdelks/scratch/freq_bias_files/evaluator/reports/gvqa/test/_hubness_exp_s0/csv_files/_hubness_exp_s0.csv']
    #method_names = ['weighted_ce_s0', 'baseline', '_hubness_exp_s0']
    for i, m in enumerate(method_names):
        if verbose:
            print('=============================')
            print(m)
        df = pd.read_csv(all_csvs[i])

        if drop_left_right and dataset == 'gvqa':
            print ('dropping left/right')
            df = df[(df.gt_rel != 286) & (df.gt_rel != 35)]
        df['rel_top1'] = df['rel_rank'] < 1
        for metric_type in raw_metrics:
            for prediction_type in all_prediction_types:
                df[prediction_type + '_' + metric_type] = df[prediction_type + '_rank'] < int(metric_type[3:])

        for metric_type in raw_metrics:
            if verbose:
                print('------', metric_type, '------')
            # Overall Accuracy
            for prediction_type in all_prediction_types:
                mu = (len(df[df[prediction_type + '_rank'] < int(metric_type[3:])])/len(df)) * 100.0
                #mu = df[prediction_type + '_' + metric_type].mean() * 100

                if verbose:
                    print ('simple-average', prediction_type, '{:2.2f}'.format(mu))

                collected_simple_means[(m, prediction_type, metric_type)] = mu

            # Overall Mean Rank
            for prediction_type in all_prediction_types:
                mu = df[prediction_type + '_rank'].mean() * 100.0 / 250.0
                #mu = df.groupby(gt_prefix + '_' + prediction_type)[prediction_type + '_rank'].mean()
                #print(mu)

                if verbose:
                    print ('overall-mr', prediction_type, '{:2.2f}'.format(mu))

                collected_per_class_means[(m, prediction_type, metric_type)] = mu

            # Per-class Accuracy
            for prediction_type in all_prediction_types:
                mu = df.groupby(gt_prefix + '_' + prediction_type)[prediction_type + '_' + metric_type].mean().mean() * 100
                #mu = df.groupby(gt_prefix + '_' + prediction_type)[prediction_type + '_rank'].mean()
                #print(mu)

                if verbose:
                    print ('per-class-average', prediction_type, '{:2.2f}'.format(mu))

                collected_per_class_means[(m, prediction_type, metric_type)] = mu

            # Per-class Mean Rank
            for prediction_type in all_prediction_types:
                mu = df.groupby(gt_prefix + '_' + prediction_type)[prediction_type + '_rank'].mean().mean() * 100.0 / 250.0
                #mu = df.groupby(gt_prefix + '_' + prediction_type)[prediction_type + '_rank'].mean()
                #print(mu)

                if verbose:
                    print ('per-class-mr', prediction_type, '{:2.2f}'.format(mu))

                collected_per_class_means[(m, prediction_type, metric_type)] = mu




    # In[10]:

    # make latex with simple and per-class means.
    for means, out_name in zip([collected_simple_means, collected_per_class_means], ['simple', 'per_class']):
        fout = open('{}_{}_mean_analysis.tex'.format(dataset, out_name), 'w')
        ndf = pd.Series(means).reset_index()
        ndf.columns = ['method', 'prediction-type', 'metric', 'accuracy']
        for metric in raw_metrics:
            df = ndf[ndf['metric'] == metric]
            for prediction in all_prediction_types:
                tdf = df[df['prediction-type'] == prediction]
                tdf.to_latex(buf=fout,
                             index=False,
                             columns=['method', 'prediction-type', 'metric', 'accuracy'],
                             float_format="{:0.2f}".format)
        fout.close()

    # exit()
    # # In[18]:
    #
    # ## Auxiliary to work with the soft-metrics (as given by Mohamed)##
    # # # and to link them to make plots that show long-tail responses.
    # ## UNCOMMENT, and run once to create/save the xxx_train_freq.csv
    # # df = pd.read_csv(all_csvs[0])
    #
    # # ndf = df[['gt_rel', 'rel_freq_gt']].groupby('gt_rel').mean().reset_index()
    # # ndf['gt_rel'] = ndf['gt_rel'].apply(lambda x: ids_to_rel_names[x])
    # # ndf = ndf.sort_values('rel_freq_gt', ascending=False)
    # # ndf.to_csv('/home/optas/DATA/OUT/ltvrd/gvqa_relation_to_train_freq.csv', index=False)
    #
    # # ndf = df[['gt_sbj', 'sbj_freq_gt']].groupby('gt_sbj').mean().reset_index()
    # # ndf['gt_sbj'] = ndf['gt_sbj'].apply(lambda x: ids_to_obj_names[x])
    # # ndf = ndf.sort_values('sbj_freq_gt', ascending=False)
    # # ndf.to_csv('/home/optas/DATA/OUT/ltvrd/gvqa_subject_to_train_freq.csv', index=False)
    #
    #
    # # In[19]:
    #
    # # Just load the csv of one method, to use the frequency characteristics of the
    # # the training data to plot your distributions.
    # cum_dists = []
    # all_figs = []
    #
    # for prediction_type in all_prediction_types:
    #     df = pd.read_csv(all_csvs[0])
    #     gb = df.groupby([gt_prefix + '_' +prediction_type]).groups
    #
    #     if prediction_type == 'rel':
    #         id_to_name = ids_to_rel_names
    #     else:
    #         id_to_name = ids_to_obj_names
    #
    #     stats = []  # <name, train_freq - times it is found in the test-data>
    #     for key, val in gb.iteritems():
    #         gt_freq = np.unique(df[prediction_type + '_freq_gt'].loc[val])
    #         assert len(gt_freq) == 1 # we grouped by the gt-type,
    #                                  # hence the frequencies must be the same for all rows.
    #         stats.append([id_to_name[key], gt_freq[0], len(val)])
    #     sl = sorted(stats, key=lambda x: x[1], reverse=True)
    #     print('{}: Most heavy items:'.format(prediction_type),  sl[:10])
    #
    #     freqs = np.array([x[1] for x in stats], dtype=np.float64)
    #     freqs = sorted(freqs, reverse=True)
    #     freqs /= np.sum(freqs)
    #     cum_dist = np.cumsum(freqs)
    #     cum_dists.append(cum_dist)
    #
    #     vals = []
    #     for i, v in enumerate(sorted([x[1] for x in stats], reverse=True)):
    #         vals.extend([i] * v )
    #
    #     fig, ax = plt.subplots(1, 2, figsize=(12, 4), dpi=300)
    #     plt.suptitle(prediction_type)
    #     sns.distplot(vals, ax=ax[0])
    #     sns.distplot(vals, hist_kws=dict(cumulative=True), ax=ax[1])
    #     all_figs.append(fig)
    #
    # for fig in all_figs:
    #     fig
    #
    #
    # # In[100]:
    #
    # # # Compare the accuracy of two methods:
    # ## Input on soft-metrics (computed separately)
    #
    # method_a = 'hubness'
    # method_b = 'baseline'
    # sim = 'word2vec_visualVG'
    #
    # # in_f1 = '/home/optas/DATA/OUT/ltvrd/sorted_via_soft_scores/subject/_hubness10k_vgqa_sorted_mean_acc_per_class_on_subject_with_word2vec_visualVG.csv'
    # # in_f2 = '/home/optas/DATA/OUT/ltvrd/sorted_via_soft_scores/subject/_baseline_vgqa_sorted_mean_acc_per_class_on_subject_with_word2vec_visualVG.csv'
    #
    # in_f1 = '/home/optas/DATA/OUT/ltvrd/sorted_via_soft_scores/relation/_baseline_vgqa_sorted_mean_acc_per_class_on_relation_with_word2vec_visualVG.csv'
    # in_f2 = '/home/optas/DATA/OUT/ltvrd/sorted_via_soft_scores/relation/_hubness_vgqa_sorted_mean_acc_per_class_on_relation_with_word2vec_visualVG.csv'
    #
    # s0=pd.read_csv(in_f1)[sim]
    # s1=pd.read_csv(in_f2)[sim]
    #
    # relative_score =  s0 - s1
    # relative_score = relative_score.values
    # n_obs = len(relative_score)
    #
    # fig, ax = plt.subplots(1, 1, figsize = (12, 5), dpi=300)
    # # plt.title('{}--{}'.format(dataset, prediction_type))
    #
    # x0 = np.arange(n_obs)[relative_score > 0]
    # x1 = np.arange(n_obs)[relative_score < 0]
    #
    # # sns.scatterplot(x0, np.ones(n_obs)[relative_score > 0], color='green')
    # # sns.scatterplot(x1, -np.ones(n_obs)[relative_score < 0], color='red')
    #
    # # sns.scatterplot(x0, relative_score[relative_score > 0], color='green')
    # # sns.scatterplot(x1, relative_score[relative_score < 0], color='red')
    #
    # sns.regplot(x0, relative_score[relative_score > 0], color='green')#, lowess=True)
    # sns.regplot(x1, relative_score[relative_score < 0], color='red')#, lowess=True)
    #
    # plt.title('Hubness vs. Baseline: relation prediction, entire class distribution.')
    # plt.legend([method_a, method_b], loc='upper left', fontsize=14)
    # plt.xlabel('Class ID (decreasing training frequency)', fontsize=15)
    # plt.grid()
    # plt.ylabel('Relative Performance', fontsize=15)
    #
    # ### Some other statistics on the "relative" curve:
    # # from scipy.stats import pearsonr
    # # x = np.arange(n_obs)[relative_score < 0]
    # # y = relative_score[relative_score < 0]
    # # rho_neg = pearsonr(x, y)[0]
    # # x = np.arange(n_obs)[relative_score > 0]
    # # y = relative_score[relative_score > 0]
    # # rho_pos = pearsonr(x, y)[0]
    # # print rho_neg, rho_pos, rho_pos + rho_neg
    # # print np.mean(relative_score > 0)
    #
    #
    # # In[76]:
    #
    # threshold_of_tail = 0.
    # metric = 'top1'
    #
    # for i, m in enumerate(method_names):
    #     print(m)
    #     df = pd.read_csv(all_csvs[i])
    #     for prediction_type in all_prediction_types:
    #         ndf = keep_only_heavy_tail_observations(df, prediction_type, threshold_of_tail=threshold_of_tail)
    #         print prediction_type, ndf[prediction_type + '_' + metric].mean()
    #     print
    #
    #
    # # In[ ]:
    #
    # # Below is now dirty.
    #
    #
    # # In[527]:
    #
    # fig, ax = plt.subplots(1, 1, figsize = (10, 10), dpi=200)
    # plt.title('{}--{}'.format(dataset, prediction_type))
    #
    # rel = g2[prediction_type+ '_top1'] - g1[prediction_type + '_top1']
    # # sns.scatterplot(np.arange(len(g1))[rel > 0], rel[rel>0], color='green', )
    #
    # plt.bar(np.arange(len(g1))[rel > 0], rel[rel>0], color='green')
    # # sns.barplot(np.arange(len(g1))[rel > 0], rel[rel>0], color='green')
    # # sns.regplot(np.arange(len(g1))[rel > 0], rel[rel>0], color='green')
    # # plt.scatter(np.arange(len(g1))[rel < 0], rel[rel<0], color='red')
    # # sns.barplot(np.arange(len(g1))[rel < 0], rel[rel<0], color='red')
    # plt.bar(np.arange(len(g1))[rel < 0], rel[rel<0], color='red')
    #
    # # sns.regplot(np.arange(len(g1))[rel < 0], rel[rel<0], color='red')
    # plt.legend(['improvement', 'worsening'])
    # plt.xlabel('Class id (decreasing training frequency)', fontsize=15)
    # plt.ylabel('Relative probility of hubness vs. baseline', fontsize=15)
    #
    #
    # # In[ ]:
    #
    # # fig, ax = plt.subplots(1, 1, figsize = (10, 15), dpi=300)
    #
    # # s = sns.barplot(x=range(1, 2*len(g1), 2), y=prediction_type+'_top1', data=g1, facecolor='red')
    # # s.set(xticklabels=[])
    #
    # # s = sns.barplot(x=range(2, 2*len(g2)+1, 2), y=prediction_type+'_top1', data=g2, facecolor='green')
    # # s.set(xticklabels=[])
    # # ax.set_xlabel('')
    #
    #
    # # In[30]:
    #
    # # sns.lineplot(x=range(len(g1)), y=prediction_type+'_top1', data=g1, color='red')
    #
    #
    # # In[350]:
    #
    # plt.figure(figsize=(20, 10))
    # sns.scatterplot(x=range(1, 5*len(g1), 10), y=prediction_type+'_top1', data=g1, marker='.', color='red', s=60)
    # sns.scatterplot(x=range(4, 5*len(g2) +1, 5), y=prediction_type+'_top1', data=g2, marker='.', color='green', s=60)
    #
    #
    # # In[351]:
    #
    # plt.figure(figsize=(20, 10))
    # sns.scatterplot(x=range(4, 5*len(g2) +1, 5), y=prediction_type+'_top1', data=g2, marker='.', color='green', s=60)
    # sns.scatterplot(x=range(1, 5*len(g1), 5), y=prediction_type+'_top1', data=g1, marker='.', color='red', s=60)
    #
    #
    # # In[349]:
    #
    # plt.figure(figsize=(20, 10))
    # sns.scatterplot(x=range(1, 2*len(g1), 2), y=prediction_type+'_top1', data=g1, marker='.', color='green', s=60)
    # sns.scatterplot(x=range(2, 2*len(g2) +1, 2), y=prediction_type+'_top1', data=g2, marker='.', color='red', s=60)
    #
    #
    # # In[31]:
    #
    # if prediction_type == 'rel':
    #     manual_bins = np.array([100000, 25000, 10000, 1000, 500, 100, 10, 1])
    #
    # if prediction_type == 'obj' or prediction_type == 'sbj':
    #     manual_bins = np.array([200000, 100000, 50000, 25000, 10000, 5000, 1000, 500, 100, 25, 1])
    #
    #
    # # In[39]:
    #
    # method_names
    #
    #
    # # In[40]:
    #
    # distance = 'top1' # or top5, or #top10
    # collected_results = []
    # use_only=['baseline', 'focal_loss_g025', 'hubness10k']
    #
    # for i in range(len(method_names)):
    #     if method_names[i] not in use_only:
    #         continue
    #     df = pd.read_csv(all_csvs[i])
    #     print (method_names[i], 'n_lines=', len(df))
    #     metric = prediction_type + '_' + distance
    #     bin_values = np.digitize(df[prediction_type + '_freq_gt'], manual_bins)
    #     df['bins'] = bin_values
    # #     print df.groupby(['bins'])[metric].mean()[1:]
    # #     collected_results.append(np.array(df.groupby(['bins'])[metric].mean()[1:]))
    #     collected_results.append(np.array(df.groupby(['bins'])[metric].mean()))
    #
    #
    # # In[50]:
    #
    # plt.figure(figsize=(9, 6))
    # plt.grid()
    # plt.xlabel('Frequency-based (sorted) logarithimic bins.', fontsize=18)
    # plt.ylabel('Top-1 Accuracy.', fontsize=18)
    # # f, ax = plt.subplots(1, 1)
    # for i, experiment in enumerate(collected_results):
    #     if i == 0:
    #         plt.plot(np.arange(len(experiment)), experiment, '--')
    #     else:
    #         plt.plot(np.arange(len(experiment)), experiment, marker='.')
    #
    # #     sns.lineplot(x=np.arange(len(experiment)), y=experiment, ax=ax , markers='*')
    # plt.legend(use_only, fontsize=18)

