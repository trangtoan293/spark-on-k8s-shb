{%- macro shb_rule_desc_config_yml() -%}
{%- set yml -%}
name: shb
version: '1.0.0'

cleansing:
  - code: CL1
    description: 'Standardize QUOC_TICH via Danhmuc_QuocGia: map MA_QG/QUOC_GIA/abbr to TEN_QG/TEN_VT/full; keep original if not mapped'
    rule_template: cleantp_replace_category
    catalog_condition: var('shb_quoc_tich_catalog')
    column_condition: 'QUOC_TICH:quoc_tich'
  - code: CL2
    description: 'Standardize LOAI_GTTT via Danhmuc_Loai_GTTT: map old values (GTTT) to new standard (LOAI_GTTT); keep original if not mapped'
    rule_template: cleantp_replace_category
    catalog_condition: var('shb_loai_gttt_catalog')
    column_condition: 'LOAI_GTTT:loai_gttt'
  - code: CL3
    description: 'Remove special characters from NOI_CAP_GTTT (keep letters and safe punctuation: _ -,.;)'
    rule_template: cleantp_remove_pattern
    character: '[^A-Za-z_\-\.\, ;]'
  - code: CL4
    description: 'If PASS_E_DT cannot be parsed as date MM/DD/YYYY, set to null (after V1 marks invalid dates)'
    rule_template: cleantp_format_datetime
    from_str_format: 'MM/DD/YYYY'
  - code: CL5
    description: 'Remove non-digits from MOBILE (and RES_PH_NO_1, RES_PH_NO_2 if present)'
    rule_template: cleantp_remove_pattern
    character: '[^0-9]'

validate:
  - code: V1
    description: 'PASS_E_DT must be convertible to date MM/DD/YYYY (future dates or malformed are invalid)'
    rule_template: validatetp_regex_not_like
    regex_pattern: '^[0-9]{2}/[0-9]{2}/[0-9]{4}$'
    warning_null: NO
  - code: V2
    description: 'MOBILE must contain only digits (no special characters)'
    rule_template: validatetp_regex_not_like
    regex_pattern: '^[0-9]+$'
    warning_null: NO
  - code: V3
    description: 'Phone length/format: if starts with 0 then 10 digits; if starts with [35789] then 9 digits (after cleansing)'
    rule_template: validatetp_regex_not_like
    regex_pattern: '^(0[0-9]{9}|[35789][0-9]{8})$'
    warning_null: NO
  - code: V4
    description: 'PASS_NO length depends on LOAI_GTTT: CCCD/THE CAN CUOC = 12 digits; CMTND/CMTQD = 9 or 12 digits'
    rule_template: validatetp_regex_not_like
    warning_null: NO
  - code: V5
    description: 'LOAI_GTTT must belong to allowed set per Danhmuc_Loai_GTTT (values not in the catalog are invalid)'
    rule_template: check_invalid_category
    catalog_condition: var('shb_loai_gttt_catalog')
    warning_null: NO
  - code: V6
    description: 'For CCCD/THE CAN CUOC, PASS_E_DT must equal PASS_I_DT + 15 years'
    rule_template: check_active_datetime_legal_id
    condition: '15:0'
  - code: V7
    description: 'PASS_I_DT must be after D_O_B and not after CIF open date (if provided)'
    rule_template: check_legal_id_range_datetime
    column_condition: 'KDI7:{{ var("shb_cif_open_date_col") }}'
  - code: V8
    description: 'QUOC_TICH must not be in special-control list per Danhmuc_QuocGia where KIEM_SOAT = 1'
    rule_template: check_invalid_category
    catalog_condition: var('shb_special_nationality_catalog')
    warning_null: NO

match:
  - code: M1
    description: 'Match on LOAI_GTTT and PASS_NO duplicates across core records'
    rule_template: match_manual_straight
    straight:
      match_column_1: LOAI_GTTT
      match_column_2: PASS_NO
  - code: M2
    description: 'Match individuals on F_NAME, M_NAME, L_NAME, D_O_B, SEX_CD (CUSTOMER_TYPE=I)'
    rule_template: match_manual_straight
    straight:
      match_column_1: F_NAME
      match_column_2: M_NAME
      match_column_3: L_NAME
      match_column_4: D_O_B
      match_column_5: SEX_CD
      match_column_6: CUSTOMER_TYPE

merge:
  - code: M3
    description: 'Merge address: prefer CARD_ADDR when available, else CORE_CIF RES_ADD_1'
    rule_template: merge_address
    source_address_table: var('shb_card_addr_table')
    target_address_column: RES_ADD_1
  - code: M4
    description: 'Merge duplicates: prefer records without invalids; then lowest error count; then individual; then newest CIF'
    rule_template: merge_dedup_priority
{%- endset -%}
{%- set model = fromyaml(yml) -%}
{{ return(model) }}
{%- endmacro -%}
