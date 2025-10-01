
{{ config(
    materialized='incremental',
    incremental_strategy='append'
) }}

SELECT 
    SAT.DV_LDT AS DV_LDT,
    cob_date AS COB_DATE,
    sat.BRN_CODE,
    hub.CUS_CUSTOMER_CODE KDC1,
    sat.CUS_NAME_1 KDC2,
    CAST(NULL AS string) KDC3,
    CAST(NULL AS string) KDC4,
    sat.CUS_ESTAB_CODE KDC5_01,
    sat.CUS_ESTAB_CODE_ISS_DATE KDC5_02,
    sat.CUS_ESTAB_CODE_ISS_AUTH KDC5_03,
    CAST(NULL AS string) KDC6,
    CAST(NULL AS string) KDC7,
    CAST(NULL AS string) KDC8,
    sat.CUS_EMAIL_1 AS KDC9,
    sat.CUS_STREET KDC10,
    CAST(NULL AS string) KDC11,
    CAST(NULL AS string) KDC11_01,
    CAST(NULL AS string) KDC11_02,
    CAST(NULL AS string) KDC11_03,
    CAST(NULL AS string) KDC11_04,
    CAST(NULL AS string) KDC11_05,
    CAST(NULL AS string) KDC12,
    CAST(NULL AS string) KDC13,
    CAST(NULL AS string) KDC14_01,
    CAST(NULL AS string) KDC14_02,
    CAST(NULL AS string) KDC14_03,
    CAST(NULL AS string) KDC14_04,
    CAST(NULL AS string) KDC14_05,
    CAST(NULL AS string) KDC15_01,
    CAST(NULL AS string) KDC15_02,
    CAST(NULL AS string) KDC15_03,
    CAST(NULL AS string) KDC15_04,
    CAST(NULL AS string) KDC15_05,
    sat.CUS_TAX_ID KDC16_01,
    sat.CUS_TAX_ID_ISS_DATE KDC16_02,
    sat.CUS_TAX_ID_ISS_AUTH KDC16_03,
    CAST(NULL AS string) KDC17,
    CAST(NULL AS string) KDC18,
    CAST(NULL AS string) KDC19,
    CAST(NULL AS string) KDC20,
    sat.CUS_RESIDENCE KDC21,
    CAST(NULL AS string) KDC22_01,
    CAST(NULL AS string) KDC22_02,
    CAST(NULL AS string) KDC23_01,
    CAST(NULL AS string) KDC23_02,
    CAST(NULL AS string) KDC24_01,
    CAST(NULL AS string) KDC24_02,
    CAST(NULL AS string) KDC25_01,
    CAST(NULL AS string) KDC25_02,
    CAST(NULL AS string) KDC26,
    CAST(NULL AS string) KDC27,
    sat.CB_MOBILE_NO KDC28,
    CAST(NULL AS string) KDC29,
    CAST(NULL AS string) KDC30,
    sat.CUS_CREATION_DATE KDC31,
    CAST(NULL AS string) KDC32,
    CAST(NULL AS string) KDC33,
    hub.CUS_CUSTOMER_CODE KDC34,
    SAT.DV_LDT AS KDC1_CDT,
    SAT.DV_LDT AS KDC2_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC3_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC4_CDT,
    SAT.DV_LDT AS KDC5_01_CDT,
    SAT.DV_LDT AS KDC5_02_CDT,
    SAT.DV_LDT AS KDC5_03_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC6_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC7_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC8_CDT,
    SAT.DV_LDT AS KDC9_CDT,
    SAT.DV_LDT AS KDC10_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC11_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC11_01_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC11_02_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC11_03_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC11_04_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC11_05_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC12_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC13_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC14_01_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC14_02_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC14_03_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC14_04_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC14_05_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC15_01_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC15_02_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC15_03_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC15_04_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC15_05_CDT,
    SAT.DV_LDT AS KDC16_01_CDT,
    SAT.DV_LDT AS KDC16_02_CDT,
    SAT.DV_LDT AS KDC16_03_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC17_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC18_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC19_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC20_CDT,
    SAT.DV_LDT AS KDC21_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC22_01_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC22_02_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC23_01_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC23_02_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC24_01_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC24_02_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC25_01_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC25_02_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC26_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC27_CDT,
    SAT.DV_LDT AS KDC28_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC29_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC30_CDT,
    SAT.DV_LDT AS KDC31_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC32_CDT,
    CAST(NULL AS TIMESTAMP) AS KDC33_CDT,
    SAT.DV_LDT AS KDC34_CDT

FROM
    {{ ref("hub_corp") }} hub

{%- if is_incremental() %}
{# incremental load using latest date from ref_t24_dates and > max(cob_date) of this #}

    CROSS JOIN (
        select to_date(cob_date, 'YYYYMMDD') cob_date, run_time, last_run_time
        from {{ref("vw_ref_eod")}}
        where cob_date = (select max(cob_date) from {{ref("vw_ref_eod")}})
            and to_date(cob_date, 'YYYYMMDD') > (select max(cob_date) from {{this}})
    ) dt

    JOIN {{ ref("sat_snp_core_corp") }} sat 
        ON hub.dv_hkey_hub_corp = sat.dv_hkey_hub_corp
        AND hub.DV_CCD = 'CORE'
        AND sat.dv_src_ldt >= dt.last_run_time
        AND sat.dv_src_ldt < dt.run_time

{%- elif var('initial_date', none) is none %}
{# initial load without var initial_date #}

    CROSS JOIN (
        select to_date(cob_date, 'YYYYMMDD') cob_date
        from {{ref("vw_ref_eod")}}
        where cob_date = (select max(cob_date) from {{ref("vw_ref_eod")}})
    ) dt

    JOIN {{ ref("sat_snp_core_corp") }} SAT 
        ON hub.dv_hkey_hub_corp = sat.dv_hkey_hub_corp 
        AND hub.DV_CCD = 'CORE'

{%- else %}
{# initial load with var initial_date #}

    CROSS JOIN (select ({{ ktl_autovault.timestamp(var('initial_date')) }}) as cob_date from DUAL) dt

    JOIN (
        select a.*,
            row_number() over (
                partition by dv_hkey_hub_corp
                order by dv_src_ldt desc, dv_kaf_ldt desc, dv_kaf_ofs desc
            ) rnk
        from {{ ref("sat_core_corp") }} a
        where dv_src_ldt < {{ ktl_autovault.timestamp(var('initial_date')) }}
    ) sat
        ON hub.dv_hkey_hub_corp = sat.dv_hkey_hub_corp 
        AND hub.DV_CCD = 'CORE'
        AND sat.rnk = 1

{%- endif %}

WHERE 1=1 
