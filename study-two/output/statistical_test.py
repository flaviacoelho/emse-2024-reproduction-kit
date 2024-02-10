
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Jan 27 22:19:57 2024

@author: flavia
"""

#Statistical testing
from scipy.stats import shapiro,levene,mannwhitneyu
import pandas as pd, numpy as np
import pingouin as pg
import matplotlib.pyplot as plt


np.set_printoptions(formatter={'float': lambda x: '%.2f' % x})
plt.style.use('ggplot')

def bootstrap_ci_median(df, variable, classes, repetitions=1000, alpha=0.05, random_state=None):
    df = df[[variable, classes]]
    bootstrap_sample_size = len(df)

    median_diffs = []
    for i in range(repetitions):
        bootstrap_sample = df.sample(n=bootstrap_sample_size, replace=True, random_state=random_state)
        median_diff = bootstrap_sample.groupby(classes).median().iloc[1, 0] - \
                      bootstrap_sample.groupby(classes).median().iloc[0, 0]
        median_diffs.append(median_diff)

    # confidence interval
    left = np.percentile(median_diffs, alpha / 2 * 100)
    right = np.percentile(median_diffs, 100 - alpha / 2 * 100)

    # point estimate
    point_est = df.groupby(classes).median().iloc[1, 0] - df.groupby(classes).median().iloc[0, 0]
    print('\nPoint estimate of difference between medians:', round(point_est, 2))
    print((1 - alpha) * 100, '%', 'confidence interval for the difference between medians:',
          (round(left, 2), round(right, 2)))
    return

def bootstrap_ci_mean(df, variable, classes, repetitions=1000, alpha=0.05, random_state=None):
    df = df[[variable, classes]]
    bootstrap_sample_size = len(df)

    mean_diffs = []
    for i in range(repetitions):
        bootstrap_sample = df.sample(n=bootstrap_sample_size, replace=True, random_state=random_state)
        mean_diff = bootstrap_sample.groupby(classes).mean().iloc[1, 0] - bootstrap_sample.groupby(classes).mean().iloc[
            0, 0]
        mean_diffs.append(mean_diff)

    # confidence interval
    left = np.percentile(mean_diffs, alpha / 2 * 100)
    right = np.percentile(mean_diffs, 100 - alpha / 2 * 100)

    # point estimate
    point_est = df.groupby(classes).mean().iloc[1, 0] - df.groupby(classes).mean().iloc[0, 0]
    print('\nPoint estimate of difference between means:', round(point_est, 2))
    print((1 - alpha) * 100, '%', 'confidence interval for the difference between means:',
          (round(left, 2), round(right, 2)))
    return

def run_test(data, developer):
    data_ripr = data.loc[data['category'] == "refactoring-inducing"]
    data_ripr_developer = data_ripr.loc[:, developer]
    # plt.hist(data_ripr_authors, color='lightgreen', ec='black', bins=15)

    data_nonripr = data.loc[data['category'] == "non-refactoring-inducing"]
    data_nonripr_developer = data_nonripr.loc[:, developer]

    # Checking for normalility
    # Shapiro-Wilk Test value > 0.05, then data is normal
    print('\nChecking for normality in PRs (> 0.05, data is normal)')
    print('Shapiro-Wilk test:', shapiro(data_ripr_developer))
    print('Shapiro-Wilk test:', shapiro(data_nonripr_developer))

    # Checking for homogeneity of variances
    # Levene test > 0.05, the homogeneity of variance is met
    print('\nChecking for homogeneity of variances PRs (> 0.05, homogeneity of variance is met)')
    print('Levene test:', levene(data_ripr_developer, data_nonripr_developer))

    bootstrap_ci_median(data, developer, 'category')
    bootstrap_ci_mean(data, developer, 'category')

    #authors vs authors
    print('\nMann Whitney U test (< 0.05, there is enough evidence that group1 < group2):',
          mannwhitneyu(data_ripr_developer, data_nonripr_developer, alternative='less'))
    #reviewers vs reviewers
    print('\nMann Whitney U test (< 0.05, there is enough evidence that group1 > group2):',
          mannwhitneyu(data_ripr_developer,data_nonripr_developer, alternative='greater'))

    print('\nMann-Whitney U test')
    print(mannwhitneyu(data_ripr_developer, data_nonripr_developer, alternative='less'))

    print('Mann Whitney U test: (pingouin)', pg.mwu(data_ripr_developer, data_nonripr_developer, alternative='less'))

    stat, p_value = mannwhitneyu(data_ripr_developer, data_nonripr_developer)
    print('Statistics=%.2f, p=%.2f' % (stat, p_value))
    # Level of significance
    alpha = 0.05
    # conclusion
    if p_value < alpha:
        print('Conclusion: Reject Null Hypothesis (Significant difference between two samples)')
    else:
        print('Conclusion: Do not Reject Null Hypothesis (No significant difference between two samples)')

    return


def run_test_versus(data_a, data_r):

    # Level of significance
    alpha = 0.05

    # refactoring-inducing PRs
    print('\nAnalyzing refactoring-inducing PRs')
    data_a_ripr = data_a.loc[data_a['category'] == "refactoring-inducing"]
    data_a_ripr_author = data_a_ripr.loc[:, 'author']

    data_r_ripr = data_r.loc[data_r['category'] == "refactoring-inducing"]
    data_r_ripr_reviewer = data_r_ripr.loc[:, 'reviewer']
    # plt.hist(data_r_ripr_reviewer, bins=10)
    # plt.show()

    # Checking for normalility
    # Shapiro-Wilk Test value > 0.05, then data is normal
    print('\nChecking for normality in refactoring-inducing PRs (> 0.05, data is normal)')
    print('Shapiro-Wilk test:', shapiro(data_a_ripr_author))
    print('Shapiro-Wilk test:', shapiro(data_r_ripr_reviewer))

    # Checking for homogeneity of variances
    # Levene test > 0.05, the homogeneity of variance is met
    print('\nChecking for homogeneity of variances in refactoring-inducing PRs (> 0.05, homogeneity of variance is met)')
    print('Levene test:', levene(data_a_ripr_author, data_r_ripr_reviewer))

    print('\nMann-Whitney U test')
    print(mannwhitneyu(data_a_ripr_author, data_r_ripr_reviewer, alternative='less'))

    stat, p_value = mannwhitneyu(data_a_ripr_author, data_r_ripr_reviewer, alternative='less')
    print('Statistics=%.2f, p=%.2f' % (stat, p_value))

    # conclusion
    if p_value < alpha:
        print('Conclusion: Reject Null Hypothesis (Significant difference between two samples)')
    else:
        print('Conclusion: Do not Reject Null Hypothesis (No significant difference between two samples)')


    # non-refactoring-inducing PRs
    print('\nAnalyzing non-refactoring-inducing PRs')
    data_a_nonripr = data_a.loc[data_a['category'] == "non-refactoring-inducing"]
    data_a_nonripr_author = data_a_nonripr.loc[:, 'author']

    data_r_nonripr = data_r.loc[data_r['category'] == "non-refactoring-inducing"]
    data_r_nonripr_reviewer = data_r_nonripr.loc[:, 'reviewer']

    # Checking for normalility
    # Shapiro-Wilk Test value > 0.05, then data is normal
    print('\nChecking for normality in non-refactoring-inducing PRs (> 0.05, data is normal)')
    print('Shapiro-Wilk test:', shapiro(data_a_nonripr_author))
    print('Shapiro-Wilk test:', shapiro(data_r_nonripr_reviewer))

    # Checking for homogeneity of variances
    # Levene test > 0.05, then the homogeneity of the variance is met
    print('\nChecking for homogeneity of variances in refactoring-inducing PRs (> 0.05, homogeneity of variance is met)')
    print('Levene test:', levene(data_a_nonripr_author, data_r_nonripr_reviewer))

    print('\nMann-Whitney U test')
    print(mannwhitneyu(data_a_nonripr_author, data_r_nonripr_reviewer, alternative='greater'))

    stat, p_value = mannwhitneyu(data_a_nonripr_author, data_r_nonripr_reviewer, alternative='greater')
    print('Statistics=%.2f, p=%.2f' % (stat, p_value))

    # conclusion
    if p_value < alpha:
        print('Conclusion: Reject Null Hypothesis (Significant difference between two samples)')
    else:
        print('Conclusion: Do not Reject Null Hypothesis (No significant difference between two samples)')

    return


def testing_samples(data,developer):

    # # sample 1
    # sample1 = data.loc[data['sample'] == 1]
    # print('Running test for sample 1')
    # run_test(sample1,developer)
    #
    # print('----------------')
    # # sample 2
    # sample2 = data.loc[data['sample'] == 2]
    # print('Running test for sample 2')
    # run_test(sample2,developer)
    #
    # print('----------------')
    # # sample 3
    # sample3 = data.loc[data['sample'] == 3]
    # print('Running test for sample 3')
    # run_test(sample3,developer)
    #
    # print('----------------')
    # # sample 4
    # sample4 = data.loc[data['sample'] == 4]
    # print('Running test for sample 4')
    # run_test(sample4,developer)

    print('----------------')
    # all samples
    print('Running test for all samples')
    run_test(data,developer)

    return


def testing_samples_versus(data_a,data_r):

    # # sample 1
    # sample1_a = data_a.loc[data_a['sample'] == 1]
    # sample1_r = data_r.loc[data_r['sample'] == 1]
    # print('\nRunning test for sample 1')
    # run_test_versus(sample1_a,sample1_r)
    #
    # print('----------------')
    # # sample 2
    # sample2_a = data_a.loc[data_a['sample'] == 2]
    # sample2_r = data_r.loc[data_r['sample'] == 2]
    # print('\nRunning test for sample 2')
    # run_test_versus(sample2_a, sample2_r)
    #
    # print('----------------')
    # # sample 3
    # sample3_a = data_a.loc[data_a['sample'] == 3]
    # sample3_r = data_r.loc[data_r['sample'] == 3]
    # print('\nRunning test for sample 3')
    # run_test_versus(sample3_a, sample3_r)
    #
    # print('----------------')
    # # sample 4
    # sample4_a = data_a.loc[data_a['sample'] == 4]
    # sample4_r = data_r.loc[data_r['sample'] == 4]
    # print('\nRunning test for sample 4')
    # run_test_versus(sample4_a, sample4_r)

    print('----------------')
    # all samples
    print('\nRunning test for all samples')
    run_test_versus(data_a,data_r)

    return


print('\n----------------')
print('Analyzing authors x authors')

data_authors = pd.read_csv('./authors_spreadsheet.csv', engine = 'python', encoding = 'ISO-8859-1')
testing_samples(data_authors,'author')

print('\n----------------')
print('Analyzing reviewers x reviewers')

data_reviewers = pd.read_csv('./reviewers_spreadsheet.csv', engine = 'python', encoding = 'ISO-8859-1')
testing_samples(data_reviewers,'reviewer')

print('\n----------------')
print('Analyzing authors x reviewers')
testing_samples_versus(data_authors,data_reviewers)
