GotSelected analysis — n=375 cases
============================================================

## M1 breadth quadratic + word count
```
                           Logit Regression Results                           
==============================================================================
Dep. Variable:            GotSelected   No. Observations:                  375
Model:                          Logit   Df Residuals:                      371
Method:                           MLE   Df Model:                            3
Date:                Sun, 09 Aug 2026   Pseudo R-squ.:                 0.01164
Time:                        23:19:58   Log-Likelihood:                -200.77
converged:                       True   LL-Null:                       -203.13
Covariance Type:            nonrobust   LLR p-value:                    0.1928
=====================================================================================
                        coef    std err          z      P>|z|      [0.025      0.975]
-------------------------------------------------------------------------------------
Intercept            -1.0883      0.149     -7.318      0.000      -1.380      -0.797
breadth_z             0.2033      0.150      1.359      0.174      -0.090       0.496
I(breadth_z ** 2)    -0.1321      0.099     -1.337      0.181      -0.326       0.061
word_count_z          0.1673      0.125      1.339      0.180      -0.078       0.412
=====================================================================================
```

## M2 domain count (collapsed) + word count
```
                           Logit Regression Results                           
==============================================================================
Dep. Variable:            GotSelected   No. Observations:                  375
Model:                          Logit   Df Residuals:                      371
Method:                           MLE   Df Model:                            3
Date:                Sun, 09 Aug 2026   Pseudo R-squ.:                0.005809
Time:                        23:19:58   Log-Likelihood:                -201.95
converged:                       True   LL-Null:                       -203.13
Covariance Type:            nonrobust   LLR p-value:                    0.5011
========================================================================================
                           coef    std err          z      P>|z|      [0.025      0.975]
----------------------------------------------------------------------------------------
Intercept               -1.2641      0.197     -6.403      0.000      -1.651      -0.877
n_domains_cat[T.1-2]    -0.0056      0.346     -0.016      0.987      -0.683       0.672
n_domains_cat[T.4-5]     0.1462      0.273      0.535      0.592      -0.389       0.682
word_count_z             0.1665      0.121      1.376      0.169      -0.071       0.404
========================================================================================
```

## M3 joint + transcript incomplete
```
                           Logit Regression Results                           
==============================================================================
Dep. Variable:            GotSelected   No. Observations:                  375
Model:                          Logit   Df Residuals:                      368
Method:                           MLE   Df Model:                            6
Date:                Sun, 09 Aug 2026   Pseudo R-squ.:                 0.01233
Time:                        23:19:58   Log-Likelihood:                -200.63
converged:                       True   LL-Null:                       -203.13
Covariance Type:            nonrobust   LLR p-value:                    0.5427
=========================================================================================
                            coef    std err          z      P>|z|      [0.025      0.975]
-----------------------------------------------------------------------------------------
Intercept                -1.1609      0.215     -5.396      0.000      -1.583      -0.739
n_domains_cat[T.1-2]      0.0570      0.349      0.163      0.870      -0.627       0.741
n_domains_cat[T.4-5]      0.1286      0.276      0.465      0.642      -0.413       0.670
breadth_z                 0.1962      0.152      1.294      0.196      -0.101       0.493
I(breadth_z ** 2)        -0.1332      0.099     -1.349      0.177      -0.327       0.060
word_count_z              0.1654      0.125      1.319      0.187      -0.080       0.411
transcript_incomplete     0.0788      0.376      0.209      0.834      -0.658       0.816
=========================================================================================
```

## M4 joint + appearance/demographics
```
                           Logit Regression Results                           
==============================================================================
Dep. Variable:            GotSelected   No. Observations:                  356
Model:                          Logit   Df Residuals:                      345
Method:                           MLE   Df Model:                           10
Date:                Sun, 09 Aug 2026   Pseudo R-squ.:                  0.1117
Time:                        23:19:58   Log-Likelihood:                -168.50
converged:                       True   LL-Null:                       -189.68
Covariance Type:            nonrobust   LLR p-value:                 6.445e-06
=========================================================================================
                            coef    std err          z      P>|z|      [0.025      0.975]
-----------------------------------------------------------------------------------------
Intercept                -1.7534      0.266     -6.604      0.000      -2.274      -1.233
n_domains_cat[T.1-2]      0.2174      0.381      0.570      0.568      -0.530       0.964
n_domains_cat[T.4-5]      0.2963      0.306      0.969      0.333      -0.303       0.896
C(Gender)[T.1.0]          0.8567      0.310      2.766      0.006       0.250       1.464
breadth_z                 0.1777      0.170      1.046      0.296      -0.155       0.511
I(breadth_z ** 2)        -0.1160      0.100     -1.164      0.244      -0.311       0.079
word_count_z              0.1806      0.140      1.288      0.198      -0.094       0.455
transcript_incomplete     0.3740      0.412      0.908      0.364      -0.433       1.181
zBMI                     -0.6090      0.171     -3.559      0.000      -0.944      -0.274
zAttractiveness           0.3024      0.144      2.102      0.036       0.020       0.584
zAgeAI                   -0.0829      0.153     -0.543      0.587      -0.382       0.216
=========================================================================================
```

## Composition — DFV (exploratory)

## Desirability count + word count + transcript incomplete
```
                           Logit Regression Results                           
==============================================================================
Dep. Variable:            GotSelected   No. Observations:                  375
Model:                          Logit   Df Residuals:                      371
Method:                           MLE   Df Model:                            3
Date:                Sun, 09 Aug 2026   Pseudo R-squ.:                 0.01464
Time:                        23:19:58   Log-Likelihood:                -200.16
converged:                       True   LL-Null:                       -203.13
Covariance Type:            nonrobust   LLR p-value:                    0.1143
=========================================================================================
                            coef    std err          z      P>|z|      [0.025      0.975]
-----------------------------------------------------------------------------------------
Intercept                -0.7433      0.273     -2.725      0.006      -1.278      -0.209
breadth_D                -0.2427      0.127     -1.916      0.055      -0.491       0.006
word_count_z              0.2079      0.124      1.676      0.094      -0.035       0.451
transcript_incomplete     0.1046      0.374      0.280      0.780      -0.628       0.838
=========================================================================================
```

## Feasibility count + word count + transcript incomplete
```
                           Logit Regression Results                           
==============================================================================
Dep. Variable:            GotSelected   No. Observations:                  375
Model:                          Logit   Df Residuals:                      371
Method:                           MLE   Df Model:                            3
Date:                Sun, 09 Aug 2026   Pseudo R-squ.:                 0.02107
Time:                        23:19:58   Log-Likelihood:                -198.85
converged:                       True   LL-Null:                       -203.13
Covariance Type:            nonrobust   LLR p-value:                   0.03578
=========================================================================================
                            coef    std err          z      P>|z|      [0.025      0.975]
-----------------------------------------------------------------------------------------
Intercept                -2.1011      0.382     -5.504      0.000      -2.849      -1.353
breadth_F                 0.2117      0.083      2.541      0.011       0.048       0.375
word_count_z              0.1825      0.125      1.457      0.145      -0.063       0.428
transcript_incomplete     0.1178      0.376      0.313      0.754      -0.619       0.855
=========================================================================================
```

## Viability count + word count + transcript incomplete
```
                           Logit Regression Results                           
==============================================================================
Dep. Variable:            GotSelected   No. Observations:                  375
Model:                          Logit   Df Residuals:                      371
Method:                           MLE   Df Model:                            3
Date:                Sun, 09 Aug 2026   Pseudo R-squ.:                0.005105
Time:                        23:19:58   Log-Likelihood:                -202.09
converged:                       True   LL-Null:                       -203.13
Covariance Type:            nonrobust   LLR p-value:                    0.5572
=========================================================================================
                            coef    std err          z      P>|z|      [0.025      0.975]
-----------------------------------------------------------------------------------------
Intercept                -1.2063      0.217     -5.552      0.000      -1.632      -0.780
breadth_V                -0.0066      0.112     -0.059      0.953      -0.226       0.213
word_count_z              0.1737      0.121      1.435      0.151      -0.064       0.411
transcript_incomplete     0.0964      0.373      0.258      0.796      -0.635       0.828
=========================================================================================
```

## M5 breadth + premise similarity control + transcript incomplete
```
                           Logit Regression Results                           
==============================================================================
Dep. Variable:            GotSelected   No. Observations:                  375
Model:                          Logit   Df Residuals:                      369
Method:                           MLE   Df Model:                            5
Date:                Sun, 09 Aug 2026   Pseudo R-squ.:                 0.01227
Time:                        23:19:58   Log-Likelihood:                -200.64
converged:                       True   LL-Null:                       -203.13
Covariance Type:            nonrobust   LLR p-value:                    0.4176
=========================================================================================
                            coef    std err          z      P>|z|      [0.025      0.975]
-----------------------------------------------------------------------------------------
Intercept                -1.0989      0.156     -7.067      0.000      -1.404      -0.794
breadth_z                 0.2136      0.152      1.407      0.159      -0.084       0.511
I(breadth_z ** 2)        -0.1340      0.099     -1.354      0.176      -0.328       0.060
premise_sim_mean_z        0.0546      0.123      0.442      0.658      -0.187       0.296
word_count_z              0.1642      0.126      1.304      0.192      -0.083       0.411
transcript_incomplete     0.0955      0.374      0.255      0.798      -0.637       0.828
=========================================================================================
```

## M6 domain count + domain separation control + transcript incomplete
```
                           Logit Regression Results                           
==============================================================================
Dep. Variable:            GotSelected   No. Observations:                  371
Model:                          Logit   Df Residuals:                      366
Method:                           MLE   Df Model:                            4
Date:                Sun, 09 Aug 2026   Pseudo R-squ.:                 0.01358
Time:                        23:19:58   Log-Likelihood:                -196.96
converged:                       True   LL-Null:                       -199.67
Covariance Type:            nonrobust   LLR p-value:                    0.2466
=========================================================================================
                            coef    std err          z      P>|z|      [0.025      0.975]
-----------------------------------------------------------------------------------------
Intercept                -1.2442      0.135     -9.238      0.000      -1.508      -0.980
n_domains_z               0.1684      0.124      1.356      0.175      -0.075       0.412
domain_sep_z              0.0877      0.122      0.716      0.474      -0.152       0.328
word_count_z              0.2017      0.126      1.599      0.110      -0.045       0.449
transcript_incomplete     0.0609      0.378      0.161      0.872      -0.680       0.802
=========================================================================================
```

## Breadth curvature
linear: 0.2033 (p=0.1741)
quadratic: -0.1321 (p=0.1811)
turning point (z): 0.769

## M0 breadth linear (nested)
```
                           Logit Regression Results                           
==============================================================================
Dep. Variable:            GotSelected   No. Observations:                  375
Model:                          Logit   Df Residuals:                      372
Method:                           MLE   Df Model:                            2
Date:                Sun, 09 Aug 2026   Pseudo R-squ.:                0.006610
Time:                        23:19:58   Log-Likelihood:                -201.79
converged:                       True   LL-Null:                       -203.13
Covariance Type:            nonrobust   LLR p-value:                    0.2612
================================================================================
                   coef    std err          z      P>|z|      [0.025      0.975]
--------------------------------------------------------------------------------
Intercept       -1.2075      0.123     -9.784      0.000      -1.449      -0.966
breadth_z        0.1008      0.122      0.827      0.408      -0.138       0.340
word_count_z     0.1659      0.122      1.360      0.174      -0.073       0.405
================================================================================
```
LRT quadratic vs linear: chi2(1)=2.044
