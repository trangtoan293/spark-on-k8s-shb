{%- macro shb_rule_field_apply_config_yml() -%}
{%- set yml -%}
name: shb
version: '1.0.0'

KTL_MDM:
  - product: INDIVIDUAL
    source_system:
      - name: SHB
        cleansing:
          - name: CL1
            list_column:
              - QUOC_TICH
          - name: CL2
            list_column:
              - LOAI_GTTT
          - name: CL3
            list_column:
              - NOI_CAP_GTTT
          - name: CL4
            list_column:
              - PASS_E_DT
          - name: CL5
            list_column:
              - MOBILE
              - RES_PH_NO_1
              - RES_PH_NO_2
        validate:
          - name: V1
            list_column:
              - PASS_E_DT
          - name: V2
            list_column:
              - MOBILE
          - name: V3
            list_column:
              - MOBILE
          - name: V4
            list_column:
              - PASS_NO
          - name: V5
            list_column:
              - LOAI_GTTT
          - name: V6
            list_column:
              - PASS_E_DT
          - name: V7
            list_column:
              - PASS_I_DT
          - name: V8
            list_column:
              - QUOC_TICH
        match:
          - name: M1
            type: manual
            straight:
              match_column_1: LOAI_GTTT
              match_column_2: PASS_NO
          - name: M2
            type: manual
            straight:
              match_column_1: F_NAME
              match_column_2: M_NAME
              match_column_3: L_NAME
              match_column_4: D_O_B
              match_column_5: SEX_CD
              match_column_6: CUSTOMER_TYPE
        matched_by_rules:
          - name: M1
            type: manual
            straight:
              match_column_1: LOAI_GTTT
              match_column_2: PASS_NO
          - name: M2
            type: manual
            straight:
              match_column_1: F_NAME
              match_column_2: M_NAME
              match_column_3: L_NAME
              match_column_4: D_O_B
              match_column_5: SEX_CD
              match_column_6: CUSTOMER_TYPE
        merge:
          - name: M3
          - name: M4
{%- endset -%}
{%- set model = fromyaml(yml) -%}
{{ return(model) }}
{%- endmacro -%}
