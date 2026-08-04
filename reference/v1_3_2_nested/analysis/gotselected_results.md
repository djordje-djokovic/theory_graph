GotSelected analysis — n=376 cases
============================================================

## M1 breadth quadratic + word count
```
                           Logit Regression Results                           
==============================================================================
Dep. Variable:            GotSelected   No. Observations:                  376
Model:                          Logit   Df Residuals:                      372
Method:                           MLE   Df Model:                            3
Date:                Sun, 02 Aug 2026   Pseudo R-squ.:                 0.02737
Time:                        10:03:08   Log-Likelihood:                -197.83
converged:                       True   LL-Null:                       -203.39
Covariance Type:            nonrobust   LLR p-value:                   0.01103
=====================================================================================
                        coef    std err          z      P>|z|      [0.025      0.975]
-------------------------------------------------------------------------------------
Intercept            -1.1563      0.153     -7.541      0.000      -1.457      -0.856
breadth_z             0.3734      0.151      2.474      0.013       0.078       0.669
I(breadth_z ** 2)    -0.1038      0.107     -0.973      0.331      -0.313       0.105
word_count_z          0.1600      0.138      1.156      0.248      -0.111       0.431
=====================================================================================
```

## M2 domain count (collapsed) + word count
```
                           Logit Regression Results                           
==============================================================================
Dep. Variable:            GotSelected   No. Observations:                  376
Model:                          Logit   Df Residuals:                      372
Method:                           MLE   Df Model:                            3
Date:                Sun, 02 Aug 2026   Pseudo R-squ.:                 0.03491
Time:                        10:03:08   Log-Likelihood:                -196.29
converged:                       True   LL-Null:                       -203.39
Covariance Type:            nonrobust   LLR p-value:                  0.002643
========================================================================================
                           coef    std err          z      P>|z|      [0.025      0.975]
----------------------------------------------------------------------------------------
Intercept               -0.9655      0.160     -6.025      0.000      -1.280      -0.651
n_domains_cat[T.1-2]    -1.4593      0.547     -2.666      0.008      -2.532      -0.387
n_domains_cat[T.4-5]    -0.3292      0.268     -1.228      0.220      -0.855       0.196
word_count_z             0.2101      0.132      1.592      0.111      -0.049       0.469
========================================================================================
```

## M3 joint + truncation
```
                           Logit Regression Results                           
==============================================================================
Dep. Variable:            GotSelected   No. Observations:                  376
Model:                          Logit   Df Residuals:                      369
Method:                           MLE   Df Model:                            6
Date:                Sun, 02 Aug 2026   Pseudo R-squ.:                 0.05652
Time:                        10:03:08   Log-Likelihood:                -191.90
converged:                       True   LL-Null:                       -203.39
Covariance Type:            nonrobust   LLR p-value:                 0.0007989
========================================================================================
                           coef    std err          z      P>|z|      [0.025      0.975]
----------------------------------------------------------------------------------------
Intercept               -0.9897      0.193     -5.139      0.000      -1.367      -0.612
n_domains_cat[T.1-2]    -1.3661      0.551     -2.480      0.013      -2.446      -0.286
n_domains_cat[T.4-5]    -0.3495      0.272     -1.283      0.199      -0.883       0.184
breadth_z                0.3861      0.155      2.486      0.013       0.082       0.691
I(breadth_z ** 2)       -0.1213      0.112     -1.088      0.277      -0.340       0.097
word_count_z             0.1641      0.142      1.154      0.249      -0.115       0.443
truncated                0.5923      0.355      1.671      0.095      -0.103       1.287
========================================================================================
```

## M4 joint + appearance/demographics
```
                           Logit Regression Results                           
==============================================================================
Dep. Variable:            GotSelected   No. Observations:                  357
Model:                          Logit   Df Residuals:                      346
Method:                           MLE   Df Model:                           10
Date:                Sun, 02 Aug 2026   Pseudo R-squ.:                  0.1616
Time:                        10:03:08   Log-Likelihood:                -159.25
converged:                       True   LL-Null:                       -189.94
Covariance Type:            nonrobust   LLR p-value:                 1.988e-09
========================================================================================
                           coef    std err          z      P>|z|      [0.025      0.975]
----------------------------------------------------------------------------------------
Intercept               -1.4647      0.248     -5.915      0.000      -1.950      -0.979
n_domains_cat[T.1-2]    -1.2902      0.642     -2.009      0.045      -2.549      -0.031
n_domains_cat[T.4-5]    -0.3645      0.306     -1.191      0.234      -0.964       0.235
C(Gender)[T.1.0]         0.7464      0.321      2.327      0.020       0.118       1.375
breadth_z                0.5194      0.180      2.886      0.004       0.167       0.872
I(breadth_z ** 2)       -0.1249      0.127     -0.980      0.327      -0.375       0.125
word_count_z             0.1699      0.162      1.048      0.295      -0.148       0.488
truncated                0.7278      0.393      1.851      0.064      -0.043       1.498
zBMI                    -0.6175      0.175     -3.519      0.000      -0.961      -0.274
zAttractiveness          0.3419      0.150      2.286      0.022       0.049       0.635
zAgeAI                  -0.1229      0.160     -0.767      0.443      -0.437       0.191
========================================================================================
```

## Breadth curvature
linear: 0.3734 (p=0.0134)
quadratic: -0.1038 (p=0.3307)
turning point (z): 1.799
breadth_z range: [-2.73, 2.27]
Turning point inside observed range: True

## M0 breadth linear (nested)
```
                           Logit Regression Results                           
==============================================================================
Dep. Variable:            GotSelected   No. Observations:                  376
Model:                          Logit   Df Residuals:                      373
Method:                           MLE   Df Model:                            2
Date:                Sun, 02 Aug 2026   Pseudo R-squ.:                 0.02489
Time:                        10:03:08   Log-Likelihood:                -198.33
converged:                       True   LL-Null:                       -203.39
Covariance Type:            nonrobust   LLR p-value:                  0.006336
================================================================================
                   coef    std err          z      P>|z|      [0.025      0.975]
--------------------------------------------------------------------------------
Intercept       -1.2444      0.127     -9.799      0.000      -1.493      -0.995
breadth_z        0.3162      0.131      2.406      0.016       0.059       0.574
word_count_z     0.1807      0.136      1.331      0.183      -0.085       0.447
================================================================================
```
LRT quadratic vs linear: chi2(1)=1.010
