# Robustness grid — breadth vs modularity (shared controls)

n = 376 cases, HC1 robust SEs (BMI paper: `vce(robust)`)
cases file: `data\theory_dags\analysis\v132_nested\gotselected_analysis_cases.csv`
IVs: breadth, modularity, balance, granularity

## BMI paper Study 2 baseline

```
logit GotSelected c.zBMI##c.know_cent_biz Gender AgeAI RaceAI Attractiveness ent_formality_13 i.eventID, vce(robust)
```

Our closest match: **C5** (z demographics + zBMI + event FE) and **C8/C9** (add word count, truncation, presenter count).

## Significant quadratic (p<.05) by IV

             n_specs  quad_sig  lrt_sig  lin_sig
iv                                              
balance           12         0        0        0
breadth           12         0        0        6
granularity       12         0        0        2
modularity        12         0        5        1

## Full grid (quad p-values)

### breadth

                  controls  linear_b  linear_p  quad_b  quad_p  lrt_quad_p  inverted_u_sig
                   C0 none    0.4159    0.0024 -0.1204  0.1926      0.2273           False
           C1 word_count_z    0.3734    0.0093 -0.1038  0.2769      0.3148           False
          C2 BMI_paper_raw    0.5413    0.0005 -0.1152  0.2800      0.2992           False
            C3 BMI_paper_z    0.5413    0.0005 -0.1152  0.2800      0.2992           False
            C4 BMI+eventFE       NaN       NaN     NaN     NaN         NaN           False
       C5 BMI+eventFE+zBMI    0.5407    0.0060 -0.1419  0.2899         NaN           False
              C6 meas_plan    0.3352    0.0668 -0.0908  0.4475      0.4510           False
        C7 meas+appearance    0.6442    0.0161 -0.1404  0.4366      0.3494           False
C8 meas+appearance+eventFE       NaN       NaN     NaN     NaN         NaN           False
    C9 full+BMI_moderators       NaN       NaN     NaN     NaN         NaN           False
         C10 full+industry       NaN       NaN     NaN     NaN         NaN           False
             C11 full+year       NaN       NaN     NaN     NaN         NaN           False

### modularity

                  controls  linear_b  linear_p  quad_b  quad_p  lrt_quad_p  inverted_u_sig
                   C0 none    0.2644    0.0489 -0.2185  0.0688      0.0172           False
           C1 word_count_z    0.2236    0.0968 -0.2104  0.0817      0.0243           False
          C2 BMI_paper_raw    0.2664    0.0673 -0.2091  0.0716      0.0332           False
            C3 BMI_paper_z    0.2664    0.0673 -0.2091  0.0716      0.0332           False
            C4 BMI+eventFE    0.1246    0.4750 -0.2057  0.1910      0.0843           False
       C5 BMI+eventFE+zBMI       NaN       NaN     NaN     NaN         NaN           False
              C6 meas_plan    0.1655    0.3948 -0.2987  0.0572      0.0335           False
        C7 meas+appearance    0.2662    0.2600 -0.2307  0.2097      0.1907           False
C8 meas+appearance+eventFE       NaN       NaN     NaN     NaN         NaN           False
    C9 full+BMI_moderators       NaN       NaN     NaN     NaN         NaN           False
         C10 full+industry       NaN       NaN     NaN     NaN         NaN           False
             C11 full+year       NaN       NaN     NaN     NaN         NaN           False

### balance

                  controls  linear_b  linear_p  quad_b  quad_p  lrt_quad_p  inverted_u_sig
                   C0 none    0.1322    0.4656 -0.0487  0.5579      0.6054           False
           C1 word_count_z    0.0915    0.6147 -0.0473  0.5855      0.6260           False
          C2 BMI_paper_raw    0.1284    0.5155 -0.0364  0.7107      0.7336           False
            C3 BMI_paper_z    0.1284    0.5155 -0.0364  0.7107      0.7336           False
            C4 BMI+eventFE       NaN       NaN     NaN     NaN         NaN           False
       C5 BMI+eventFE+zBMI    0.1074    0.6785 -0.1358  0.4745         NaN           False
              C6 meas_plan    0.2370    0.2995  0.0734  0.5599      0.5920           False
        C7 meas+appearance    0.3326    0.2513  0.1058  0.4777      0.5163           False
C8 meas+appearance+eventFE       NaN       NaN     NaN     NaN         NaN           False
    C9 full+BMI_moderators       NaN       NaN     NaN     NaN         NaN           False
         C10 full+industry       NaN       NaN     NaN     NaN         NaN           False
             C11 full+year       NaN       NaN     NaN     NaN         NaN           False

### granularity

                  controls  linear_b  linear_p  quad_b  quad_p  lrt_quad_p  inverted_u_sig
                   C0 none   -0.2007    0.1175 -0.0073  0.9389      0.9402           False
           C1 word_count_z   -0.1741    0.1827 -0.0000  0.9999      0.9999           False
          C2 BMI_paper_raw   -0.2835    0.0416 -0.0077  0.9378      0.9417           False
            C3 BMI_paper_z   -0.2835    0.0416 -0.0077  0.9378      0.9417           False
            C4 BMI+eventFE   -0.2502    0.1492 -0.0509  0.6618      0.6777           False
       C5 BMI+eventFE+zBMI       NaN       NaN     NaN     NaN         NaN           False
              C6 meas_plan   -0.2060    0.2183  0.0611  0.6049      0.6034           False
        C7 meas+appearance   -0.2864    0.1490  0.0332  0.8108      0.8082           False
C8 meas+appearance+eventFE       NaN       NaN     NaN     NaN         NaN           False
    C9 full+BMI_moderators       NaN       NaN     NaN     NaN         NaN           False
         C10 full+industry       NaN       NaN     NaN     NaN         NaN           False
             C11 full+year       NaN       NaN     NaN     NaN         NaN           False

