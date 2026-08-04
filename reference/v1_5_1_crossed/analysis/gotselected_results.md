GotSelected analysis — n=376 cases
============================================================

## M1 breadth quadratic + word count
```
                           Logit Regression Results                           
==============================================================================
Dep. Variable:            GotSelected   No. Observations:                  376
Model:                          Logit   Df Residuals:                      372
Method:                           MLE   Df Model:                            3
Date:                Sun, 02 Aug 2026   Pseudo R-squ.:                 0.01337
Time:                        10:03:29   Log-Likelihood:                -200.68
converged:                       True   LL-Null:                       -203.39
Covariance Type:            nonrobust   LLR p-value:                    0.1424
=====================================================================================
                        coef    std err          z      P>|z|      [0.025      0.975]
-------------------------------------------------------------------------------------
Intercept            -1.1286      0.149     -7.584      0.000      -1.420      -0.837
breadth_z             0.0127      0.146      0.087      0.930      -0.273       0.299
I(breadth_z ** 2)    -0.0975      0.096     -1.015      0.310      -0.286       0.091
word_count_z          0.2323      0.138      1.679      0.093      -0.039       0.503
=====================================================================================
```

## M2 domain count (collapsed) + word count
```
                           Logit Regression Results                           
==============================================================================
Dep. Variable:            GotSelected   No. Observations:                  376
Model:                          Logit   Df Residuals:                      372
Method:                           MLE   Df Model:                            3
Date:                Sun, 02 Aug 2026   Pseudo R-squ.:                 0.01996
Time:                        10:03:29   Log-Likelihood:                -199.33
converged:                       True   LL-Null:                       -203.39
Covariance Type:            nonrobust   LLR p-value:                   0.04360
========================================================================================
                           coef    std err          z      P>|z|      [0.025      0.975]
----------------------------------------------------------------------------------------
Intercept               -1.3133      0.201     -6.519      0.000      -1.708      -0.918
n_domains_cat[T.1-2]    -0.7925      0.646     -1.226      0.220      -2.059       0.474
n_domains_cat[T.4-5]     0.2631      0.258      1.020      0.308      -0.243       0.769
word_count_z             0.2194      0.131      1.670      0.095      -0.038       0.477
========================================================================================
```

## M3 joint + truncation
```
                           Logit Regression Results                           
==============================================================================
Dep. Variable:            GotSelected   No. Observations:                  376
Model:                          Logit   Df Residuals:                      369
Method:                           MLE   Df Model:                            6
Date:                Sun, 02 Aug 2026   Pseudo R-squ.:                 0.03208
Time:                        10:03:29   Log-Likelihood:                -196.87
converged:                       True   LL-Null:                       -203.39
Covariance Type:            nonrobust   LLR p-value:                   0.04228
========================================================================================
                           coef    std err          z      P>|z|      [0.025      0.975]
----------------------------------------------------------------------------------------
Intercept               -1.4023      0.236     -5.955      0.000      -1.864      -0.941
n_domains_cat[T.1-2]    -0.8365      0.654     -1.279      0.201      -2.118       0.445
n_domains_cat[T.4-5]     0.2976      0.261      1.138      0.255      -0.215       0.810
breadth_z               -0.0192      0.148     -0.129      0.897      -0.310       0.272
I(breadth_z ** 2)       -0.0857      0.097     -0.885      0.376      -0.275       0.104
word_count_z             0.2586      0.141      1.832      0.067      -0.018       0.535
truncated                0.5887      0.291      2.023      0.043       0.018       1.159
========================================================================================
```

## M4 joint + appearance/demographics
```
                           Logit Regression Results                           
==============================================================================
Dep. Variable:            GotSelected   No. Observations:                  357
Model:                          Logit   Df Residuals:                      346
Method:                           MLE   Df Model:                           10
Date:                Sun, 02 Aug 2026   Pseudo R-squ.:                  0.1373
Time:                        10:03:29   Log-Likelihood:                -163.85
converged:                       True   LL-Null:                       -189.94
Covariance Type:            nonrobust   LLR p-value:                 1.062e-07
========================================================================================
                           coef    std err          z      P>|z|      [0.025      0.975]
----------------------------------------------------------------------------------------
Intercept               -1.7800      0.270     -6.585      0.000      -2.310      -1.250
n_domains_cat[T.1-2]    -1.0784      0.724     -1.489      0.137      -2.498       0.341
n_domains_cat[T.4-5]     0.2252      0.287      0.784      0.433      -0.338       0.788
C(Gender)[T.1.0]         0.8564      0.319      2.687      0.007       0.232       1.481
breadth_z                0.0695      0.172      0.404      0.686      -0.268       0.407
I(breadth_z ** 2)       -0.1625      0.117     -1.387      0.165      -0.392       0.067
word_count_z             0.2494      0.158      1.579      0.114      -0.060       0.559
truncated                0.7606      0.327      2.327      0.020       0.120       1.401
zBMI                    -0.6355      0.176     -3.614      0.000      -0.980      -0.291
zAttractiveness          0.3365      0.147      2.291      0.022       0.049       0.624
zAgeAI                  -0.1211      0.154     -0.788      0.431      -0.422       0.180
========================================================================================
```

## Breadth curvature
linear: 0.0127 (p=0.9305)
quadratic: -0.0975 (p=0.3101)
turning point (z): 0.065
breadth_z range: [-2.78, 3.07]
Turning point inside observed range: True

## M0 breadth linear (nested)
```
                           Logit Regression Results                           
==============================================================================
Dep. Variable:            GotSelected   No. Observations:                  376
Model:                          Logit   Df Residuals:                      373
Method:                           MLE   Df Model:                            2
Date:                Sun, 02 Aug 2026   Pseudo R-squ.:                 0.01058
Time:                        10:03:29   Log-Likelihood:                -201.24
converged:                       True   LL-Null:                       -203.39
Covariance Type:            nonrobust   LLR p-value:                    0.1164
================================================================================
                   coef    std err          z      P>|z|      [0.025      0.975]
--------------------------------------------------------------------------------
Intercept       -1.2177      0.124     -9.814      0.000      -1.461      -0.974
breadth_z       -0.0279      0.133     -0.209      0.834      -0.289       0.233
word_count_z     0.2665      0.134      1.991      0.047       0.004       0.529
================================================================================
```
LRT quadratic vs linear: chi2(1)=1.135
