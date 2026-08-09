GotSelected analysis — n=375 cases
============================================================

## M1 breadth quadratic + word count
```
                           Logit Regression Results                           
==============================================================================
Dep. Variable:            GotSelected   No. Observations:                  375
Model:                          Logit   Df Residuals:                      371
Method:                           MLE   Df Model:                            3
Date:                Sun, 09 Aug 2026   Pseudo R-squ.:                0.008935
Time:                        05:31:57   Log-Likelihood:                -201.32
converged:                       True   LL-Null:                       -203.13
Covariance Type:            nonrobust   LLR p-value:                    0.3043
=====================================================================================
                        coef    std err          z      P>|z|      [0.025      0.975]
-------------------------------------------------------------------------------------
Intercept            -1.1256      0.149     -7.546      0.000      -1.418      -0.833
breadth_z            -0.0667      0.141     -0.474      0.635      -0.343       0.209
I(breadth_z ** 2)    -0.0878      0.096     -0.916      0.360      -0.276       0.100
word_count_z          0.1722      0.124      1.385      0.166      -0.072       0.416
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
Date:                Sun, 09 Aug 2026   Pseudo R-squ.:                0.009197
Time:                        05:31:57   Log-Likelihood:                -201.26
converged:                       True   LL-Null:                       -203.13
Covariance Type:            nonrobust   LLR p-value:                    0.4428
=========================================================================================
                            coef    std err          z      P>|z|      [0.025      0.975]
-----------------------------------------------------------------------------------------
Intercept                -1.1389      0.155     -7.356      0.000      -1.442      -0.835
breadth_z                -0.0658      0.141     -0.467      0.640      -0.342       0.210
I(breadth_z ** 2)        -0.0902      0.096     -0.936      0.349      -0.279       0.099
word_count_z              0.1752      0.125      1.405      0.160      -0.069       0.420
transcript_incomplete     0.1232      0.374      0.329      0.742      -0.610       0.857
=========================================================================================
```

## M4 breadth + appearance/demographics
```
                           Logit Regression Results                           
==============================================================================
Dep. Variable:            GotSelected   No. Observations:                  356
Model:                          Logit   Df Residuals:                      347
Method:                           MLE   Df Model:                            8
Date:                Sun, 09 Aug 2026   Pseudo R-squ.:                  0.1051
Time:                        05:31:57   Log-Likelihood:                -169.75
converged:                       True   LL-Null:                       -189.68
Covariance Type:            nonrobust   LLR p-value:                 3.405e-06
=========================================================================================
                            coef    std err          z      P>|z|      [0.025      0.975]
-----------------------------------------------------------------------------------------
Intercept                -1.7038      0.211     -8.087      0.000      -2.117      -1.291
C(Gender)[T.1.0]          0.8680      0.309      2.805      0.005       0.262       1.474
breadth_z                -0.0648      0.153     -0.424      0.671      -0.364       0.234
I(breadth_z ** 2)        -0.0005      0.095     -0.005      0.996      -0.187       0.186
word_count_z              0.1956      0.141      1.391      0.164      -0.080       0.471
transcript_incomplete     0.4317      0.406      1.064      0.287      -0.363       1.226
zBMI                     -0.6056      0.172     -3.513      0.000      -0.943      -0.268
zAttractiveness           0.3051      0.142      2.141      0.032       0.026       0.584
zAgeAI                   -0.0661      0.152     -0.434      0.664      -0.365       0.232
=========================================================================================
```

## M5 breadth + premise similarity control + transcript incomplete
```
                           Logit Regression Results                           
==============================================================================
Dep. Variable:            GotSelected   No. Observations:                  375
Model:                          Logit   Df Residuals:                      369
Method:                           MLE   Df Model:                            5
Date:                Sun, 09 Aug 2026   Pseudo R-squ.:                0.009635
Time:                        05:31:57   Log-Likelihood:                -201.17
converged:                       True   LL-Null:                       -203.13
Covariance Type:            nonrobust   LLR p-value:                    0.5618
=========================================================================================
                            coef    std err          z      P>|z|      [0.025      0.975]
-----------------------------------------------------------------------------------------
Intercept                -1.1433      0.155     -7.361      0.000      -1.448      -0.839
breadth_z                -0.0783      0.144     -0.545      0.586      -0.360       0.203
I(breadth_z ** 2)        -0.0871      0.096     -0.903      0.366      -0.276       0.102
premise_sim_mean_z       -0.0547      0.131     -0.418      0.676      -0.311       0.202
word_count_z              0.1722      0.125      1.377      0.169      -0.073       0.417
transcript_incomplete     0.1288      0.375      0.344      0.731      -0.605       0.863
=========================================================================================
```

## Breadth curvature
linear: -0.0667 (p=0.6353)
quadratic: -0.0878 (p=0.3599)
turning point (z): -0.380

## M0 breadth linear (nested)
```
                           Logit Regression Results                           
==============================================================================
Dep. Variable:            GotSelected   No. Observations:                  375
Model:                          Logit   Df Residuals:                      372
Method:                           MLE   Df Model:                            2
Date:                Sun, 09 Aug 2026   Pseudo R-squ.:                0.006639
Time:                        05:31:57   Log-Likelihood:                -201.78
converged:                       True   LL-Null:                       -203.13
Covariance Type:            nonrobust   LLR p-value:                    0.2596
================================================================================
                   coef    std err          z      P>|z|      [0.025      0.975]
--------------------------------------------------------------------------------
Intercept       -1.2072      0.123     -9.784      0.000      -1.449      -0.965
breadth_z       -0.1059      0.128     -0.825      0.410      -0.358       0.146
word_count_z     0.1901      0.122      1.554      0.120      -0.050       0.430
================================================================================
```
LRT quadratic vs linear: chi2(1)=0.933
