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
Time:                        00:13:20   Log-Likelihood:                -200.77
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

No domain partition in this run; M2 skipped.

## M3 breadth + word count + transcript incomplete
```
                           Logit Regression Results                           
==============================================================================
Dep. Variable:            GotSelected   No. Observations:                  375
Model:                          Logit   Df Residuals:                      370
Method:                           MLE   Df Model:                            4
Date:                Sun, 09 Aug 2026   Pseudo R-squ.:                 0.01180
Time:                        00:13:20   Log-Likelihood:                -200.73
converged:                       True   LL-Null:                       -203.13
Covariance Type:            nonrobust   LLR p-value:                    0.3093
=========================================================================================
                            coef    std err          z      P>|z|      [0.025      0.975]
-----------------------------------------------------------------------------------------
Intercept                -1.0994      0.155     -7.074      0.000      -1.404      -0.795
breadth_z                 0.2027      0.150      1.354      0.176      -0.091       0.496
I(breadth_z ** 2)        -0.1328      0.099     -1.343      0.179      -0.327       0.061
word_count_z              0.1699      0.125      1.356      0.175      -0.076       0.415
transcript_incomplete     0.0944      0.374      0.253      0.801      -0.638       0.827
=========================================================================================
```

## M4 breadth + appearance/demographics
```
                           Logit Regression Results                           
==============================================================================
Dep. Variable:            GotSelected   No. Observations:                  356
Model:                          Logit   Df Residuals:                      347
Method:                           MLE   Df Model:                            8
Date:                Sun, 09 Aug 2026   Pseudo R-squ.:                  0.1091
Time:                        00:13:20   Log-Likelihood:                -168.99
converged:                       True   LL-Null:                       -189.68
Covariance Type:            nonrobust   LLR p-value:                 1.768e-06
=========================================================================================
                            coef    std err          z      P>|z|      [0.025      0.975]
-----------------------------------------------------------------------------------------
Intercept                -1.5978      0.204     -7.820      0.000      -1.998      -1.197
C(Gender)[T.1.0]          0.8573      0.309      2.779      0.005       0.253       1.462
breadth_z                 0.1838      0.168      1.092      0.275      -0.146       0.514
I(breadth_z ** 2)        -0.1129      0.100     -1.127      0.260      -0.309       0.083
word_count_z              0.1881      0.140      1.340      0.180      -0.087       0.463
transcript_incomplete     0.4119      0.406      1.015      0.310      -0.384       1.207
zBMI                     -0.6012      0.171     -3.518      0.000      -0.936      -0.266
zAttractiveness           0.3039      0.144      2.114      0.035       0.022       0.586
zAgeAI                   -0.0832      0.153     -0.545      0.585      -0.382       0.216
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
Time:                        00:13:20   Log-Likelihood:                -200.64
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
Time:                        00:13:20   Log-Likelihood:                -201.79
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
