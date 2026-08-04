# Robustness grid — breadth vs modularity (shared controls)

n = 376 cases, HC1 robust SEs (BMI paper: `vce(robust)`)
cases file: `data\theory_dags\analysis\v151_crossed\gotselected_analysis_cases.csv`
IVs: breadth, modularity, balance, granularity

## BMI paper Study 2 baseline

```
logit GotSelected c.zBMI##c.know_cent_biz Gender AgeAI RaceAI Attractiveness ent_formality_13 i.eventID, vce(robust)
```

Our closest match: **C5** (z demographics + zBMI + event FE) and **C8/C9** (add word count, truncation, presenter count).

## Significant quadratic (p<.05) by IV

             n_specs  quad_sig  lrt_sig  lin_sig
iv                                              
balance           12         0        0        1
breadth           12         0        3        0
granularity       12         1        1        1
modularity        12         0        1        4

## Full grid (quad p-values)

### breadth

                  controls  linear_b  linear_p  quad_b  quad_p  lrt_quad_p  inverted_u_sig
                   C0 none    0.0900    0.4887 -0.1325  0.1472      0.1254           False
           C1 word_count_z    0.0127    0.9255 -0.0975  0.2960      0.2866           False
          C2 BMI_paper_raw    0.0806    0.5868 -0.2137  0.0584      0.0294           False
            C3 BMI_paper_z    0.0806    0.5868 -0.2137  0.0584      0.0294           False
            C4 BMI+eventFE    0.0956    0.6292 -0.2677  0.1170         NaN           False
       C5 BMI+eventFE+zBMI    0.1182    0.5589 -0.2400  0.1823      0.0902           False
              C6 meas_plan   -0.0288    0.8667 -0.2061  0.0897      0.0800           False
        C7 meas+appearance    0.0593    0.8021 -0.3587  0.1054      0.0336           False
C8 meas+appearance+eventFE       NaN       NaN     NaN     NaN         NaN           False
    C9 full+BMI_moderators       NaN       NaN     NaN     NaN         NaN           False
         C10 full+industry       NaN       NaN     NaN     NaN         NaN           False
             C11 full+year       NaN       NaN     NaN     NaN         NaN           False

### modularity

                  controls  linear_b  linear_p  quad_b  quad_p  lrt_quad_p  inverted_u_sig
                   C0 none    0.3220    0.0076 -0.0116  0.8715      0.8838           False
           C1 word_count_z    0.2889    0.0216 -0.0020  0.9775      0.9803           False
          C2 BMI_paper_raw    0.2440    0.0770 -0.0950  0.3260      0.3524           False
            C3 BMI_paper_z    0.2440    0.0770 -0.0950  0.3260      0.3524           False
            C4 BMI+eventFE    0.3161    0.0835  0.0258  0.8188      0.8336           False
       C5 BMI+eventFE+zBMI    0.3659    0.0528  0.0138  0.9032      0.0000           False
              C6 meas_plan    0.5413    0.0007  0.0075  0.9263      0.9433           False
        C7 meas+appearance    0.5205    0.0050 -0.0657  0.6165      0.6700           False
C8 meas+appearance+eventFE       NaN       NaN     NaN     NaN         NaN           False
    C9 full+BMI_moderators       NaN       NaN     NaN     NaN         NaN           False
         C10 full+industry       NaN       NaN     NaN     NaN         NaN           False
             C11 full+year       NaN       NaN     NaN     NaN         NaN           False

### balance

                  controls  linear_b  linear_p  quad_b  quad_p  lrt_quad_p  inverted_u_sig
                   C0 none    0.1930    0.2541 -0.0444  0.5529      0.5793           False
           C1 word_count_z    0.1773    0.2930 -0.0282  0.6888      0.7326           False
          C2 BMI_paper_raw    0.0570    0.7551 -0.0786  0.4054      0.3983           False
            C3 BMI_paper_z    0.0570    0.7551 -0.0786  0.4054      0.3983           False
            C4 BMI+eventFE    0.0288    0.9006 -0.0479  0.6681         NaN           False
       C5 BMI+eventFE+zBMI       NaN       NaN     NaN     NaN         NaN           False
              C6 meas_plan    0.4551    0.0239  0.0042  0.9589      0.9691           False
        C7 meas+appearance    0.3099    0.1765 -0.0075  0.9458      0.9586           False
C8 meas+appearance+eventFE       NaN       NaN     NaN     NaN         NaN           False
    C9 full+BMI_moderators       NaN       NaN     NaN     NaN         NaN           False
         C10 full+industry       NaN       NaN     NaN     NaN         NaN           False
             C11 full+year       NaN       NaN     NaN     NaN         NaN           False

### granularity

                  controls  linear_b  linear_p  quad_b  quad_p  lrt_quad_p  inverted_u_sig
                   C0 none    0.1563    0.2535 -0.2050  0.0759      0.0648           False
           C1 word_count_z    0.2160    0.1225 -0.1716  0.1552      0.1386           False
          C2 BMI_paper_raw    0.1466    0.3158 -0.2265  0.0503      0.0535           False
            C3 BMI_paper_z    0.1466    0.3158 -0.2265  0.0503      0.0535           False
            C4 BMI+eventFE       NaN       NaN     NaN     NaN         NaN           False
       C5 BMI+eventFE+zBMI       NaN       NaN     NaN     NaN         NaN           False
              C6 meas_plan    0.3928    0.0186 -0.2647  0.0387      0.0439            True
        C7 meas+appearance    0.2594    0.1732 -0.2567  0.0540      0.0754           False
C8 meas+appearance+eventFE       NaN       NaN     NaN     NaN         NaN           False
    C9 full+BMI_moderators       NaN       NaN     NaN     NaN         NaN           False
         C10 full+industry       NaN       NaN     NaN     NaN         NaN           False
             C11 full+year       NaN       NaN     NaN     NaN         NaN           False

